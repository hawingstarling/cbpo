import logging
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from app.financial.models import Alert, DataFlattenTrack, AlertDigest, AlertItem
from app.financial.services.api_data_source_centre import ApiCentreContainer
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party, get_flatten_source_name
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY

DS_TOKEN = settings.DS_TOKEN

logger = logging.getLogger(__name__)


class CollectSaleAlert:
    def __init__(self, client_id, alert_id):
        self.client_id = client_id
        self.alert_id = alert_id
        self.alert = Alert.objects.tenant_db_for(client_id).get(pk=alert_id)
        self.time_now = timezone.now()
        #
        self.last_refresh_rate = self.get_last_refresh_rate()
        #
        self.alert_digest = self.on_process_alert_digest()
        #
        self.is_alert_item = False

    def on_validate(self):
        assert self.alert_digest is not None, "Alert Digest is not empty"
        return self

    def on_process(self):
        self.on_process_ids_from_query()
        return self

    def on_complete(self):
        if self.is_alert_item:
            self.alert.last_refresh_rate = self.time_now
            self.alert.save()

    def get_last_refresh_rate(self):
        last_refresh_rate = self.alert.last_refresh_rate
        try:
            is_digest = AlertDigest.objects.tenant_db_for(self.client_id).filter(alert_id=self.alert_id).exists()
            if not is_digest:
                last_refresh_rate = None
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][load_conditions_from_builder] {ex}]")
        return last_refresh_rate

    @property
    def get_query_builder(self):
        try:
            query_builder = self.alert.custom_view.ds_filter["builder"]["config"]["query"]
            assert len(query_builder["conditions"]) > 0, "Query builder conditions is not empty"
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][load_conditions_from_builder] {ex}]")
            query_builder = {}
        return query_builder

    @property
    def get_query_ds(self):
        try:
            query = {"filter": self.alert.custom_view.ds_filter["base"]["config"]["query"]}
            query_builder = self.get_query_builder
            if query_builder:
                query["filter"]["conditions"].append(query_builder)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_query_ds] {ex}]")
            query = {}
        return query

    def on_process_alert_digest(self):
        try:
            name = f"{self.alert.name} - {self.time_now.replace(second=0).strftime('%Y-%m-%d %H:%M:%S')}"
            alert_digest, _ = AlertDigest.objects.tenant_db_for(self.client_id).get_or_create(client_id=self.client_id,
                                                                                              alert_id=self.alert_id,
                                                                                              is_digest=False,
                                                                                              defaults=dict(name=name))
            return alert_digest
        except MultipleObjectsReturned:
            AlertDigest.objects.tenant_db_for(self.client_id) \
                .filter(client_id=self.client_id, alert_id=self.alert_id, is_digest=False).delete()
            return None
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][on_process_alert_digest] {ex}]")
            raise ex

    def add_change_conditions(self, query: {}):
        try:
            # update sort query
            query.update({
                "orders": [{"column": "modified", "direction": "desc"}],
                "group": {
                    "columns": [],
                    "aggregations": []
                },
                "timezone": settings.DS_TZ_CALCULATE
            })
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_query_ds] {ex}]")

    def on_process_ids_from_query(self):
        query = self.get_query_ds
        #
        self.add_change_conditions(query)
        data_source_tracking = DataFlattenTrack.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                                          type=FLATTEN_SALE_ITEM_KEY)
        table_name = get_flatten_source_name(client_id=self.client_id, type_flatten=FLATTEN_SALE_ITEM_KEY)
        data_source_service = DataSource(client_id=self.client_id, type_flatten=FLATTEN_SALE_ITEM_KEY,
                                         table=table_name, access_token=DS_TOKEN,
                                         api_centre=ApiCentreContainer.data_source_central(),
                                         source=data_source_tracking.source, token_type="DS_TOKEN")
        external_id = get_id_data_source_3rd_party(source=data_source_tracking.source, client_id=self.client_id,
                                                   type_flatten=FLATTEN_SALE_ITEM_KEY)

        #
        limit = 1000
        current = 1
        alert_items = []
        try:
            query["paging"] = {"limit": limit, "current": current}
            #
            logger.info(
                f"[{self.__class__.__name__}][{external_id}][on_process_ids_from_query] query = {query}")
            fields = [
                {
                    "name": "modified",
                    "alias": "modified"
                },
                {
                    "name": "sale_item_id",
                    "alias": "sale_item_id"
                }
            ]
            query_result = data_source_service.call_query(external_id=external_id, fields=fields, **query)
            logger.info(
                f"[{self.__class__.__name__}][{external_id}][on_process_ids_from_query] totals rows = {len(query_result['rows'])}")
            for row in query_result["rows"]:
                try:
                    if AlertItem.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id,
                                                                              alert_digest__alert=self.alert,
                                                                              sale_item_id=row[1]).exists():
                        continue
                    #
                    alert_items.append(
                        AlertItem(client_id=self.client_id, alert_digest=self.alert_digest, sale_item_id=row[1]))
                except Exception as ex:
                    logger.error(f"[{self.__class__.__name__}][on_process_ids_from_query] {ex}]")

            if alert_items:
                logger.info(
                    f"[{self.__class__.__name__}][on_process_ids_from_query] number sale alert find = {len(alert_items)}")
                AlertItem.objects.tenant_db_for(self.client_id).bulk_create(alert_items, ignore_conflicts=True)
                self.is_alert_item = True
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][on_process_ids_from_query] {ex}")
