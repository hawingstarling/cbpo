from celery import current_app
from celery.utils.log import get_task_logger

from app.financial.services.shipping_cost.builder import ShippingCostBuilder

logger = get_task_logger(__name__)


@current_app.task(bind=True)
def handler_shipping_cost_fedex_shipment_calculation(self, client_id: str):
    logger.info(f"[Tasks][{self.request.id}][{client_id}][Shipping Cost] [FedEx Shipment] Automation")
    ShippingCostBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .with_chunk_size(100) \
        .with_is_recalculate(True) \
        .build_from_fedex_shipment_for_sale_items_passive().update()


@current_app.task(bind=True)
def handler_shipping_cost_calculation(self, client_id: str):
    logger.info(f"[Tasks][{self.request.id}][{client_id}][Shipping Cost] [Brand Settings] Automation")
    ShippingCostBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .with_chunk_size(5000) \
        .with_is_recalculate(False) \
        .build_from_brand_settings_12h_recent().update()

    logger.info(f"[Tasks][{client_id}][Warehouse Processing Fee] [Brand Settings] Automation")
    ShippingCostBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .with_chunk_size(5000) \
        .with_is_recalculate(False) \
        .build_from_brand_settings_for_drop_ship_fee_12h_recent().update()


@current_app.task(bind=True)
def handler_warehouse_processing_fee_calculation(self, client_id: str, sale_item_ids: list = []):
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][handler_warehouse_processing_fee_calculation] sale_item_ids = {len(sale_item_ids)}")
    ShippingCostBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .with_sale_item_ids(sale_item_ids) \
        .with_chunk_size(5000) \
        .with_is_recalculate(True) \
        .build_from_brand_settings_for_drop_ship_fee().update()
