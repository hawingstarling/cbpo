import dependency_injector.containers as containers
import dependency_injector.providers as providers

from app.financial.sql_generator.flat_advertising_sql_generator import FlatAdvertisingSQLGenerator
from app.financial.sql_generator.flat_broken_down_sales_sql_generator import FlatBrokenDownSalesSQLGenerator
from app.financial.sql_generator.flat_items_sql_generator import FlatItemsSQLGenerator
from app.financial.sql_generator.flat_financial_sql_generator_container import FlatSaleItemFinancialSQLGenerator
from app.financial.sql_generator.flat_overall_sales_sql_generator import FlatOverallSalesSQLGenerator
from app.financial.sql_generator.flat_parent_asin_comparision_sql_generator import FlatParentAsinComparisonSQLGenerator
from app.financial.sql_generator.flat_product_comparision_sql_generator import FlatProductComparisonSQLGenerator
from app.financial.sql_generator.flat_product_type_comparision_sql_generator import \
    FlatProductTypeComparisonSQLGenerator
from app.financial.sql_generator.flat_sale_brand_30_day_sale_sql_generator import FlatBrand30DaysSaleSQLGenerator
from app.financial.sql_generator.flat_top_style_30_days import FlatTopPerformingStyles30DaysSQLGenerator
from app.financial.sql_generator.flat_top_style_daily import FlatTopPerformingStylesDailySQLGenerator
from app.financial.sql_generator.flat_top_style_mtd import FlatTopPerformingStylesMTDSQLGenerator
from app.financial.sql_generator.flat_top_style_ytd import FlatTopPerformingStylesYTDSQLGenerator
from app.financial.sql_generator.flat_yoy_monthly_sale_sql_generator import FlatYOYMonthlySaleSQLGenerator
from app.financial.sql_generator.flat_yoy_30_day_sale_sql_generator import FlatYOY30DaySaleSQLGenerator
from app.financial.sql_generator.flat_sale_by_dollar_sql_generator import FlatSaleByDollarSQLGenerator
from app.financial.sql_generator.flat_sale_big_move_sql_generator import FlatSaleBigMovesSQLGenerator
from app.financial.sql_generator.flat_all_sale_comparision_sql_generator import FlatAllSaleComparisonSQLGenerator
from app.financial.sql_generator.flat_sale_by_unit_sql_generator import FlatSaleByUnitSQLGenerator
from app.financial.sql_generator.flat_order_product_sale_sql_generator import FlatOrderProductSaleSQLGenerator
from app.financial.sql_generator.flat_fulfillment_monthly_sale_sql_generator import \
    FlatFulfillmentMonthlySaleSQLGenerator

from app.financial.sql_generator.flat_sale_by_divisions_sql_generator import FlatSaleByDivisionsSQLGenerator


class SqlGeneratorContainer(containers.DeclarativeContainer):
    """IoC container of Sql generator providers."""

    flat_sale_items = providers.Factory(FlatItemsSQLGenerator)

    flat_sale_items_financial = providers.Factory(FlatSaleItemFinancialSQLGenerator)

    flat_yoy_monthly_sale = providers.Factory(FlatYOYMonthlySaleSQLGenerator)

    flat_yoy_30_day_sale = providers.Factory(FlatYOY30DaySaleSQLGenerator)

    flat_sale_by_dollar = providers.Factory(FlatSaleByDollarSQLGenerator)

    flat_sale_by_unit = providers.Factory(FlatSaleByUnitSQLGenerator)

    flat_advertising = providers.Factory(FlatAdvertisingSQLGenerator)

    flat_sale_big_move = providers.Factory(FlatSaleBigMovesSQLGenerator)

    flat_brand_30_day_sale = providers.Factory(FlatBrand30DaysSaleSQLGenerator)

    flat_all_sale_comparision = providers.Factory(FlatAllSaleComparisonSQLGenerator)

    flat_product_comparison = providers.Factory(FlatProductComparisonSQLGenerator)

    flat_product_type_comparison = providers.Factory(FlatProductTypeComparisonSQLGenerator)

    flat_parent_asin_comparison = providers.Factory(FlatParentAsinComparisonSQLGenerator)

    flat_order_product_sale = providers.Factory(FlatOrderProductSaleSQLGenerator)

    flat_fulfillment_monthly_sale = providers.Factory(FlatFulfillmentMonthlySaleSQLGenerator)

    flat_sale_by_divisions = providers.Factory(FlatSaleByDivisionsSQLGenerator)

    flat_overall_sales = providers.Factory(FlatOverallSalesSQLGenerator)

    flat_broken_down_sales = providers.Factory(FlatBrokenDownSalesSQLGenerator)

    flat_top_styles_daily = providers.Factory(FlatTopPerformingStylesDailySQLGenerator)

    flat_top_styles_mtd = providers.Factory(FlatTopPerformingStylesMTDSQLGenerator)

    flat_top_styles_ytd = providers.Factory(FlatTopPerformingStylesYTDSQLGenerator)

    flat_top_styles_30_days = providers.Factory(FlatTopPerformingStyles30DaysSQLGenerator)
