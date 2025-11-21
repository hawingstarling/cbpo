
from app.core.exceptions import InvalidParameterException
from app.tenancies.models import Client
from app.tenancies.permissions_mw import IsMWServices
from app.tenancies.serializers import ClientInfoInternalSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView

TAG_NAME = "services"


class RetrieveClientView(RetrieveAPIView):
    permission_classes = (IsMWServices,)
    serializer_class = ClientInfoInternalSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_authentication(self, request):
        pass

    def get_object(self):
        try:
            return Client.objects.get(id=self.kwargs.get("client_id"))
        except Client.DoesNotExist:
            raise InvalidParameterException(message="invalid client id")
