class SortingApplication:
    @staticmethod
    def handler_sort_permission_app(app_name: str = None):
        args = {
            'mwrw': {},
            'matrix': {
                'mat_ov_view': 'Brand Overview - View',
                'mat_ov_edit': 'Brand Overview - Edit',
                'mat_oa_view': 'Operational Analytics - View',
                'mat_oa_edit': 'Operational Analytics - Edit',
                'mat_pl_view': 'Product Listing - View',
                'mat_pl_edit': 'Product Listing - Edit',
                'mat_mp_view': 'Marketing Performance - View',
                'mat_mp_edit': 'Marketing Performance - Edit',
                'mat_cm_view': 'Category Market Share - View',
                'mat_cm_edit': 'Category Market Share - Edit',
                'mat_si_view': 'Sellers & Investigations - View',
                'mat_si_edit': 'Sellers & Investigations - Edit',
                'mat_cd_view': 'Custom Dashboard View',
                'mat_cd_edit': 'Custom Dashboard Management',
                'mat_admin_si_sellers_view': 'View Sellers (Admin)',
                'mat_admin_si_sellers_man': 'Manage Sellers (Admin)',
                'mat_admin_si_listings_view': 'View Listings (Admin)',
                'mat_admin_si_listings_man': 'Manage Listings (Admin)',
                'mat_admin_generate_ds_edit': 'Generate Default DataSource (Admin)',
                'mat_admin_generate_dashboard_edit': 'Generate Default Dashboard (Admin)',
                'mat_setting_edit': 'Edit Settings (Admin)'
            },
            'data_central': {
                'dc_asin_view': 'ASIN - View',
                'dc_asin_edit': 'ASIN - Edit',
                'dc_asin_import': 'ASIN - Import',
                'dc_asin_edit_bulk': 'ASIN - Bulk Edit',
                'dc_upc_ean_view': 'UPC/EAN - View',
                'dc_po_view': 'PURCHASE ORDER - View',
                'dc_po_man': 'PURCHASE ORDER - Manage',
                'dc_pr_view': 'PRODUCT REVIEWS - View',
                'dc_profile_view': 'PROFILE - View',
                'dc_profile_man': 'PROFILE - Manage',
                'dc_inv_summary_view': 'INVENTORY SUMMARY - View',
                'dc_inv_sellers_view': 'INVENTORY SELLERS - View',
                'dc_inv_sellers_man': 'INVENTORY SELLERS - Manage',
                'dc_brand_view': 'BRAND - View',
                'dc_brand_export': 'BRAND - Export',
                'dc_brand_edit': 'BRAND - Edit',
                'dc_dd_report_man': 'DD REPORT - Manage',
                'dc_dd_report_view': 'DD REPORT - View',
                'dc_sys_monitor': 'SYSTEM STATUS - View',
                'dc_tool_index_man': 'TOOL INDEX - Manage',
                'dc_client_man': 'CLIENTS - Manage',
                'dc_settings_man': 'SETTINGS - Manage',
            }
        }
        return args.get(app_name, {})
