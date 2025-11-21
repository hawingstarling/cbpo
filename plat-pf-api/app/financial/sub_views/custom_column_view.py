import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from app.financial.models import CustomColumn
from app.financial.sub_views.base_view import CustomBaseListCreateAPIViewSerializer, CustomBaseListListCreateShareModeView, \
    CustomBaseRetrieveUpdateDestroyView
from ..sub_serializers.custom_view_serializer import CustomColumnSerializer, CustomColumnCreateSerializer

logger = logging.getLogger(__name__)


class CustomColumnListCreateView(CustomBaseListCreateAPIViewSerializer):
    serializer_class = CustomColumnSerializer
    custom_model = CustomColumn

    @swagger_auto_schema(operation_description="create custom column profile for filter data source",
                         request_body=CustomColumnCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomColumnSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomColumnRetrieveUpdateDestroyView(CustomBaseRetrieveUpdateDestroyView):
    queryset = CustomColumn.objects.all()
    serializer_class = CustomColumnSerializer
    custom_model = CustomColumn

    @swagger_auto_schema(operation_description="put update custom column profile for filter data source",
                         request_body=CustomColumnCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomColumnSerializer})
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="patch update custom column profile for filter data source",
                         request_body=CustomColumnCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomColumnSerializer})
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CustomColumnListCreateShareModeView(CustomBaseListListCreateShareModeView):
    custom_model = CustomColumn
