import DefaultContainer from '@/containers/DefaultContainer'
import { convertedPermissions as permissions } from '@/shared/utils'
const routes = {
  path: '/',
  name: 'DefaultContainer',
  meta: {
    label: 'Home'
  },
  component: DefaultContainer,
  // redirect: { name: 'Analysis' },
  children: [
    // Dashboard
    {
      path: 'pf/:client_id/overview',
      meta: {
        label: 'Overview',
        reloadPermissions: true,
        title: 'Overview',
        permissions: [permissions.overview.dashboardManagement]
      },
      name: 'PFOverview',
      component: { template: `<PFOverview></PFOverview>` }
    },
    // Analysis
    {
      path: 'pf/:client_id/analysis',
      meta: {
        label: 'Analysis',
        reloadPermissions: true,
        title: 'Analysis',
        permissions: [
          permissions.sale.viewAll,
          permissions.sale.view24h
        ]
      },
      name: 'PFAnalysis',
      component: { template: `<PFAnalysis></PFAnalysis>` }
    },
    // List Filters
    {
      path: 'pf/:client_id/filters',
      meta: {
        label: 'Filters',
        reloadPermissions: true,
        title: 'Filters',
        permissions: [permissions.filter.view]
      },
      name: 'PFFilterList',
      component: { template: `<PFFilterList></PFFilterList>` }
    },
    // List advertising
    {
      path: 'pf/:client_id/advertising',
      meta: {
        label: 'Advertising',
        reloadPermissions: true,
        title: 'Advertising',
        permissions: [permissions.advertising.dashboardManagement]
      },
      name: 'PFAdvertising',
      component: { template: `<PFAdvertising></PFAdvertising>` }
    },
    // List Columns
    {
      path: 'pf/:client_id/column-sets',
      meta: {
        label: 'Column Sets',
        reloadPermissions: true,
        title: 'Columns Sets',
        permissions: [permissions.columnSet.view]
      },
      name: 'PFColumnSetList',
      component: { template: `<PFColumnSetList></PFColumnSetList>` }
    },

    {
      path: 'pf/:client_id/:module/step2-validate/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2Validate',
      component: { template: `<PFStep2Validate></PFStep2Validate>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3Process',
      component: { template: `<PFStep3Process></PFStep3Process>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4Result',
      component: { template: `<PFStep4Result></PFStep4Result>` }
    },
    // Geographic Analysis
    {
      path: 'pf/:client_id/geographic-analysis',
      meta: {
        label: 'Geographic Analysis',
        reloadPermissions: true,
        title: 'Geographic Analysis'
        // permissions: [permissions.overview.dashboardManagement]
      },
      name: 'PFGeographicAnalysis',
      component: { template: `<PFGeographicAnalysis></PFGeographicAnalysis>` }
    },
    // Import Items
    {
      path: 'pf/:client_id/:module/step1-import-items',
      meta: {
        label: 'Import Items',
        reloadPermissions: true,
        title: 'Import Items',
        permissions: [permissions.sale.import]
      },
      name: 'PFStep1ImportItems',
      component: { template: `<PFStep1ImportItems></PFStep1ImportItems>` }
    },
    {
      path: 'pf/:client_id/:module/step2-validate-items/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2ValidateItems',
      component: { template: `<PFStep2ValidateItems></PFStep2ValidateItems>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process-items/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3ProcessItems',
      component: { template: `<PFStep3ProcessItems></PFStep3ProcessItems>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result-items/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4ResultItems',
      component: { template: `<PFStep4ResultItems></PFStep4ResultItems>` }
    },
    {
      path: 'pf/:client_id/:module/step1-import-brand-setting',
      meta: {
        label: 'Import Brand Setting',
        reloadPermissions: true,
        title: 'Import Brand Setting'
      },
      name: 'PFStep1ImportBrandSetting',
      component: { template: `<PFStep1ImportBrandSetting></PFStep1ImportBrandSetting>` }
    },
    {
      path: 'pf/:client_id/:module/step2-validate-brand-setting/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2ValidateBrandSetting',
      component: { template: `<PFStep2ValidateBrandSetting></PFStep2ValidateBrandSetting>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process-brand-setting/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3ProcessBrandSetting',
      component: { template: `<PFStep3ProcessBrandSetting></PFStep3ProcessBrandSetting>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result-brand-setting/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4ResultBrandSetting',
      component: { template: `<PFStep4ResultBrandSetting></PFStep4ResultBrandSetting>` }
    },
    {
      path: 'pf/:client_id/:module/step1-import-brand',
      meta: {
        label: 'Import Brand',
        reloadPermissions: true,
        title: 'Import Brand'
      },
      name: 'PFStep1ImportBrand',
      component: { template: `<PFStep1ImportBrand></PFStep1ImportBrand>` }
    },
    {
      path: 'pf/:client_id/:module/step2-validate-brand/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2ValidateBrand',
      component: { template: `<PFStep2ValidateBrand></PFStep2ValidateBrand>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process-brand/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3ProcessBrand',
      component: { template: `<PFStep3ProcessBrand></PFStep3ProcessBrand>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result-brand/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4ResultBrand',
      component: { template: `<PFStep4ResultBrand></PFStep4ResultBrand>` }
    },
    {
      path: 'pf/:client_id/:module/step1-import-fedex-shipments',
      meta: {
        label: 'Import Shipping Invoices',
        reloadPermissions: true,
        title: 'Import Shipping Invoices'
      },
      name: 'PFStep1ImportFedex',
      component: { template: `<PFStep1ImportFedex></PFStep1ImportFedex>` }
    },
    {
      path: 'pf/:client_id/:module/step2-validate-fedex-shipments/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2ValidateFedex',
      component: { template: `<PFStep2ValidateFedex></PFStep2ValidateFedex>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process-fedex-shipments/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3ProcessFedex',
      component: { template: `<PFStep3ProcessFedex></PFStep3ProcessFedex>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result-fedex-shipments/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4ResultFedex',
      component: { template: `<PFStep4ResultFedex></PFStep4ResultFedex>` }
    },
    {
      path: 'pf/:client_id/:module/step1-import-top-asins',
      meta: {
        label: 'Import Top ASINs',
        reloadPermissions: true,
        title: 'Import Top ASINs',
        permissions: [permissions.sale.import]
      },
      name: 'PFStep1ImportTopASIN',
      component: { template: `<PFStep1ImportTopASIN></PFStep1ImportTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/step2-validate-top-asins/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2ValidateTopASIN',
      component: { template: `<PFStep2ValidateTopASIN></PFStep2ValidateTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process-top-asins/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3ProcessTopASIN',
      component: { template: `<PFStep3ProcessTopASIN></PFStep3ProcessTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result-top-asins/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4ResultTopASIN',
      component: { template: `<PFStep4ResultTopASIN></PFStep4ResultTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/step1-import-delete-top-asins',
      meta: {
        label: 'Import To Delete Top ASINs',
        reloadPermissions: true,
        title: 'Import To Delete Top ASINs',
        permissions: [permissions.sale.import]
      },
      name: 'PFStep1ImportToDeleteTopASIN',
      component: { template: `<PFStep1ImportToDeleteTopASIN></PFStep1ImportToDeleteTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/step2-validate-delete-top-asins/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2ValidateDeleteTopASIN',
      component: { template: `<PFStep2ValidateDeleteTopASIN></PFStep2ValidateDeleteTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process-delete-top-asins/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3ProcessDeleteTopASIN',
      component: { template: `<PFStep3ProcessDeleteTopASIN></PFStep3ProcessDeleteTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result-delete-top-asins/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4ResultDeleteTopASIN',
      component: { template: `<PFStep4ResultDeleteTopASIN></PFStep4ResultDeleteTopASIN>` }
    },
    {
      path: 'pf/:client_id/:module/bulk-progress/:bulk_id',
      meta: {
        label: 'Bulk Progress',
        reloadPermissions: true,
        title: 'Bulk Progress',
        permissions: [
          permissions.sale.viewAll,
          permissions.sale.view24h
        ]
      },
      name: 'PFBulkProgressDetail',
      component: { template: `<PFBulkProgressDetail></PFBulkProgressDetail>` }
    },
    {
      path: 'pf/:client_id/brand-list',
      meta: {
        label: 'Brands',
        reloadPermissions: true,
        title: 'Brands'
        // permissions: [permissions.brand.view]
      },
      name: 'PFBrandList',
      component: { template: `<PFBrandList></PFBrandList>` }
    },
    {
      path: 'pf/:client_id/:module/step1-import-repricing',
      meta: {
        label: 'Import Repricing',
        reloadPermissions: true,
        title: 'Import Repricing'
      },
      name: 'PFStep1ImportRepricing',
      component: { template: `<PFStep1ImportRepricing></PFStep1ImportRepricing>` }
    },
    {
      path: 'pf/:client_id/:module/step2-validate-repricing/:import_id',
      meta: {
        label: 'Data Preview',
        reloadPermissions: true,
        title: 'Data Preview'
      },
      name: 'PFStep2ValidateRepricing',
      component: { template: `<PFStep2ValidateRepricing></PFStep2ValidateRepricing>` }
    },
    {
      path: 'pf/:client_id/:module/step3-process-repricing/:import_id',
      meta: {
        label: 'Validation Results',
        reloadPermissions: true,
        title: 'Validation Results'
      },
      name: 'PFStep3ProcessRepricing',
      component: { template: `<PFStep3ProcessRepricing></PFStep3ProcessRepricing>` }
    },
    {
      path: 'pf/:client_id/:module/step4-result-repricing/:import_id',
      meta: {
        label: 'Processing Results',
        reloadPermissions: true,
        title: 'Processing Results'
      },
      name: 'PFStep4ResultRepricing',
      component: { template: `<PFStep4ResultRepricing></PFStep4ResultRepricing>` }
    },
    {
      path: 'pf/:client_id/settings',
      meta: {
        label: 'Settings',
        reloadPermissions: true,
        title: 'Settings',
        permissions: [permissions.admin.settingsView]
      },
      name: 'PFSettings',
      component: { template: `<PFSettings></PFSettings>` }
    },
    {
      path: 'pf/sc-oauth-redirect',
      meta: {
        label: 'SC OAuth Redirect',
        reloadPermissions: true,
        title: 'SC OAuth Redirect'
      },
      name: 'PFSCOAuthRedirect',
      component: { template: `<PFSCOAuthRedirect></PFSCOAuthRedirect>` }
    },
    {
      path: 'pf/:client_id/user-administration',
      meta: {
        label: 'User Administration',
        reloadPermissions: true,
        title: 'User Administration',
        permissions: [permissions.admin.itemView]
      },
      name: 'PFUserAdministration',
      component: { template: `<PFUserAdministration></PFUserAdministration>` },
      redirect: 'pf/:client_id/user-administration/:module/step1-import/',
      children: [
        {
          path: ':module/step1-import/',
          meta: {
            label: 'Import Sale Items',
            reloadPermissions: true,
            title: 'Import Sale Items',
            permissions: [permissions.sale.import]
          },
          name: 'PFStep1Import',
          component: { template: `<PFStep1Import></PFStep1Import>` }
        },
        {
          path: 'import-history/',
          meta: {
            label: 'Import History',
            reloadPermissions: true,
            title: 'Import History',
            permissions: [permissions.fedEx.view]
          },
          name: 'PFImportHistory',
          component: { template: `<PFImportHistory></PFImportHistory>` }
        },
        {
          path: 'activities/',
          meta: {
            label: 'Activities',
            reloadPermissions: true,
            title: 'Activities',
            permissions: [permissions.admin.activity]
          },
          name: 'PFActivities',
          component: { template: `<PFActivities></PFActivities>` }
        },
        {
          path: 'bulk-progress/',
          meta: {
            label: 'Bulk Progress',
            reloadPermissions: true,
            title: 'Bulk Progress',
            permissions: [
              permissions.sale.viewAll,
              permissions.sale.view24h
            ]
          },
          name: 'PFBulkProgress',
          component: { template: `<PFBulkProgress></PFBulkProgress>` }
        },
        {
          path: 'repricing/',
          meta: {
            label: 'Repricing',
            reloadPermissions: true,
            title: 'Repricing',
            permissions: [permissions.repricing.view]
          },
          name: 'PFRepricing',
          component: { template: `<PFRepricing></PFRepricing>` }
        },
        {
          path: 'tools/',
          meta: {
            label: 'Tools',
            reloadPermissions: true,
            title: 'Tools',
            permissions: [permissions.admin.tool]
          },
          name: 'PFTools',
          component: { template: `<PFTools></PFTools>` }
        }
      ]
    },
    {
      path: 'pf/:client_id/brand-management',
      meta: {
        label: 'Brand Management',
        reloadPermissions: true,
        title: 'Brand Management',
        permissions: [permissions.admin.itemView]
      },
      name: 'PFBrandManagement',
      component: { template: `<PFBrandManagement></PFBrandManagement>` },
      redirect: 'pf/:client_id/brand-management/brands/',
      children: [
        {
          path: 'brands/',
          meta: {
            label: 'Brand Settings',
            reloadPermissions: true,
            title: 'Brands Settings',
            permissions: [permissions.brand.view]
          },
          name: 'PFBrands',
          component: { template: `<PFBrands></PFBrands>` }
        },
        {
          path: 'items/',
          meta: {
            label: 'Items',
            reloadPermissions: true,
            title: 'Items',
            permissions: [permissions.brand.view]
          },
          name: 'PFItems',
          component: { template: `<PFItems></PFItems>` }
        },
        {
          path: 'top-asins/',
          meta: {
            label: 'Top ASINs',
            reloadPermissions: true,
            title: 'Top ASINs',
            permissions: [permissions.topASINs.view]
          },
          name: 'PFTopASINs',
          component: { template: `<PFTopASINs></PFTopASINs>` }
        }
      ]
    },
    {
      path: 'pf/:client_id/view-management',
      meta: {
        label: 'View Management',
        reloadPermissions: true,
        title: 'View Management',
        permissions: [permissions.admin.itemView]
      },
      name: 'PFViewManagement',
      component: { template: `<PFViewManagement></PFViewManagement>` },
      redirect: 'pf/:client_id/view-management/views/',
      children: [
        // List Reports
        {
          path: 'views/',
          meta: {
            label: 'Views',
            reloadPermissions: true,
            title: 'Views',
            permissions: [permissions.view.viewAll, permissions.view.view24h]
          },
          name: 'PFViewList',
          component: { template: `<PFViewList></PFViewList>` }
        },
        {
          path: 'custom-reports/',
          meta: {
            label: 'Custom Reports',
            reloadPermissions: true,
            title: 'Custom Reports',
            permissions: [permissions.customReport.view]
          },
          name: 'PFCustomReports',
          component: { template: `<PFCustomReports></PFCustomReports>` }
        }
      ]
    },
    {
      path: 'pf/:client_id/shipping-management/',
      meta: {
        label: 'Shipping Management',
        reloadPermissions: true,
        title: 'Shipping Management',
        permissions: [permissions.fedEx.view]
      },
      name: 'PFShippingManagement',
      component: { template: `<PFShippingManagement></PFShippingManagement>` },
      redirect: 'pf/:client_id/shipping-management/shipping-invoices/',
      children: [
        {
          path: 'shipping-invoices',
          meta: {
            label: 'Shipping Invoices',
            reloadPermissions: true,
            title: 'Shipping Invoices',
            permissions: [permissions.fedEx.view]
          },
          name: 'PFShippingInvoices',
          component: { template: `<PFShippingInvoices></PFShippingInvoices>` }
        },
        {
          path: 'history',
          meta: {
            label: 'Shipping Invoice History',
            reloadPermissions: true,
            title: 'Shipping Invoice History',
            permissions: [permissions.fedEx.view]
          },
          name: 'PFShippingInvoiceHistory',
          component: {template: `<PFShippingInvoiceHistory></PFShippingInvoiceHistory>`}
        },
        {
          path: ':shipping_invoice_id/transactions',
          meta: {
            breadcrumbs: [
              {text: 'Shipping Invoices', to: {name: 'PFShippingInvoices'}}
            ],
            label: 'Shipping Invoice Transactions',
            reloadPermissions: true,
            title: 'Shipping Invoice Transactions',
            permissions: [permissions.fedEx.view]
          },
          name: 'PFShippingInvoiceTransactions',
          component: { template: `<PFShippingInvoiceTransactions></PFShippingInvoiceTransactions>` }
        }
      ]
    },
    {
      path: 'pf/:client_id/reports',
      meta: {
        label: 'Reports',
        reloadPermissions: true,
        title: 'Reports',
        permissions: [ permissions.customReport.view ]
      },
      name: 'PFReports',
      component: { template: `<PFReports></PFReports>` }
    },
    {
      path: 'pf/:client_id/cogs-conflicts-report',
      meta: {
        label: 'COGS Conflicts Report',
        reloadPermissions: true,
        title: 'COGS Conflicts Report',
        permissions: [permissions.cogsConflictsReport.view]
      },
      name: 'PFCOGSConflictsReport',
      component: { template: `<PFCOGSConflictsReport></PFCOGSConflictsReport>` }
    }
  ]
}

export default routes
