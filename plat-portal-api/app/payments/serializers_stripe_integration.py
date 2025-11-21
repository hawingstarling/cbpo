from typing import Union

from rest_framework import serializers

from app.core.logger import logger
from app.payments.config import (
    PLAN_CUSTOM,
    SUBSCRIPTION_FULL_PACKAGE,
)
from app.payments.exceptions import (
    OrganizationSubscribedPlanException,
    OrganizationHasNotSubscribedAnyPlanException,
)
from app.payments.models import (
    Plan,
    StripeCustomer,
    Subscription,
    FundPackage,
)
from app.payments.services.stripe_payment_methods import StripePaymentMethods
from app.payments.services.utils import StripeApiServices
from app.tenancies.models import User


class __SerializerMixin(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class _CheckoutSessionSerializerMixin(__SerializerMixin):
    @classmethod
    def get_stripe_customer(cls, user: User):
        try:
            return StripeCustomer.objects.get(user=user)
        except StripeCustomer.DoesNotExist:
            pass

        create_stripe_customer = StripeApiServices.create_customer(user)
        stripe_customer = StripeCustomer.objects.create(
            user=user, customer_stripe_id=create_stripe_customer["id"]
        )
        return stripe_customer

    def get_subscription(self) -> Union[Subscription, None]:
        view = self.context["view"]
        try:
            return Subscription.objects.get(
                organization_id=view.kwargs.get("organization_id")
            )
        except Subscription.DoesNotExist:
            return None


class CreateCheckoutSessionSerializer(_CheckoutSessionSerializerMixin):
    # checkout session for subscription
    success_callback_url = serializers.URLField()
    cancel_callback_url = serializers.URLField()
    plan_id = serializers.UUIDField()

    def validate(self, attrs):
        plan_id = attrs.get("plan_id")
        try:
            plan = Plan.objects.exclude(type__exact=PLAN_CUSTOM).get(id=plan_id)
            attrs.update(
                {
                    "plan": plan,
                    "trial_period_days": plan.trial_days,
                    "allow_promotion_codes": True,
                    "mode": SUBSCRIPTION_FULL_PACKAGE,
                }
            )
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Invalid plan id")

        subscription = self.get_subscription()
        request = self.context["request"]
        user_payment = request.user if not subscription else subscription.user
        stripe_customer = self.get_stripe_customer(user=user_payment)

        if (
            StripeApiServices.check_customer_subscription_exist(
                stripe_customer_id=stripe_customer.customer_stripe_id
            )
            is True
        ):
            raise OrganizationSubscribedPlanException()

        attrs.update({"customer_stripe_id": stripe_customer.customer_stripe_id})

        # ignore trialing mode for users purchased
        if subscription:
            # allow_promotion_codes is eligible for new users
            attrs.update({"trial_period_days": 0, "allow_promotion_codes": False})

        return attrs


class CreateCheckoutSessionForGradeChangesSerializer(
    _CheckoutSessionSerializerMixin, __SerializerMixin
):
    plan_id = serializers.UUIDField()

    def validate(self, attrs):
        plan_id = attrs.get("plan_id")

        try:
            plan = Plan.objects.exclude(type__exact=PLAN_CUSTOM).get(id=plan_id)
            attrs.update({"plan": plan})
        except Plan.DoesNotExist:
            raise serializers.ValidationError(detail={"plan_id": "Invalid plan"})

        subscription = self.get_subscription()
        if not subscription:
            raise OrganizationHasNotSubscribedAnyPlanException()

        if str(subscription.plan_id) == str(plan_id):
            raise serializers.ValidationError(
                detail={"plan_id": "Grade changes for the same plan is invalid!"}
            )

        if subscription.plan.type == PLAN_CUSTOM:
            raise serializers.ValidationError(
                "Not allowed to make a grade change from CUSTOM plan."
            )

        try:
            subscription_data_stripe = StripeApiServices.retrieve_subscription_data(
                external_subscription_id=subscription.external_subscription_id
            )
        except Exception as err:
            logger.error(
                f"[{0}] subscription does not exist on stripe {1}".format(
                    self.__class__.__name__, err
                )
            )
            raise OrganizationHasNotSubscribedAnyPlanException()
        if subscription_data_stripe.get("status") == "canceled":
            raise serializers.ValidationError(
                "The organization has already unsubscribed a plan"
            )

        attrs.update(
            {
                "plan": plan,
                "subscription": subscription,
                "subscription_data_stripe": subscription_data_stripe,
            }
        )
        return attrs


class PaymentMethodSerializer(__SerializerMixin):
    def validate(self, attrs):
        try:
            view = self.context.get("view")
            organization_id = view.kwargs.get("organization_id")
            subscription = Subscription.objects.get(organization_id=organization_id)
            attrs.update({"subscription": subscription})
        except Subscription.DoesNotExist:
            raise serializers.ValidationError(
                detail={
                    "organization": "The organization has not subscribed for any plans"
                }
            )
        if subscription.plan.type == PLAN_CUSTOM:
            raise serializers.ValidationError(
                detail={"plan": "Custom plan does not support this feature!"}
            )
        try:
            stripe_customer = StripeCustomer.objects.get(user=subscription.user)
        except StripeCustomer.DoesNotExist as err:
            raise err
        attrs.update({"customer_stripe_id": stripe_customer.customer_stripe_id})
        return attrs


class CreateCheckoutSessionSetupPaymentIntentSerializer(PaymentMethodSerializer):
    success_callback_url = serializers.URLField()
    cancel_callback_url = serializers.URLField()


class SetDefaultSubscriptionPaymentMethodSerializer(__SerializerMixin):
    payment_method_id = serializers.CharField()

    def validate(self, attrs):
        try:
            view = self.context.get("view")
            organization_id = view.kwargs.get("organization_id")
            subscription = Subscription.objects.get(organization_id=organization_id)
        except Subscription.DoesNotExist:
            raise serializers.ValidationError(
                "The organization has not subscribed for any plans"
            )
        attrs.update(
            {"external_subscription_id": subscription.external_subscription_id, "subscription_id": subscription.id}
        )
        return attrs


class DeleteSubscriptionPaymentMethodSerializer(
    SetDefaultSubscriptionPaymentMethodSerializer
):
    def validate(self, attrs):
        try:
            view = self.context.get("view")
            organization_id = view.kwargs.get("organization_id")
            subscription = Subscription.objects.get(organization_id=organization_id)

            stripe_customer = StripeCustomer.objects.get(user=subscription.user)
        except Subscription.DoesNotExist:
            raise serializers.ValidationError(
                "The organization has not subscribed for any plans"
            )
        except StripeCustomer.DoesNotExist as err:
            raise err

        payment_methods = StripePaymentMethods(
            stripe_customer_id=stripe_customer.customer_stripe_id
        ).get_all()

        if len(payment_methods) <= 1:
            raise serializers.ValidationError(
                "Subscription requires at least one default card for the next invoice payment attempt"
            )

        find_valid_payment_method = filter(
            lambda ele: ele.get("id") == attrs.get("payment_method_id"), payment_methods
        )
        try:
            next(find_valid_payment_method)
        except StopIteration:
            raise serializers.ValidationError(
                detail={"payment_method_id": "Invalid payment method id"}
            )

        sub_data = StripeApiServices.retrieve_subscription_data(
            subscription.external_subscription_id
        )

        if sub_data.get("default_payment_method") == attrs.get("payment_method_id"):
            raise serializers.ValidationError(
                detail={
                    "payment_method_id": "Can not remove the default payment method of the subscription"
                }
            )

        attrs.update(
            {
                "external_subscription_id": subscription.external_subscription_id,
                "stripe_customer_id": stripe_customer.customer_stripe_id,
                "subscription_id": subscription.id
            }
        )
        return attrs


class CreateCheckoutSessionAddingFundPackageSerializer(_CheckoutSessionSerializerMixin):
    # checkout session for buying more fund
    success_callback_url = serializers.URLField()
    cancel_callback_url = serializers.URLField()
    fund_package_id = serializers.UUIDField()

    def validate(self, attrs):
        fund_package_id = attrs.get("fund_package_id")
        try:
            fund_package = FundPackage.objects.get(id=fund_package_id)
            attrs.update({"fund_package": fund_package})
        except FundPackage.DoesNotExist:
            raise serializers.ValidationError({"fund_package_id": "Invalid plan id"})

        subscription = self.get_subscription()
        request = self.context["request"]
        user_payment = request.user if not subscription else subscription.user
        stripe_customer = self.get_stripe_customer(user_payment)

        attrs.update({"customer_stripe_id": stripe_customer.customer_stripe_id})
        return attrs
