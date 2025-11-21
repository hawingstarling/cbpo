import logging
from ..utils.variable import SYNC_ANALYSIS_CATEGORY
from ...core.helper import get_connections_client_channels
from ...core.variable.marketplace import INFORMED_MARKETPLACE_CONNECTION, SELLER_PARTNER_CONNECTION, \
    CART_ROVER_CONNECTION, CHANNEL_DEFAULT
from ...core.variable.ws_setting import WS_IS_OE, DS_TRACK_ENABLED

logger = logging.getLogger(__name__)


class CategoryJobValidation:
    def __init__(self, category: str, job: any):
        self.category = category
        self.job = job
        self.client_connections = None
        self._status = False
        self._msg = []

    @property
    def status(self):
        return self._status

    @property
    def msg(self):
        return self._msg

    def on_valid_validation(self, connection_type: str):
        logger.debug(f"[on_valid_validation][{self.category}][{self.job.pk}][{connection_type}] Begin ...")
        configs = {
            DS_TRACK_ENABLED: {
                "category": [SYNC_ANALYSIS_CATEGORY],
                "verify": True,
                "msg": "data service is not ready"
            },
            WS_IS_OE: {
                "verify": False,
                "msg": "seller partner marketplace is not connection"
            },
            SELLER_PARTNER_CONNECTION: {
                "verify": True,
                "msg": "seller partner marketplace is not connection"
            },
            CART_ROVER_CONNECTION: {
                "verify": True,
                "msg": "cart rover is not connection"
            },
            INFORMED_MARKETPLACE_CONNECTION: {
                "verify": True,
                "msg": "informed marketplace enabled is not valid"
            }
        }
        status = self.client_connections[connection_type].get(self.job.meta.get("marketplace", CHANNEL_DEFAULT), False)
        category = configs[connection_type].get("category", [])
        if category and self.category not in category:
            return
        assert status is configs[connection_type]["verify"], configs[connection_type]["msg"]

    def on_process(self):
        logger.info(f"[on_process][{self.category}][{self.job.pk}] Begin ...")
        if not self.job.is_run_validations or not self.job.validations:
            return self
        #
        try:
            self.client_connections = get_connections_client_channels(
                client_id=self.job.client_id,
                marketplaces=[self.job.meta.get("marketplace", CHANNEL_DEFAULT)],
                connection_types=self.job.validations
            )
        except Exception as ex:
            self._msg.append(f"get_connections_client_channels: {ex}")
            return self

        for validation in self.job.validations:
            try:
                self.on_valid_validation(validation)
            except Exception as ex:
                self._msg.append(f"{validation}: {ex}")
        return self

    def on_complete(self):
        logger.info(f"[on_complete][{self.category}][{self.job.pk}] Begin ...")
        if len(self._msg) == 0:
            self._status = True
        return self
