import logging
from app.financial.services.integrations.skuvaults.skuvault import SaleSKUVaultManager
from app.financial.variable.job_status import CART_ROVER_JOB

logger = logging.getLogger(__name__)


class SaleCartRoverManager(SaleSKUVaultManager):
    JOB_TYPE = CART_ROVER_JOB
