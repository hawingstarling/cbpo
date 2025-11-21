import logging
from django.conf import settings
from elasticsearch import Elasticsearch

from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_SALE_ITEM_FINANCIAL_KEY, \
    FLATTEN_TOP_STYLES_DAILY_KEY, FLATTEN_TOP_STYLES_MTD_KEY, FLATTEN_TOP_STYLES_YTD_KEY, \
    FLATTEN_TOP_STYLES_30_DAYS_KEY, FLATTEN_YOY_MONTHLY_SALE_KEY, FLATTEN_YOY_30_DAY_SALE_KEY, \
    FLATTEN_SALE_BY_DOLLAR_KEY, FLATTEN_SALE_BY_UNIT_KEY, FLATTEN_ADVERTISING_KEY, FLATTEN_SALE_BIG_MOVES_KEY, \
    FLATTEN_ALL_SALE_COMPARISON_KEY, FLATTEN_PRODUCT_COMPARISON_KEY, FLATTEN_PRODUCT_TYPE_COMPARISON_KEY, \
    FLATTEN_PARENT_ASIN_COMPARISON_KEY, FLATTEN_PRODUCT_SALE_KEY, FLATTEN_FF_MONTHLY_SALE_KEY, \
    FLATTEN_BRAND_30_DAY_SALE_KEY, FLATTEN_SALE_BY_DIVISION_KEY, FLATTEN_OVERALL_SALES_KEY, FLATTEN_BROKEN_DOWN_SALE_KEY
from app.es.variables.config import ELASTICSEARCH_INDEX_SETTING_DEFAULT, ES_TIMEOUT

logger = logging.getLogger(__name__)


def get_es_client(client_id):
    from .models import ESClientConfig
    try:
        es_client = ESClientConfig.objects.tenant_db_for(
            client_id).get(client_id=client_id)
    except ESClientConfig.DoesNotExist:
        logger.debug(f"[get_es_client_config][{client_id}] using config default")
        es_client = None
    return es_client


def get_es_host_client(client_id):
    try:
        es_host = get_es_client(client_id).es.url
    except Exception as ex:
        es_host = settings.ELASTICSEARCH_URL_DEFAULT
    return es_host


def get_es_health(client_id: str, index: str):
    try:
        host = get_es_host_client(client_id)
        es = Elasticsearch(hosts=host, timeout=ES_TIMEOUT)
        rs = es.cluster.health(index=index)
        logger.info(f"[get_es_health][{client_id}][{index}] {rs}")
        assert rs["status"] in ["green", "yellow"], f"ES Index {index} status = 'RED'"
        return True
    except Exception as ex:
        logger.debug(f"[get_es_health][{client_id}][{index}] {ex}")
        return False


def get_es_settings_client(client_id):
    try:
        es_client = get_es_client(client_id)
        assert es_client.settings, "es client settings is not empty"
        es_setting = es_client.settings
    except Exception as ex:
        es_setting = ELASTICSEARCH_INDEX_SETTING_DEFAULT
    return es_setting


def get_es_sources_configs():
    from app.es.services.documents.sources.sale_financial import SaleFinancialDocument
    from app.es.services.documents.sources.sale_item import SaleItemDocument
    from app.es.services.documents.sources.yoy_monthly import YOYMonthlyDocument
    from app.es.services.documents.sources.yoy_30_day_sale import YOY30DaySaleDocument
    from app.es.services.documents.sources.sale_by_dollar import SaleByDollarDocument
    from app.es.services.documents.sources.sale_by_unit import SaleByUnitDocument
    from app.es.services.documents.sources.advertising import AdvertisingDocument
    from app.es.services.documents.sources.sale_big_moves import SaleBigMovesDocument
    from app.es.services.documents.sources.all_sale_comparision import AllSaleComparisionDocument
    from app.es.services.documents.sources.product_comparison import ProductComparisonDocument
    from app.es.services.documents.sources.product_type_comparison import ProductTypeComparisonDocument
    from app.es.services.documents.sources.parent_asin_comparison import ParentAsinComparisonDocument
    from app.es.services.documents.sources.product_sale import ProductSaleDocument
    from app.es.services.documents.sources.ff_monthly_sale import FFMonthlySaleDocument
    from app.es.services.documents.sources.brand_30_day_sale import Brand30DaySaleDocument
    from app.es.services.documents.sources.sale_by_division import SaleByDivisionDocument
    from app.es.services.documents.sources.overall_sales import OverallSalesDocument
    from app.es.services.documents.sources.broken_down_sale import BrokenDownSaleDocument
    from app.es.services.documents.sources.tstyle_daily import TopASINsDailyDocument
    from app.es.services.documents.sources.tstyle_mtd import TopASINsMTDDocument
    from app.es.services.documents.sources.tstyle_ytd import TopASINsYTDDocument
    from app.es.services.documents.sources.tstyle_30_days import TopASINs30DaysDocument
    return {
        FLATTEN_SALE_ITEM_KEY: SaleItemDocument,
        FLATTEN_SALE_ITEM_FINANCIAL_KEY: SaleFinancialDocument,
        FLATTEN_YOY_MONTHLY_SALE_KEY: YOYMonthlyDocument,
        FLATTEN_YOY_30_DAY_SALE_KEY: YOY30DaySaleDocument,
        FLATTEN_SALE_BY_DOLLAR_KEY: SaleByDollarDocument,
        FLATTEN_SALE_BY_UNIT_KEY: SaleByUnitDocument,
        FLATTEN_ADVERTISING_KEY: AdvertisingDocument,
        FLATTEN_SALE_BIG_MOVES_KEY: SaleBigMovesDocument,
        FLATTEN_ALL_SALE_COMPARISON_KEY: AllSaleComparisionDocument,
        FLATTEN_PRODUCT_COMPARISON_KEY: ProductComparisonDocument,
        FLATTEN_PRODUCT_TYPE_COMPARISON_KEY: ProductTypeComparisonDocument,
        FLATTEN_PARENT_ASIN_COMPARISON_KEY: ParentAsinComparisonDocument,
        FLATTEN_PRODUCT_SALE_KEY: ProductSaleDocument,
        FLATTEN_FF_MONTHLY_SALE_KEY: FFMonthlySaleDocument,
        FLATTEN_BRAND_30_DAY_SALE_KEY: Brand30DaySaleDocument,
        FLATTEN_SALE_BY_DIVISION_KEY: SaleByDivisionDocument,
        FLATTEN_OVERALL_SALES_KEY: OverallSalesDocument,
        FLATTEN_BROKEN_DOWN_SALE_KEY: BrokenDownSaleDocument,
        FLATTEN_TOP_STYLES_DAILY_KEY: TopASINsDailyDocument,
        FLATTEN_TOP_STYLES_MTD_KEY: TopASINsMTDDocument,
        FLATTEN_TOP_STYLES_YTD_KEY: TopASINsYTDDocument,
        FLATTEN_TOP_STYLES_30_DAYS_KEY: TopASINs30DaysDocument
    }
