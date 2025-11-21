from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from app.core.context import AppContext
from app.financial.exceptions import UserPermissionsException
from app.financial.models import UserPermission
from app.financial.permissions.base import ClientUserSyncPermission
from app.financial.sub_serializers.client_serializer import UserPermissionSerializer
from app.core.variable.permission import MODULE_PF_KEY


class ClientUserSettingPermissionsView(generics.ListAPIView):
    permission_classes = (ClientUserSyncPermission,)
    serializer_class = UserPermissionSerializer

    def get_queryset(self):
        client_id = AppContext.instance().client_id
        user_id = AppContext.instance().user_id
        return UserPermission.objects.tenant_db_for(client_id).get(client_id=client_id, user_id=user_id, module=MODULE_PF_KEY)

    def get(self, request, *args, **kwargs):
        try:
            obj = self.get_queryset()
            data = UserPermissionSerializer(obj).data
            return Response(status=HTTP_200_OK, data=data)
        except Exception as ex:
            raise UserPermissionsException(message=str(ex), verbose=True)
