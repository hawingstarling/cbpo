import calendar
import logging
import math
import pandas as pds
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import connections, DatabaseError, transaction
from plat_import_lib_api.services.utils import utils as import_lib_utils
from app.core.exceptions import SqlExecutionException
from app.financial.services.feeds.base import BaseDataFeed
from app.financial.sql_generator.flat_items_sql_generator import FlatItemsSQLGenerator
from app.financial.sub_serializers.data_feed_serializer import DataFeedTrackSerializer
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.financial.variable.job_status import SUCCESS
from config.settings.common import DATA_FLATTEN_EXPORT_FOLDER
from app.financial.variable.data_feed import DATA_FEED_FILE_SIZE

logger = logging.getLogger(__name__)


class SaleItemDataFeed(BaseDataFeed):
    FEED_TYPE = FLATTEN_SALE_ITEM_KEY

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)

    def prefetch_range_date_scheduler(self):
        self.from_date = self.yesterday - relativedelta(months=12)
        self.from_date = self.from_date.replace(day=1, hour=0, minute=0, second=0, microsecond=000)
        #
        number_day = calendar.monthrange(self.to_date.year, self.to_date.month)[1]
        self.to_date = self.to_date.replace(day=number_day, hour=23, minute=59, second=59, microsecond=999)
        self._prefetch_ranges_date_split_month(self.from_date, self.to_date)

    def generate(self):
        list_file_paths = set()
        list_file_uris = set()
        try:
            for range_date in self.ranges_dates:
                from_date = range_date['from_date']
                to_date = range_date['to_date']
                month = from_date.month
                year = from_date.year

                feed_date = from_date.strftime('%Y-%m-%d')

                time_format_storage = from_date.strftime('%Y/%m/%d')

                with transaction.atomic():
                    count = self.count_rows_flatten(from_date, to_date)
                    page_size = DATA_FEED_FILE_SIZE
                    total_page = math.ceil(count / page_size)

                    if count == 0:
                        logger.info(
                            f'[{self.__class__.__name__}][{self.client_id}][{self.channel.name}][{self.brand.name}][{month}][{year}] No found data for generate file')
                        continue

                    # Set latest=False for other old_data_feeds
                    self.disabled_before_feeds(from_date=from_date, to_date=to_date)

                    logger.info(
                        f'[{self.__class__.__name__}][{self.client_id}][{self.channel.name}][{self.brand.name}][{month}][{year}] Begin generate file feed ... ')

                    for i in range(total_page):
                        page = i + 1
                        logger.info(
                            f'[{self.__class__.__name__}] Generating - Page:{page} - Total:{total_page} - Records:{count}')
                        offset = i * page_size
                        file_path, timestamp = self.export_rows_flatten(from_date=from_date, to_date=to_date,
                                                                        offset=offset, limit=page_size)
                        list_file_paths.add(file_path)
                        # Upload local file to gcloud
                        file_name = f'{self.client_id}.{self.channel.name}.{self.brand.name}.{str.lower(self.FEED_TYPE)}.{str(timestamp)}'
                        file_uri = self.upload_file_to_gcloud(file_path=file_path, name=file_name,
                                                              time_format_storage=time_format_storage)
                        list_file_uris.add(file_uri)

                        # Create data_feed_track record
                        data_feed_data = dict(
                            client=self.client_id,
                            channel=self.channel.id,
                            action=self.action,
                            type=self.FEED_TYPE,
                            brand=self.brand.id,
                            file_uri=file_uri,
                            date=feed_date,
                            status=SUCCESS
                        )
                        serializer = DataFeedTrackSerializer(data=data_feed_data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        logger.info(
                            f'[{self.__class__.__name__}] Generated - Page:{page} - Total:{total_page} - Records:{count}')
        except Exception as ex:
            logger.error(
                f'[{self.__class__.__name__}][{self.client_id}] Failed to generate data_feed for [{self.brand}] {ex}')
            for file_uri in list_file_uris:
                import_lib_utils.delete_file_google_storage(file_uri)
        # Delete local file
        for file_path in list_file_paths:
            utils.delete_file_local(file_path)

    def get_sql_query_analysis(self, conditions: dict):
        return FlatItemsSQLGenerator().build_flat_query(client_id=self.client_id, **conditions)

    def count_rows_flatten(self, from_date: datetime, to_date: datetime):
        """
        Count rows of table flatten with conditions
        """
        # Build SQL to count rows by max_sale_date
        base_condition = self.get_base_condition_query()
        range_condition = self.get_range_condition_analysis_query(from_date, to_date)
        conditions = {
            "additional_query": range_condition
        }
        analysis_sql = self.get_sql_query_analysis(conditions).replace(";", "")
        sql = f"""
            SELECT COUNT(*)
            FROM ({analysis_sql}) AS {self.data_source_handler.get_flatten_name}
            WHERE {base_condition}
        """

        with connections[self.client_db].cursor() as cursor:
            try:
                cursor.execute(sql)
                res = cursor.fetchone()
                count = res[0]
                return count
            except Exception or DatabaseError as err:
                logger.error(err)
                raise SqlExecutionException(
                    f'[{self.__class__.__name__}] SQL execution count_rows_flatten error client_id: [{self.client_id}]')

    def export_rows_flatten(self, from_date: datetime = None, to_date: datetime = None, offset=0, limit=1000,
                            order_by='sale_date', direction='DESC'):
        """
        Export rows of table flatten
        """
        # Build SQL to retrieve rows by max_sale_date
        base_condition = self.get_base_condition_query()
        fields = ['channel_name', 'channel_id', 'state', 'state_key', 'county_key', 'sale_date', 'asin', 'title',
                  'brand', 'upc', 'sku', 'quantity', 'fulfillment_type', 'postal_code', 'spmr',
                  'state_population']
        query_field_list = ','.join(fields)
        conditions = {
            "additional_query": self.get_range_condition_analysis_query(from_date, to_date),
            "order_by_query": f""" ORDER BY "{order_by}" {direction} """
        }
        analysis_sql = self.get_sql_query_analysis(conditions).replace(";", "")
        sql = f"""
            SELECT {query_field_list}
            FROM ({analysis_sql}) AS {self.data_source_handler.get_flatten_name}
            WHERE {base_condition} 
            OFFSET {offset} LIMIT {limit}
        """
        # Retrieve and export rows to local file
        try:
            timestamp = datetime.now().timestamp()
            file_path = f'{DATA_FLATTEN_EXPORT_FOLDER}/{self.data_source_handler.get_flatten_name}.{timestamp}.csv'
            data_frame = pds.read_sql(sql, connections[self.client_db])
            data_frame.to_csv(file_path, index=False, header=True)
            return file_path, timestamp
        except Exception or DatabaseError as err:
            logger.error(err)
            raise SqlExecutionException(
                f'[{self.__class__.__name__}] SQL execution export_rows_flatten error client_id: [{self.client_id}]')

    def get_base_condition_query(self):
        brand_name = self.brand.name.replace("'", "''")
        channel_name = self.channel.name.replace("'", "''")
        condition = f"{self.data_source_handler.get_flatten_name}.brand='{brand_name}'"
        condition += f" AND {self.data_source_handler.get_flatten_name}.channel_name='{channel_name}'"
        condition += f" AND {self.data_source_handler.get_flatten_name}.state_key IS NOT NULL"
        return condition
