import logging
from celery import current_app

from app.payments.models import SubscriptionActivity
from app.payments.services.fetching_stripe_event import FetchStripeEvent

logger = logging.getLogger(__name__)


# @current_app.task(bind=True)
# def notify_low_balance(self, *args, **kwargs):
#     logger.info(f"[Scheduler][{self.request.id}][notify_low_balance] begin ...")
#     org_balance_list = OrganizationBalance.objects.all()
#     celery_result = {}
#     for ele in org_balance_list:
#         if ele.available_balance < 10000:
#             notify_low_organization_balance(ele.organization_id)
#             celery_result.update(
#                 {
#                     str(ele.organization_id): {
#                         "name": ele.organization.name,
#                         "current_balance": ele.available_balance,
#                     }
#                 }
#             )
#     return celery_result


@current_app.task(bind=True)
def cover_health_stripe_subscription_status(self, *args, **kwargs):
    logger.info(f"[Scheduler][{self.request.id}][cover_health_stripe_subscription_status] begin ...")
    checkout_session_id, organization_id, _type = (
        kwargs.get("checkout_session_id"),
        kwargs.get("organization_id"),
        kwargs.get("type"),
    )
    handler = FetchStripeEvent()

    res_actions = ["well"]
    if _type == "subscription":
        res_actions = handler.cover_health_stripe_session_subscription(
            checkout_session_id, organization_id
        )
    return {"actions": res_actions}


@current_app.task(bind=True)
def subscription_activity_tracking(self, *args, **kwargs):
    logger.info(f"[Scheduler][{self.request.id}][subscription_activity_tracking] begin ...")
    _type, subscription_id, user_id = kwargs.get("type"), kwargs.get("subscription_id"), kwargs.get("user_id")
    SubscriptionActivity.objects.create(
        subscription_id=subscription_id,
        user_id=user_id,
        action=_type,
        data=kwargs.get("data", {})
    )
    return _type
