from typing import Dict, List, Union

from django.conf import settings
from stripe.error import InvalidRequestError

from app.core.logger import logger
from app.payments.config import STRIPE_CHECKOUT_FUND, STRIPE_CHECKOUT_SUBSCRIPTION
from app.payments.exceptions import InvalidCouponException
from app.payments.models import (
    ApprovalOrganizationalPayment,
    Plan,
    Subscription,
    ApprovalOrganizationalServiceConfig,
)
from app.payments.services.notifications import PaymentEmailNotification
from app.payments.stripe_configured import stripe_configured
from app.permission.config_static_varible.permissions_groups.client.map_watcher.map_watcher import (
    MW_SI_GROUP_KEY,
    MW_SALE_ENFORCEMENT_GROUP_KEY,
)
from app.tenancies.models import Client, Organization, OrganizationUser, User


class StripeApiServices:
    """
    wrap codes for making mockup data easily
    """

    @staticmethod
    def create_checkout_session(
        organization_id: str,
        customer_stripe_id: str,
        plan_id: str,
        application: Union[None, str],
        mode: Union[None, str],
        user_id: str,
        external_plan_id,
        success_url: str,
        cancel_url: str,
        subscription_data: dict,
        allow_promotion_codes: bool,
    ):
        checkout_session = stripe_configured.checkout.Session.create(
            client_reference_id=organization_id,
            customer=customer_stripe_id,
            metadata={
                "plan_id": plan_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "external_plan_id": external_plan_id,
                "application": application,
                "mode": mode,
                "checkout_type": STRIPE_CHECKOUT_SUBSCRIPTION,
            },
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=["card"],
            mode="subscription",
            subscription_data=subscription_data,
            allow_promotion_codes=allow_promotion_codes,
        )
        return {
            "sessionId": checkout_session["id"],
            "publicKey": settings.STRIPE_PUBLISHABLE_KEY,
        }

    @staticmethod
    def create_checkout_adding_fund(
        organization_id: str,
        customer_stripe_id: str,
        user_id: str,
        success_url: str,
        cancel_url: str,
        line_items: List[dict],
        fund_package_id: str,
        external_fund_package_id: str,
    ):
        """
        create checkout session for buying fund
        @rtype: object
        """
        checkout_session = stripe_configured.checkout.Session.create(
            client_reference_id=organization_id,
            customer=customer_stripe_id,
            metadata={
                "fund_package_id": fund_package_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "external_fund_package_id": external_fund_package_id,
                "checkout_type": STRIPE_CHECKOUT_FUND,
            },
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            allow_promotion_codes=False,
        )
        return {
            "sessionId": checkout_session["id"],
            "publicKey": settings.STRIPE_PUBLISHABLE_KEY,
        }

    @staticmethod
    def create_checkout_setup_payment(
        customer_stripe_id: str,
        success_url: str,
        cancel_url: str,
    ):
        checkout_session = stripe_configured.checkout.Session.create(
            payment_method_types=["card"],
            mode="setup",
            customer=customer_stripe_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {
            "sessionId": checkout_session["id"],
            "publicKey": settings.STRIPE_PUBLISHABLE_KEY,
        }

    @staticmethod
    def verify_data_from_event_webhook(request):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

        try:
            event_data = stripe_configured.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            return event_data
        except Exception as e:
            raise e

    @staticmethod
    def cancel_subscription(external_subscription_id):
        try:
            res = stripe_configured.Subscription.delete(external_subscription_id)
            return True if res.get("status") == "canceled" else False
        except Exception as er:
            logger.error(f"[cancel_subscription] {er}")
            raise er

    @staticmethod
    def apply_promo_code(external_subscription_id: str, promo_code_id: str):
        try:
            res = stripe_configured.Subscription.modify(
                external_subscription_id,
                promotion_code=promo_code_id
            )
            return res
        except InvalidRequestError as invalid_promo:
            raise InvalidCouponException(invalid_promo.user_message)
        except Exception as err:
            logger.error(f"[apply promotion code] {err}")
            raise err

    @staticmethod
    def retrieve_promo_code_id(promo_code: str) -> Union[str, None]:
        try:
            res = stripe_configured.PromotionCode.list(code=promo_code, limit=1, active=True)
            data = res['data']
            if not len(data):
                return None
            return data[0]['id']
        except Exception as err:
            logger.error(f"[get_list_promo_code] {err}")
            raise err

    @staticmethod
    def force_trial_end_now(external_subscription_id):
        try:
            stripe_configured.Subscription.modify(
                external_subscription_id, trial_end="now"
            )
        except Exception as er:
            logger.error(f"[force_trial_end_now] {er}")
            raise er

    @staticmethod
    def force_billing_cycle_now(external_subscription_id: str):
        """
        Stripe API
        force reset billing cycle
        testing purpose
        """
        try:
            stripe_configured.Subscription.modify(
                external_subscription_id, billing_cycle_anchor="now"
            )
        except Exception as err:
            logger.error(f"[force_billing_cycle_now] {err}")
            raise err

    @staticmethod
    def get_incoming_invoice(
        external_subscription_id: str,
        sub_items: Union[List[Dict], None],
        proration_date,
    ):
        """[summary]
        if has sub_item and proration_date -> preview
        else -> get current invoice
        Args:
            external_subscription_id (str): [description]
            sub_items (List[Dict]): [description]
            proration_date ([type]): [description]

        Returns:
            [type]: [description]
        """
        if sub_items and proration_date:
            incoming_invoice = stripe_configured.Invoice.upcoming(
                subscription=external_subscription_id,
                subscription_items=sub_items,
                subscription_proration_date=proration_date,
            )
        else:
            incoming_invoice = stripe_configured.Invoice.upcoming(
                subscription=external_subscription_id
            )
        return incoming_invoice

    @staticmethod
    def retrieve_subscription_data(external_subscription_id: str):
        return stripe_configured.Subscription.retrieve(external_subscription_id)

    @staticmethod
    def modify_subscription(external_subscription_id: str, new_items: List[Dict]):
        """
        modify items
        Args:
            external_subscription_id:
            new_items:
        """
        stripe_configured.Subscription.modify(
            external_subscription_id,
            items=new_items,
            proration_behavior="create_prorations",
        )

    @staticmethod
    def modify_subscription_payment_method(
        external_subscription_id: str, payment_method_id: str
    ):
        """
        modify payment method for the subscription
        next payment

        Args:
            external_subscription_id:
            payment_method_id:

        Returns:

        """
        return stripe_configured.Subscription.modify(
            external_subscription_id, default_payment_method=payment_method_id
        )

    @staticmethod
    def delete_subscription_payment_method(payment_method_id):
        """
        must validate owner's payment method id
        Args:
            payment_method_id:

        Returns:

        """
        return stripe_configured.PaymentMethod.detach(payment_method_id)

    @staticmethod
    def delete_card_from_customer(customer_stripe_id: str, card_id: str):
        """
        delete card from stripe
        Args:
            customer_stripe_id:
            card_id:

        Returns:

        """
        return stripe_configured.Customer.delete_source(customer_stripe_id, card_id)

    @staticmethod
    def get_current_period(external_subscription_id: str):
        sub = stripe_configured.Subscription.retrieve(external_subscription_id)
        current_period_start, current_period_end = sub.get(
            "current_period_start"
        ), sub.get("current_period_end")
        return current_period_start, current_period_end

    @staticmethod
    def get_list_charge(stripe_customer_id: str):
        result = stripe_configured.Charge.list(customer=stripe_customer_id, limit=3)
        return result.get("data", [])

    @staticmethod
    def create_invoice_item(
        external_subscription_id: str,
        stripe_customer_id: str,
        amount: int,
        description: str,
    ):
        # TODO: add tax rates
        stripe_configured.InvoiceItem.create(
            customer=stripe_customer_id,
            subscription=external_subscription_id,
            amount=amount,  # cent
            description=description,
            currency="USD",
            # tax_rates=None
        )

    @staticmethod
    def get_payment_methods(stripe_customer_id: str):
        return stripe_configured.PaymentMethod.list(
            customer=stripe_customer_id, type="card"
        )

    @staticmethod
    def create_product(amount: int, name: str):
        """
        create plan on stripe
        Args:
            amount: cent
            name: product name

        Returns:
        plan id as price
        """
        plan = stripe_configured.Plan.create(
            amount=amount, currency="usd", interval="month", product={"name": name}
        )
        return plan["id"]

    @staticmethod
    def check_customer_subscription_exist(stripe_customer_id: str) -> bool:
        """
        at least 1 subscription -> True
        else -> False
        Returns:
            object:
        """
        res = stripe_configured.Subscription.list(customer=stripe_customer_id, limit=1)
        data = res.get("data", [])
        return True if len(data) else False

    @staticmethod
    def create_customer(user: User) -> dict:
        return stripe_configured.Customer.create(
            email=user.email,
            name=user.name,
            phone=user.phone,
            metadata={"user_id": str(user.user_id)},
        )

    @staticmethod
    def get_promo_code_usage(promo_code: str) -> str:
        pro_obj: dict = stripe_configured.PromotionCode.retrieve(promo_code)
        return pro_obj.get("code", "")


def check_limit_external_users_of_organization(organization_id: str) -> bool:
    try:
        approval_org_config = ApprovalOrganizationalPayment.objects.get(
            organization_id=organization_id
        )
        limit_number = approval_org_config.max_external_users
        if limit_number == -1 or limit_number is None:
            # no limit
            return True

        current_number_org_users = OrganizationUser.objects.filter(
            organization_id=organization_id, role__key="CLIENT"
        ).count()
        if current_number_org_users < limit_number:
            return True
        return False
    except Exception as err:
        logger.error(f"[check_limit_external_users_of_organization] {err}")
        return False


def check_limit_client_of_organization(organization_id: str) -> bool:
    try:
        approval_org_config = ApprovalOrganizationalPayment.objects.get(
            organization_id=organization_id
        )
        limit_number = approval_org_config.max_workspaces
        if limit_number == -1 or limit_number is None:
            # no limit
            return True
        current_number_org_clients = Client.objects.filter(
            organization_id=organization_id
        ).count()

        if current_number_org_clients < limit_number:
            return True
        return False
    except Exception as err:
        logger.error(f"[check_limit_client_of_organization] {err}")
        return False


def convert_res_value_to_label(_input: Union[int, None]) -> Union[str, int]:
    if _input in [-1, None]:
        return "unlimited"
    return _input


def is_warned(current_value: int, intent_value: Union[None, int]) -> bool:
    if intent_value in [-1, None]:
        return False
    if current_value > intent_value:
        return True
    return False


def resource_comparison(current_value: int, intent_value: Union[None, int]) -> dict:
    return {
        "current": current_value,
        "intent": convert_res_value_to_label(intent_value),
        "is_warned": is_warned(current_value, intent_value),
    }


def warn_resource_in_organization(
    organization: Organization, intent_plan: Plan
) -> dict:
    current_number_org_clients = Client.objects.filter(
        organization_id=organization.id
    ).count()

    current_number_external_users = OrganizationUser.objects.filter(
        organization_id=organization.id, role__key="CLIENT"
    ).count()

    current_number_internal_users = (
        OrganizationUser.objects.filter(organization_id=organization.id)
        .exclude(role__key="CLIENT")
        .count()
    )
    return {
        "clients": resource_comparison(
            current_number_org_clients, intent_plan.max_workspaces
        ),
        "internal_users": resource_comparison(
            current_number_internal_users, intent_plan.max_internal_users
        ),
        "external_users": resource_comparison(
            current_number_external_users, intent_plan.max_external_users
        ),
    }


def check_limit_internal_users_of_organization(organization_id: str) -> bool:
    try:
        approval_org_config = ApprovalOrganizationalPayment.objects.get(
            organization_id=organization_id
        )

        limit_number = approval_org_config.max_internal_users
        if limit_number == -1 or limit_number is None:
            # no limit
            return True
        current_number_org_users = (
            OrganizationUser.objects.filter(organization_id=organization_id)
            .exclude(role__key="CLIENT")
            .count()
        )
        if current_number_org_users < limit_number:
            return True
        return False
    except Exception as err:
        logger.error(f"[check_limit_internal_users_of_organization] {err}")
        return False


def notify_grade_changes(
    previous_plan_name: str,
    action: str,
    subscription: Subscription,
    time_grade_changes: int,
    user: User,
    subscription_items: List,
    meta_info: dict,
):
    """

    Args:
        previous_plan_name:
        action:
        subscription:
        time_grade_changes:
        user:
        subscription_items:
        meta_info:
    """
    incoming_invoice = StripeApiServices.get_incoming_invoice(
        external_subscription_id=subscription.external_subscription_id,
        sub_items=subscription_items,
        proration_date=time_grade_changes,
    )
    extra_information = {
        "action": action,
        "previous_plan": previous_plan_name,
        "incoming_invoice": incoming_invoice,
        "subscription_proration_date": time_grade_changes,
    }
    mail_handler = PaymentEmailNotification(
        subscription=subscription,
        external_subscription_id=subscription.external_subscription_id,
        transaction_data=None,
        **extra_information,
    )
    mail_handler.mail_grade_changes(user=user, **meta_info)


def get_exclude_condition(org_id: str) -> Union[None, Dict]:
    """
    use for django ORM
    Args:
        org_id:

    Returns:

    """
    # TODO: name, refactor
    try:
        org_service_config = ApprovalOrganizationalServiceConfig.objects.get(
            organization_id=org_id
        )
        seller_and_investigation = org_service_config.config.get(
            "seller_investigation_dashboard"
        )
        seller_enforcement_enabled = org_service_config.config.get(
            "seller_enforcement_enabled"
        )

        group_in = []
        if seller_and_investigation is False:
            group_in.append(MW_SI_GROUP_KEY)
        if seller_enforcement_enabled is False:
            group_in.append(MW_SALE_ENFORCEMENT_GROUP_KEY)

        if len(group_in):
            return {"group__in": group_in}
        return None
    except ApprovalOrganizationalServiceConfig.DoesNotExist:
        return None
