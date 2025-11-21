from django.conf import settings
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION, CART_ROVER_CONNECTION, \
    INFORMED_MARKETPLACE_CONNECTION, THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION
from app.core.variable.ws_setting import DS_TRACK_ENABLED, WS_IS_OE
from app.job.models import ImportJobClient, BulkJobClient, SyncAnalysisJobClient, CommunityJobClient, \
    TimeControlJobClient, SyncDataSourceJobClient, DataSourceCalculationJobClient, SellingPartnerJobClient, \
    StatsReportJobClient, COGSMappingJobClient
from app.job.utils.variable import IMPORT_CATEGORY, BULK_CATEGORY, SYNC_ANALYSIS_CATEGORY, COMMUNITY_CATEGORY, \
    TIME_CONTROL_CATEGORY, SYNC_DATA_SOURCE_CATEGORY, DATA_SOURCE_CALCULATION_CATEGORY, SELLING_PARTNER_CATEGORY, \
    STATS_REPORT_CATEGORY, COGS_MAPPING_CATEGORY

CATEGORY_MODEL = {
    COMMUNITY_CATEGORY: CommunityJobClient,
    IMPORT_CATEGORY: ImportJobClient,
    BULK_CATEGORY: BulkJobClient,
    SYNC_ANALYSIS_CATEGORY: SyncAnalysisJobClient,
    TIME_CONTROL_CATEGORY: TimeControlJobClient,
    SYNC_DATA_SOURCE_CATEGORY: SyncDataSourceJobClient,
    DATA_SOURCE_CALCULATION_CATEGORY: DataSourceCalculationJobClient,
    SELLING_PARTNER_CATEGORY: SellingPartnerJobClient,
    STATS_REPORT_CATEGORY: StatsReportJobClient,
    COGS_MAPPING_CATEGORY: COGSMappingJobClient,
}

CATEGORY_PRIORITY_CONFIG = {
    SYNC_ANALYSIS_CATEGORY: {
        "default": 5,
        "app.financial.jobs.live_feed.handler_trigger_live_feed_sale_item_ws": 1,
        "app.financial.jobs.data_flatten.flat_sale_items_bulks_sync_task": 3,
        "app.financial.jobs.event.handler_trigger_trans_event_sale_item_ws": 3,
        "app.financial.jobs.sale_event.handler_trans_event_data_to_sale_level": 3,
        "app.financial.jobs.informed.handler_trigger_informed_sale_item_ws": 3,
        "app.financial.jobs.cart_rover.handler_trigger_cart_rover_sale_item_ws": 3,
        "app.third_party_logistic.tasks.handler_getting_prime_3pl_central_ws": 3,
    },
    BULK_CATEGORY: {
        "default": 2
    },
    IMPORT_CATEGORY: {
        "default": 5
    },
    COMMUNITY_CATEGORY: {
        "default": 7,
        "app.financial.jobs.alert.process_alert_refresh_rate_ws": 3,
        "app.financial.jobs.alert.process_alert_throttling_period_ws": 3
    },
    TIME_CONTROL_CATEGORY: {
        "default": 7,
        "app.financial.jobs.time_control.handler_time_control_process_type_is_ready_workspace": 5
    },
    SYNC_DATA_SOURCE_CATEGORY: {
        "default": 5
    },
    DATA_SOURCE_CALCULATION_CATEGORY: {
        "default": 5
    },
    SELLING_PARTNER_CATEGORY: {
        "default": 5
    },
    STATS_REPORT_CATEGORY: {
        "default": 5
    },
    COGS_MAPPING_CATEGORY: {
        "default": 2
    },
}

CATEGORY_TIME_LIMIT_CONFIG = {
    SYNC_ANALYSIS_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    BULK_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT,
        "app.financial.jobs.bulk_process.processing_bulk_brand_setting": 1805,
        "app.financial.jobs.bulk_process.processing_bulk_module_chunk": 1805,
    },
    IMPORT_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    COMMUNITY_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    TIME_CONTROL_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    SYNC_DATA_SOURCE_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    DATA_SOURCE_CALCULATION_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    SELLING_PARTNER_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    STATS_REPORT_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    },
    COGS_MAPPING_CATEGORY: {
        "default": settings.CELERYD_TASK_SOFT_TIME_LIMIT
    }
}

CATEGORY_MAX_RECURSIVE_CONFIG = {
    SYNC_ANALYSIS_CATEGORY: {
        "default": 1
    },
    BULK_CATEGORY: {
        "default": 1
    },
    IMPORT_CATEGORY: {
        "default": 1
    },
    COMMUNITY_CATEGORY: {
        "default": 1
    },
    TIME_CONTROL_CATEGORY: {
        "default": 1
    },
    SYNC_DATA_SOURCE_CATEGORY: {
        "default": 1
    },
    DATA_SOURCE_CALCULATION_CATEGORY: {
        "default": 1
    },
    SELLING_PARTNER_CATEGORY: {
        "default": 1
    },
    STATS_REPORT_CATEGORY: {
        "default": 1
    },
    COGS_MAPPING_CATEGORY: {
        "default": 1
    }
}

CATEGORY_VALIDATIONS_CONFIG = {
    SYNC_ANALYSIS_CATEGORY: {
        "default": [DS_TRACK_ENABLED],
        "app.financial.jobs.mapping_common_fields_items.handler_mapping_common_fields_sale_item_from_dc": [
            DS_TRACK_ENABLED,
            WS_IS_OE
        ],
        "app.financial.jobs.live_feed.handler_trigger_live_feed_sale_item_ws": [
            DS_TRACK_ENABLED,
            SELLER_PARTNER_CONNECTION
        ],
        "app.financial.jobs.event.handler_trigger_trans_event_sale_item_ws": [
            DS_TRACK_ENABLED,
            SELLER_PARTNER_CONNECTION
        ],
        "app.financial.jobs.sale_event.handler_trans_event_data_to_sale_level": [
            DS_TRACK_ENABLED,
            SELLER_PARTNER_CONNECTION
        ],
        "app.financial.jobs.informed.handler_trigger_informed_sale_item_ws": [
            DS_TRACK_ENABLED,
            INFORMED_MARKETPLACE_CONNECTION
        ],
        "app.financial.jobs.cart_rover.handler_trigger_cart_rover_sale_item_ws": [
            DS_TRACK_ENABLED,
            CART_ROVER_CONNECTION
        ],
        "app.third_party_logistic.tasks.handler_getting_prime_3pl_central_ws": [
            DS_TRACK_ENABLED,
            THIRD_PARTY_LOGISTIC_CENTRAL_CONNECTION
        ]
    },
    BULK_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    IMPORT_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    COMMUNITY_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    TIME_CONTROL_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    SYNC_DATA_SOURCE_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    DATA_SOURCE_CALCULATION_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    SELLING_PARTNER_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    STATS_REPORT_CATEGORY: {
        "default": [DS_TRACK_ENABLED]
    },
    COGS_MAPPING_CATEGORY: {
        "default": [DS_TRACK_ENABLED],
        "app.financial.jobs.mapping_common_fields_items.handler_mapping_cog_fields_sale_item_from_dc": [
            DS_TRACK_ENABLED,
            WS_IS_OE
        ],
    }
}
