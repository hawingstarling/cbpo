import calendar
import logging
import os
from datetime import timedelta, datetime

import maya
from django.db.models import Q
from django.utils import timezone
from plat_import_lib_api.services.utils import utils as import_lib_utils
from app.database.helper import get_connection_workspace
from app.financial.models import Channel, Brand, DataFeedTrack, DataFlattenTrack
from app.financial.services.data_flatten import DataFlatten
from app.financial.sql_generator.flat_sql_generator_container import SqlGeneratorContainer
from app.financial.variable.data_feed import FEED_ACTION_SCHEDULER, FEED_ACTION_ON_DEMAND
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from config.settings.common import DATA_FLATTEN_EXPORT_FOLDER, DATA_FEED_STORAGE_FOLDER

logger = logging.getLogger(__name__)


class BaseDataFeed:
    FEED_TYPE = None

    def __init__(self, client_id: str, *args, **kwargs):
        assert kwargs.get('channel') or kwargs.get('channel_id') or kwargs.get('channel_name'), \
            "channel, channel_id or channel_name should be provided"
        assert kwargs.get('brand') or kwargs.get('brand_id') or kwargs.get('brand_name'), \
            "brand, brand_id or brand_name should be provided"

        self.args = args
        self.kwargs = kwargs
        self.client_id = str(client_id)
        self.client_db = get_connection_workspace(self.client_id)
        data_flatten_track = DataFlattenTrack.objects.tenant_db_for(client_id).get(client_id=client_id,
                                                                                   type=FLATTEN_SALE_ITEM_KEY)
        self.data_source_handler = DataFlatten(client_id=str(client_id), type_flatten=FLATTEN_SALE_ITEM_KEY,
                                               sql_generator=SqlGeneratorContainer.flat_sale_items(),
                                               source=data_flatten_track.source)

        self.__load_instances()
        # Create a temporary folder for
        os.makedirs(DATA_FLATTEN_EXPORT_FOLDER, exist_ok=True)

        #
        self.date_now = timezone.now()

        self.from_date = None
        self.to_date = self.yesterday

        #
        self._get_action()
        #
        self.ranges_dates = []
        #
        self.prefetch_range_date()

    def _get_action(self):
        if 'from_date' in self.kwargs and 'to_date' in self.kwargs:
            self.action = FEED_ACTION_ON_DEMAND
        else:
            self.action = FEED_ACTION_SCHEDULER

    def prefetch_range_date(self):
        if self.action == FEED_ACTION_ON_DEMAND:
            self._prefetch_ranges_dates_on_demand()
        else:
            self.prefetch_range_date_scheduler()

    def prefetch_range_date_scheduler(self):
        raise NotImplementedError

    def _prefetch_ranges_dates_on_demand(self):
        fd = f"{self.kwargs.get('from_date')} 00:00:00"
        td = f"{self.kwargs.get('to_date')} 23:59:59"
        self.from_date = maya.parse(fd).datetime()
        self.to_date = maya.parse(td).datetime()
        #
        self._prefetch_ranges_date_split_month(self.from_date, self.to_date)

    def _prefetch_ranges_date_split_month(self, from_date, to_date):
        if from_date.month == to_date.month and from_date.year == to_date.year:
            self.ranges_dates = [dict(from_date=from_date, to_date=to_date)]
        else:
            _date_start_fetch = from_date
            while True:
                _from_month, _from_year = _date_start_fetch.month, _date_start_fetch.year
                number_day = calendar.monthrange(_from_year, _from_month)[1]
                _from_date = datetime(year=_from_year, month=_from_month, day=1, hour=0, minute=0, second=0)
                _to_date = datetime(year=_from_year, month=_from_month, day=number_day, hour=23, minute=59,
                                    second=59)
                self.ranges_dates.append(dict(from_date=_from_date, to_date=_to_date))
                if _to_date.month == to_date.month and _to_date.year == to_date.year:
                    break
                #
                _next_date = _to_date + timedelta(days=1)
                _date_start_fetch = _next_date.replace(hour=0, minute=0, second=0)
            self.ranges_dates[0]['from_date'] = from_date
            self.ranges_dates[-1]['to_date'] = to_date

    @property
    def yesterday(self):
        return self.date_now - timedelta(days=1)

    def generate(self, *args, **kwargs):
        raise NotImplementedError

    def count_rows_flatten(self, *args, **kwargs):
        raise NotImplementedError

    def export_rows_flatten(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_range_condition_analysis_query(from_date: datetime, to_date: datetime):
        from_date, to_date = from_date.strftime('%Y-%m-%d %H:%M:%S'), to_date.strftime('%Y-%m-%d %H:%M:%S')
        additional_query = f" AND _source_table_.sale_date >= '{from_date}' " \
                           f"AND _source_table_.sale_date <= '{to_date}'"
        return additional_query

    def disabled_before_feeds(self, from_date: datetime, to_date: datetime):
        cond = Q(
            client_id=self.client_id,
            channel_id=self.channel.id,
            action=self.action,
            type=self.FEED_TYPE,
            brand_id=self.brand.id,
            date__gte=from_date.date(), date__lte=to_date.date()
        )
        DataFeedTrack.objects.tenant_db_for(self.client_id) \
            .filter(cond) \
            .update(latest=False)

    def __load_instances(self):
        if self.kwargs.get('channel'):
            self.channel = self.kwargs.get('channel')
        elif self.kwargs.get('channel_name'):
            self.channel = Channel.objects.tenant_db_for(self.client_id).get(name=self.kwargs.get('channel_name'))
        else:
            self.channel = Channel.objects.tenant_db_for(self.client_id).get(id=self.kwargs.get('channel_id'))

        if self.kwargs.get('brand'):
            self.brand = self.kwargs.get('brand')
        elif self.kwargs.get('brand_name'):
            self.brand = Brand.objects.tenant_db_for(self.client_id).get(name=self.kwargs.get('brand_name'),
                                                                         client_id=self.client_id)
        else:
            self.brand = Brand.objects.tenant_db_for(self.client_id).get(id=self.kwargs.get('brand_id'))

    @classmethod
    def remove_by(cls, **kwargs):
        """
        Remove all sale_item_data_feed of current client_id that matches conditions
        @param kwargs: filter conditions for DataFeedTrack
        """
        client_id = kwargs['client_id']
        old_data_feeds = DataFeedTrack.objects.tenant_db_for(client_id).filter(**kwargs)
        for data_feed in old_data_feeds:
            client_id = data_feed.client_id
            file_uri = data_feed.file_uri
            kwargs_info = [cls.__class__.__name__, str(client_id), data_feed.channel.name, data_feed.brand.name,
                           str(data_feed.pk), file_uri]
            try:
                import_lib_utils.delete_file_google_storage(file_uri)
                logger.info(f"[{']['.join(kwargs_info)}] Removed from cloud")
            except Exception as ex:
                logger.error(f"[{']['.join(kwargs_info)}] Failed to remove from cloud {ex}")
        old_data_feeds.delete()

    def upload_file_to_gcloud(self, file_path: str, name: str, time_format_storage: str) -> str:
        path = self.create_path_file(file_path, name, time_format_storage)
        bucket = import_lib_utils.get_bucket_google_storage()
        blob = bucket.blob(path)
        blob.upload_from_filename(file_path)
        blob.make_public()
        url = blob.public_url
        return url

    def create_path_file(self, file_path: str, name: str, time_format_storage: str):
        file_name, file_extension = import_lib_utils.get_extension_file(file_path)
        file_name = f'{name}.{file_extension}'
        if not time_format_storage:
            d, m, y = self.date_now.strftime('%d'), self.date_now.strftime('%m'), self.date_now.year
            time_format_storage = f'{y}/{m}/{d}'
        path = f"{DATA_FEED_STORAGE_FOLDER}/{time_format_storage}/{file_name}"
        return path
