from datetime import timezone, datetime

from rest_framework import serializers

from app.payments import models as payment_models
from app.payments.services.utils import StripeApiServices

MW_VALID_SERVICE_KEYS = (
    "amazon_scraping",
    "amazon_screenshot",
    "google_scraping",
    "google_screenshot",
    "amazon_inventory_scraping",
)


# class ServiceBalanceSubmissionSerializer(serializers.ModelSerializer):
#     service_key = serializers.ChoiceField(
#         choices=MW_VALID_SERVICE_KEYS, write_only=True
#     )
#     description = serializers.CharField(default="MAP Watcher submission")
#
#     class Meta:
#         model = PaymentModels.ServiceBalanceSubmission
#         fields = (
#             "application",
#             "quantity",
#             "service_key",
#             "description",
#         )


class GetSubExpiredSerializer(serializers.ModelSerializer):
    expired_in = serializers.SerializerMethodField()

    class Meta:
        model = payment_models.Subscription
        fields = ("expired_in",)

    @classmethod
    def get_expired_in(cls, obj):
        if not obj.expired_in:
            sub_data = StripeApiServices.retrieve_subscription_data(obj.external_subscription_id)
            expired_in = datetime.fromtimestamp(
                sub_data.get("current_period_end"), tz=timezone.utc
            )
            payment_models.Subscription.objects.filter(id=obj.id).update(expired_in=expired_in)
            return expired_in
        return obj.expired_in
