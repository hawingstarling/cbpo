from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.core.exceptions import InvalidParameterException
from app.payments.models import SubscriptionCouponCode, Subscription
from app.payments.serializers_coupon import CouponSerializer, ApplyNewPromoCodeSerializer
from app.payments.services.coupon import CouponService
from app.tenancies.models import Organization
from app.tenancies.permissions import IsOwnerOrAdminOrganizationPermission

TAG_NAME = "coupon"


class GetOrganizationMixin:
    @property
    def get_organization(self):
        try:
            organization_id = self.kwargs.get("organization_id")  # noqa
            return Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise InvalidParameterException(
                message="parameter 'organization_id' is invalid."
            )

    @property
    def get_subscription(self):
        org = self.get_organization
        try:
            return Subscription.objects.get(organization=org)
        except Organization.DoesNotExist:
            raise InvalidParameterException(
                message="parameter 'organization_id' is invalid."
            )


class ListCouponsView(GetOrganizationMixin, generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CouponSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return SubscriptionCouponCode.objects.filter(subscription=self.get_subscription).order_by(
            '-is_active', '-created')


class ApplyNewPromoCodeView(GetOrganizationMixin, generics.GenericAPIView):
    serializer_class = ApplyNewPromoCodeSerializer
    permission_classes = (IsOwnerOrAdminOrganizationPermission,)

    @swagger_auto_schema(tags=[TAG_NAME])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        promo_code_id = serializer.validated_data['promo_code_id']

        CouponService(subscription=self.get_subscription).apply_new_promo_code(
            promo_code_id=promo_code_id)

        return Response({}, status=status.HTTP_200_OK)
