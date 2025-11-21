#
JOB_ACTION = 'job_action'
LIVE_FEED_JOB = 'live_feed_job'
TRANS_EVENT_JOB = 'trans_event_job'
TRANS_DATA_EVENT_JOB = 'trans_data_event_job'
SALE_ITEM_FINANCIAL_JOB = 'sale_item_financial_job'
BULK_SYNC_LIVE_FEED_JOB = 'bulk_sync_live_feed_job'
BULK_SYNC_TRANS_EVENT_JOB = 'bulk_sync_trans_event_job'
BULK_SYNC_TRANS_DATA_EVENT_JOB = 'bulk_sync_trans_data_event_job'
ADVERTISING_JOB = 'advertising_job'
SKU_VAULT_JOB = 'sku_vault_job'
CART_ROVER_JOB = 'cart_rover_job'
CONNECT_3Pl_CENTRAL_JOB = 'connect_3pl_central_job'
SALE_ITEM_SEGMENT_JOB = 'sale_item_segment_job'
SALE_ITEM_FREIGHT_COST_JOB = 'sale_item_freight_cost_job'
INFORMED_PROFILE_JOB = 'informed_profile_job'
IMPORT_JOB = 'import_job'
SALE_ITEM_USER_PROVIDED_COST_JOB = 'sale_item_user_provided_cost_job'
EXTENSIV_COG_CALCULATION_JOB = 'extensiv_cog_calculation_job'

#
POSTED_FILTER_MODE = 'posted'
MODIFIED_FILTER_MODE = 'modified'

PENDING = 'PENDING'
SUCCESS = 'SUCCESS'
ERROR = 'ERROR'
GENERATING = 'GENERATING'
DEAD = 'DEAD'

JOB_STATUS = (
    (PENDING, 'Pending'),
    (SUCCESS, 'Success'),
    (ERROR, 'Error'),
    (GENERATING, 'Generating'),
    (DEAD, 'Dead'),
)
