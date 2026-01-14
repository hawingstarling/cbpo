<template>
  <div
    v-if="configReady"
    :id="getId"
    ref="chartWidget"
    class="cbpo-s cbpo-widget cbpo-chart-widget"
    :class="config.css"
    :style="config.style"
    v-cbpo-loading="{ loading: loading }"
  >
    <div
      v-show="!isElementHidden"
      class="cbpo-chart-title"
      v-if="config.widget.title.enabled"
    >
      {{ config.widget.title.text }}
    </div>
    <cbpo-drill-down-chart
      ref="drillDown"
      v-if="config.drillDown.enabled"
      :channelId="config.dataSource"
      :is-chart="true"
      :configObj="config.drillDown.config"
      @input="drillDownChange"
    ></cbpo-drill-down-chart>
    <div
      v-show="!isElementHidden"
      v-if="config.charts && config.charts.length > 0"
      class="chart-container"
    >
      <div
        v-for="(chart, indexChart) in config.charts"
        :key="indexChart"
        class="chartSets"
      ></div>
    </div>
    <div class="warning-size-content" v-show="isElementHidden">
      <span>{{ warningText }}</span>
    </div>
  </div>
</template>

<script>
import WidgetBase from '@/components/WidgetBase'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import CBPO from '@/services/CBPO'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import DataManager from '@/services/ds/data/DataManager'
import ChartLib from '@/components/widgets/elements/chart/ChartLib'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import _ from 'lodash'
import loadingDirective from '@/directives/loadingDirective'
import $ from 'jquery'
import isEmpty from 'lodash/isEmpty'
import DrillDownChart from '@/components/widgets/drillDown/DrillDownChart'
import { makeDefaultChartConfig } from '@/components/widgets/elements/chart/ChartConfig'
import { BUS_EVENT } from '@/services/eventBusType'
import * as util from '@/utils/chartUtil'
import { getAggregationObjFromAggregationName } from '@/services/ds/data/DataTypes'
import { createBinType } from '@/utils/binUtils'
import { makeDOMId } from '@/components/widgets/elements/chart/types/ChartTypes'
import { getFileName, getPollingSetting, getPollingIntervalSetting } from '@/utils/multiExportUtil'
import uuidv4 from 'uuid'
import cloneDeep from 'lodash/cloneDeep'
import get from 'lodash/get'

export default {
  name: 'Chart',
  extends: WidgetBase,
  mixins: [WidgetBaseMixins, WidgetLoaderMixins],
  props: {
    filterObj: {
      type: Object,
      default() {
        return {}
      }
    },
    colorStyle: {
      type: Object,
      default() {
        return {}
      }
    }
  },
  components: {
    'cbpo-drill-down-chart': DrillDownChart
  },
  data() {
    return {
      id: null,
      currentTimezone: null,
      drillDownManager: null, // will be init after widget config
      isElementHidden: false,
      warningText: '',
      cacheConfig: null
    }
  },
  directives: {
    'cbpo-loading': loadingDirective
  },
  watch: {
    filterObj: {
      deep: true,
      handler(val) {
        if (this.cancelToken) this.cancelToken.cancel('Cancel token is applied')
        this.createCancelToken()
        this.config.filter = val
        this.saveRootConfig()
        this.widgetResetCurrentPage()
        this.fetchAndRender()
        this.calcTotalPage()
      }
    },
    colorStyle: {
      deep: true,
      handler(val) {
        this.changeColor()
      }
    },
    configReady(val) {
      if (val) {
        this.$nextTick(() => this.saveRootConfig())
      }
    }
  },
  computed: {
    getId() {
      return makeDOMId(_.get(this.config, 'library'), this.id)
    }
  },
  methods: {
    saveRootConfig() {
      let drillDown = this.$refs.drillDown
      if (!drillDown) return false
      if (drillDown.breadcrumbs.length === 0) {
        this.cacheConfig = _.cloneDeep(this.config)
      }
    },
    getRootConfig() {
      return _.cloneDeep(this.cacheConfig)
    },
    openDrillDown({ value, column }) {
      let {bins, grouping, sorting, filter} = this.getRootConfig()
      let drillDownData = {
        value,
        column,
        query: {
          bins,
          grouping,
          filter,
          orders: sorting
        }
      }
      _.get(this.config, 'drillDown.config.path.enabled', false)
        ? (this.config.drillDown.config.path.settings.length ? this.$refs.drillDown.applyPath(drillDownData) : void (0))
        : this.$refs.drillDown.openModal(drillDownData)
    },
    async drillDownChange({ query, columns }) {
      // empty chart
      $(this.$el).find('.chartSets').html('')
      let {bins, filter, grouping, orders} = query
      this.config.bins = bins
      this.config.filter = filter
      this.config.grouping = grouping
      this.config.sorting = orders

      // mapping new data into config sdk
      let xColumn = columns.find(column => column.name === grouping.columns[0].name || createBinType(column.name) === grouping.columns[0].name)
      this.config.columns = this.config.columns.filter(column => column.name !== this.config.charts[0].series[0].data.x)

      this.config.charts[0].series.forEach(item => {
        let yColumn = columns.find(column => column.name === item.data.y)
        let aggregation = grouping.aggregations.find(aggr => aggr.column === item.data.y)
        let aggregationObj = getAggregationObjFromAggregationName(aggregation.aggregation)
        item.data.x = xColumn.name
        item.name = `${yColumn.displayName || yColumn.name} (${aggregationObj.label})`
      })

      this.config.columns = [...this.config.columns, xColumn]

      // fetch API
      return this.fetchAndRender()
    },
    async calcTotalPage() {
      // Do nothing right now
    },
    changeIndexColumn(columns) {
      this.config.columns = columns
      this._buildTableParams()
    },
    _buildMainQuery() {
      let q = new QueryBuilder()
      if (!_.isEmpty(this.config.sorting)) {
        let { column, direction } = this.config.sorting[0]
        let binColumn = this.config.bins.find(
          (bin) => bin.column.name === column
        )
        q.addOrder(binColumn ? binColumn.alias : column, direction)
      } else {
        const xCol = _.get(this.config.charts[0], 'series[0].data.x', '')
        if (xCol) {
          this.config.sorting[0] = { column: xCol, direction: 'asc' }
          let { column, direction } = this.config.sorting[0]
          let binColumn = this.config.bins.find(
            (bin) => bin.column.name === column
          )
          q.addOrder(binColumn ? binColumn.alias : column, direction)
        }
      }
      let { current, limit } = this.config.pagination
      q.setPaging({ current, limit })
      let { columns, aggregations } = this.config.grouping
      if (!_.isEmpty(this.config.grouping.aggregations)) {
        q.setGroup(columns, aggregations)
      }
      if (!_.isEmpty(this.config.filter)) {
        q.setFilter(this.config.filter)
      }
      if (!_.isEmpty(this.config.bins)) {
        q.setBins(this.config.bins)
      }
      // add timezone
      if (this.config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }
      return q
    },
    /**
     * * Call to build data source query params
     * - Input: this.config data.
     * @return Query Params
     */
    _buildMainQueryParams() {
      let query = this._buildMainQuery().getParams()
      CBPO.dataQueryManager().setQuery(
        this.config.dataSource,
        _.cloneDeep(query)
      )
      return query
    },
    _buildMainQueryParamsExport() {
      const query = cloneDeep(this._buildMainQuery().getParams())
      let { group: { aggregations } } = query
      if (!isEmpty(aggregations)) {
        query.group.aggregations = aggregations.map(aggr => {
          aggr.alias = `${aggr.column}(${aggr.aggregation})`
          return aggr
        })
      }
      Object.keys(query).forEach(item => {
        if (get(this.config.exportConfig, `query.${item}`) !== undefined) {
          query[`${item}`] = this.config.exportConfig.query[`${item}`]
        }
      })
      // support export with specific data
      if (_.get(this.config, 'exportConfig.query.order_export')) {
        query.order_export = this.config.exportConfig.query['order_export']
      }
      // support export by specific ds id
      CBPO.dataQueryManager().setQuery(get(this.config.exportConfig, 'query.dataSource', this.config.dataSource), query)
      return query
    },
    widgetResetCurrentPage() {
      if (this.config.pagination) {
        this.config.pagination.current = 1
      }
    },
    /**
     * Fetch table data from the configuration object.
     */
    async fetch() {
      this.showLoading()
      try {
        let data = await CBPO.dsManager()
          .getDataSource(this.config.dataSource)
          .query(this._buildMainQueryParams(), this.cancelToken)
        this.dm.setData(data.cols, data.rows)
        // Get the last updated time
        const modifiedColumnIndex = data.cols && data.cols.findIndex(item => item.name === 'modified')
        const firstRowData = data.rows && data.rows[0]

        if (modifiedColumnIndex !== -1 && firstRowData) {
          this.$emit('getLastUpdated', firstRowData[modifiedColumnIndex])
        }
        this.render()
      } catch (err) {
        console.log(err)
        this.dm.rows = []
        this.warningText = this.config.messages.no_data_at_all
      } finally {
        this.isElementHidden = _.isEmpty(this.dm.rows)
        this.warningText = _.isEmpty(this.dm.rows)
          ? this.config.messages.no_data_at_all
          : ''
        this.hideLoading()
        this.$emit('autoHeightEvent', this.config.id)
      }
    },
    /**
     * Render chart
     */
    render() {
      let { rows, cols } = this.dm
      let chart = ChartLib.getInstance(this.config.library)
      chart.isChartSupported(this.config)
        ? chart.render(this.id, this.$el, this.config, { rows, cols }, {
          drillDownCallback: this.config.drillDown.enabled ? this.openDrillDown : null
        })
        : this.showElementHidden(`${_.upperFirst(this.config.library || '')} doesn’t support this chart type`)
    },
    fetchAndRender() {
      this.fetch().then(() => {
        this.shouldShowElement()
      })
    },
    widgetConfig(config) {
      this.config = Object.assign(
        {},
        _.cloneDeep(makeDefaultChartConfig(config))
      )
      // render id for render chart
      this.id = uuidv4()
      this.currentTimezone = this.config.timezone.utc
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id), () => {
        // check visible
        const isSmallerThanMinSize = this.$refs.chartWidget.clientWidth < this.config.sizeSettings.defaultMinSize
        const isNoData = _.isEmpty(this.dm.rows)
        this.isElementHidden = isSmallerThanMinSize || _.isEmpty(this.dm.rows)
        this.$emit('checkHeaderWidget', this.isElementHidden)
        if (this.isElementHidden) {
          isNoData
            ? this.shouldShowElement()
            : (this.warningText = this.config.sizeSettings.warningText)
        }
        this.resizeChart()
      })
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id), (config) => {
        this.$set(this, 'config', config)
        this.widgetInit()
      })
      CBPO.$bus.$on(BUS_EVENT.EXPORT_WIDGET(this.config.id), async (widget, handleResponse) => {
        this.widgetExport(
          widget.fileType,
          getFileName(this.config),
          getPollingSetting(this.config),
          getPollingIntervalSetting(this.config),
          true
        ).then((res) => {
          handleResponse(res)
        })
      })
    },
    resizeChart() {
      const library = this.config.library
      if (library === 'highcharts') {
        ChartLib.getInstance(library).updateSizeChart(this.id, this.config)
      }
    },
    /**
     * @override
     */
    widgetExport(fileType, fileName, polling, pollingInterval, isMulti = false) {
      if (!isMulti) {
        var toast = this.$toasted.show('Downloading...', {
          theme: 'outline',
          position: 'top-center',
          iconPack: 'custom-class',
          className: 'cpbo-toast-export',
          icon: {
            name: 'fa fa-spinner fa-spin fa-fw',
            after: false
          },
          duration: null
        })
      }
      // support export by specific ds id
      return CBPO.dsManager()
        .getDataSource(get(this.config.exportConfig, 'query.dataSource', this.config.dataSource))
        /**
         * Export table data with optional polling support
         * @param {Object} queryParams - The query parameters for export
         * @param {String} fileName - Name of the exported file
         * @param {String} fileType - Type of export (csv, xlsx, etc.)
         * @param {Array} columns - Columns to include in export
         * @param {Boolean} polling - Whether to use polling mode for large exports
         * @param {Number} pollingInterval - How often to check export status in ms
         */
        .export(
          this._buildMainQueryParamsExport(),
          fileName,
          fileType,
          this.config.columns,
          polling,
          pollingInterval
        )
        .then(
          () => {
            if (!isMulti) toast.goAway(1500)
            return true
          },
          /* eslint handle-callback-err: ["error", "error"] */
          (err) => {
            if (!isMulti) toast.goAway(1500)
            return false
          }
        )
    },
    widgetInit() {
      this.config.filter = this.filterObj
      this.fetchColumnsAndSaveToService(this.config.dataSource) // widget base mixins
      this.fetchAndRender()
    },
    calculateElementHeight() {
      let numberOfPadding = 1
      let sizeOfPadding = 8
      return ($(this.$el).height() || 0) + numberOfPadding * sizeOfPadding
    },
    /**
     * Calculated and hide element if table's size is too small
     * Default min size is 250
     * Will be called inside mounted hook
     * **/
    shouldShowElement() {
      // grid item in widget layout delay this element rendered with full size
      this.$nextTick(() => {
        this.isElementHidden =
          $(this.$el).width() < this.config.sizeSettings.defaultMinSize ||
          isEmpty(this.dm.rows)
        this.warningText = isEmpty(this.dm.rows)
          ? this.config.messages.no_data_at_all
          : this.config.sizeSettings.warningText
      })
    },
    showElementHidden(message) {
      this.$nextTick(() => {
        this.isElementHidden = true
        this.warningText = message
      })
    },
    changeColor() {
      const { library, id, charts = [] } = this.config
      const yAxisNum = _.get(charts, '[0].axis.y.length', 1)
      let themeStyles = util.getStyle()
      let colorData = {
        color: themeStyles.accentColor
      }
      if (!isEmpty(this.colorStyle)) {
        colorData = { ...this.colorStyle }
      }
      const chartType = _.get(this.config, 'charts[0].series[0].type')
      let updateColorFn = ChartLib.getInstance(library).updateColor
      if (updateColorFn) {
        updateColorFn(colorData, id, yAxisNum, chartType)
      }
    }
  },
  created() {
    if (!isEmpty(this.filterObj)) {
      this.config.filter = this.filterObj
    }
    this.dm = new DataManager()
  },
  mounted() {
    this.dm.reset()
    CBPO.$bus.$on(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA, () => {
      this.fetchAndRender()
    })
  },
  destroyed() {
    CBPO.$bus.$off(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA)
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.EXPORT_WIDGET(this.config.id))
  }
}
</script>
<style scoped lang="scss">
@import 'Chart';
</style>
