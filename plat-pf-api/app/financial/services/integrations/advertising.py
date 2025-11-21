import logging
from abc import ABC
from datetime import timedelta, datetime
from typing import List

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from plat_import_lib_api.services.utils.utils import divide_chunks

from app.financial.models import Brand, DataFlattenTrack, AdSpendInformation
from app.financial.services.integrations.base import IntegrationFinancialBase
from app.financial.services.utils.helper import bulk_sync
from app.financial.variable.job_status import ADVERTISING_JOB

logger = logging.getLogger(__name__)

BRAND_CHUNK_SIZE = 10
AD_DATA_CHUNK_SIZE = 2000


class AdvertisingManager(IntegrationFinancialBase, ABC):
    JOB_TYPE = ADVERTISING_JOB

    def __init__(self, client_id: str, flatten: DataFlattenTrack, **kwargs):
        super().__init__(client_id=client_id, flatten=flatten, **kwargs)
        #
        self.log_feed = self._init_log()
        brands = Brand.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id)
        self.brand_map = {brand.name: brand for brand in brands}

    def progress(self):
        brand_names = list(set(self.brand_map.keys()))
        for chunk in divide_chunks(brand_names, BRAND_CHUNK_SIZE):
            query_params = {
                'date_from': self.from_date,
                'date_to': self.to_date,
                'brand_names': chunk
            }
            rs = self.ac_manager.get_ad_spend_information(**query_params)
            ad_data = self._handler_result(rs)
            self.__insert_or_update_ad_spend_information(ad_data)
            logger.info("Finished syncing ad_spend_info of {}".format(chunk))

    @property
    def fields_accept_mapping(self):
        return ['brand', 'date', 'sales', 'spend', 'impression', 'acos', 'roas', 'ad_revenue_1_day', 'ad_revenue_7_day',
                'ad_revenue_14_day', 'ad_revenue_30_day']

    def __insert_or_update_ad_spend_information(self, ad_data: List[dict]):
        brand_names = []
        instances = []
        for data in ad_data:
            try:
                name = data['name']
                #
                brand_names.append(name)
                #
                validated_data = {}
                #
                for field in self.fields_accept_mapping:
                    if field == 'brand':
                        val = self.brand_map[name]
                    elif field == 'date':
                        val = datetime.strptime(data[field], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                    else:
                        val = data[field]
                    validated_data.update({field: val})
                #
                instance = AdSpendInformation(**validated_data)
                instances.append(instance)
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}]: {ex}")
                continue
        if not instances:
            return
        filters = Q(brand__name__in=brand_names)
        for chunk in divide_chunks(instances, AD_DATA_CHUNK_SIZE):
            try:
                with transaction.atomic():
                    bulk_sync(client_id=self.client_id, new_models=chunk,
                              filters=filters,
                              fields=self.fields_accept_mapping,
                              key_fields=['brand', 'date'],
                              skip_deletes=True)
            except Exception as ex:
                logger.error(ex)

    @classmethod
    def _from_date(cls):
        return (timezone.now() - timedelta(days=3)).replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d')

    @classmethod
    def _to_date(cls):
        return timezone.now().strftime('%Y-%m-%d')
