from app.financial.models import ClientSettings
from app.financial.observer.interface_listener import IListener
from app.job.utils.helper import register_list
from app.job.utils.variable import MODE_RUN_SEQUENTIALLY, COGS_MAPPING_CATEGORY
import logging

logger = logging.getLogger(__name__)


class SaleItemMappingCogListener(IListener):
    def run(self, **kwargs):
        """
        Register COG mapping jobs for sale items.

        Creates batch jobs to map Cost of Goods data for each item ID,
        only if COG functionality is enabled for the client workspace.

        Args:
            client_id (str): Client identifier
            item_ids (list): Item IDs to process

        Note: Jobs run sequentially to prevent conflicts.
        """
        client_id = kwargs.get("client_id")
        item_ids = kwargs.get("item_ids")

        if not client_id:
            logger.error("SaleItemMappingCogListener: client_id is required")
            return

        if not item_ids:
            logger.warning(
                f"[{client_id}][SaleItemMappingCogListener] No item_ids provided")
            return

        if not isinstance(item_ids, (list, tuple)):
            logger.error(
                f"[{client_id}][SaleItemMappingCogListener] item_ids must be a list or tuple")
            return
        try:
            client_settings = ClientSettings.objects.tenant_db_for(
                client_id).get(client_id=client_id)
            assert client_settings.cog_use_pf is True, \
                f"The workspace doesn't enable to use COG ITEM for {client_id}"
            job_data = [
                {
                    "name": f"register_mapping_sale_item_cog_{str(item_id)}",
                    "client_id": client_id,
                    "job_name": "register_mapping_sale_item_cog",
                    "module": "app.financial.jobs.mapping_common_fields_items",
                    "method": "handler_mapping_cog_sale_item_from_item_triggered",
                    "meta": {
                        "client_id": str(client_id),
                        "item_id": str(item_id)
                    }
                }
                for item_id in item_ids
            ]

            register_list(COGS_MAPPING_CATEGORY, job_data,
                          mode_run=MODE_RUN_SEQUENTIALLY)
        except ClientSettings.DoesNotExist:
            logger.error(
                f"[{client_id}][SaleItemMappingCogListener] Client settings not found")
            return
        except Exception as ex:
            logger.error(
                f"[{client_id}][SaleItemMappingCogListener][run] Unexpected error: {ex}")
