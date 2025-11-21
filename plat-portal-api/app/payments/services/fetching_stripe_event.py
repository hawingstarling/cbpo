import time
from datetime import datetime, timedelta, timezone
from typing import Tuple

from app.core.logger import logger
from app.payments.models import Subscription
from app.payments.services.stripe_object_type_handler import StripeObjectTypeHandler
from app.payments.stripe_configured import stripe_configured


class FetchStripeEvent:
    def __init__(self, range_days_to_fetch: int = 10):
        self._subscriptions = []
        self._status_should_check = ["active", "trialing", "canceled"]
        self._status_should_check_invoice = ["active", "trialing"]
        self.__range_days_to_fetch = range_days_to_fetch

    @property
    def get_statuses_for_active_subscription(self):
        return self._status_should_check_invoice

    def _get_subscriptions(self):
        created_subscription = datetime.now(tz=timezone.utc) - timedelta(
            days=self.__range_days_to_fetch
        )
        condition = {
            "created": {"gte": int(created_subscription.timestamp())},
            "limit": 99,
        }

        list_subscriptions = []

        res = stripe_configured.Subscription.list(**condition)

        list_subscriptions.extend(res.get("data", []))
        has_more = res.get("has_more", False)

        while has_more:
            logger.info(
                f"[{self.__class__.__name__}] fetching subscription from stripe ..."
            )
            time.sleep(2)
            starting_after = list_subscriptions[-1].get("id")
            res = stripe_configured.Subscription.list(
                **condition, starting_after=starting_after
            )
            has_more = res.get("has_more", False)
            list_subscriptions.extend(res.get("data", []))

        # filter only status are "active" or "trialing"
        return [
            ele
            for ele in list_subscriptions
            if ele.get("status") in self._status_should_check
        ]

    @classmethod
    def _check_is_valid_subscription_in_db(
        cls, external_subscription_id: str, status: str
    ) -> Tuple[bool, bool, bool]:
        """
        1 - subscription status
        2 - subscription's active status
        3 - subscription's instance in db
        """

        try:
            res = Subscription.objects.get(
                external_subscription_id=external_subscription_id
            )
            correct_status = False
            if res.status == status:
                correct_status = True
            return correct_status, res.is_active, True
        except Subscription.DoesNotExist:
            return False, False, False
        except Exception as err:
            logger.error(f"{err}")
            return False, False, False

    def _handle_error_subscription(self, session_obj):
        actions = []
        external_subscription_id = session_obj.get("subscription")
        stripe_subscription_data = stripe_configured.Subscription.retrieve(
            external_subscription_id
        )

        (
            correct_status,
            correct_active_status,
            exists_in_db,
        ) = self._check_is_valid_subscription_in_db(
            external_subscription_id=external_subscription_id,
            status=stripe_subscription_data.get("status"),
        )

        if not exists_in_db:
            # create subscription instance
            handler = StripeObjectTypeHandler(
                event_type="checkout.session.completed",
                data=session_obj,
            )
            handler.handle()
            actions.append("create subscription instance")

            # update status subscription
            handler = StripeObjectTypeHandler(
                event_type="customer.subscription.updated",
                data=stripe_subscription_data,
            )
            handler.handle()
            actions.append("update status subscription")

            # update subscription active status
            # send email
            # post successful payment event for apps
            latest_invoice = stripe_subscription_data.get("latest_invoice")
            raw_data_invoice = stripe_configured.Invoice.retrieve(latest_invoice)
            if (
                raw_data_invoice.get("status") == "paid"
                and raw_data_invoice.get("paid") is True
            ):
                handler_invoice = StripeObjectTypeHandler(
                    event_type="invoice.paid", data=raw_data_invoice
                )
                handler_invoice.handle()
                actions.append("update subscription active status")
                actions.append("send email")
                actions.append("post successful payment event for apps")
        else:
            # exist in db
            # status is incorrect
            if not correct_status:
                # payment is successful
                # but the status is incorrect
                handler = StripeObjectTypeHandler(
                    event_type="customer.subscription.updated",
                    data=stripe_subscription_data,
                )
                handler.handle()
                actions.append("update status subscription")
            if not correct_active_status:
                # active status is incorrect
                latest_invoice = stripe_subscription_data.get("latest_invoice")
                raw_data_invoice = stripe_configured.Invoice.retrieve(latest_invoice)
                if (
                    raw_data_invoice.get("status") == "paid"
                    and raw_data_invoice.get("paid") is True
                ):
                    handler_invoice = StripeObjectTypeHandler(
                        event_type="invoice.paid", data=raw_data_invoice
                    )
                    handler_invoice.handle()
                    actions.append("update subscription active status")
                    actions.append("send email")
                    actions.append("post successful payment event for apps")

    def __get_checkout_session(self, checkout_session_id: str):
        try:
            return stripe_configured.checkout.Session.retrieve(checkout_session_id)
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][_get_checkout_session] {err}")
            raise err

    def cover_health_stripe_session_subscription(
        self, checkout_session_id, organization_id
    ):
        try:
            subscription = Subscription.objects.get(organization_id=organization_id)
            if subscription.status is not None and subscription.is_active:
                return ["well"]
        except Subscription.DoesNotExist:
            pass
        session_obj = self.__get_checkout_session(checkout_session_id)
        try:
            if session_obj.get("payment_status") == "paid":
                return self._handle_error_subscription(session_obj)

        except Exception as err:
            logger.error(
                f"[{self.__class__.__name__}][cover_health_stripe_session_subscription] {err}"
            )
            raise err
