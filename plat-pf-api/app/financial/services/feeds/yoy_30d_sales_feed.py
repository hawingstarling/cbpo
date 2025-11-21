import logging
import math
import pandas as pds
from datetime import datetime, timedelta
from django.db.models import CharField
from django.db.models.functions import Cast
from plat_import_lib_api.services.utils import utils as import_lib_utils
from django.db import connections, DatabaseError, transaction
from app.core.exceptions import SqlExecutionException
from app.financial.models import SaleStatus
from app.financial.services.feeds.base import BaseDataFeed
from app.financial.sql_generator.flat_items_sql_generator import FlatItemsSQLGenerator
from app.financial.sub_serializers.data_feed_serializer import DataFeedTrackSerializer
from app.financial.variable.data_feed import DATA_FEED_FILE_SIZE
from app.financial.variable.data_flatten_variable import FLATTEN_YOY_30_DAY_SALE_KEY
from app.financial.variable.job_status import SUCCESS
from app.financial.variable.sale_status_static_variable import SALE_PENDING_STATUS, SALE_SHIPPED_STATUS, \
    SALE_PARTIALLY_REFUNDED_STATUS, SALE_UNSHIPPED_STATUS
from config.settings.common import DATA_FLATTEN_EXPORT_FOLDER

logger = logging.getLogger(__name__)


class YOYSaleDataFeed(BaseDataFeed):
    FEED_TYPE = FLATTEN_YOY_30_DAY_SALE_KEY

    def __init__(self, client_id: str, *args, **kwargs):
        super().__init__(client_id, *args, **kwargs)
        self.sale_status_accept = [SALE_PENDING_STATUS, SALE_UNSHIPPED_STATUS, SALE_SHIPPED_STATUS,
                                   SALE_PARTIALLY_REFUNDED_STATUS]

        self.sale_status_ids = SaleStatus.objects.tenant_db_for(self.client_id) \
            .filter(value__in=self.sale_status_accept).annotate(id_cast=Cast('pk', CharField())) \
            .values_list('id_cast', flat=True)

        self.yoy_source_alias = "yoy_sale_data_feed"

        self.additional_analysis_query = self._get_additional_analysis_query()

    def prefetch_range_date_scheduler(self):
        self.from_date = self.yesterday - timedelta(days=30)
        self.from_date = self.from_date.replace(hour=0, minute=0, second=0, microsecond=000)
        #
        self.to_date = self.to_date.replace(hour=23, minute=59, second=59, microsecond=999)
        #
        self.ranges_dates = [dict(from_date=self.from_date, to_date=self.to_date)]

    def generate(self):
        list_file_paths = set()
        list_file_uris = set()
        try:
            for date_range in self.ranges_dates:
                from_date = date_range['from_date']
                to_date = date_range['to_date']
                month = from_date.month
                year = from_date.year
                count = self.count_rows_flatten(from_date, to_date)
                #
                feed_date = from_date.strftime('%Y-%m-%d')
                time_format_storage = from_date.strftime('%Y/%m/%d')

                with transaction.atomic():
                    page_size = DATA_FEED_FILE_SIZE
                    total_page = math.ceil(count / page_size)

                    if count == 0:
                        logger.info(
                            f'[{self.__class__.__name__}][{self.client_id}][{self.channel.name}][{self.brand.name}][{month}][{year}] No found data for generate file')
                        return

                    # Set latest=False for other old_data_feeds
                    self.disabled_before_feeds(from_date, to_date)

                    logger.info(
                        f'[{self.__class__.__name__}][{self.client_id}][{self.channel.name}][{self.brand.name}][{month}][{year}] Begin generate file feed ... ')

                    for i in range(total_page):
                        page = i + 1
                        logger.info(
                            f'[{self.__class__.__name__}] Generating - Page:{page} - Total:{total_page} - Records:{count}')
                        offset = i * page_size
                        file_path, timestamp = self.export_rows_flatten(from_date=from_date, to_date=to_date,
                                                                        offset=offset,
                                                                        limit=page_size)
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

    def build_base_filter(self, client_id):
        #
        sql = f"""
            {self.data_source_handler.get_flatten_name}.channel_name = '{self.channel.name}' 
        """
        return sql

    def get_sql_query_analysis(self, conditions: dict = {}):
        return FlatItemsSQLGenerator().build_flat_query(client_id=self.client_id, **conditions)

    def _get_additional_analysis_query(self, from_date: datetime = None, to_date: datetime = None):
        if not from_date and not to_date:
            from_date, to_date = self.from_date, self.to_date
        #
        additional_query = self.get_range_condition_analysis_query(from_date, to_date)
        additional_query += f"""
            AND _source_table_.sale_status_id IN {tuple(self.sale_status_ids)} 
            AND _source_table_.brand_id = '{self.brand.id}' 
            AND _source_table_.fulfillment_type_id IS NOT NULL 
        """
        return {
            "additional_query": additional_query
        }

    def generate_cross_tab_30_days_sql(self, from_date: datetime = None, to_date: datetime = None,
                                       aggregate: str = None):
        base_cond = self.build_base_filter(self.client_id)
        #
        sql_query_analysis = self.get_sql_query_analysis(
            self._get_additional_analysis_query(from_date, to_date)).replace(';', '')

        __select_statement = """"""
        __order_by_statement = """"""
        if aggregate == 'COUNT':
            __select_statement = f"""
                DATE({self.data_source_handler.get_flatten_name}.sale_date) AS date
            """
        else:
            __select_statement = f"""
                DATE({self.data_source_handler.get_flatten_name}.sale_date) AS date, 
                ----- MFN -----
                (COUNT(DISTINCT {self.data_source_handler.get_flatten_name}.sale_id) 
                FILTER (WHERE {self.data_source_handler.get_flatten_name}."fulfillment_type" LIKE '%MFN%'))::numeric AS mfn_unit,
                (SUM({self.data_source_handler.get_flatten_name}.item_sale_charged)
                FILTER (WHERE {self.data_source_handler.get_flatten_name}."fulfillment_type" LIKE '%MFN%'))::numeric AS mfn_amount,
                ----- FBA -----
                (COUNT(DISTINCT {self.data_source_handler.get_flatten_name}.sale_id) 
                FILTER (WHERE {self.data_source_handler.get_flatten_name}."fulfillment_type" = 'FBA'))::numeric AS fba_unit,
                (SUM({self.data_source_handler.get_flatten_name}.item_sale_charged)
                FILTER (WHERE {self.data_source_handler.get_flatten_name}."fulfillment_type" = 'FBA'))::numeric AS fba_amount,
                ----- Total -----
                COUNT(DISTINCT {self.data_source_handler.get_flatten_name}.sale_id)::numeric AS total_unit,
                SUM({self.data_source_handler.get_flatten_name}.item_sale_charged)::numeric AS total_amount 
            """
            __order_by_statement = f"""
                ORDER BY date
            """

        sql = f"""
            SELECT 
                {__select_statement}
            FROM 
                ({sql_query_analysis}) AS {self.data_source_handler.get_flatten_name}
            WHERE 
                {base_cond} 
            GROUP BY {self.data_source_handler.get_flatten_name}.brand, date 
            {__order_by_statement}
        """
        return sql

    def count_rows_flatten(self, from_date: datetime, to_date: datetime):
        # Build SQL to count rows by max_sale_date
        cross_tab_30_days_sql = self.generate_cross_tab_30_days_sql(aggregate='COUNT', from_date=from_date,
                                                                    to_date=to_date)
        sql = f"""
            SELECT COUNT(*)
            FROM ({cross_tab_30_days_sql}) AS {self.yoy_source_alias}
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

    def export_rows_flatten(self, from_date: datetime, to_date: datetime, offset=0, limit=1000):
        """
        Export rows of table flatten
        """
        cross_tab_days_sql = self.generate_cross_tab_30_days_sql(from_date=from_date, to_date=to_date)
        sql = f"""
            {cross_tab_days_sql}
            LIMIT {limit} OFFSET {offset};
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
