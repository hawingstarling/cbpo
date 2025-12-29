<template>
  <b-card v-if="isReady && isGetFullDsId" class="custom-dashboard card-custom">
    <div class="mb-2 d-flex justify-content-between align-items-center dashboard-header">
        <div>
          <h5 class="mb-0">
            Dashboard
          </h5>
        </div>
        <div class="d-flex align-items-center">
          <cbpo-multiple-export :widgets="multiExportWidgets">
            <template v-slot:button="{ openModal }">
              <div class="export-btn" @click="openModal"></div>
            </template>
          </cbpo-multiple-export>
          <cbpo-manage-widgets :widget-list="widgetsDashboard" @updated="saveDashBoard" :configObj="sdkConfig.widgetManager.config">
            <template v-slot:button="{ openModal }">
              <div @click="openModal" class="settings-btn"></div>
            </template>
          </cbpo-manage-widgets>
        </div>
    </div>
    <div class="row wrap-widget" id="wrapWidget">
      <template v-for="widget in widgetsDashboard">
        <div :key="widget.id" v-if="widget.enabled && getConfig(widget)" :class="[getConfig(widget).class, { 'widget-default-height': !getConfig(widget).hasConfigHeight }]" :style="getConfig(widget).style">
          <cbpo-lazy-load :default-height="getConfig(widget).defaultHeight">
            <component v-if="getConfig(widget).component" :is="getConfig(widget).component" v-bind="getConfig(widget).props" :settingGoal="getSettingGoal(widget)" />
            <widget-chart v-else v-bind="getConfig(widget).props" />
          </cbpo-lazy-load>
        </div>
      </template>
    </div>
  </b-card>
  <div v-else-if="!isGetFullDsId" class="alert alert-warning" role="alert">
    The data source is not ready.
  </div>
</template>

<script>
// import mockData from './WidgetConfig/DemoDataWidget'
// import INVCustomerReturns from './widgets/INVCustomerReturns'
// import Movement from './widgets/Movement'
// import AverageSalesPrice from './widgets/AverageSalesPrice'
// utils
import { convertedPermissions as permissions } from '@/shared/utils'
import { convertYToCurrentYear, compareTwoColInWidget, configMaxProgressBar } from './OverviewMethod.js'
// libs
import { mapActions, mapGetters } from 'vuex'

import cloneDeep from 'lodash/cloneDeep'
import isEmpty from 'lodash/isEmpty'
import get from 'lodash/get'
// widgets
import { multiExportWidgetsConfig } from './MultipleExportConfig.js'
import dashboardWidget from './WidgetConfig/DetailWidgetConfig'

import BigMovesDashboard from './widgets/BigMovesDashboard'
import AllSalesComparison from './widgets/AllSalesComparison'
import ViewComparison from './widgets/ViewComparison'
import AllSales from './widgets/AllSales'
import SalesAmount from './widgets/Salesby$Amount'
import YOYMonthlySales from '@/components/pages/sales/overview/widgets/YOYMonthlySales'
import OrderedProductSales from '@/components/pages/sales/overview/widgets/OrderedProductSales'
import TotalSalesTracker from '@/components/pages/sales/overview/widgets/TotalSalesTracker'
import PAndL from '@/components/pages/sales/overview/widgets/custom/p-and-l/PAndL'
import BrokenDownSales from '@/components/pages/sales/overview/widgets/custom/broken-down-sales/BrokenDownSales'
import TopProductPerformance from '@/components/pages/sales/overview/widgets/custom/top-product-performance/TopProductPerformance'
import ThirtyDaySalesBrand from '@/components/pages/sales/overview/widgets/ThirtyDaySalesBrand'
import WidgetChart from '@/components/pages/sales/overview/widgets/WidgetChart.vue'
import DashboardDate from '@/components/pages/sales/overview/widgets/DashboardDate.vue'
import SalesByASIN from '@/components/pages/sales/overview/widgets/SalesByASIN.vue'
import OverallSales from './widgets/custom/overall-sales/OverallSales.vue'
import SalesByDivision from '@/components/pages/sales/overview/widgets/custom/sale-by-divisions/SalesByDivision.vue'
import TopPerformingStylesBySegment from '@/components/pages/sales/overview/widgets/TopPerformingStylesBySegment.vue'
// mixins
import PermissionsMixin from '@/components/common/PermissionsMixin'
import toastMixin from '@/components/common/toastMixin'
import sdkMixins from '@/components/pages/sdkMixins'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'

export default {
  name: 'Overview',
  components: {
    ThirtyDaySalesBrand,
    WidgetChart,
    TopProductPerformance,
    BrokenDownSales,
    PAndL,
    TotalSalesTracker,
    OrderedProductSales,
    YOYMonthlySales,
    OverallSales,
    // INVCustomerReturns,
    BigMovesDashboard,
    AllSalesComparison,
    // Movement,
    // AverageSalesPrice,
    AllSales,
    SalesAmount,
    ViewComparison,
    DashboardDate,
    SalesByASIN,
    SalesByDivision,
    TopPerformingStylesBySegment
  },
  mixins: [
    toastMixin,
    PermissionsMixin,
    sdkMixins,
    spapiReconnectAlertMixin
  ],
  data() {
    return {
      configs: cloneDeep(dashboardWidget),
      isReady: false,
      isGetFullDsId: true,
      permissions,
      multiExportWidgetsConfig,
      searchInput: '',
      widgetsDashboard: []
    }
  },
  computed: {
    ...mapGetters({
      dsIdForMapping: `pf/overview/dsIdForMapping`
    }),
    multiExportWidgets() {
      return this.multiExportWidgetsConfig.filter(widget => {
        return !!this.widgetsDashboard.find(p => p.widget.key === widget.name && p.enabled)
      })
    },
    widgetListConfig() {
      return {
        dashboard_date: {
          component: DashboardDate,
          class: 'h-auto col-12',
          defaultHeight: 100 // default height for lazy load
        },
        overall_sales: {
          component: OverallSales,
          style: 'min-height: 175px; height: auto;',
          props: { config: this.configs.OverallSales.config, dashboard: 'overview' },
          class: 'col-12'
        },
        sales_by_division: {
          component: SalesByDivision,
          class: 'col-12',
          props: {
            dsId: this.dsIdForMapping ? this.dsIdForMapping.SALE_BY_DIVISIONS : {},
            config: this.configs.SalesByDivision.config,
            dashboard: 'overview'
          },
          defaultHeight: 600, // default height for lazy load
          hasConfigHeight: true
        },
        sales_by_asin: {
          component: SalesByASIN,
          class: 'col-12 h-100',
          props: { salesByAsin: this.configs.SalesByASIN }
        },
        big_moves: {
          component: BigMovesDashboard,
          class: 'col-12',
          style: 'min-height: 436px; height: auto',
          props: {
            bigMovesUp: this.configs.BigMovesUp,
            bigMovesDown: this.configs.BigMovesDown,
            dsId: this.dsIdForMapping ? this.dsIdForMapping.SALE_BIG_MOVES : {}
          }
        },
        all_sales_comparison: {
          component: AllSalesComparison,
          class: 'col-12 h-100',
          props: {
            sdkConfig: this.configs.AllSalesComparison,
            dsId: this.dsIdForMapping
          }
        },
        total_sales_tracker: {
          component: TotalSalesTracker,
          class: 'col-12',
          style: 'height: 220px',
          props: {
            dsId: this.dsIdForMapping ? this.dsIdForMapping.SALE_ITEMS : {},
            config: this.configs.TotalSalesTracker.config
          }
        },
        broken_down_sales: {
          component: BrokenDownSales,
          style: 'min-height: 436px; height: auto',
          class: 'col-12',
          props: {
            dsId: this.dsIdForMapping ? this.dsIdForMapping.BROKEN_DOWN_SALES : {},
            config: this.configs.BrokenDownSales.config
          },
          defaultHeight: 400 // default height for lazy load
        },
        'p_&_l': {
          component: PAndL,
          class: 'col-12',
          props: {
            dsId: this.dsIdForMapping ? this.dsIdForMapping.SALE_ITEMS : {},
            config: this.configs.PAndL.config,
            showTitle: true
          },
          hasConfigHeight: true
        },
        ordered_product_sales: {
          component: OrderedProductSales,
          class: 'col-6',
          props: {
            configThirtyDays: this.configs.OrderedProductSales30days.config,
            configToday: this.configs.OrderedProductSalesToday.config
          }
        },
        yoy_monthly_sales: {
          component: YOYMonthlySales,
          class: 'col-6',
          props: { config: this.configs.YOYMonthlySales.config }
        },
        view_comparison_tag: {
          component: ViewComparison,
          class: 'col-12 h-auto'
        },
        top_product_performance: {
          component: TopProductPerformance,
          class: 'col-12',
          style: 'min-height: 175px; height: auto;',
          props: {
            dsId: this.dsIdForMapping ? this.dsIdForMapping.SALE_ITEMS : {},
            config: this.configs.TopProductPerformance.config,
            showTitle: true
          }
        },
        sale_by_dollar: {
          component: SalesAmount,
          class: 'col-12',
          props: { sdkConfig: this.configs.Salesby$Amount }
        },
        all_sales: {
          component: AllSales,
          class: 'col-12',
          props: { sdkConfig: this.configs.AllSales },
          defaultHeight: 400 // default height for lazy load
        },
        '30_day_sales': {
          component: ThirtyDaySalesBrand,
          class: 'col-6',
          props: { config: this.configs.thirtyDaySales$.config }
        },
        '30_day_sales_brand': {
          class: 'col-6 widget-thirty-day-sales-brand',
          props: { configObj: this.configs.thirtyDaySales$Brand.config }
        },
        all_sales_last_30_days: {
          class: 'col-6',
          props: { configObj: this.configs.AllOrdersDay.config, class: 'custom-opacity-chart' }
        },
        all_sales_last_20_months: {
          class: 'col-6',
          props: { configObj: this.configs.AllOrdersMonth.config, class: 'custom-opacity-chart' }
        },
        top_performing_styles: {
          component: TopPerformingStylesBySegment,
          class: 'col-12 h-100',
          props: {
            topPerformingStylesBySegment: this.configs.TopPerformingStylesBySegment,
            dsId: this.dsIdForMapping
          }
        }
      }
    }
  },
  methods: {
    ...mapActions({
      fetchDSIdForMapping: `pf/overview/fetchDSIdForMapping`,
      fetchWidgetsDashboard: `pf/manageWidgetDashboard/fetchWidgetsDashboard`,
      saveWidgetsDashboard: `pf/manageWidgetDashboard/saveWidgetsDashboard`
    }),
    mapDSIdToWidgetConfig() {
      for (let config in this.configs) {
        let dsId = this.configs[config].config.elements[0].config.dataSource
        this.configs[config].config.elements[0].config.dataSource = this.dsIdForMapping[dsId]
          ? this.dsIdForMapping[dsId].data_source_id
          : dsId
        if (get(this.configs[config].config, 'filter.form.config.controls.length', 0) > 0) {
          this.configs[config].config.filter.form.config.controls.forEach(control => {
            let dsFilterId = control.config.dataSource
            control.config.dataSource = this.dsIdForMapping[dsFilterId]
              ? this.dsIdForMapping[dsFilterId].data_source_id
              : dsFilterId
          })
        }
      }
      if (isEmpty(this.dsIdForMapping)) {
        this.isGetFullDsId = false
      }
    },
    async handleGetSettingsWidgets() {
      try {
        this.widgetsDashboard = await this.fetchWidgetsDashboard({client_id: this.$route.params.client_id, dashboard: 'overview'})
      } catch (error) {
        this.vueToast('error', 'The settings widget has been gotten failed.')
      }
    },
    getConfig(widget) {
      return (widget && widget.widget && widget.widget.key)
        ? this.widgetListConfig[widget.widget.key] : null
    },
    async saveDashBoard(value) {
      try {
        const data = value.map((item, index) => {
          return {
            widget: item.widget.key,
            enabled: item.enabled,
            position: index + 1
          }
        })
        const params = {
          client_id: this.$route.params.client_id,
          dashboard: 'overview',
          payload: {
            data
          }
        }
        await this.saveWidgetsDashboard(params)
        this.vueToast('success', 'The widgets has been saved successfully.')
        await this.handleGetSettingsWidgets()
      } catch (error) {
        this.vueToast('error', error.response.data.message)
      }
    },
    getSettingGoal(widget) {
      return (widget && widget.settings && widget.settings.goal) ? widget.settings.goal : 0
    }
  },
  async created() {
    await this.fetchDSIdForMapping({client_id: this.$route.params.client_id})
    this.mapDSIdToWidgetConfig()
    convertYToCurrentYear(this.configs)
    compareTwoColInWidget(this.configs.AllSales)
    compareTwoColInWidget(this.configs.Salesby$Amount)
    configMaxProgressBar(['max_amount_30d', 'max_amount_30d_prior'], ['amount_30d', 'amount_30d_prior'], this.configs.thirtyDaySales$Brand)
    // window.repricingInstance = this.mockData.repricingInstance
    // window.allSales = this.mockData.allSales
    // window.orderProductSales = this.mockData.orderProductSales
    // window.saleOf30Day = this.mockData.saleOf30Day
    // window.allOrders = this.mockData.allOrders
    // window.daySales = this.mockData.daySales
    // window.daySalesNum = this.mockData.daySalesNum
    // window.salesComparison = this.mockData.salesComparison
    // window.movementUp = this.mockData.movementUp
    // window.movementDown = this.mockData.movementDown
    // window.totalInven = this.mockData.totalInven
    // window.invenMohValue = this.mockData.invenMohValue
    // window.earnTurnRatio = this.mockData.earnTurnRatio
    // window.etGraph = this.mockData.etGraph
    // window.MFNCategory = this.mockData.MFNCategory
    // window.MFNCategoryLine = this.mockData.MFNCategoryLine
    // window.totalRAOrder30Days = this.mockData.totalRAOrder30Days
    // window.averageSalesPrice = this.mockData.averageSalesPrice
    // window.handlingTime = this.mockData.handlingTime
    // window.storeOnlineSale = this.mockData.storeOnlineSale
    this.handleGetSettingsWidgets()
    this.isReady = true
  }
}
</script>

<style lang="scss" scoped>
  @import '@/components/pages/sales/overview/Overview.scss';
  @import '@/assets/scss/themes/precise-theme.scss';
</style>
