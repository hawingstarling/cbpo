import json
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.payments.models import (
    Subscription,
    ApprovalOrganizationalPayment,
    Plan,
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


@override_settings(
    STRIPE_SECRET_KEY="fake_sc_key",
    STRIPE_PUBLISHABLE_KEY="fake_public_key",
    STRIPE_ENDPOINT_SECRET="fake_endpoint_sc_key",
    MAILCHIMP_ENABLED=True,
    MAILCHIMP_API_KEY="123123123",
    MAILCHIMP_PREFIX_SERVER="us1",
    MAILCHIMP_LIST_ID="123123123",
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",  # send email in console
)
class BasicPaymentTest(APITestCase, WebhookMixin):
    fixtures = fixtures

    def setUp(self) -> None:
        self.user = User.objects.get(email="vnhd1@example.com")
        self.token = UserService.create_token(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_all_plans(self):
        """
        TEST get all initial PLANS
        """
        url = reverse(
            "get-plans",
            kwargs={"organization_id": "4e50aaab-78a8-4373-90b7-2690ae214d31"},
        )
        response = self.client.get(url, {"app": "transit"}, format="json")
        res = json.loads(response.content)
        self.assertEqual(res.get("count"), 4, "initial plans error")

    def test_create_a_checkout_session(self):
        """
        TEST create checkout session id STRIPE
        mockup checkout session
        """
        body = {
            "success_callback_url": "http://localhost:8080",
            "cancel_callback_url": "http://localhost:8080",
            "plan_id": "4c571926-b6a0-4db0-81a2-829cfb246434",
        }
        url = reverse(
            "organization-checkout",
            kwargs={"organization_id": "4e50aaab-78a8-4373-90b7-2690ae214d31"},
        )
        patcher_stripe_session = patch(
            "app.payments.services.utils.StripeApiServices.create_checkout_session",
            return_value={
                "sessionId": "123123123",
                "publicKey": settings.STRIPE_PUBLISHABLE_KEY,
            },
        )
        patcher_create_customer = patch(
            "app.payments.services.utils.StripeApiServices.create_customer",
            return_value=self._get_fake_data(f"{FAKE_DATA_PATH}/create_customer.json"),
        )
        patcher_checkout_customer_exist = patch(
            "app.payments.services.utils.StripeApiServices.check_customer_subscription_exist",
            return_value=False,
        )
        patcher_create_customer.start()
        patcher_checkout_customer_exist.start()
        patcher_stripe_session.start()
        response = self.client.post(url, body, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "create session error"
        )
        patcher_stripe_session.stop()
        patcher_checkout_customer_exist.stop()
        patcher_create_customer.stop()

    def test_event_webhook(self):
        """
        TEST event webhook subscription
        - case 1: event checkout.session.completed
            -> create Subscription
            -> write down transaction
        - case 2: event customer.subscription.created
            -> write down transaction
        - case 4: event customer.subscription.updated (trailing) optional with trialing mode
            -> save subscription status
            -> write down transaction
        - case 4a: event customer.subscription.trial_will_end (trialing) optional with trialing mode
            -> send email
            -> write down transaction
        - case 5: event invoice.paid
            -> mark active subscription
            -> enable approval configuration from the PLAN
            -> send mail notification
            -> add mailchimp tag
            -> write down transaction
        - case 6: event customer.subscription.updated
            -> save subscription status
            -> write down transaction

        - get subscription detail of the organization

        - get approval subscription of the organization
        """
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        """
        case 1
            -> create Subscription
            -> write down transaction
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_checkout.session.completed.json"
        self._web__hook(fake_data_path)
        # subscription
        subscription = Subscription.objects.get(organization_id=organization_id)

        self.assertEqual(
            Subscription.objects.filter(organization_id=organization_id).count(),
            1,
            "create subscription record",
        )
        self.assertEqual(subscription.status, None, "event checkout session completed")
        self.assertEqual(
            subscription.expired_in, None, "event checkout session completed"
        )
        self.assertEqual(
            subscription.is_active, False, "event checkout session completed"
        )

        """
        - case 2: event customer.subscription.created
            -> write down transaction
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_customer.subscription.created.json"
        self._web__hook(fake_data_path)

        """
        - case 4: event customer.subscription.updated (trailing) optional with trialing mode
            -> save subscription status
            -> write down transaction
        """
        # this fake data is from another subscription
        # just consider the relevant data for making mockup data ~ subscription_id, status, expired_in
        fake_data_path = (
            f"{FAKE_DATA_PATH}/webhook_customer.subscription.updated_trialing.json"
        )
        self._web__hook(fake_data_path)
        # subscription
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, "trialing")
        self.assertNotEqual(subscription.expired_in, None)

        """
        - case 4a: event customer.subscription.trial_will_end (trialing) optional with trialing mode
            -> send email
            -> write down transaction
        """
        # this fake data is from another subscription
        # just consider the relevant data for making mockup data ~ subscription_id, status, expired_in
        fake_data_path = (
            f"{FAKE_DATA_PATH}/webhook_customer.subscription.trial_will_end.json"
        )
        self._web__hook(fake_data_path)

        """
         - case 5: event invoice.paid
            -> mark active subscription
            -> enable approval configuration from the PLAN
            -> send mail notification
            -> add mailchimp tag
            -> write down transaction
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_invoice.paid.json"
        plan_subscribe = Plan.objects.get(id="4c571926-b6a0-4db0-81a2-829cfb246434")
        patcher_sub_data = patch(
            "app.payments.services.utils.StripeApiServices.retrieve_subscription_data",
            return_value=self._get_fake_data(
                f"{FAKE_DATA_PATH}/subscription_data.json"
            ),
        )
        patcher_sub_data.start()
        self._web__hook(fake_data_path)
        # subscription
        subscription.refresh_from_db()
        self.assertEqual(subscription.is_active, True)
        self.assertEqual(subscription.amount, plan_subscribe.price)
        # approval organization payment
        approval_config_subscription = ApprovalOrganizationalPayment.objects.get(
            organization_id=organization_id, subscription_id=subscription.id
        )
        self.assertEqual(
            approval_config_subscription.max_workspaces, plan_subscribe.max_workspaces
        )
        self.assertEqual(
            approval_config_subscription.max_external_users,
            plan_subscribe.max_external_users,
        )
        self.assertEqual(
            approval_config_subscription.max_internal_users,
            plan_subscribe.max_internal_users,
        )
        patcher_sub_data.stop()

        """
        - case 6: event customer.subscription.updated
            -> save subscription status
            -> write down transaction
         """

        fake_data_path = f"{FAKE_DATA_PATH}/webhook_customer.subscription.updated.json"
        self._web__hook(fake_data_path)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, "active")

        """
        - get approval subscription of the organization
        """
        url = reverse("me-organization-approval-subscriptions")

        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        """
        - get subscription detail of the organization
        """
        url = reverse(
            "get-organization-subscription",
            kwargs={"organization_id": "4e50aaab-78a8-4373-90b7-2690ae214d31"},
        )
        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_webhook_2(self):
        """[summary]
        TEST event webhook subscription
        - case 1: event checkout.session.completed
            -> create Subscription
            -> write down transaction
        - case 2: event customer.subscription.created
            -> write down transaction
        - case 3: event invoice.paid (trialing ~ amount 0) optional with trialing mode
            -> mark active subscription
            -> enable approval configuration from the PLAN
            -> send mail notification
            -> add mailchimp tag
            -> write down transaction
        """
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        """
        case 1
            -> create Subscription
            -> write down transaction
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_checkout.session.completed.json"
        self._web__hook(fake_data_path)
        # subscription
        subscription = Subscription.objects.get(organization_id=organization_id)

        self.assertEqual(
            Subscription.objects.filter(organization_id=organization_id).count(),
            1,
            "create subscription record",
        )
        self.assertEqual(subscription.status, None, "event checkout session completed")
        self.assertEqual(
            subscription.expired_in, None, "event checkout session completed"
        )
        self.assertEqual(
            subscription.is_active, False, "event checkout session completed"
        )

        """
        - case 2: event customer.subscription.created
            -> write down transaction
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_customer.subscription.created.json"
        self._web__hook(fake_data_path)

        """
        - case 3: event invoice.paid (trialing ~ amount 0) optional with trialing mode
            -> mark active subscription
            -> enable approval configuration from the PLAN
            -> send mail notification
            -> add mailchimp tag
            -> write down transaction
        """
        # this fake data is from another subscription
        # just consider the relevant data for making mockup data ~ subscription_id, amount
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_invoice.paid_trialing.json"
        patcher_sub_data = patch(
            "app.payments.services.utils.StripeApiServices.retrieve_subscription_data",
            return_value=self._get_fake_data(
                f"{FAKE_DATA_PATH}/subscription_data.json"
            ),
        )
        patcher_sub_data.start()
        self._web__hook(fake_data_path)
        # subscription
        subscription.refresh_from_db()
        self.assertEqual(subscription.amount, 0)
        self.assertEqual(subscription.is_active, True)
        patcher_sub_data.stop()


@override_settings(
    STRIPE_SECRET_KEY="fake_sc_key",
    STRIPE_PUBLISHABLE_KEY="fake_public_key",
    STRIPE_ENDPOINT_SECRET="fake_endpoint_sc_key",
    MAILCHIMP_ENABLED=True,
    MAILCHIMP_API_KEY="123123123",
    MAILCHIMP_PREFIX_SERVER="us1",
    MAILCHIMP_LIST_ID="123123123",
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",  # send email in console
)
class PaymentTest(APITestCase, WebhookMixin):
    fixtures = fixtures + [
        APPS_DIR + "payments/tests/fixtures/subscription_for_transit.json",
        APPS_DIR + "payments/tests/fixtures/approval_organization_payment.json",
        APPS_DIR + "payments/tests/fixtures/stripe_customer.json",
    ]

    def setUp(self) -> None:
        self.user = User.objects.get(email="vnhd1@example.com")
        self.token = UserService.create_token(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_unsubscribe(self):
        """
        TEST unsubscribe API
        - send request to Stripe to unsubscribe
        - webhook
        -> subscription is deactivate, status -> canceled
        """
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        url = reverse(
            "organization-unsubscribe",
            kwargs={"organization_id": organization_id},
        )
        patcher_stripe_unsubscribe = patch(
            "app.payments.services.utils.StripeApiServices.cancel_subscription",
            return_value=True,
        )
        patcher_stripe_unsubscribe.start()
        response = self.client.get(url, None, format="json")
        patcher_stripe_unsubscribe.stop()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # webhook
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_customer.subscription.deleted.json"
        self._web__hook(fake_data_path)
        subscription = Subscription.objects.get(organization_id=organization_id)
        self.assertEqual(subscription.is_active, False)
        self.assertEqual(subscription.status, "canceled")

    def test_preview(self):
        """
        TEST get preview data and upgrade
        - get preview data and stripe information payment

        """
        patcher_sub_data = patch(
            "app.payments.services.utils.StripeApiServices.retrieve_subscription_data",
            return_value=self._get_fake_data(
                f"{FAKE_DATA_PATH}/subscription_data.json"
            ),
        )
        patcher_incoming_invoice = patch(
            "app.payments.services.utils.StripeApiServices.get_incoming_invoice",
            return_value=self._get_fake_data(f"{FAKE_DATA_PATH}/invoice_incoming.json"),
        )
        patcher_payment_method = patch(
            "app.payments.services.utils.StripeApiServices.get_payment_methods",
            return_value={},
        )

        patcher_sub_data.start()
        patcher_incoming_invoice.start()
        patcher_payment_method.start()

        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        url = reverse(
            "organization-grade-changes-preview",
            kwargs={"organization_id": organization_id},
        )
        plan = Plan.objects.get(type__exact="BUSINESS")
        body = {"plan_id": plan.id}

        response = self.client.post(url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        patcher_sub_data.stop()
        patcher_incoming_invoice.stop()

    def test_upgrade(self):
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        patcher_sub_data = patch(
            "app.payments.services.utils.StripeApiServices.retrieve_subscription_data",
            return_value=self._get_fake_data(
                f"{FAKE_DATA_PATH}/subscription_data.json"
            ),
        )
        patcher_incoming_invoice = patch(
            "app.payments.services.utils.StripeApiServices.get_incoming_invoice",
            return_value=self._get_fake_data(f"{FAKE_DATA_PATH}/invoice_incoming.json"),
        )
        patcher_modify_subscription = patch(
            "app.payments.services.utils.StripeApiServices.modify_subscription",
            return_value={},
        )

        patcher_sub_data.start()
        patcher_incoming_invoice.start()
        patcher_modify_subscription.start()

        plan = Plan.objects.get(type__exact="BUSINESS")
        body = {"plan_id": plan.id}

        url = reverse(
            "organization-grade-changes-checkout",
            kwargs={"organization_id": organization_id},
        )
        response = self.client.post(url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subscription = Subscription.objects.get(organization_id=organization_id)
        self.assertEqual(subscription.plan.id, plan.id)
        approval_payment = ApprovalOrganizationalPayment.objects.get(
            organization_id=organization_id
        )
        self.assertEqual(approval_payment.max_workspaces, plan.max_workspaces)
        self.assertEqual(approval_payment.max_external_users, plan.max_external_users)
        self.assertEqual(approval_payment.max_internal_users, plan.max_internal_users)

        patcher_sub_data.stop()
        patcher_incoming_invoice.stop()
        patcher_modify_subscription.stop()
