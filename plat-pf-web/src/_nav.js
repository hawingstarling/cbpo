import concat from 'lodash/concat'
import get from 'lodash/get'
import { convertedPermissions as permissions } from '@/shared/utils'
const DUMMY_CLIENT_ID = process.env.VUE_APP_PF_CLIENT_ID || ''

export default {
  name: 'pf',
  clientId: DUMMY_CLIENT_ID,
  // *******************************
  // ================================
  // this section is for build lib, can comment when developing
  // ================================
  _items: [
    // {
    //   title: true,
    //   name: 'Sale Items',
    //   class: '',
    //   wrapper: {
    //     element: '',
    //     attributes: {}
    //   },
    //   permissions: [
    //     permissions.filter.view,
    //     permissions.columnSet.view,
    //     permissions.view.viewAll,
    //     permissions.view.view24h,
    //     permissions.sale.import,
    //     permissions.sale.viewAll,
    //     permissions.sale.view24h
    //   ]
    // },
    {
      name: 'Dashboard',
      icon: 'fa fa-tachometer',
      image: 'nav/dashboard.svg',
      to: { name: 'PFOverview', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.overview.dashboardManagement]
    },
    {
      name: 'Analysis',
      icon: 'fa fa-dollar',
      image: 'nav/analysis.svg',
      to: { name: 'PFAnalysis', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [
        permissions.sale.viewAll,
        permissions.sale.view24h
      ]
    },
    {
      name: 'Views',
      icon: 'icon-screen-desktop',
      image: 'nav/view.svg',
      to: { name: 'PFViewManagement', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.view.viewAll, permissions.view.view24h]
    },
    {
      name: 'Geographic Analysis',
      icon: 'fa fa-area-chart',
      image: 'nav/geo.svg',
      to: { name: 'PFGeographicAnalysis', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      }
      // permissions: [permissions.overview.dashboardManagement]
    },
    // {
    //   title: true,
    //   name: 'Administration',
    //   class: '',
    //   wrapper: {
    //     element: '',
    //     attributes: {}
    //   },
    //   permissions: [permissions.admin.tool, permissions.admin.activity]
    // },
    {
      name: 'Brand Management',
      icon: 'icon-flag',
      image: 'nav/brand-management.svg',
      to: { name: 'PFBrandManagement', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.brand.view]
    },
    {
      name: 'Shipping Invoices',
      icon: 'fa fa-ship',
      image: 'nav/shipping-invoices.svg',
      to: { name: 'PFShippingManagement', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.fedEx.view]
    },
    {
      name: 'User Administration',
      icon: 'fa fa-users',
      image: 'nav/user-administration.svg',
      to: { name: 'PFUserAdministration', params: { client_id: DUMMY_CLIENT_ID, module: 'SaleItem' } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.admin.itemView]
    },
    {
      name: 'Reports',
      icon: '',
      image: 'nav/report.svg',
      to: { name: 'PFReports', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.customReport.view]
    },
    {
      name: 'COGS Conflicts Report',
      icon: '',
      image: 'nav/cogs-report.svg',
      imageStyle: { filter: 'brightness(0.7)' },
      to: { name: 'PFCOGSConflictsReport', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.cogsConflictsReport.view]
    },
    {
      name: '',
      icon: 'fa fa-cog',
      image: 'nav/settings.svg',
      to: { name: 'PFSettings', params: { client_id: DUMMY_CLIENT_ID } },
      badge: {
        variant: 'primary'
      },
      permissions: [permissions.admin.settingsView]
    }
  ],
  set setItem(clientID) {
    let self = this
    self._items = self._items.map(item => {
      if (get(item, 'to.params')) {
        item.to.params.client_id = clientID
      }
      return item
    })
    self.clientId = clientID
  },
  get items() {
    return this._items
  },
  set addItems(arr) {
    if (arr && arr.length) {
      this._items = concat(arr, this._items)
    }
  }
  // ================================
}
