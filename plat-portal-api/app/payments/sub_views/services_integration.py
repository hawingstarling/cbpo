from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from app.core.exceptions import InvalidParameterException

from app.payments import models as payment_models
from app.payments import serializers_services_integration as service_serializers

from app.tenancies.permissions_dtd import IsDTDServices

TAG_NAME = "services"


class GetExpiredTimeView(generics.RetrieveAPIView):
    """
    Get expired time of the subscription

    webhook from stripe is sometimes delayed
    need to get directly from stripe
    when portal api has not received webhook yet

    """

    permission_classes = (IsDTDServices,)
    serializer_class = service_serializers.GetSubExpiredSerializer

    @swagger_auto_schema(
        tags=[TAG_NAME],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)  # noqa

    def perform_authentication(self, request):
        pass

    def get_object(self):
        try:
            return payment_models.Subscription.objects.get(
                organization_id=self.kwargs.get("organization_id")
            )
        except payment_models.Subscription.DoesNotExist:
            raise InvalidParameterException(
                message="parameter 'organization_id' is invalid."
            )
