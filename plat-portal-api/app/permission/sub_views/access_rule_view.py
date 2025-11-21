from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from app.core.simple_authentication import get_app_name_from_request
from app.core.exceptions import InvalidParameterException
from app.core.logger import logger
from app.permission.config_static_varible.common import (
    CUSTOM_TYPE_CREATED_USER_KEY,
    CUSTOM_TYPE_CREATED_SYSTEM_KEY,
)
from app.permission.models import AccessRule, AccessRulePermission, CustomRoleAccessRule
from app.permission.permissions import IsAdminOrOwnerForActionRoleAndRule
from app.permission.services.compose_permission_service import ComposePermissionService
from app.permission.services.custom_role_service import CustomRoleService
from app.permission.sub_serializers.access_rule_serializer import (
    AccessRuleSerializer,
    AccessRuleForListingSerializer,
    AccessRuleDetailSerializer,
)
from app.permission.sub_views.base_view import (
    OrgClientBaseView,
    ClientAccessRuleBaseView,
)
from app.tenancies.config_app_and_module import APP_MODULE_BUILD_PROFILE


class AccessRuleRetrieveUpdateDestroyView(
    ClientAccessRuleBaseView, generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = (IsAdminOrOwnerForActionRoleAndRule,)
    serializer_class = AccessRuleDetailSerializer
    queryset = AccessRule.objects.all()

    content_object = None

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AccessRuleDetailSerializer
        #  put or patch
        return AccessRuleSerializer

    @swagger_auto_schema(
        operation_description="Update access rules with list permissions groups info",
        tags=["Roles & Rules"],
    )
    def put(self, request, *args, **kwargs):
        try:
            self.content_object = self.get_content_obj()
            return super(AccessRuleRetrieveUpdateDestroyView, self).put(
                request, *args, **kwargs
            )
        except AccessRule.DoesNotExist as err:
            raise err
        except Exception as err:
            logger.error("[AccessRuleRetrieveUpdateDestroyView][UPDATE] %s" % str(err))
            raise err

    def perform_update(self, serializer):
        with transaction.atomic():
            #  update access rule, changes permission in access rule
            super(AccessRuleRetrieveUpdateDestroyView, self).perform_update(serializer)
            #  sync permission on affected roles
            access_rule = serializer.instance
            affected_custom_role_ids = (
                CustomRoleService.get_custom_roles_config_contain_access_rule_client(
                    self.content_object, access_rule
                )
            )
            # get list id of user_client, user_org contain by list affected custom roles
            affected_content_object_ids = (
                CustomRoleService.get_list_org_ws_user_ids_by_custom_roles(
                    custom_role_ids=affected_custom_role_ids
                )
            )
            ComposePermissionService.sync_permission_of_user_client_org(
                affected_content_object_ids
            )

    @swagger_auto_schema(
        operation_description="Delete access rules in system", tags=["Roles & Rules"]
    )
    def delete(self, request, *args, **kwargs):
        try:
            self.content_object = self.get_content_obj()
            return super().delete(request, *args, **kwargs)
        except AccessRule.DoesNotExist as err:
            raise err
        except Exception as err:
            logger.error("[AccessRuleRetrieveUpdateDestroyView][DELETE] %s" % str(err))
            raise err

    def perform_destroy(self, instance):
        with transaction.atomic():
            AccessRulePermission.objects.filter(access_rule=instance).delete()

            custom_role_ids = CustomRoleAccessRule.objects.filter(
                access_rule=instance,
            ).values_list("custom_role_id", flat=True)
            affected_custom_role_ids = [str(i) for i in custom_role_ids]

            CustomRoleAccessRule.objects.filter(access_rule=instance).delete()
            instance.delete()

            # get list id of user_client, user_org contain by list affected custom roles
            affected_content_object_ids = (
                CustomRoleService.get_list_org_ws_user_ids_by_custom_roles(
                    custom_role_ids=affected_custom_role_ids
                )
            )
            ComposePermissionService.sync_permission_of_user_client_org(
                affected_content_object_ids
            )

    @swagger_auto_schema(tags=["Roles & Rules"])
    def get(self, request, *args, **kwargs):
        try:
            self.content_object = self.get_content_obj()
            return super().get(request, *args, **kwargs)
        except AccessRule.DoesNotExist as err:
            raise err
        except Exception as err:
            logger.error("[AccessRuleRetrieveUpdateDestroyView][GET] %s" % str(err))
            raise err

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            obj = AccessRule.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except AccessRule.DoesNotExist:
            raise InvalidParameterException(message="invalid access rule pk")


class ListCreateAccessRuleView(OrgClientBaseView, generics.ListCreateAPIView):
    permission_classes = (IsAdminOrOwnerForActionRoleAndRule,)

    content_object = None

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AccessRuleSerializer
        return AccessRuleForListingSerializer

    @swagger_auto_schema(
        operation_description="Create access rules with permissions groups config",
        tags=["Roles & Rules"],
    )
    def post(self, request, *args, **kwargs):
        try:
            self.content_object = self.get_content_obj()
            return super().post(request, *args, **kwargs)
        except Exception as err:
            logger.error("[ListCreateAccessRuleView][POST] %s" % str(err))
            raise err

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            type_created=CUSTOM_TYPE_CREATED_USER_KEY,
            content_object=self.content_object,
            level=self.get_level_view(),
        )

    keyword = openapi.Parameter(
        "keyword",
        in_=openapi.IN_QUERY,
        description="""Filter by name""",
        type=openapi.TYPE_STRING,
    )
    option_filter = openapi.Parameter(
        "option_filter",
        in_=openapi.IN_QUERY,
        description="""USER or SYSTEM """,
        type=openapi.TYPE_STRING,
    )
    is_user_assignment = openapi.Parameter(
        "is_user_assignment",
        in_=openapi.IN_QUERY,
        description="""Get all available scopes for user assignment""",
        type=openapi.TYPE_BOOLEAN,
    )

    def get_queryset(self):
        is_user_assignment = self.request.GET.get("is_user_assignment", False)
        is_user_assignment = True if is_user_assignment == "true" else False
        """
        if is a user assignment action -> filter by client_id and org_id
                                else   -> filter by client or org_id
        """
        list_object_ids = (
            self.get_serializer_context().get("object_ids")
            if is_user_assignment is True
            else self.get_serializer_context().get("object_id")
        )

        level = self.get_serializer_context().get("level")
        option_filter = self.request.GET.get("option_filter", None)

        app_name = get_app_name_from_request(request=self.request)
        available_modules = []
        if app_name:
            available_modules.extend(APP_MODULE_BUILD_PROFILE.get(app_name, []))

        cond_args = {
            CUSTOM_TYPE_CREATED_SYSTEM_KEY: Q(
                level=level,
                type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY,
            )
                                            & Q(Q(module__isnull=True) | Q(module__in=available_modules)),
            CUSTOM_TYPE_CREATED_USER_KEY: Q(object_id__in=list_object_ids),
            None: Q(object_id__in=list_object_ids)
                  | Q(
                Q(
                    level=level,
                    type_created=CUSTOM_TYPE_CREATED_SYSTEM_KEY,
                )
                & Q(Q(module__isnull=True) | Q(module__in=available_modules))
            ),
        }
        cond = cond_args.get(option_filter)

        keyword = self.request.GET.get("keyword", None)
        if keyword:
            return (
                AccessRule.objects.filter(cond)
                .filter(name__icontains=keyword)
                .order_by("-created")
            )
        return AccessRule.objects.filter(cond).order_by("-created")

    @swagger_auto_schema(
        operation_description="Get list access rules",
        manual_parameters=[keyword, option_filter, is_user_assignment],
        tags=["Roles & Rules"],
    )
    def get(self, request, *args, **kwargs):
        try:
            self.content_object = self.get_content_obj()
            return super().get(request, *args, **kwargs)
        except Exception as err:
            logger.error("[ListCreateAccessRuleView][POST] %s" % str(err))
            raise err
