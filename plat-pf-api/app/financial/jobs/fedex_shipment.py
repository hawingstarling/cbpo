from celery import current_app
from celery.utils.log import get_task_logger

from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.services.fedex_shipment.config import REOPEN_BY_EXTENSION
from app.financial.services.shipping_cost.shipping_cost_from_fedex_shipment import ShippingCostFromFedExShipment
from app.financial.services.fedex_shipment.reopen import FedExShipmentManage
from app.job.base.tasks import TaskBasement

logger = get_task_logger(__name__)


class FedExShipmentBackgroundJob(TaskBasement):
    track_started = True
    expires = (60 * 30)  # seconds

    soft_time_limit = (60 * 30)  # seconds
    time_limit = (60 * 30) + 5  # seconds

    def run(self, *args, **kwargs):
        pass


@current_app.task(bind=True, base=FedExShipmentBackgroundJob)
def sale_item_match_fedex_shipment_job(self, client_id: str, sale_item_ids: [str]):
    logger.info(f"[{client_id}][{self.request.id}][sale_item_match_fedex_shipment_job]process ... ")
    ShippingCostFromFedExShipment(sale_item_ids, client_id, 100, True).update()


@current_app.task(bind=True, base=FedExShipmentBackgroundJob)
def sale_item_reopen_fedex_shipment_job(self, client_id: str, marketplace: str = CHANNEL_DEFAULT,
                                        reopen_action: str = REOPEN_BY_EXTENSION, obj_ids: list = []):
    assert len(obj_ids) > 0 or reopen_action == REOPEN_BY_EXTENSION, \
        "[sale_item_reopen_fedex_shipment_job] sale item ids is not empty"
    logger.info(
        f"[{self.request.id}][{client_id}][{marketplace}][sale_item_reopen_fedex_shipment_job][{reopen_action}]: process reopen ... ")
    instance = FedExShipmentManage(client_id=client_id, marketplace=marketplace, obj_ids=obj_ids,
                                   reopen_action=reopen_action)
    instance.process()
