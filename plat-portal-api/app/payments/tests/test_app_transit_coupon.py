from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.payments.models import (
    Subscription,
    SubscriptionCouponCode,
)
from app.payments.tests.webhook_mixin import WebhookMixin
from app.tenancies.models import User
from app.tenancies.services import UserService

APPS_DIR = settings.ROOT_DIR.path("app")

fixtures = [
    APPS_DIR + "payments/tests/fixtures/user.json",
    APPS_DIR + "payments/tests/fixtures/role.json",
    APPS_DIR + "payments/tests/fixtures/organization.json",
    APPS_DIR + "payments/tests/fixtures/organization_user.json",
    APPS_DIR + "payments/tests/fixtures/plan.json",
]

FAKE_DATA_PATH = f"{APPS_DIR}/payments/tests/fake_data/app_transit"
FAKE_DATA_COUPON_PATH = f"{APPS_DIR}/payments/tests/fake_data/app_transit_coupon"


@override_settings(
    STRIPE_SECRET_KEY="fake_sc_key",
    STRIPE_PUBLISHABLE_KEY="fake_public_key",
    STRIPE_ENDPOINT_SECRET="fake_endpoint_sc_key",
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",  # send email in console
)
class SubscriptionCouponTest(APITestCase, WebhookMixin):
    fixtures = fixtures
    organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"

    def test_1(self):
        """
        use coupon from checking out session (create subscription)
        """

        fake_data_path = f"{FAKE_DATA_PATH}/webhook_checkout.session.completed.json"
        self._web__hook(fake_data_path)

        fake_data_path = f"{FAKE_DATA_COUPON_PATH}/webhook_invoice.paid.json"

        promo_code = "THE_REDEEMED_CODE"
        promo_code_duration_mode = 'once'

        patcher_promo_code = patch(
            "app.payments.services.utils.StripeApiServices.get_promo_code_usage",
            return_value=promo_code
        )
        patcher_promo_code.start()
        self._web__hook(fake_data_path)

        # in fixtures
        discount_id = "di_1M5Q3kBhZLR2oJFVOFYsgfN0"
        discount_start = 1668760588
        discount_end = None
        discount_amount_off = 1000
        discount_percent_off = None

        self.assertEqual(
            Subscription.objects.filter(organization_id=self.organization_id, is_active=True).count(),
            1,
            "create subscription record",
        )

        subscription_coupon = SubscriptionCouponCode.objects.get(coupon_promotion_code=promo_code)

        self.assertEqual(subscription_coupon.discount_id, discount_id)
        self.assertEqual(subscription_coupon.duration_mode, promo_code_duration_mode)
        self.assertEqual(
            subscription_coupon.start,
            datetime.fromtimestamp(discount_start, tz=timezone.utc))
        self.assertEqual(
            subscription_coupon.end,
            discount_end)
        self.assertEqual(
            subscription_coupon.amount_off,
            Decimal(discount_amount_off / 100))
        self.assertEqual(subscription_coupon.percent_off, discount_percent_off)
        self.assertEqual(subscription_coupon.is_active, True)

        self.assertEqual(subscription_coupon.invoice_applied_count(), 1)

    def test_2(self):
        """
        use coupon from checking out session (create subscription with some trial days)

        - phase 1 -> not applied count
        - phase 2 -> next invoice (force end trialing mode) -> applied count by redemption
        - phase 3 -> next billing -> redemption code is expired
        """

        fake_data_path = f"{FAKE_DATA_PATH}/webhook_checkout.session.completed.json"
        self._web__hook(fake_data_path)

        fake_data_path = f"{FAKE_DATA_COUPON_PATH}/webhook_invoice.paid_trialing.json"

        promo_code = "XOIXOI2"

        patcher_promo_code = patch(
            "app.payments.services.utils.StripeApiServices.get_promo_code_usage",
            return_value=promo_code
        )
        patcher_promo_code.start()
        self._web__hook(fake_data_path)

        # in fixtures
        discount_id = "di_1M79iPBhZLR2oJFVylfT4tf3"
        self.assertEqual(
            Subscription.objects.filter(organization_id=self.organization_id, is_active=True).count(),
            1,
            "create subscription record",
        )

        subscription_coupon = SubscriptionCouponCode.objects.get(coupon_promotion_code=promo_code)

        self.assertEqual(subscription_coupon.discount_id, discount_id)
        self.assertEqual(subscription_coupon.is_active, True)

        # in trialing mode, the redeem code is not applied for the current trial invoice
        # phase 1
        self.assertEqual(subscription_coupon.invoice_applied_count(), 0)

        # next invoice (end trialing mode)
        # phase 2
        fake_data_path = f"{FAKE_DATA_COUPON_PATH}/webhook_invoice.paid_end_trialing.json"
        self._web__hook(fake_data_path)
        self.assertEqual(subscription_coupon.invoice_applied_count(), 1)

        # next invoice
        # phase 3, the redemption code is expired, not applied anymore
        fake_data_path = f"{FAKE_DATA_COUPON_PATH}/webhook_invoice.paid_redemption_expired.json"
        self._web__hook(fake_data_path)
        subscription_coupon.refresh_from_db()
        self.assertEqual(subscription_coupon.is_active, False)


@override_settings(
    STRIPE_SECRET_KEY="fake_sc_key",
    STRIPE_PUBLISHABLE_KEY="fake_public_key",
    STRIPE_ENDPOINT_SECRET="fake_endpoint_sc_key",
    MAILCHIMP_ENABLED=False,
    MAILCHIMP_API_KEY="123123123",
    MAILCHIMP_PREFIX_SERVER="us1",
    MAILCHIMP_LIST_ID="123123123",
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",  # send email in console
)
class ApplyCouponManuallyTest(APITestCase, WebhookMixin):
    fixtures = fixtures + [
        APPS_DIR + "payments/tests/fixtures/subscription_for_transit.json",
        # APPS_DIR + "payments/tests/fixtures/approval_organization_payment.json",
        APPS_DIR + "payments/tests/fixtures/stripe_customer.json",
    ]

    def setUp(self) -> None:
        self.user = User.objects.get(email="vnhd1@example.com")
        self.token = UserService.create_token(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_apply_new_coupon(self):
        """
        apply new coupon code

        the promo code is just prepared for next billing
        """
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        url = reverse(
            "subscription-apply-promo-code",
            kwargs={"organization_id": organization_id},
        )
        patcher_get_promo_id = patch(
            "app.payments.services.utils.StripeApiServices.retrieve_promo_code_id",
            return_value="promo_sdjkfhakjdsfhd",
        )
        fake_data_path = f"{FAKE_DATA_COUPON_PATH}/discount_from_apply_promo_code.json"
        fake_data = self._get_fake_data(fake_data_path)
        patcher_apply_promo = patch(
            "app.payments.services.utils.StripeApiServices.apply_promo_code",
            return_value=fake_data
        )
        patcher_get_promo_code_usage = patch(
            "app.payments.services.utils.StripeApiServices.get_promo_code_usage",
            return_value="CODE123"
        )
        patcher_apply_promo.start()
        patcher_get_promo_id.start()
        patcher_get_promo_code_usage.start()
        #
        response = self.client.post(url, {
            "promo_code": "CODE123"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subscription_coupon = SubscriptionCouponCode.objects.get(coupon_promotion_code="CODE123", is_active=True)

        # current billing
        self.assertEqual(subscription_coupon.invoice_applied_count(), 0)

        fake_data_path = f"{FAKE_DATA_COUPON_PATH}/webhook_invoice.paid_after_apply_promo_manually.json"
        self._web__hook(fake_data_path)
        subscription_coupon.refresh_from_db()
        # next billing
        self.assertEqual(subscription_coupon.invoice_applied_count(), 1)
