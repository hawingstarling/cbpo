from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.core.exceptions import InvalidParameterException
from app.core.logger import logger
from app.permission.config_static_varible.common import CUSTOM_TYPE_CREATED_USER_KEY, ROLE_CUSTOM_KEY, \
    CUSTOM_TYPE_CREATED_SYSTEM_KEY
from app.permission.exceptions import CustomRoleLevelException
from app.permission.models import CustomRole, CustomRoleAccessRule, OrgClientCustomRoleUser
from app.permission.permissions import IsAdminOrOwnerForActionRoleAndRule
from app.permission.services.compose_permission_service import ComposePermissionService
from app.permission.services.custom_role_service import CustomRoleService
from app.permission.sub_serializers.custom_role_serializer import (
    CustomRolePayloadUpdateSerializer, CustomRolePayloadBaseSerializer)
from app.permission.sub_serializers.custom_role_serializer import (
    CustomRoleSerializer, CustomRoleForListingSerializer, CustomRoleDetailSerializer)
from app.permission.sub_serializers.permission_group_serializer import PermissionGroupListSerializer
from app.permission.sub_views.base_view import ClientCustomRoleBaseView
from app.permission.sub_views.base_view import OrgClientBaseView


class CustomRoleListCreateOrgClientView(OrgClientBaseView, generics.ListCreateAPIView):
    permission_classes = (IsAdminOrOwnerForActionRoleAndRule,)
    content_obj = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomRoleSerializer
        return CustomRoleForListingSerializer

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Filter by name""",
                                type=openapi.TYPE_STRING)
    option_filter = openapi.Parameter('option_filter', in_=openapi.IN_QUERY,
                                      description="""USER or SYSTEM """,
                                      type=openapi.TYPE_STRING)
    is_user_assignment = openapi.Parameter('is_user_assignment', in_=openapi.IN_QUERY,
                                           description="""Get all available scopes for user assignment""",
                                           type=openapi.TYPE_BOOLEAN)

    @swagger_auto_schema(operation_description='Get list custom roles',
                         manual_parameters=[keyword, option_filter, is_user_assignment],
                         tags=["Roles & Rules"])
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as err:
            logger.error('[CustomRoleListCreateOrgClientView][GET] %s' % err)
            raise err

    def get_queryset(self):
        is_user_assignment = self.request.GET.get('is_user_assignment', False)
        is_user_assignment = True if is_user_assignment == 'true' else False
        '''
        if is a user assignment action -> filter by client_id and org_id
                                else   -> filter by client or org_id
        '''
        list_object_ids = self.get_serializer_context().get(
            'object_ids') if is_user_assignment is True else self.get_serializer_context().get('object_id')

        level = self.get_serializer_context().get('level')

        option_filter = self.request.GET.get('option_filter', None)
        cond_args = {
            CUSTOM_TYPE_CREATED_SYSTEM_KEY: Q(level=level, type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY),
            CUSTOM_TYPE_CREATED_USER_KEY: Q(object_id__in=list_object_ids),
            None: Q(object_id__in=list_object_ids) | (Q(level=level, type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY))
        }
        cond = cond_args.get(option_filter)
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            return CustomRole.objects.filter(cond).filter(name__icontains=keyword).order_by('-created')
        return CustomRole.objects.filter(cond).order_by('-created')

    @swagger_auto_schema(
        tags=["Roles & Rules"]
    )
    def post(self, request, *args, **kwargs):
        try:
            self.content_obj = self.get_content_obj()
            return super().post(request, *args, **kwargs)
        except Exception as err:
            logger.error('[CustomRoleListCreateOrgClientView][POST] %s' % err)
            raise err

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user,
                        type_created=CUSTOM_TYPE_CREATED_USER_KEY,
                        key=ROLE_CUSTOM_KEY,
                        content_object=self.content_obj,
                        level=self.get_level_view())


class CustomRoleRetrieveUpdateDetailDeleteOrgClientView(ClientCustomRoleBaseView,
                                                        generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminOrOwnerForActionRoleAndRule,)
    serializer_class = CustomRoleDetailSerializer
    queryset = CustomRole.objects.all()

    content_object = None

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'DELETE':
            return CustomRoleSerializer
        #  get
        return CustomRoleDetailSerializer

    @swagger_auto_schema(
        tags=["Roles & Rules"]
    )
    def get(self, request, *args, **kwargs):
        try:
            self.get_content_obj()
            return super().get(request, *args, **kwargs)
        except CustomRole.DoesNotExist as err:
            raise err
        except Exception as err:
            logger.error('[CustomRoleRetrieveUpdateDetailDeleteOrgClientView][GET] %s' % err)
            raise err

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            obj = CustomRole.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except CustomRole.DoesNotExist:
            raise InvalidParameterException(message='invalid custom role pk')

    @swagger_auto_schema(
        operation_description="Update custom role with list access rule config",
        request_body=CustomRolePayloadUpdateSerializer,
        tags=["Roles & Rules"]
    )
    def put(self, request, *args, **kwargs):
        try:
            self.content_object = self.get_content_obj()
            return super().put(request, *args, **kwargs)
        except CustomRole.DoesNotExist as custom_exc:
            raise custom_exc
        except Exception as err:
            logger.error('[CustomRoleRetrieveUpdateDetailDeleteOrgClientView][PUT] %s' % err)
            raise err

    def perform_update(self, serializer):
        super(CustomRoleRetrieveUpdateDetailDeleteOrgClientView, self).perform_update(serializer)
        with transaction.atomic():
            # sync permission on affected objects
            # get list id of user_client, user_org contain by list affected custom roles
            affected_content_object_ids = CustomRoleService.get_list_org_ws_user_ids_by_custom_roles(
                custom_role_ids=[serializer.instance.id])
            ComposePermissionService.sync_permission_of_user_client_org(affected_content_object_ids)

    @swagger_auto_schema(
        operation_description="Delete custom role of client level",
        tags=["Roles & Rules"]
    )
    def delete(self, request, *args, **kwargs):
        try:
            self.content_object = self.get_content_obj()
            return super(CustomRoleRetrieveUpdateDetailDeleteOrgClientView, self).delete(request, *args, **kwargs)
        except CustomRole.DoesNotExist as custom_exc:
            raise custom_exc
        except Exception as err:
            logger.error('[CustomRoleRetrieveUpdateDetailDeleteOrgClientView][DELETE] %s' % err)
            raise err

    def perform_destroy(self, instance):
        with transaction.atomic():
            CustomRoleAccessRule.objects.filter(custom_role=instance).delete()

            affected_content_object_ids = CustomRoleService.get_list_org_ws_user_ids_by_custom_roles(
                custom_role_ids=[instance.id])

            OrgClientCustomRoleUser.objects.filter(custom_role=instance).delete()
            instance.delete()

            ComposePermissionService.sync_permission_of_user_client_org(affected_content_object_ids)


class CustomRolePreviewOrgClientView(OrgClientBaseView, APIView):
    permission_classes = (IsAdminOrOwnerForActionRoleAndRule,)

    @swagger_auto_schema(
        operation_description="Custom role preview by list config access rules",
        request_body=CustomRolePayloadBaseSerializer,
        responses={status.HTTP_200_OK: PermissionGroupListSerializer},
        tags=["Roles & Rules"]
    )
    def post(self, request, *args, **kwargs):
        level = self.get_level_view()
        try:
            data = request.data
            serializer_class = CustomRolePayloadBaseSerializer(data=data,
                                                               context={'level': level,
                                                                        'content_obj': self.get_content_obj(),
                                                                        'client_ids': self.get_client_ids(),
                                                                        'object_ids': self.get_object_ids()})
            serializer_class.is_valid(raise_exception=True)
            validated_data = serializer_class.validated_data
            rs = serializer_class.preview_permissions_groups(data=validated_data['access_rules'])
            return Response(status=status.HTTP_200_OK, data=rs)
        except Exception as ex:
            logger.error('[CustomRolePreviewOrgClientView][{level}]: {message}'.format(level=level, message=str(ex)))
            raise CustomRoleLevelException(message_content=str(ex), level=level)
