import logging

from app.financial.services.sale_item_bulk.custom_report_type.cogs_conflict import COGSConflictCustomReportModuleService
from app.financial.services.sale_item_bulk.custom_report_type.item import ItemCustomReportModuleService
from plat_import_lib_api.models import DataImportTemporary

from app.core.context import AppContext
from app.database.helper import get_connection_workspace
from app.financial.services.sale_item_bulk.custom_report_type.analysis import SaleItemCustomReportModuleService
from app.financial.services.sale_item_bulk.custom_report_type.shipping_invoice import \
    ShippingInvoiceCustomReportModuleService
from app.financial.services.sale_item_bulk.custom_report_type.shipping_invoice_trans import \
    ShippingInvoiceTransCustomReportModuleService
from app.financial.services.sale_item_bulk.custom_report_type.shipping_invoice_trans_unmatched import \
    ShippingInvoiceTransUnmatchedCustomReportModuleService
from app.financial.services.sale_item_bulk.custom_report_type.top_asins import TopASINsCustomReportModuleService
from app.financial.variable.report import SHIPPING_INVOICE_CR_TYPE, ANALYSIS_CR_TYPE, SHIPPING_INVOICE_TRANS_CR_TYPE, \
    ITEMS_CR_TYPE, SHIPPING_INVOICE_TRANS_UNMATCHED_CR_TYPE, TOP_ASINS_CR_TYPE, COGS_CONFLICT_CR_TYPE
from plat_import_lib_api.static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)


class CustomReportManager:

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        self.client_id = client_id
        self.client_db = get_connection_workspace(self.client_id)
        self.bulk = DataImportTemporary.objects.db_manager(using=self.client_db).get(pk=bulk_id, client_id=client_id)
        self.custom_report_type = self.bulk.meta.get('custom_report_type')
        self.report_service = self.get_service(self.custom_report_type)(bulk_id=bulk_id,
                                                                        jwt_token=jwt_token,
                                                                        user_id=user_id,
                                                                        client_id=client_id)

        self.load_queue_environment()

    def load_queue_environment(self):
        if plat_import_setting.use_queue:
            context = AppContext.instance()
            context.client_id = str(self.client_id)

    @property
    def config_services(self):
        return {
            ANALYSIS_CR_TYPE: SaleItemCustomReportModuleService,
            SHIPPING_INVOICE_CR_TYPE: ShippingInvoiceCustomReportModuleService,
            SHIPPING_INVOICE_TRANS_CR_TYPE: ShippingInvoiceTransCustomReportModuleService,
            SHIPPING_INVOICE_TRANS_UNMATCHED_CR_TYPE: ShippingInvoiceTransUnmatchedCustomReportModuleService,
            ITEMS_CR_TYPE: ItemCustomReportModuleService,
            TOP_ASINS_CR_TYPE: TopASINsCustomReportModuleService,
            COGS_CONFLICT_CR_TYPE: COGSConflictCustomReportModuleService
        }

    def get_service(self, report_type):
        return self.config_services.get(report_type, SaleItemCustomReportModuleService)

    def create_bulk_process_chunks(self):
        self.report_service.create_bulk_process_chunks()

    def start_processing(self):
        self.report_service.start_processing()
