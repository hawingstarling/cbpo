from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from app.core.exceptions import InvalidParameterException
from app.core.logger import logger
from app.permission.exceptions import UserClientMemberException, UserLevelCustomRolePermissionException
from app.permission.permissions import IsAdminOrOwnerForActionRoleAndRule
from app.permission.services.compose_permission_service import ComposePermissionService
from app.permission.services.custom_role_service import CustomRoleService
from app.permission.sub_serializers.compose_final_permission_serializer import (
    ComposePermissionSerializer, PermissionGroupingResSerializer, COMPOSE_TYPE_APPROVE_KEY,
    UserClientCustomRoleGETPayloadSerializer)
from app.permission.sub_views.base_view import OrgClientBaseView
from app.tenancies.models import User
from app.tenancies.activity_services import ActivityService
from app.tenancies.tasks import log_activity_task


class ComposePermissionView(OrgClientBaseView, APIView):
    permission_classes = (IsAdminOrOwnerForActionRoleAndRule,)

    def get_user_in_param(self):
        try:
            return User.objects.get(pk=self.kwargs.get('user_id'))
        except User.DoesNotExist:
            raise InvalidParameterException(message="user 'pk' does not exist")

    @swagger_auto_schema(
        operation_description="Get user custom role permissions client level",
        responses={status.HTTP_200_OK: UserClientCustomRoleGETPayloadSerializer},
        tags=["Roles & Rules"]
    )
    def get(self, request, *args, **kwargs):
        level = self.get_level_view()
        granted_user = self.get_user_in_param()
        try:
            generic_obj_user_request = self.get_content_object_user(granted_user)
            serializer_class = UserClientCustomRoleGETPayloadSerializer(
                context={
                    'generic_obj_user_request': generic_obj_user_request,
                    'level': level
                }
            )
            data = serializer_class.get_payloads_data()
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as ex:
            logger.error('[UserRolePermissionClientView][GET]', str(ex))
            raise UserLevelCustomRolePermissionException(message_content=str(ex), level=level)

    @swagger_auto_schema(
        operation_description="Compose Permission Client",
        request_body=ComposePermissionSerializer,
        responses={status.HTTP_200_OK: PermissionGroupingResSerializer},
        tags=["Roles & Rules"]
    )
    def post(self, request, *args, **kwargs):
        try:
            granted_user = self.get_user_in_param()
            content_object_user = self.get_content_object_user(granted_user)
            content_obj = self.get_content_obj()
            level = self.get_level_view()
            serializer = ComposePermissionSerializer(data=request.data, context={'object_ids': self.get_object_ids(),
                                                                                 'level': level})
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            roles = validated_data.get('roles')
            roles = sorted(roles, key=lambda x: x['priority'])
            role_ids = [item['id'] for item in roles]
            overriding_permissions_groups = validated_data.get('permissions_groups')

            default_custom_role_ids = CustomRoleService.get_default_role_ids(content_object_user, level)

            access_rule_query_set = ComposePermissionService.compose_access_rules_from_custom_roles(
                [*role_ids, *default_custom_role_ids])
            res_composed = ComposePermissionService.compose_permission_from_access_rules(access_rule_query_set,
                                                                                         overriding_permissions_groups)

            action = validated_data.get('type')
            if action == COMPOSE_TYPE_APPROVE_KEY:
                CustomRoleService.sync_custom_roles_of_org_client_users(generic_obj=content_object_user,
                                                                        custom_role_ids=role_ids)
                ComposePermissionService.save_overriding_permission(overriding_permissions_groups, content_object_user)
                ComposePermissionService.save_composed_permission(res_composed, content_object_user)

            res_composed = ComposePermissionService.filter_org_client_user_permission_dict(res_composed, level,
                                                                                           content_obj)
            res = ComposePermissionService.group_composed_permission(res_composed)
            if action == COMPOSE_TYPE_APPROVE_KEY:
                # Log update member activity
                data = ComposePermissionService.rearrange_data_to_log_activity(res)
                log_activity_task.delay(user_id=request.user.pk, action=ActivityService.action_update_member(), data=data)

            return Response(status=status.HTTP_200_OK, data={'permissions_groups': res})

        except ValidationError as err:
            raise err
        except UserClientMemberException as err:
            raise err
        except Exception as err:
            logger.error('[ComposePermissionView][POST] %s' % str(err))
            raise err
