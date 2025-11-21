import logging

from celery import current_app
from app.edi.services.up_to_fedex import FedExEDIIntegration
from app.financial.models import DataFlattenTrack
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def handler_up_edi_to_fedex_shipment(self, client_id):
    try:
        flatten = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id, live_feed=True,
                                                                         type=FLATTEN_SALE_ITEM_KEY)
        logger.info(f"[up_edi_to_fedex_shipment][{self.request.id}][{flatten.client}] processing ...")
        integration = FedExEDIIntegration(client=flatten.client)
        integration.processing()
    except Exception as ex:
        logger.error(f"[{client_id}][up_edi_to_fedex_shipment] {ex}")
