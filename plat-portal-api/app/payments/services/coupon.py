from app.payments.exceptions import DuplicatedCouponUsageException
from app.payments.models import SubscriptionCouponCode, Subscription
from app.payments.services.stripe_discount_obj_extraction import StripeDiscountObjExtractionServices
from app.payments.services.utils import StripeApiServices


class CouponService:

    def __init__(self, subscription: Subscription):
        self.stripe_subscription_id = subscription.external_subscription_id
        self.subscription = subscription

    def apply_new_promo_code(self, promo_code_id: str):
        """
        force a coupon to a subscription for the future charging
        """
        res = StripeApiServices.apply_promo_code(
            external_subscription_id=self.stripe_subscription_id,
            promo_code_id=promo_code_id)
        discount = res['discount']

        is_duplicated, message = self._is_duplicated_coupon(new_discount_id=discount['id'])
        if is_duplicated is True:
            raise DuplicatedCouponUsageException(message=message)
        self._update_all_current_coupon_code_to_inactive()
        self.update_or_create_new_promo_code(
            stripe_discount_object=discount,
        )

    def _update_all_current_coupon_code_to_inactive(self):
        SubscriptionCouponCode.objects.filter(subscription=self.subscription, is_active=True).update(is_active=False)

    def update_or_create_new_promo_code(self, stripe_discount_object: dict):
        extract_handler = StripeDiscountObjExtractionServices(
            stripe_discount_obj=stripe_discount_object)
        (
            discount_id,
            is_valid,
            promo_code_usage,
            discount_start,
            discount_end,
            duration_mode,
            amount_off,
            percent_off,
        ) = (
            extract_handler.get_discount_id(),
            extract_handler.is_valid_discount(),
            extract_handler.get_coupon_promo_code(),
            extract_handler.get_discount_start(),
            extract_handler.get_discount_end(),
            extract_handler.get_coupon_duration_mode(),
            extract_handler.get_amount_off(),
            extract_handler.get_percent_off(),
        )

        query_obj = {
            "subscription": self.subscription,
            "coupon_promotion_code": promo_code_usage,
        }
        defaults_value = {
            "user_redeemed_by_id": self.subscription.user_id,
            "is_valid": True,
            "discount_id": discount_id,
            "start": discount_start,
            "end": discount_end,
            "duration_mode": duration_mode,
            "amount_off": amount_off,
            "percent_off": percent_off,
            "is_active": True,
            "raw": stripe_discount_object,
        }

        SubscriptionCouponCode.objects.update_or_create(
            **query_obj,
            defaults=defaults_value,
        )

    def _is_duplicated_coupon(self, new_discount_id: str) -> (bool, str):
        try:
            coupon_usage = SubscriptionCouponCode.objects.get(subscription=self.subscription, is_active=True)
            current_discount_id = coupon_usage.discount_id
        except SubscriptionCouponCode.DoesNotExist:
            return False, ''

        is_duplicated = new_discount_id == current_discount_id
        if is_duplicated:
            return True, f"The new coupon code has the same value as {coupon_usage.coupon_promotion_code}"
        return False, ''
