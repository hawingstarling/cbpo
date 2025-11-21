import json
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.payments.models import (
    Subscription,
    Plan,
    ApprovalOrganizationalPayment,
    ApprovalOrganizationalServiceConfig,
    MapWatcherConfigOnDemand,
)
from app.payments.services.on_demand_plan import OnDemandPlan
from app.payments.tests.util_mixin import AssertComparison
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
    APPS_DIR + "payments/tests/fixtures/map_watcher_service_config.json",
    APPS_DIR + "payments/tests/fixtures/fund_package.json",
]

FAKE_DATA_PATH = f"{APPS_DIR}/payments/tests/fake_data/app_MW"


@override_settings(
    STRIPE_SECRET_KEY="fake_sc_key",
    STRIPE_PUBLISHABLE_KEY="fake_public_key",
    STRIPE_ENDPOINT_SECRET="fake_endpoint_sc_key",
    MAILCHIMP_ENABLED=False,
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",  # send email in console
)
class BasicPaymentTest(APITestCase, AssertComparison, WebhookMixin):
    fixtures = fixtures

    def setUp(self) -> None:
        self.user = User.objects.get(email="vnhd1@example.com")
        self.token = UserService.create_token(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_all_plans(self):
        """
        get all plans for app MAP
        """
        url = reverse(
            "get-plans",
            kwargs={"organization_id": "4e50aaab-78a8-4373-90b7-2690ae214d31"},
        )
        response = self.client.get(url, {"app": "mwrw"}, format="json")
        res = json.loads(response.content)
        self.assertEqual(res.get("count"), 2, "initial plans error")

    def test_create_a_checkout_session(self):
        """
        create checkout session id STRIPE
        mockup checkout session
        """
        body = {
            "success_callback_url": "http://localhost:8080",
            "cancel_callback_url": "http://localhost:8080",
            "plan_id": "bf71292e-ffd8-40a9-a9a6-5b05a04eb707",  # mwrw plan
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
        patcher_stripe_session.start()
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
        response = self.client.post(url, body, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "create session error"
        )
        patcher_stripe_session.stop()
        patcher_create_customer.stop()

    def test_event_webhook(self):
        """
        event webhook from stripes -> main flows for a successful payment
        - checkout.session.completed
        - customer.subscription.updated (trialing mode)
        - customer.subscription.trial_will_end (notify ending time for trialing mode)
        - invoice.paid
        """
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"

        """
        case 1
            -> create Subscription
            -> write down transaction
            -> reset Organization balance
            -> clone MAP Standardization
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_checkout.session.completed.json"
        self._web__hook(fake_data_path)

        # subscription
        subscription = Subscription.objects.get(organization_id=organization_id)
        list_assert_equal_subscription = [
            {
                "key": "application",
                "value": "mwrw",
                "description": "expect application mwrw",
            },
            {
                "key": "is_active",
                "value": False,
                "description": "expect is_active is False",
            },
            {"key": "status", "value": None, "description": "expect is_active is None"},
            {
                "key": "mode",
                "value": "FULL_PACK",
                "description": "expect mode is FULL_PACK",
            },
            {
                "key": "expired_in",
                "value": None,
                "description": "expect expired_in is None",
            },
        ]
        self.compare(list_assert_equal_subscription, self.assertEqual, subscription)

        """
        - case 2: event customer.subscription.updated (trailing) optional with trialing mode
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
        self.compare(
            [
                {
                    "key": "status",
                    "value": "trialing",
                    "description": "status expect trialing",
                }
            ],
            self.assertEqual,
            subscription,
        )

        """
        - case 3: event customer.subscription.trial_will_end (trialing) optional with trialing mode
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
        - case 4: event invoice.paid (trialing ~ amount 0) optional with trialing mode
            -> mark active subscription
            -> enable approval configuration from the PLAN
            -> send mail notification
            -> write down transaction
            ->
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
        patcher_sub_data.stop()
        # subscription
        subscription.refresh_from_db()
        self.compare(
            [
                {
                    "key": "amount",
                    "value": 0,
                    "description": "amount expect 0",
                },
                {
                    "key": "is_active",
                    "value": True,
                    "description": "is_active expect True",
                },
            ],
            self.assertEqual,
            subscription,
        )

        # approval organization payment
        approval_config_subscription = ApprovalOrganizationalPayment.objects.get(
            organization_id=organization_id, subscription_id=subscription.id
        )
        plan_subscribe = Plan.objects.get(id="bf71292e-ffd8-40a9-a9a6-5b05a04eb707")
        list_assert_equal_approval_member_resource = [
            {
                "key": "max_workspaces",
                "value": plan_subscribe.max_workspaces,
                "description": f"max_workspaces expect {plan_subscribe.max_workspaces}",
            },
            {
                "key": "max_external_users",
                "value": plan_subscribe.max_external_users,
                "description": f"max_external_users expect {plan_subscribe.max_external_users}",
            },
            {
                "key": "max_internal_users",
                "value": plan_subscribe.max_internal_users,
                "description": f"max_internal_users expect {plan_subscribe.max_internal_users}",
            },
        ]
        self.compare(
            list_assert_equal_approval_member_resource,
            self.assertEqual,
            approval_config_subscription,
        )

        # MAP watcher service config
        approval_map_config = ApprovalOrganizationalServiceConfig.objects.get(
            organization_id=organization_id
        )
        plan_service_config = approval_map_config.config.get("plan_service_config")
        plan_service_config = {ele["key"]: ele["value"] for ele in plan_service_config}
        tenancy_config = approval_map_config.config.get("tenancy_config")
        tenancy_config = {ele["key"]: ele["value"] for ele in tenancy_config}
        daily_limitation_config = approval_map_config.config.get(
            "daily_limitation_config"
        )
        daily_limitation_config = {
            ele["key"]: ele["value"] for ele in daily_limitation_config
        }

        init_plan_service_config = subscription.plan.get_plan_service_config()
        init_plan_service_config = [
            {**ele, "description": None} for ele in init_plan_service_config
        ]
        self.compare(init_plan_service_config, self.assertEqual, plan_service_config)
        init_tenancy_config = subscription.plan.get_tenancy_config()
        init_tenancy_config = [
            {**ele, "description": None} for ele in init_tenancy_config
        ]
        self.compare(init_tenancy_config, self.assertEqual, tenancy_config)
        init_daily_limitation_config = subscription.plan.get_daily_limitation_config()
        init_daily_limitation_config = [
            {**ele, "description": None} for ele in init_daily_limitation_config
        ]
        self.compare(
            init_daily_limitation_config, self.assertEqual, daily_limitation_config
        )

        """
        - case 5: event customer.subscription.updated
            -> write down transaction
            -> update subscription status, expired_in
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_customer.subscription.updated.json"
        self._web__hook(fake_data_path)

        subscription.refresh_from_db()
        self.compare(
            [
                {
                    "key": "status",
                    "value": "active",
                    "description": "status expect active",
                }
            ],
            self.assertEqual,
            subscription,
        )
        self.compare(
            [
                {
                    "key": "expired_in",
                    "value": None,
                    "description": "expired_in expect not None",
                }
            ],
            self.assertNotEqual,
            subscription,
        )

        """
         - case 5: event invoice.paid
            -> mark active subscription
            -> enable approval configuration from the PLAN
            -> send mail notification
            -> write down transaction
        """
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_invoice.paid.json"
        plan_subscribe = Plan.objects.get(id="bf71292e-ffd8-40a9-a9a6-5b05a04eb707")
        patcher_sub_data = patch(
            "app.payments.services.utils.StripeApiServices.retrieve_subscription_data",
            return_value=self._get_fake_data(
                f"{FAKE_DATA_PATH}/subscription_data.json"
            ),
        )
        patcher_sub_data.start()
        self._web__hook(fake_data_path)
        patcher_sub_data.stop()
        # subscription
        subscription.refresh_from_db()
        self.compare(
            [
                {
                    "key": "is_active",
                    "value": True,
                    "description": "is_active expect True",
                },
                {
                    "key": "amount",
                    "value": plan_subscribe.price,
                    "description": "expired_in expect None",
                },
            ],
            self.assertEqual,
            subscription,
        )
        self.assertNotEqual(subscription.expired_in, None, "expect expired_in not null")


@override_settings(
    STRIPE_SECRET_KEY="fake_sc_key",
    STRIPE_PUBLISHABLE_KEY="fake_public_key",
    STRIPE_ENDPOINT_SECRET="fake_endpoint_sc_key",
    MAILCHIMP_ENABLED=False,
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",  # send email in console
)
class PaymentTest(APITestCase, WebhookMixin, AssertComparison):
    fixtures = fixtures + [
        APPS_DIR + "payments/tests/fixtures/subscription_for_mw.json",
        APPS_DIR + "payments/tests/fixtures/approval_organization_payment.json",
        APPS_DIR + "payments/tests/fixtures/stripe_customer.json",
        APPS_DIR + "payments/tests/fixtures/setting.json",
        APPS_DIR + "payments/tests/fixtures/map_watcher_config_on_demand.json",
    ]

    def setUp(self) -> None:
        self.user = User.objects.get(email="vnhd1@example.com")
        self.token = UserService.create_token(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_unsubscribe(self):
        """
        unsubscribe
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

    def test_upcoming_invoice(self):
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        # webhook
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_invoice.upcoming.json"
        patcher_incoming_invoice = patch(
            "app.payments.services.utils.StripeApiServices.get_incoming_invoice",
            return_value=self._get_fake_data(f"{FAKE_DATA_PATH}/invoice_incoming.json"),
        )
        patcher_incoming_invoice.start()
        self._web__hook(fake_data_path)
        patcher_incoming_invoice.stop()

    def test_preview(self):
        """
        get preview data and upgrade
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
        plan = Plan.objects.get(type__exact="PROFESSIONAL", application="mwrw")
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

        plan = Plan.objects.get(type__exact="PROFESSIONAL", application="mwrw")
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

        # MAP watcher service config
        approval_map_config = ApprovalOrganizationalServiceConfig.objects.get(
            organization_id=organization_id
        )
        plan_service_config = approval_map_config.config.get("plan_service_config")
        plan_service_config = {ele["key"]: ele["value"] for ele in plan_service_config}
        tenancy_config = approval_map_config.config.get("tenancy_config")
        tenancy_config = {ele["key"]: ele["value"] for ele in tenancy_config}
        daily_limitation_config = approval_map_config.config.get(
            "daily_limitation_config"
        )
        daily_limitation_config = {
            ele["key"]: ele["value"] for ele in daily_limitation_config
        }

        init_plan_service_config = subscription.plan.get_plan_service_config()
        init_plan_service_config = [
            {**ele, "description": None} for ele in init_plan_service_config
        ]
        self.compare(init_plan_service_config, self.assertEqual, plan_service_config)
        init_tenancy_config = subscription.plan.get_tenancy_config()
        init_tenancy_config = [
            {**ele, "description": None} for ele in init_tenancy_config
        ]
        self.compare(init_tenancy_config, self.assertEqual, tenancy_config)
        init_daily_limitation_config = subscription.plan.get_daily_limitation_config()
        init_daily_limitation_config = [
            {**ele, "description": None} for ele in init_daily_limitation_config
        ]
        self.compare(
            init_daily_limitation_config, self.assertEqual, daily_limitation_config
        )

        patcher_sub_data.stop()
        patcher_incoming_invoice.stop()
        patcher_modify_subscription.stop()

    def test_invoice_payment_failed(self):
        """verify subscription status when payment is fail"""
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        # webhook
        fake_data_path = f"{FAKE_DATA_PATH}/webhook_invoice.payment_failed.json"
        self._web__hook(fake_data_path)

        subscription = Subscription.objects.get(organization_id=organization_id)
        self.assertEqual(subscription.is_active, False, "is_active must be false")
        self.assertEqual(
            subscription.status,
            "invoice.payment_failed",
            "status must be invoice.payment_failed",
        )

    def test_demand_plan(self):
        """
        portal admin create new demand plans for customer
        upgrade current plan to new demand plan
        verify new config
        Returns:

        """
        organization_id = "4e50aaab-78a8-4373-90b7-2690ae214d31"
        demand_id = "7a0f00b2-5b16-4429-9f73-327fd19081ce"  # from fixture
        patcher_create_plan = patch(
            "app.payments.services.utils.StripeApiServices.create_product",
            return_value="plan_123456",
        )
        patcher_create_plan.start()
        # create plan on stripe based on customer's demand
        handler = OnDemandPlan(demand_config_id=demand_id)
        handler.create()
        url = reverse(
            "get-plans",
            kwargs={"organization_id": organization_id},
        )
        response = self.client.get(url, {"app": "mwrw"}, format="json")
        res = json.loads(response.content)
        self.assertEqual(res.get("count"), 3, "initial plans error")

        demand = MapWatcherConfigOnDemand.objects.get(id=demand_id)

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
        plan = demand.plan
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

        # MAP watcher service config
        approval_map_config = ApprovalOrganizationalServiceConfig.objects.get(
            organization_id=organization_id
        )
        plan_service_config = approval_map_config.config.get("plan_service_config")
        plan_service_config = {ele["key"]: ele["value"] for ele in plan_service_config}
        tenancy_config = approval_map_config.config.get("tenancy_config")
        tenancy_config = {ele["key"]: ele["value"] for ele in tenancy_config}
        daily_limitation_config = approval_map_config.config.get(
            "daily_limitation_config"
        )
        daily_limitation_config = {
            ele["key"]: ele["value"] for ele in daily_limitation_config
        }

        init_plan_service_config = subscription.plan.get_plan_service_config()
        init_plan_service_config = [
            {**ele, "description": None} for ele in init_plan_service_config
        ]
        self.compare(init_plan_service_config, self.assertEqual, plan_service_config)
        init_tenancy_config = subscription.plan.get_tenancy_config()
        init_tenancy_config = [
            {**ele, "description": None} for ele in init_tenancy_config
        ]
        self.compare(init_tenancy_config, self.assertEqual, tenancy_config)
        init_daily_limitation_config = subscription.plan.get_daily_limitation_config()
        init_daily_limitation_config = [
            {**ele, "description": None} for ele in init_daily_limitation_config
        ]
        self.compare(
            init_daily_limitation_config, self.assertEqual, daily_limitation_config
        )

        patcher_sub_data.stop()
        patcher_incoming_invoice.stop()
        patcher_modify_subscription.stop()
        patcher_create_plan.stop()
