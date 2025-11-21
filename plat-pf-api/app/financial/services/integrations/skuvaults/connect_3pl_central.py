import logging
from app.financial.services.integrations.skuvaults.skuvault import SaleSKUVaultManager
from app.financial.variable.job_status import CONNECT_3Pl_CENTRAL_JOB

logger = logging.getLogger(__name__)


class Connect3PLCentralManager(SaleSKUVaultManager):
    JOB_TYPE = CONNECT_3Pl_CENTRAL_JOB
