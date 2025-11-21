from rest_framework import serializers

from app.payments.models import SubscriptionCouponCode
from app.payments.services.utils import StripeApiServices


class CouponSerializer(serializers.ModelSerializer):
    invoice_applied_count = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionCouponCode
        exclude = ['raw']

    @classmethod
    def get_invoice_applied_count(cls, ins: SubscriptionCouponCode):
        return ins.invoice_applied_count()


class ApplyNewPromoCodeSerializer(serializers.Serializer):
    promo_code = serializers.CharField()

    def validate(self, attrs):
        # validate promo code
        promo_code_id = StripeApiServices.retrieve_promo_code_id(promo_code=attrs['promo_code'])
        if not promo_code_id:
            raise serializers.ValidationError(detail={
                'promo_code': "The promotion code does not exist!"
            })

        attrs.update({"promo_code_id": promo_code_id})
        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
