from typing import List

from celery.utils.log import get_task_logger

from celery import current_app
from app.financial.models import Item, ClientSettings
from app.financial.services.sale_item_mapping.builder import MappingSaleItemBuilder
from app.job.utils.helper import register_list
from app.job.utils.variable import COGS_MAPPING_CATEGORY, MODE_RUN_PARALLEL

logger = get_task_logger(__name__)


@current_app.task(bind=True)
def handler_mapping_cog_sale_item(self, client_id: str):
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][handler_mapping_cog_sale_item] "
        f"Mapping Cog for Sale Item which are null value at COG field."
    )
    ins = MappingSaleItemBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .with_chunk_size_query_set_sale_item(5000) \
        .build_mapping_cog_from_item_12h_recent_only()
    ins.exec()


def pick_jobs_mapping_cog_sale_item_recent(client_ids: List[str]):
    jobs_data = list()
    job_name = "app.financial.jobs.mapping_common_fields_items.handler_mapping_cog_sale_item"
    module = "app.financial.jobs.mapping_common_fields_items"
    method = "handler_mapping_cog_sale_item"
    for client_id in client_ids:
        try:
            client_settings = ClientSettings.objects.tenant_db_for(
                client_id).get(client_id=client_id)
            assert client_settings.cog_use_pf is True, \
                f"The workspace doesn't enable to use COG ITEM"
            data = dict(
                name=f"mapping_cog_sale_item",
                client_id=client_id,
                job_name=job_name,
                module=module,
                method=method,
                is_run_validations=False,
                meta=dict(client_id=client_id)
            )
            jobs_data.append(data)
        except Exception as ex:
            logger.error(
                f"[{client_id}][pick_jobs_mapping_cog_sale_item_recent] {ex}")

    if jobs_data:
        register_list(COGS_MAPPING_CATEGORY, jobs_data,
                      mode_run=MODE_RUN_PARALLEL)
        logger.info(
            f"[pick_jobs_mapping_cog_sale_item_recent][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def handler_mapping_cog_sale_item_from_item_triggered(self, client_id: str, item_id: str):
    logger.info(f"[Tasks][{self.request.id}][{client_id}]"
                f"[handler_mapping_cog_sale_item_from_item_triggered] Begin ...")
    item = Item.objects.tenant_db_for(client_id).get(id=item_id)
    ins = MappingSaleItemBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .build_mapping_cog_from_item_based(item)
    ins.exec()


@current_app.task(bind=True)
def handler_mapping_common_fields_sale_item(self, client_id: str):
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}]"
        f"[mapping_common_fields_sale_item] Mapping Common Fields for Sale Item which are null at values"
    )
    mapping_fields = ["asin", "title", "upc", "size", "style",
                      "brand", "product_number", "product_type", "parent_asin"]
    ins = MappingSaleItemBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .with_chunk_size_query_set_sale_item(5000) \
        .with_common_mapping_fields(mapping_fields) \
        .with_override_mode(False) \
        .build_mapping_common_from_item_12h_recent()
    ins.exec()

    logger.info(f"[Task][{client_id}][classify fulfillment type MFN]")
    ins = MappingSaleItemBuilder.instance() \
        .tenant_db_for_only(client_id) \
        .with_chunk_size_query_set_sale_item(5000) \
        .with_override_mode(False) \
        .build_mapping_mfn_classification_12h_recent()
    ins.exec()


@current_app.task(bind=True)
def handler_mapping_common_fields_sale_item_from_ac(self, client_id: str):
    builder_mapping_sale_item = MappingSaleItemBuilder.instance()
    builder_mapping_sale_item \
        .tenant_db_for_only(client_id) \
        .with_override_mode(False) \
        .with_chunk_size_query_set_sale_item(1000)

    # AC
    builder_mapping_sale_item.with_common_mapping_fields(["upc"])

    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][BRAND][USE CACHED AC] Mapping Fields for Sale Item From AC")
    builder_mapping_sale_item.with_cached(True)
    handler_ac = builder_mapping_sale_item.build_mapping_from_live_feed_12h_recent_ac()
    handler_ac.exec()

    logger.info(
        f"[Tasks][{client_id}][BRAND][DON'T USE CACHED AC] Mapping Fields for Sale Item From AC")
    builder_mapping_sale_item.with_cached(False)
    handler_ac = builder_mapping_sale_item.build_mapping_from_live_feed_12h_recent_ac()
    handler_ac.exec()


def handler_mapping_all_fields_sale_item_from_dc(self, client_id: str, fields_mapping: List[str] = None):
    if fields_mapping is None:
        fields_mapping = ["upc", "unit_cog", "cog", "brand", "channel_brand"]
    builder_mapping_sale_item = MappingSaleItemBuilder.instance()
    builder_mapping_sale_item \
        .tenant_db_for_only(client_id) \
        .with_override_mode(False) \
        .with_chunk_size_query_set_sale_item(1000)

    # DC
    logger.info(
        f"[Tasks][{self.request.id}][{client_id}][{fields_mapping}] Mapping Fields for Sale Item From DC")
    builder_mapping_sale_item.with_common_mapping_fields(fields_mapping)
    handler_dc = builder_mapping_sale_item.build_mapping_from_live_feed_12h_recent_dc()
    handler_dc.exec()


@current_app.task(bind=True)
def handler_mapping_common_fields_sale_item_from_dc(self, client_id: str):
    fields_mapping = ["upc", "brand", "channel_brand"]
    handler_mapping_all_fields_sale_item_from_dc(
        self, client_id, fields_mapping)


def pick_jobs_mapping_sale_item_cog_dc_recent(client_ids: List[str]):
    jobs_data = list()
    job_name = "app.financial.jobs.mapping_common_fields_items.handler_mapping_cog_fields_sale_item_from_dc"
    module = "app.financial.jobs.mapping_common_fields_items"
    method = "handler_mapping_cog_fields_sale_item_from_dc"
    for client_id in client_ids:
        try:
            client_settings = ClientSettings.objects.tenant_db_for(
                client_id).get(client_id=client_id)
            assert client_settings.cog_use_dc is True, \
                f"The workspace doesn't enable to use COG DC"
            data = dict(
                name=f"mapping_cog_fields_sale_item_from_dc",
                client_id=client_id,
                job_name=job_name,
                module=module,
                method=method,
                is_run_validations=False,
                meta=dict(client_id=client_id)
            )
            jobs_data.append(data)
        except Exception as ex:
            logger.error(
                f"[{client_id}][pick_jobs_mapping_sale_item_cog_dc_recent] {ex}")

    if jobs_data:
        register_list(COGS_MAPPING_CATEGORY, jobs_data,
                      mode_run=MODE_RUN_PARALLEL)
        logger.info(
            f"[pick_jobs_mapping_sale_item_cog_dc_recent][{client_ids}] register_list app jobs completed")


@current_app.task(bind=True)
def handler_mapping_cog_fields_sale_item_from_dc(self, client_id: str):
    fields_mapping = ["unit_cog", "cog"]
    handler_mapping_all_fields_sale_item_from_dc(
        self, client_id, fields_mapping)
