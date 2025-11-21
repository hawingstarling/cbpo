from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from app.app_setting.models import LWACredentialClientSetting
from app.app_setting.serializers import LWACredentialClientSettingSerializer
from app.tenancies.permissions_internal_services import IsInternalServices


# Create your views here.


class RetrieLWACredentialSettingView(generics.RetrieveAPIView):
    permission_classes = (IsInternalServices,)
    serializer_class = LWACredentialClientSettingSerializer
    queryset = LWACredentialClientSetting.objects.all()
    lookup_field = "app_id"

    def perform_authentication(self, request):
        pass

    @swagger_auto_schema(tags=["App setting"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
