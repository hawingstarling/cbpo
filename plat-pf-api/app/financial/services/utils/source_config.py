from app.financial.variable.data_flatten_variable import FLATTEN_BROKEN_DOWN_SALE_KEY, FLATTEN_OVERALL_SALES_KEY, \
    FLATTEN_YOY_MONTHLY_SALE_KEY, FLATTEN_YOY_30_DAY_SALE_KEY, \
    FLATTEN_SALE_BY_DOLLAR_KEY, FLATTEN_ADVERTISING_KEY, FLATTEN_SALE_BIG_MOVES_KEY, FLATTEN_ALL_SALE_COMPARISON_KEY, \
    FLATTEN_SALE_BY_UNIT_KEY, FLATTEN_PRODUCT_SALE_KEY, FLATTEN_FF_MONTHLY_SALE_KEY, FLATTEN_SALE_ITEM_KEY, \
    FLATTEN_SALE_ITEM_FINANCIAL_KEY, DATA_FLATTEN_ANALYSIS_INDEXES_CONFIG, FLATTEN_BRAND_30_DAY_SALE_KEY, \
    FLATTEN_PRODUCT_COMPARISON_KEY, FLATTEN_PRODUCT_TYPE_COMPARISON_KEY, FLATTEN_PARENT_ASIN_COMPARISON_KEY, \
    FLATTEN_SALE_BY_DIVISION_KEY, FLATTEN_TOP_STYLES_DAILY_KEY, FLATTEN_TOP_STYLES_30_DAYS_KEY, \
    FLATTEN_TOP_STYLES_MTD_KEY, FLATTEN_TOP_STYLES_YTD_KEY, CREATE_SOURCE_BY_QUERY, UPDATE_SOURCE_BY_BUILD_UPSERT_QUERY, \
    CREATE_SOURCE_BY_SCHEMA, UPDATE_SOURCE_BY_BUILD_INSERT_QUERY, UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY


def data_source_generator_config():
    from app.financial.sql_generator.flat_sql_generator_container import SqlGeneratorContainer
    args = {
        FLATTEN_SALE_ITEM_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_sale_items(),
            "es_key_id": "sale_item_id",
            "unique_fields": ["sale_item_id"],
            "index_fields": DATA_FLATTEN_ANALYSIS_INDEXES_CONFIG,
            "create_source_method": CREATE_SOURCE_BY_QUERY,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_UPSERT_QUERY,
            "clear_old_data": False
        },
        FLATTEN_SALE_ITEM_FINANCIAL_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_sale_items_financial(),
            "es_key_id": "financial_id",
            "unique_fields": ["financial_id"],
            "index_fields": DATA_FLATTEN_ANALYSIS_INDEXES_CONFIG,
            "create_source_method": CREATE_SOURCE_BY_QUERY,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_UPSERT_QUERY,
            "clear_old_data": False
        },
        FLATTEN_YOY_MONTHLY_SALE_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_yoy_monthly_sale(),
            "unique_fields": ["date"],
            "index_fields": [{"columns": ["date"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_INSERT_QUERY,
            "clear_old_data": False
        },
        FLATTEN_YOY_30_DAY_SALE_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_yoy_30_day_sale(),
            "unique_fields": ["date", "prior_month_date"],
            "index_fields": [{"columns": ["date", "prior_month_date"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_SALE_BY_DOLLAR_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_sale_by_dollar(),
            "unique_fields": ["brand", "fulfillment_type", "sku"],
            "index_fields": [{"columns": ["brand", "fulfillment_type", "sku"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True,
            "filter_by_last_run": True
        },
        FLATTEN_ADVERTISING_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_advertising(),
            "unique_fields": ["date", "brand_name"],
            "index_fields": [{"columns": ["date", "brand_name"], "type": "BRIN"}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_UPSERT_QUERY,
            "clear_old_data": False
        },
        FLATTEN_SALE_BIG_MOVES_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_sale_big_move(),
            "unique_fields": ["product_number"],
            "index_fields": [{"columns": ["product_number"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_BRAND_30_DAY_SALE_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_brand_30_day_sale(),
            "unique_fields": ["brand"],
            "index_fields": [{"columns": ["brand"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_ALL_SALE_COMPARISON_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_all_sale_comparision(),
            "unique_fields": ["product", "product_type", "parent_asin", "product_description"],
            "index_fields": [{"columns": ["product", "product_type", "parent_asin", "product_description"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_PRODUCT_COMPARISON_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_product_comparison(),
            "unique_fields": ["product"],
            "index_fields": [{"columns": ["product"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_PRODUCT_TYPE_COMPARISON_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_product_type_comparison(),
            "unique_fields": ["product_type"],
            "index_fields": [{"columns": ["product_type"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_PARENT_ASIN_COMPARISON_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_parent_asin_comparison(),
            "unique_fields": ["parent_asin"],
            "index_fields": [{"columns": ["parent_asin"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True,
            "filter_by_last_run": True
        },
        FLATTEN_SALE_BY_UNIT_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_sale_by_unit(),
            "unique_fields": ["brand", "fulfillment_type", "sku"],
            "index_fields": [{"columns": ["brand", "fulfillment_type", "sku"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True,
            "filter_by_last_run": True
        },
        FLATTEN_PRODUCT_SALE_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_order_product_sale(),
            "unique_fields": ["fulfillment_type"],
            "index_fields": [{"columns": ["fulfillment_type"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_INSERT_QUERY,
            "clear_old_data": False
        },
        FLATTEN_FF_MONTHLY_SALE_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_fulfillment_monthly_sale(),
            "unique_fields": ["date"],
            "index_fields": [{"columns": ["date"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_SALE_BY_DIVISION_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_sale_by_divisions(),
            "unique_fields": ["division"],
            "index_fields": [{"columns": ["division"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_OVERALL_SALES_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_overall_sales(),
            "unique_fields": ["division"],
            "index_fields": [{"columns": ["division"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_BROKEN_DOWN_SALE_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_broken_down_sales(),
            "unique_fields": ["division"],
            "index_fields": [{"columns": ["division"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_BUILD_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_TOP_STYLES_DAILY_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_top_styles_daily(),
            "unique_fields": ["parent_asin", "child_asin", "sku", "ff_type"],
            "index_fields": [{"columns": ["parent_asin", "child_asin", "sku", "ff_type"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_TOP_STYLES_MTD_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_top_styles_mtd(),
            "unique_fields": ["parent_asin", "child_asin", "sku", "ff_type"],
            "index_fields": [{"columns": ["parent_asin", "child_asin", "sku", "ff_type"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_TOP_STYLES_YTD_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_top_styles_ytd(),
            "unique_fields": ["parent_asin", "child_asin", "sku", "ff_type"],
            "index_fields": [{"columns": ["parent_asin", "child_asin", "sku", "ff_type"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
        FLATTEN_TOP_STYLES_30_DAYS_KEY: {
            "sql_generator": SqlGeneratorContainer.flat_top_styles_30_days(),
            "unique_fields": ["parent_asin", "child_asin", "sku", "ff_type"],
            "index_fields": [{"columns": ["parent_asin", "child_asin", "sku", "ff_type"]}],
            "create_source_method": CREATE_SOURCE_BY_SCHEMA,
            "update_source_method": UPDATE_SOURCE_BY_SEGMENT_INSERT_QUERY,
            "clear_old_data": True
        },
    }
    return args
