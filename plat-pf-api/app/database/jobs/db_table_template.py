import logging
from ..db.schema_tables.schema_manage import DBTableModelManage
from ..db.schema_tables.tables.cache_transaction import CacheTransactionTblModel
from ..db.schema_tables.tables.cogs_conflict import COGSConflictTblModel
from ..db.schema_tables.tables.fedex_shipment import FedExShipmentTblModel
from ..db.schema_tables.tables.item import ItemTblModel
from ..db.schema_tables.tables.item_cog import ItemCOGTblModel
from ..db.schema_tables.tables.log_entry import LogEntryTblModel
from ..db.schema_tables.tables.sale import SaleTblModel
from ..db.schema_tables.tables.sale_charge_and_cost import SaleChargeAndCostTblModel
from ..db.schema_tables.tables.sale_item import SaleItemTblModel
from ..db.schema_tables.tables.sale_item_financial import SaleItemFinancialTblModel
from ..db.schema_tables.tables.generic_transaction import GenericTransactionTblModel
from ..db.schema_tables.tables.activity import ActivityTblModel
from celery import current_app
from ..db.schema_tables.tables.shipping_invoice import ShippingInvoiceTblModel
from ..db.schema_tables.tables.sku_vault_prime_track import SKUVaultPrimeTrackTblModel

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def sync_db_table_template_workspace(self, client_id: str, new_table: bool = False, sync_column: bool = False):
    db_tbl_models = [SaleTblModel, SaleChargeAndCostTblModel, SaleItemTblModel, SaleItemFinancialTblModel, ItemTblModel,
                     ItemCOGTblModel, GenericTransactionTblModel, CacheTransactionTblModel, LogEntryTblModel,
                     ActivityTblModel, SKUVaultPrimeTrackTblModel, ShippingInvoiceTblModel, FedExShipmentTblModel,
                     COGSConflictTblModel]
    client_id = str(client_id)
    for db_tbl_model in db_tbl_models:
        logger.info(
            f"[{self.request.id}][{client_id}] {db_tbl_model.__name__} processing create schema ...")
        tbl_model_manage = DBTableModelManage(client_id=client_id, tbl_model_service=db_tbl_model,
                                              new_table=new_table, sync_column=sync_column)
        try:
            tbl_model_manage.create_db_table()
        except Exception as ex:
            logger.error(f"[{db_tbl_model.__name__}][{client_id}] {ex}")
        finally:
            pass
