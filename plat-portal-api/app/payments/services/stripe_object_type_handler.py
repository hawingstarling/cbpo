from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
from time import sleep
from typing import Union, List, Dict

from django.conf import settings

from app.core.logger import logger
from app.payments.config import (
    APP_MWRW,
    APP_TRANSIT,
    SUBSCRIPTION_POST_PAID,
    SUBSCRIPTION_PRE_PAID,
    STRIPE_CHECKOUT_SUBSCRIPTION,
    STRIPE_CHECKOUT_FUND,
)
from app.payments.exceptions import HandleSubscriptionOnlyException
from app.payments.models import (
    ApprovalOrganizationalPayment,
    ApprovalOrganizationalServiceConfig,
    Subscription,
    Transaction, SubscriptionCouponCode, CouponCodeHistory, )
from app.payments.serializers import (
    PlanConfigSerializer,
    MwPlanConfigSerializer,
    TransitPlanConfigSerializer,
)
from app.payments.services.coupon import CouponService
from app.payments.services.notifications import PaymentEmailNotification
from app.payments.services.utils import StripeApiServices
from app.tenancies.mailchimp_services import (
    MAILCHIMP_PLAN_KEY,
    MAILCHIMP_TAG_KEY,
    MAILCHIMP_TAG_PAID_KEY,
    mailchimp_handler,
)


class StripeObjectTypeHandler:
    def __init__(self, event_type: str, data: dict, **kwargs):
        """
        object types are divided into many types
        just consider 3 types which are mainly ones
        - checkout session
        - subscription
        - invoice
        """
        self.event_type = event_type
        self.object_type = data.get("object")
        self.object_status = data.get("status")
        self.raw_data = data
        self._is_from_admin_command = kwargs.get("is_from_admin_command", False)

        external_created_time = self.raw_data.get("created")
        self.external_created_time = (
            datetime.fromtimestamp(external_created_time, tz=timezone.utc)
            if external_created_time
            else None
        )

        self.dict_handler = {
            "subscription": "_object_type_subscription",  # object subscription update
            "checkout.session": "_object_type_checkout_session",  # object checkout session
            "invoice": "_object_type_invoice",  # object invoice, related with subscription
            "invoiceitem": "_object_invoiceitem",  # object invoice, change subscription plan hook,
            "charge": "_object_charge",
            "payment_intent": "_pass_handle",
        }

    @property
    def external_subscription_id(self):
        if self.object_type == "subscription":
            return self.raw_data.get("id")
        return self.raw_data.get("subscription")

    def handle(self):
        logger.info(
            "[{0}][{1}] [{2}]".format(
                self.__class__.__name__, self.object_type, self.event_type
            )
        )
        func_name = self.dict_handler.get(self.object_type, None)
        if not func_name:
            raise HandleSubscriptionOnlyException()

        handler_event_func = getattr(
            self, func_name, lambda: print("no func name matched")
        )
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self._write_down_traction)
            handler_event_func()

    def _write_down_traction(self):
        logger.info(f"[{self.__class__.__name__}][_write_down_traction]")
        try:
            Transaction.objects.create(
                transaction_type=self.event_type,
                raw_data=self.raw_data,
                status=self.object_status,
                external_subscription_id=self.external_subscription_id,
                object_type=self.object_type,
                external_created_time=self.external_created_time,
            )
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][_write_down_traction] {err}")

    def _object_invoiceitem(self):
        logger.info(f"[{self.__class__.__name__}] [grade changes event]")
        return

    def _object_type_checkout_session(self):
        """
        object type checkout.session must handle transaction type
        checkout.session.completed -> create subscription
        """
        if self.event_type == "checkout.session.completed":
            try:
                meta_data = self.raw_data.get("metadata")
                org_id = meta_data["organization_id"]
                checkout_type = meta_data.get("checkout_type", None)
                if checkout_type == STRIPE_CHECKOUT_SUBSCRIPTION:
                    data_default = {
                        "external_subscription_id": self.external_subscription_id,
                        "plan_id": meta_data["plan_id"],
                        "user_id": meta_data["user_id"],
                        "application": meta_data["application"],
                        "mode": meta_data.get("mode", None),
                        "is_removed": False,
                        "status": None,
                        "is_active": False,
                    }
                    subscription, _ = Subscription.all_objects.update_or_create(
                        organization_id=org_id, defaults=data_default
                    )
                    self._post_checkout_session_handler(subscription=subscription)
                elif (
                    checkout_type == STRIPE_CHECKOUT_FUND
                    and self.raw_data.get("payment_status", None) == "paid"
                ):
                    pass
                    # payment only-one time
                    # use this event as completed payment
                    # not as STRIPE_CHECKOUT_SUBSCRIPTION -> interval payment -> use event invoice.paid

                    # customer_stripe_id = self.raw_data.get("customer")
                    # payment_intent = self.raw_data.get("payment_intent")
                    # receipt_url = self.__get_receipt_url(
                    #     customer_stripe_id, payment_intent
                    # )
                    # user_id = meta_data.get("user_id")
                    # fund_package_id = meta_data.get("fund_package_id")
                    # self._add_balance_from_payment(
                    #     org_id,
                    #     fund_package_id,
                    #     user_id,
                    #     receipt_url,
                    # )
                    # sub = Subscription.objects.get(organization__id=org_id)
                    # # send email
                    # mailer = PaymentEmailNotification(
                    #     sub, self.external_subscription_id, self.raw_data
                    # )
                    # mailer.mail_adding_packages(
                    #     user=User.objects.get(user_id=user_id),
                    #     fund_package=FundPackage.objects.get(id=fund_package_id),
                    #     receipt_url=receipt_url,
                    # )

            except Exception as err:
                logger.error(
                    f"[{self.__class__.__name__}][_object_type_checkout_session] {err}"
                )
                raise err

    def _object_type_invoice(self):
        """
        object type "invoice" must consider event types
            - "invoice.paid"
                -> mark paid
                -> mail successful payment for client
                -> mailchimp for tag and merge vars
            - "invoice.payment_failed"
                -> change status subscription
                -> notify to both client and admin
            - "invoice.upcoming"
                -> calculate fees from submitted services
                -> notify upcoming invoice
        """
        logger.info(f"[{self.__class__.__name__}][_object_type_invoice]")
        try:
            if self.event_type == "invoice.paid":
                res = self.__get_subscription
                # save status subscription
                amount_paid = self.raw_data.get("amount_paid")
                amount = Decimal(amount_paid / 100)
                res.is_active, res.amount = True, amount
                # update subscription
                res.save(update_fields=["is_active", "amount"])

                if res.mode == SUBSCRIPTION_POST_PAID:
                    pass
                    # TODO: TBD
                    # draft invoice
                    # invoice, invoice item term
                    # used for post paid only
                    # self._invoice_handler(res, invoice_pdf_path)
                elif res.mode == SUBSCRIPTION_PRE_PAID:
                    pass
                    # balance, balance transaction term
                    # used for pre paid only
                    # is_trialing_mode = False if amount > 0 else True
                    # self._apply_balance_from_recurring_charge(
                    #     res, invoice_pdf_path, is_trialing_mode, hosted_invoice_url
                    # )
                    # send email

                _ = self.raw_data.get("invoice_pdf", None)
                _ = self.raw_data.get("hosted_invoice_url", None)

                # mode None | fully package
                # config app services
                if self.__is_subscription_create is True:
                    # do this stuff for the first payment only of the subscription
                    # update resource member
                    ApprovalOrganizationalPayment.all_objects.update_or_create(
                        organization_id=res.organization_id,
                        defaults={
                            "subscription_id": res.id,
                            "max_internal_users": res.plan.max_internal_users,
                            "max_external_users": res.plan.max_external_users,
                            "is_removed": False,
                            "max_workspaces": res.plan.max_workspaces,
                        },
                    )
                    # config
                    self.__success_payment_for_apps(res)

                # send mail
                mailer = PaymentEmailNotification(
                    res, self.external_subscription_id, self.raw_data
                )
                mailer.mail_has_subscribed()

                if self._is_coupon_applied():
                    self._update_coupon_usage(stripe_discount_object=self.raw_data["discount"])
                    self._track_coupon_history(total_discount_amounts=self.raw_data["total_discount_amounts"])
                else:
                    self._disable_all_coupons()

            elif self.event_type == "invoice.payment_failed":
                res = Subscription.objects.get(
                    external_subscription_id=self.external_subscription_id
                )
                res.is_active, res.status = False, "invoice.payment_failed"
                res.save(update_fields=["is_active", "status"])

                mail_handler = PaymentEmailNotification(
                    subscription=res,
                    external_subscription_id=res.external_subscription_id,
                    transaction_data=None,
                )

                mail_handler.mail_payment_fail(user=res.user)
                mail_handler.mail_payment_fail_admin()

            elif self.event_type == "invoice.upcoming":
                # this event comes 3 days before charging the bill
                # need to set up in stripe dashboard
                res = Subscription.objects.get(
                    external_subscription_id=self.external_subscription_id
                )
                incoming_invoice = StripeApiServices.get_incoming_invoice(
                    external_subscription_id=res.external_subscription_id,
                    sub_items=None,
                    proration_date=None,
                )
                mail_handler = PaymentEmailNotification(
                    subscription=res,
                    external_subscription_id=res.external_subscription_id,
                    transaction_data=None,
                    incoming_invoice=incoming_invoice,
                )
                mail_handler.mail_incoming_invoice(user=res.user)

        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][_object_type_invoice] {err}")
            raise err

    def _object_type_subscription(self):
        """
        object type "subscription" must consider
            - customer.subscription.deleted -> change status
            - customer.subscription.updated -> change status
            - customer.subscription.trial_will_end -> mail incoming invoice before ending trialing mode
        -> change status of subscription
        """
        if self.event_type in [
            "customer.subscription.deleted",
            "customer.subscription.updated",
            "customer.subscription.trial_will_end",
        ]:
            res = self.__get_subscription
            res.status = self.object_status

            update_fields = ["status"]
            if self.event_type == "customer.subscription.deleted":
                res.is_active = False
                update_fields = ["status", "is_active"]

                mailer = PaymentEmailNotification(
                    res, self.external_subscription_id, self.raw_data
                )
                mailer.mail_unsubscribe()

                self._deactivate_coupon_applied()
            elif self.event_type == "customer.subscription.trial_will_end":
                mailer = PaymentEmailNotification(
                    res, self.external_subscription_id, self.raw_data
                )
                mailer.mail_trial_will_end()
                if not res.expired_in:
                    expired_in = datetime.fromtimestamp(
                        self.raw_data.get("current_period_end"), tz=timezone.utc
                    )
                    res.expired_in = expired_in
                    update_fields.append("expired_in")
            elif self.event_type == "customer.subscription.updated":
                expired_in = datetime.fromtimestamp(
                    self.raw_data.get("current_period_end"), tz=timezone.utc
                )
                res.expired_in = expired_in
                update_fields = ["status", "expired_in"]

            res.save(update_fields=update_fields)

    def _object_charge(self):
        # TODO: notify client
        logger.info(f"[{self.__class__.__name__}][_object_charge] user payment")

    def _pass_handle(self):
        pass

    def __success_payment_for_apps(self, subscription: Subscription):
        logger.info(f"[{self.__class__.__name__}][__success_payment_for_apps]")
        if subscription.application == APP_TRANSIT:
            # add member mailchimp for subscription creation
            if settings.MAILCHIMP_ENABLED:
                _extra_kwargs = {
                    MAILCHIMP_PLAN_KEY: subscription.plan.type,
                    MAILCHIMP_TAG_KEY: [subscription.plan.type, MAILCHIMP_TAG_PAID_KEY],
                }

                mailchimp_handler.update_member(
                    user=subscription.user, extra_kwargs=_extra_kwargs
                )

            # tenancy config
            serializer = TransitPlanConfigSerializer(subscription.plan)
        elif subscription.application == APP_MWRW:
            # tenancy config
            # service config
            # limit daily config
            serializer = MwPlanConfigSerializer(subscription.plan)
        else:
            # tenancy config
            serializer = PlanConfigSerializer(subscription.plan)

        # save for the organization
        ApprovalOrganizationalServiceConfig.all_objects.update_or_create(
            organization=subscription.organization,
            defaults={"config": serializer.data, "is_removed": False},
        )

    @property
    def __is_subscription_create(self) -> bool:
        return (
            True
            if self.raw_data.get("billing_reason", None) == "subscription_create"
            else False
        )

    # def _invoice_handler(self, subscription: Subscription, invoice_pdf) -> Invoice:
    #     logger.info(f"[{self.__class__.__name__}][_invoice_handler]")
    #     with transaction.atomic():
    #         try:
    #             invoice = Invoice.objects.get(
    #                 organization_id=subscription.organization_id
    #             )
    #             invoice.status, invoice.invoice_pdf = INVOICE_SUCCESS, invoice_pdf
    #             invoice.save(update_fields=["status", "invoice_pdf"])
    #         except Invoice.DoesNotExist:
    #             pass
    #
    #         # get current subscription billing info
    #         current_subscription_on_stripe = (
    #             StripeApiServices.retrieve_subscription_data(
    #                 subscription.external_subscription_id
    #             )
    #         )
    #         # create the draft invoice for the next period
    #         return Invoice.objects.create(
    #             organization_id=subscription.organization_id,
    #             status=INVOICE_DRAFT,
    #             period_start=datetime.fromtimestamp(
    #                 current_subscription_on_stripe.get("current_period_start"),
    #                 tz=timezone.utc,
    #             ),
    #             period_end=datetime.fromtimestamp(
    #                 current_subscription_on_stripe.get("current_period_end"),
    #                 tz=timezone.utc,
    #             ),
    #         )

    def _post_checkout_session_handler(self, subscription: Subscription):
        logger.info(f"[{self.__class__.__name__}][_post_checkout_session_handler]")

    # def _apply_balance_from_recurring_charge(
    #     self,
    #     subscription: Subscription,
    #     invoice_pdf: str,
    #     is_trialing_mode: bool,
    #     hosted_invoice_url: str,
    # ):
    #     """
    #     fill balance from subscription's recurring charge
    #     reset balance_subscription only
    #     @param subscription:
    #     """
    #     logger.info(
    #         f"[{self.__class__.__name__}][_apply_balance_from_recurring_charge]"
    #     )
    #     with transaction.atomic():
    #         try:
    #             if self.raw_data.get("billing_reason", None) == "subscription_create":
    #                 description = f"{subscription.plan.name} subscription"
    #             else:
    #                 description = (
    #                     f"{subscription.plan.name} subscription recurrence (monthly)"
    #                 )
    #             amount = self.__get_standardization_config_balance(subscription)
    #             if is_trialing_mode:
    #                 amount = int(amount * 0.25)
    #
    #             org_balance = self.__get_organization_balance(
    #                 organization_id=subscription.organization.id
    #             )
    #             applied_balance_recurring_charge = (
    #                 amount - org_balance.balance_subscription
    #             )
    #
    #             org_balance.balance_subscription = amount
    #             org_balance.save(update_fields=["balance_subscription"])
    #             BalanceTransaction.objects.create(
    #                 organization_balance=org_balance,
    #                 amount=applied_balance_recurring_charge,
    #                 source=TRANSACTION_TYPE_RECURRING_CHARGE,
    #                 meta={
    #                     "invoice_pdf": invoice_pdf,
    #                     "hosted_invoice_url": hosted_invoice_url,
    #                 },
    #                 description=description,
    #             )
    #         except Exception as err:
    #             logger.error(
    #                 f"[{self.__class__.__name__}][_apply_balance_from_recurring_charge] {err}"
    #             )
    #             raise err
    #
    # def _add_balance_from_payment(
    #     self,
    #     organization_id: str,
    #     fund_package_id: str,
    #     user_id: str,
    #     receipt_url: str,
    # ):
    #     logger.info(f"[{self.__class__.__name__}][_add_balance_from_payment]")
    #     with transaction.atomic():
    #         org_balance = self.__get_organization_balance(
    #             organization_id=organization_id
    #         )
    #         fund_package = FundPackage.objects.get(id=fund_package_id)
    #
    #         org_balance.balance_fund = F("balance_fund") + fund_package.balance
    #         org_balance.meta = {
    #             "warned_low_balance": False,
    #             "warned_negative_balance": False,
    #         }
    #         org_balance.save(update_fields=["balance_fund", "meta"])
    #
    #         BalanceTransaction.objects.create(
    #             organization_balance=org_balance,
    #             amount=fund_package.balance,
    #             source=TRANSACTION_TYPE_USER_PURCHASE,
    #             user_id=user_id,
    #             meta={"receipt_url": receipt_url},
    #             description=f"{fund_package.name} credit package purchased.",
    #         )

    def __get_receipt_url(
            self, customer_stripe_id: str, payment_intent: str
    ) -> Union[str, None]:
        logger.info(f"[{self.__class__.__name__}][__get_invoice_path]")
        # get current charge customer
        data_charge = StripeApiServices.get_list_charge(customer_stripe_id)
        find_one = filter(
            lambda ele: ele.get("customer") == customer_stripe_id
                        and ele.get("payment_intent") == payment_intent,
            data_charge,
        )
        try:
            res = next(find_one)
            return res.get("receipt_url", None)
        except StopIteration:
            return None

    @property
    def __get_subscription(self):
        for _ in range(5):
            try:
                return Subscription.objects.get(
                    external_subscription_id=self.external_subscription_id
                )
            except Subscription.DoesNotExist:
                sleep(1)
        raise Exception("webhook error")

    # @classmethod
    # def __get_organization_balance(cls, organization_id: str):
    #     for _ in range(5):
    #         try:
    #             return OrganizationBalance.objects.get(organization_id=organization_id)
    #         except OrganizationBalance.DoesNotExist:
    #             sleep(1)
    #     raise Exception("webhook error")

    def _is_coupon_applied(self) -> bool:
        dis_count_list = self.raw_data.get("discounts", [])
        return True if len(dis_count_list) else False

    def _deactivate_coupon_applied(self):
        query_set = SubscriptionCouponCode.objects.filter(
            subscription=self.__get_subscription, is_active=True)
        if query_set.count():
            query_set.update(is_active=False)

    def _update_coupon_usage(self, stripe_discount_object: dict):
        CouponService(subscription=self.__get_subscription).update_or_create_new_promo_code(
            stripe_discount_object=stripe_discount_object)

    @classmethod
    def _track_coupon_history(cls, total_discount_amounts: List[Dict]):
        data = [{
            "discount_id": ele["discount"],
            "amount": Decimal(ele["amount"] / 100)
        } for ele in total_discount_amounts]
        if len(data):
            data = [CouponCodeHistory(**ele) for ele in data]
            CouponCodeHistory.objects.bulk_create(data)

    def _disable_all_coupons(self):
        SubscriptionCouponCode.objects.filter(subscription=self.__get_subscription).update(is_active=False)
