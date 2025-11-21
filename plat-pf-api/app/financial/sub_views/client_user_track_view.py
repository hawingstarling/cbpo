import copy
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.core.context import AppContext
from app.core.exceptions import InvalidParameterException
from app.financial.models import ClientUserTrack
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.client_user_track_serializer import ClientUserTrackSerializer, \
    ClientUserTrackPayloadSerializer


class ClientUserTrackView(APIView):
    serializer_class = ClientUserTrackSerializer
    permission_classes = [JwtTokenPermission]

    def get_object(self):
        client_id = self.kwargs.get('client_id')
        user_id = AppContext.instance().user_id
        obj, _ = ClientUserTrack.objects.tenant_db_for(client_id).get_or_create(client_id=client_id, user_id=user_id)
        return obj

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = self.serializer_class(obj).data
        return Response(status=status.HTTP_200_OK, data=data)

    @staticmethod
    def normalize_data_validated(obj, validated_data: dict):
        data = {}
        for key, vals in validated_data.items():
            col_val = copy.deepcopy(getattr(obj, key))
            if not vals:
                raise InvalidParameterException(f'{key} column not accept empty')
            for v, k in vals.items():
                col_val.update({v: k})
            data.update({key: col_val})
        return data

    @swagger_auto_schema(
        operation_description='Add user tracking for category',
        request_body=ClientUserTrackPayloadSerializer, responses={status.HTTP_200_OK: ClientUserTrackSerializer})
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = ClientUserTrackPayloadSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        #
        client_id = self.kwargs.get('client_id')
        user_id = AppContext.instance().user_id
        #
        data_input = self.normalize_data_validated(obj, validated_data)
        #
        data_input.update(
            dict(
                client_id=client_id,
                user_id=user_id
            )
        )
        ins = serializer.update(obj, data_input)
        data = self.serializer_class(ins).data
        return Response(status=status.HTTP_200_OK, data=data)
