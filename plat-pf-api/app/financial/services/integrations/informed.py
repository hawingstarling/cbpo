import itertools
import logging
import maya
from django.core.paginator import Paginator
from django.db.models import Q, F
from rest_framework import status
from app.financial.variable.job_status import INFORMED_PROFILE_JOB, MODIFIED_FILTER_MODE
from app.financial.services.integrations.live_feed import SaleItemsLiveFeedManager
from app.financial.models import SaleItem, AppEagleProfile, DataFlattenTrack, InformedMarketplace

logger = logging.getLogger(__name__)


class InformedProfileManager(SaleItemsLiveFeedManager):
    JOB_TYPE = INFORMED_PROFILE_JOB
    LIMIT_SIZE = 100

    def __init__(self, client_id: str, flatten: DataFlattenTrack, marketplace: str, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, marketplace=marketplace, **kwargs)

        self.informed_co_marketplace_id = InformedMarketplace.objects \
            .get(client=self.client, channel=self.channel).informed_co_marketplace_id

    def _get_data_request(self, page: int = 1):
        try:
            query_params = {
                "marketplace_id": str(self.informed_co_marketplace_id),
                "id_type": "SKU"
            }
            #
            self.prefetch_query_params(query_params)
            #
            rs = self.ac_manager.get_informed_profiles_report(client_id=self.client_id, **query_params)
            data = self._handler_result(rs)
            return data
        except Exception as ex:
            content = str(ex)
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.filter_mode}]"
                f"[{self.time_tracking}]: {content}"
            )
            self._write_errors_request(status.HTTP_400_BAD_REQUEST, content)
            return {}

    @property
    def sale_item_ids(self):
        return self.kwargs.get("sale_item_ids", [])

    @property
    def sku_ids(self):
        return self.kwargs.get("sku_ids", [])

    @property
    def is_override(self):
        return self.kwargs.get("override", False)

    def prefetch_query_params(self, query_params: dict):
        # check has request channel sale ids
        if len(self.sku_ids) > 0:
            query_params.update({"ids": self.sku_ids})
        # if len(self.sku_ids) == 0:
        #     query_params.update(
        #         {"fromDate": self.__from_date(str_format=True), "toDate": self.__to_date(str_format=True)})

    def get_items(self):
        #
        cond = Q(client_id=self.client_id, sale__channel=self.channel, sku__isnull=False)

        if not self.is_override:
            cond = cond & Q(strategy_id__isnull=True)

        # is bulk sync data
        if len(self.sale_item_ids) > 0:
            logger.info(f"[{self.__class__.__name__}][sale_item_ids]: {self.sale_item_ids}")
            cond = cond & Q(pk__in=self.sale_item_ids)
        else:
            from_date = maya.parse(self.from_date).datetime()
            to_date = maya.parse(self.to_date).datetime()
            if self.filter_mode == MODIFIED_FILTER_MODE:
                cond = cond & Q(sale_date__gte=from_date, sale_date__lte=to_date)
            else:
                cond = cond & Q(sale_date__date__gte=from_date.date(), sale_date__date__lte=to_date.date())
        #
        queryset = SaleItem.objects.tenant_db_for(self.client_id).filter(cond).order_by("-sale_date") \
            .values("sku") \
            .annotate(channel=F("sale__channel__name"), channel_sale_id=F("sale__channel_sale_id")) \
            .distinct()

        paging = Paginator(queryset, self.limit_size_request, allow_empty_first_page=False)

        return paging

    def progress(self):
        #
        pages = self.get_items()

        if pages.count == 0:
            logger.error(
                f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}] "
                f"Not found records for update..."
            )
            return

        #
        num_pages = pages.num_pages
        #
        for i in range(num_pages):
            page = i + 1

            items = pages.page(number=page).object_list

            sku_items = self.prefetch_items_for_update(items)
            #
            self.kwargs.update({"sku_ids": list(sku_items.keys())})
            #
            data = self._get_data_request()

            if not data.get("items"):
                logger.error(
                    f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}][{num_pages}] "
                    f"Not found items page {page}"
                )
                continue

            self.__process_data_page(data["items"], sku_items)

            self.bulk_process()

        self.import_manage.complete_process()

        self._write_log_process()

    def __process_data_page(self, data: list, sku_items: dict):
        for item in data:
            try:
                sku = item.get("sku")
                strategy_id = item.get("strategy_id")
                self.create_tracking(strategy_id)
                items = sku_items.pop(sku)
                for sale_item_data in items:
                    sale_item_data.update({"strategy_id": strategy_id})
                self._processing(items)
            except Exception as ex:
                logger.error(
                    f"[{self.client_id}][{self.marketplace}][{self.JOB_TYPE}][{self.time_tracking}]"
                    f"[__process_data_page] {ex}"
                )

    def create_tracking(self, strategy_id: int):
        try:
            AppEagleProfile.objects.tenant_db_for(self.client_id).get(client_id=self.client_id, profile_id=strategy_id)
        except AppEagleProfile.DoesNotExist:
            AppEagleProfile.objects.tenant_db_for(self.client_id).create(client_id=self.client_id,
                                                                         profile_id=strategy_id,
                                                                         profile_name=str(strategy_id))

    def normalize_data_item(self, item):
        return item

    @staticmethod
    def prefetch_items_for_update(items):
        sku_items = {}
        for sku, objs in itertools.groupby(items, lambda x: x["sku"]):
            sku_items.update({sku: list(objs)})
        return sku_items
