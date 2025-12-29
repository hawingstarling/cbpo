import defaultRoutes from './_routerConfig'
import _ from 'lodash'

/* eslint-disable */
import PFAnalysis from '@/components/pages/sales/analysis/Analysis'
import PFReports from '@/components/pages/sales/report/Reports'
import PFAdvertising from '@/components/pages/sales/advertising/Advertising'
import PFFilterList from '@/components/pages/sales/filters/FilterList'
import PFColumnSetList from '@/components/pages/sales/column-sets/ColumnSetList'
import PFViewList from '@/components/pages/sales/views/ViewList'
import PFStep1Import from '@/components/pages/sales/import/Step1Import'
import PFStep2Validate from '@/components/pages/sales/import/Step2Validate'
import PFStep3Process from '@/components/pages/sales/import/Step3Process'
import PFStep4Result from '@/components/pages/sales/import/Step4Result'
import PFStep1ImportItems from '@/components/pages/sales/import/Step1Import'
import PFStep2ValidateItems from '@/components/pages/sales/import/Step2Validate'
import PFStep3ProcessItems from '@/components/pages/sales/import/Step3Process'
import PFStep4ResultItems from '@/components/pages/sales/import/Step4Result'
import PFStep1ImportBrandSetting from '@/components/pages/sales/import/Step1Import'
import PFStep2ValidateBrandSetting from '@/components/pages/sales/import/Step2Validate'
import PFStep3ProcessBrandSetting from '@/components/pages/sales/import/Step3Process'
import PFStep4ResultBrandSetting from '@/components/pages/sales/import/Step4Result'
import PFStep1ImportBrand from '@/components/pages/sales/import/Step1Import'
import PFStep2ValidateBrand from '@/components/pages/sales/import/Step2Validate'
import PFStep3ProcessBrand from '@/components/pages/sales/import/Step3Process'
import PFStep4ResultBrand from '@/components/pages/sales/import/Step4Result'
import PFStep1ImportTopASIN from '@/components/pages/sales/import/Step1Import'
import PFStep2ValidateTopASIN from '@/components/pages/sales/import/Step2Validate'
import PFStep3ProcessTopASIN from '@/components/pages/sales/import/Step3Process'
import PFStep4ResultTopASIN from '@/components/pages/sales/import/Step4Result'
import PFStep1ImportToDeleteTopASIN from '@/components/pages/sales/import/Step1Import'
import PFStep2ValidateDeleteTopASIN from '@/components/pages/sales/import/Step2Validate'
import PFStep3ProcessDeleteTopASIN from '@/components/pages/sales/import/Step3Process'
import PFStep4ResultDeleteTopASIN from '@/components/pages/sales/import/Step4Result'
import PFActivities from '@/components/pages/administration/activities/Activities'
import PFTools from '@/components/pages/tools/settings/Tools'
import PFItems from '@/components/pages/administration/items/Items'
import PFBulkProgress from '@/components/pages/sales/bulk-progress/BulkProgress'
import PFBulkProgressDetail from '@/components/pages/sales/bulk-progress/BulkProgressDetail'
import PFBrands from '@/components/pages/administration/brands/BrandSettings'
import PFBrandList from '@/components/pages/administration/brands/BrandList'
import PFSettings from '@/components/pages/administration/settings/Settings'
import PFShippingInvoices from '@/components/pages/administration/shippingInvoice/PFShippingInvoices'
import PFShippingInvoiceHistory from "@/components/pages/administration/shippingInvoice/PFShippingInvoiceHistory";
import PFShippingInvoiceTransactions from '@/components/pages/administration/shippingInvoice/PFTransactions'
import PFImportHistory from '@/components/pages/administration/importHistory/PFImportHistory'
import PFCustomReports from '@/components/pages/administration/reports/CustomReports'
import PFStep1ImportFedex from '@/components/pages/sales/import/Step1Import'
import PFStep2ValidateFedex from '@/components/pages/sales/import/Step2Validate'
import PFStep3ProcessFedex from '@/components/pages/sales/import/Step3Process'
import PFStep4ResultFedex from '@/components/pages/sales/import/Step4Result'
import PFOverview from '@/components/pages/sales/overview/Overview'
import PFGeographicAnalysis from '@/components/pages/sales/geographic-analysis/GeographicAnalysis'
import PFRepricing from '@/components/pages/administration/repricing/Repricing'
import PFStep1ImportRepricing from '@/components/pages/sales/import/Step1Import'
import PFStep2ValidateRepricing from '@/components/pages/sales/import/Step2Validate'
import PFStep3ProcessRepricing from '@/components/pages/sales/import/Step3Process'
import PFStep4ResultRepricing from '@/components/pages/sales/import/Step4Result'
import PFSCOAuthRedirect from '@/components/pages/administration/settings/SCOAuthRedirect'
import PFBrandManagement from '@/components/pages/administration/brandManagement'
import PFViewManagement from '@/components/pages/administration/viewManagement'
import PFUserAdministration from '@/components/pages/administration/userAdministration'
import PFShippingManagement from '@/components/pages/administration/shippingManagement'
import PFTopASINs from '@/components/pages/administration/topASINs/ListTopASINs'
import PFCOGSConflictsReport from '@/components/pages/administration/cogs/COGSConflictsReport'

const routes = {
  PFAnalysis,
  PFReports,
  PFAdvertising,
  PFFilterList,
  PFColumnSetList,
  PFViewList,
  PFStep1Import,
  PFStep2Validate,
  PFStep3Process,
  PFStep4Result,
  PFStep1ImportItems,
  PFStep2ValidateItems,
  PFStep3ProcessItems,
  PFStep4ResultItems,
  PFActivities,
  PFTools,
  PFItems,
  PFBulkProgress,
  PFBulkProgressDetail,
  PFBrands,
  PFBrandList,
  PFStep1ImportBrandSetting,
  PFStep2ValidateBrandSetting,
  PFStep3ProcessBrandSetting,
  PFStep4ResultBrandSetting,
  PFStep1ImportBrand,
  PFStep2ValidateBrand,
  PFStep3ProcessBrand,
  PFStep4ResultBrand,
  PFSettings,
  PFShippingInvoices,
  PFShippingInvoiceHistory,
  PFShippingInvoiceTransactions,
  PFImportHistory,
  PFCustomReports,
  PFStep1ImportFedex,
  PFStep2ValidateFedex,
  PFStep3ProcessFedex,
  PFStep4ResultFedex,
  PFOverview,
  PFGeographicAnalysis,
  PFRepricing,
  PFStep1ImportRepricing,
  PFStep2ValidateRepricing,
  PFStep3ProcessRepricing,
  PFStep4ResultRepricing,
  PFSCOAuthRedirect,
  PFViewManagement,
  PFBrandManagement,
  PFUserAdministration,
  PFShippingManagement,
  PFTopASINs,
  PFStep1ImportTopASIN,
  PFStep2ValidateTopASIN,
  PFStep3ProcessTopASIN,
  PFStep4ResultTopASIN,
  PFStep1ImportToDeleteTopASIN,
  PFStep2ValidateDeleteTopASIN,
  PFStep3ProcessDeleteTopASIN,
  PFStep4ResultDeleteTopASIN,
  PFCOGSConflictsReport
}
_.forEach(defaultRoutes.children, (brand, key) => {
  brand.component = routes[brand.name]
  if (brand.children) {
    _.forEach(brand.children, (brand2, key2) => {
      brand2.component = routes[brand2.name]
    })
  }
})

export default [defaultRoutes]
export const routerRender = defaultRoutes.children
