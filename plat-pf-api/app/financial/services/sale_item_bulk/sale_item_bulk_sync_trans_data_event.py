import logging
from app.financial.services.integrations.sale import SaleIntegrationTransEvent
from app.financial.variable.job_status import BULK_SYNC_TRANS_DATA_EVENT_JOB

logger = logging.getLogger(__name__)


class SaleItemBulkSyncTransDataEvent(SaleIntegrationTransEvent):
    JOB_TYPE = BULK_SYNC_TRANS_DATA_EVENT_JOB
