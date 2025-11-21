import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.payments.services.utils import get_exclude_condition
from app.permission.config_static_varible.common import CLIENT_LEVEL_KEY
from app.permission.exceptions import PermissionGroupLevelException
from app.permission.services.permssion_group_service import PermissionGroupService
from app.permission.sub_serializers.permission_group_serializer import (
    PermissionGroupListSerializer,
)
from app.permission.sub_views.base_view import OrgClientBaseView

logger = logging.getLogger(__name__)


class OrgClientPermissionGroupListView(OrgClientBaseView, APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PermissionGroupListSerializer

    search = openapi.Parameter(
        "search",
        in_=openapi.IN_QUERY,
        description="Search name of group",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        operation_description="List permissions groups Org or Client level",
        manual_parameters=[search],
        responses={status.HTTP_200_OK: PermissionGroupListSerializer},
        tags=["Roles & Rules"],
    )
    def get(self, request, *args, **kwargs):
        try:
            search = request.query_params.get("search", None)
            exclude_permission = get_exclude_condition(
                org_id=self.__get_org_id
            )
            data = PermissionGroupService.get_permissions_groups_level(
                search=search,
                level=self.get_level_view(),
                exclude_cond=exclude_permission,
            )
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as ex:
            logger.error("[OrgClientPermissionGroupListView]", str(ex))
            raise PermissionGroupLevelException(
                message_content=str(ex), level=CLIENT_LEVEL_KEY
            )

    @property
    def __get_org_id(self):
        org = self.get_org()
        if org:
            return org.id
        client = self.get_client()
        return client.organization_id
