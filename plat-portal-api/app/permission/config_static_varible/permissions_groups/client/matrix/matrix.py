MODULE_MT_KEY = "MT"
MODULE_MT_NAME = "Matrix"

# OVERVIEW
MT_OVERVIEW_GROUP_KEY = "OVERVIEW_GROUP"
MT_OVERVIEW_GROUP_NAME = "Overview"

MT_OVERVIEW_GROUP_ENUM = (MT_OVERVIEW_GROUP_KEY, MT_OVERVIEW_GROUP_NAME)

MT_OVERVIEW_VIEW_KEY = "mat_ov_view"
MT_OVERVIEW_EDIT_KEY = "mat_ov_edit"

# OPERATIONAL ANALYTICS
# MT_OA_GROUP_KEY = 'OA_GROUP'
# MT_OA_GROUP_NAME = 'Operational Analytics'
#
# MT_OA_GROUP_ENUM = (MT_OA_GROUP_KEY, MT_OA_GROUP_NAME)
#
# MT_OPERATIONAL_ANALYTICS_VIEW_KEY = 'mat_oa_view'
# MT_OPERATIONAL_ANALYTICS_EDIT_KEY = 'mat_oa_edit'

# PRODUCT LISTING
# MT_PL_GROUP_KEY = 'PL_GROUP'
# MT_PL_GROUP_NAME = 'Product Listings'
#
# MT_PL_GROUP_ENUM = (MT_PL_GROUP_KEY, MT_PL_GROUP_NAME)
#
# MT_PRODUCT_LISTING_VIEW_KEY = 'mat_pl_view'
# MT_PRODUCT_LISTING_EDIT_KEY = 'mat_pl_edit'

# MARKETING PERFORMANCE
# MT_MP_GROUP_KEY = 'MP_GROUP'
# MT_MP_GROUP_NAME = 'Marketing Performance'
#
# MT_MP_GROUP_ENUM = (MT_MP_GROUP_KEY, MT_MP_GROUP_NAME)
#
# MT_MARKETING_PERFORMANCE_VIEW_KEY = 'mat_mp_view'
# MT_MARKETING_PERFORMANCE_EDIT_KEY = 'mat_mp_edit'

# CATEGORY MARKET SHARE
# MT_CM_GROUP_KEY = 'CM_GROUP'
# MT_CM_GROUP_NAME = 'Category Market Share'
#
# MT_CM_GROUP_ENUM = (MT_CM_GROUP_KEY, MT_CM_GROUP_NAME)
#
# MT_CATEGORY_MARKET_SHARE_VIEW_KEY = 'mat_cm_view'
# MT_CATEGORY_MARKET_SHARE_EDIT_KEY = 'mat_cm_edit'

# CUSTOM DASHBOARD
MT_CD_GROUP_KEY = "CD_GROUP"
MT_CD_GROUP_NAME = "Custom Dashboard"

MT_CD_GROUP_ENUM = (MT_CD_GROUP_KEY, MT_CD_GROUP_NAME)

MT_CUSTOM_DASHBOARD_VIEW_KEY = "mat_cd_view"
MT_CUSTOM_DASHBOARD_MANAGEMENT_KEY = "mat_cd_edit"

# Advertising module
MT_ADVERTISING_GROUP_KEY = "ADVERTISING_GROUP"
MT_ADVERTISING_GROUP_NAME = "Advertising Module"

MT_ADVERTISING_GROUP_ENUM = (MT_ADVERTISING_GROUP_KEY, MT_ADVERTISING_GROUP_NAME)

MT_ADVERTISING_VIEW_KEY = "mat_am_view"
MT_ADVERTISING_EDIT_KEY = "mat_am_edit"

# Brand Integrity
MT_BRAND_INTEGRITY_GROUP_KEY = "MT_SI_GROUP"
MT_BRAND_INTEGRITY_GROUP_NAME = "Brand Integrity"

MT_BRAND_INTEGRITY_GROUP_ENUM = (
    MT_BRAND_INTEGRITY_GROUP_KEY,
    MT_BRAND_INTEGRITY_GROUP_NAME,
)

MT_BRAND_INTEGRITY_VIEW_KEY = "mat_si_view"

# Admin

MT_ADMIN_GROUP_KEY = "MT_ADMIN_GROUP"
MT_ADMIN_GROUP_NAME = "Administration"

MT_ADMIN_GROUP_ENUM = (MT_ADMIN_GROUP_KEY, MT_ADMIN_GROUP_NAME)

MT_ADMIN_SETTING_EDIT_KEY = "mat_setting_edit"
MT_ADMIN_DS_GENERATE_KEY = "mat_admin_generate_ds_edit"
MT_ADMIN_DS_DASHBOARD_GENERATE_KEY = "mat_admin_generate_dashboard_edit"

# Geographic Analysis
MT_GEOGRAPHIC_ANALYSIS_GROUP_KEY = "GA_GROUP"
MT_GEOGRAPHIC_ANALYSIS_GROUP_NAME = "Geographic Analysis"
MT_GEOGRAPHIC_ANALYSIS_GROUP_ENUM = (
    MT_GEOGRAPHIC_ANALYSIS_GROUP_KEY,
    MT_GEOGRAPHIC_ANALYSIS_GROUP_NAME,
)

MT_GEOGRAPHIC_ANALYSIS_VIEW_KEY = "mat_ga_view"
MT_GEOGRAPHIC_ANALYSIS_EDIT_KEY = "mat_ga_edit"

permission_module_mt_config = {
    MT_OVERVIEW_GROUP_KEY: {
        "name": MT_OVERVIEW_GROUP_NAME,
        "module": MODULE_MT_KEY,
        "permissions": [
            {"key": MT_OVERVIEW_VIEW_KEY, "name": "View"},  # OVERVIEW
            {"key": MT_OVERVIEW_EDIT_KEY, "name": "Edit"},
        ],
    },
    # MT_OA_GROUP_KEY: {
    #     'name': MT_OA_GROUP_NAME,
    #     'module': MODULE_MT_KEY,
    #     'permissions': [
    #         {  # OPERATIONAL ANALYTICS
    #             'key': MT_OPERATIONAL_ANALYTICS_VIEW_KEY,
    #             'name': 'View'
    #         },
    #         {
    #             'key': MT_OPERATIONAL_ANALYTICS_EDIT_KEY,
    #             'name': 'Edit'
    #         },
    #     ]
    # },
    # MT_PL_GROUP_KEY: {
    #     'name': MT_PL_GROUP_NAME,
    #     'module': MODULE_MT_KEY,
    #     'permissions': [
    #         {  # PRODUCT LISTING
    #             'key': MT_PRODUCT_LISTING_VIEW_KEY,
    #             'name': 'View'
    #         },
    #         {
    #             'key': MT_PRODUCT_LISTING_EDIT_KEY,
    #             'name': 'Edit'
    #         },
    #     ]
    # },
    # MT_MP_GROUP_KEY: {
    #     'name': MT_MP_GROUP_NAME,
    #     'module': MODULE_MT_KEY,
    #     'permissions': [
    #         {  # MARKETING PERFORMANCE
    #             'key': MT_MARKETING_PERFORMANCE_VIEW_KEY,
    #             'name': 'View'
    #         },
    #         {
    #             'key': MT_MARKETING_PERFORMANCE_EDIT_KEY,
    #             'name': 'Edit'
    #         },
    #     ]
    # },
    # MT_CM_GROUP_KEY: {
    #     'name': MT_CM_GROUP_NAME,
    #     'module': MODULE_MT_KEY,
    #     'permissions': [
    #         {  # CATEGORY MARKET SHARE
    #             'key': MT_CATEGORY_MARKET_SHARE_VIEW_KEY,
    #             'name': 'View'
    #         },
    #         {
    #             'key': MT_CATEGORY_MARKET_SHARE_EDIT_KEY,
    #             'name': 'Edit'
    #         },
    #     ]
    # },
    MT_ADMIN_GROUP_KEY: {
        "name": MT_ADMIN_GROUP_NAME,
        "module": MODULE_MT_KEY,
        "permissions": [
            {"key": MT_ADMIN_SETTING_EDIT_KEY, "name": "Edit Settings"},
            {"key": MT_ADMIN_DS_GENERATE_KEY, "name": "Generate Default Data Source"},
            {
                "key": MT_ADMIN_DS_DASHBOARD_GENERATE_KEY,
                "name": "Generate Default Dashboard",
            },
        ],
    },
    MT_ADVERTISING_GROUP_KEY: {
        "name": MT_ADMIN_GROUP_NAME,
        "module": MODULE_MT_KEY,
        "permissions": [
            {"key": MT_ADVERTISING_VIEW_KEY, "name": "View"},
            {"key": MT_ADVERTISING_EDIT_KEY, "name": "Edit"},
        ],
    },
    MT_CD_GROUP_KEY: {
        "name": MT_CD_GROUP_NAME,
        "module": MODULE_MT_KEY,
        "permissions": [
            {"key": MT_CUSTOM_DASHBOARD_VIEW_KEY, "name": "View"},  # CUSTOM DASHBOARD
            {"key": MT_CUSTOM_DASHBOARD_MANAGEMENT_KEY, "name": "Management"},
        ],
    },
    MT_BRAND_INTEGRITY_GROUP_KEY: {
        "name": MT_BRAND_INTEGRITY_GROUP_NAME,
        "module": MODULE_MT_KEY,
        "permissions": [{"key": MT_BRAND_INTEGRITY_VIEW_KEY, "name": "View"}],
    },
    MT_GEOGRAPHIC_ANALYSIS_GROUP_KEY: {
        "name": MT_GEOGRAPHIC_ANALYSIS_GROUP_NAME,
        "module": MODULE_MT_KEY,
        "permissions": [
            {"key": MT_GEOGRAPHIC_ANALYSIS_VIEW_KEY, "name": "View"},
            {"key": MT_GEOGRAPHIC_ANALYSIS_EDIT_KEY, "name": "Edit"},
        ],
    },
}
