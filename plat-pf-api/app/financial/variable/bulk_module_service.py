from app.financial.import_template.custom_report import SaleItemCustomReport
from app.financial.import_template.sale_item_bulk_edit import SaleItemBulkEdit
from app.financial.import_template.sale_item_bulk_sync import SaleItemBulkSync
from app.financial.jobs.brand_setting import BRAND_SETTING_MODULE_UPDATE_SALES
from app.financial.services.sale_item_bulk import SaleItemBulkSyncModuleService, SaleItemBulkEditModuleService
from app.financial.services.sale_item_bulk.custom_report import CustomReportManager

bulk_module_config = {
    SaleItemBulkSync.__NAME__: SaleItemBulkSyncModuleService,
    SaleItemBulkEdit.__NAME__: SaleItemBulkEditModuleService,
    SaleItemCustomReport.__NAME__: CustomReportManager,
    BRAND_SETTING_MODULE_UPDATE_SALES: None
}
