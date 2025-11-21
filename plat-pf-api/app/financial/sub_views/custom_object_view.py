from django.http import Http404
from app.financial.permissions.base import JwtTokenPermission
from app.financial.models import CustomObject
import hashlib
import json
import logging
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from ..sub_serializers.custom_view_serializer import CustomObjectSerializer

logger = logging.getLogger(__name__)


class CreateCustomObjectView(CreateAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = CustomObjectSerializer

    @swagger_auto_schema(operation_description="create custom object for filter data source",
                         request_body=CustomObjectSerializer,
                         responses={status.HTTP_201_CREATED: CustomObjectSerializer})
    def post(self, request, *args, **kwargs):
        request.data['client'] = kwargs['client_id']
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        hash_content = hashlib.md5(json.dumps(serializer.validated_data['content']).encode('utf-8')).hexdigest()
        serializer.validated_data['hash_content'] = hash_content
        return super().perform_create(serializer)


class RetrieveCustomObjectView(RetrieveAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = CustomObjectSerializer

    def get_object(self):
        filter = {
            'client_id': self.kwargs.get('client_id'),
            'pk': self.kwargs.get('pk'),
        }
        try:
            return CustomObject.objects.tenant_db_for(self.kwargs.get('client_id')).get(**filter)
        except CustomObject.DoesNotExist:
            raise Http404('No %s matches the given query.' % CustomObject._meta.object_name)
