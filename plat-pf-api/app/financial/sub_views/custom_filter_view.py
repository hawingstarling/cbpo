import logging
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from app.financial.models import CustomFilter
from app.financial.sub_views.base_view import CustomBaseListCreateAPIViewSerializer, CustomBaseListListCreateShareModeView, \
    CustomBaseRetrieveUpdateDestroyView
from ..sub_serializers.custom_view_serializer import CustomFilterSerializer, CustomFilterCreateSerializer

logger = logging.getLogger(__name__)


class CustomFilterListCreateView(CustomBaseListCreateAPIViewSerializer):
    serializer_class = CustomFilterSerializer
    custom_model = CustomFilter

    @swagger_auto_schema(operation_description="create filter column profile for filter data source",
                         request_body=CustomFilterCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomFilterSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomFilterRetrieveUpdateDestroyView(CustomBaseRetrieveUpdateDestroyView):
    queryset = CustomFilter.objects.all()
    serializer_class = CustomFilterSerializer
    custom_model = CustomFilter


class CustomFilterListCreateShareModeView(CustomBaseListListCreateShareModeView):
    custom_model = CustomFilter
