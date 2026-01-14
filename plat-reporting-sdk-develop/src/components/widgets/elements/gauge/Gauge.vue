<template>
  <div
    v-if="configReady"
    :id="getId"
    ref="gaugeChartElement"
    class="cbpo-s cbpo-widget cbpo-chart-widget"
    :class="config.css"
    :style="config.style"
    v-cbpo-loading="{loading: loading}"
  >
    <div v-show="!isElementHidden" class="cbpo-chart-title"
         v-if="config.widget.title.enabled">
      {{config.widget.title.text}}
    </div>
    <div v-show="!isElementHidden" v-if="config.charts && config.charts.length > 0" class="chart-container">
      <div v-for="(chart, indexChart) in config.charts" :key="indexChart" :class="{vertical: !config.charts[0].options.isHorizontal}" class="chartSets"></div>
    </div>
    <div class="warning-size-content" v-show="isElementHidden">
      <span>{{warningText}}</span>
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
import { makeDefaultGaugeConfig } from '@/components/widgets/elements/gauge/GaugeConfig'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import { BUS_EVENT } from '@/services/eventBusType'
import loadingDirective from '@/directives/loadingDirective'
import $ from 'jquery'
import { makeDOMId } from '@/components/widgets/elements/chart/types/ChartTypes'
import uuidv4 from 'uuid'
import { getFileName, getPollingSetting, getPollingIntervalSetting } from '@/utils/multiExportUtil'
import isEmpty from 'lodash/isEmpty'
import get from 'lodash/get'
import cloneDeep from 'lodash/cloneDeep'
import upperFirst from 'lodash/upperFirst'

export default {
  name: 'Gauge',
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
  data() {
    return {
      isElementHidden: false,
      warningText: '',
      id: null
    }
  },
  directives: {
    'cbpo-loading': loadingDirective
  },
  watch: {
    filterObj: {
      deep: true,
      handler() {
        if (this.cancelToken) this.cancelToken.cancel('Cancel token is applied')
        this.createCancelToken()
        this.config.filter = this.filterObj
        this.widgetResetCurrentPage()
        this.fetchAndRender()
      }
    },
    colorStyle: {
      deep: true,
      immediate: true,
      handler(val) {
        this.changeColor()
      }
    }
  },
  computed: {
    getId() {
      return makeDOMId(get(this.config, 'library'), this.id)
    }
  },
  methods: {
    _buildMainQuery() {
      let q = new QueryBuilder()
      if (!isEmpty(this.config.sorting)) {
        let { column, direction } = this.config.sorting[0]
        let binColumn = this.config.bins.find(bin => bin.column.name === column)
        q.addOrder(binColumn ? binColumn.alias : column, direction)
      }
      let { current, limit } = this.config.pagination
      q.setPaging({ current, limit })
      if (!isEmpty(this.config.grouping)) {
        let { columns, aggregations } = this.config.grouping
        q.setGroup(columns, aggregations)
      }
      if (!isEmpty(this.config.filter)) {
        q.setFilter(this.config.filter)
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
      CBPO.dataQueryManager().setQuery(this.config.dataSource, cloneDeep(query))
      return query
    },
    widgetResetCurrentPage: function() {
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
      } catch (err) {
        this.dm.rows = []
        this.warningText = this.config.messages.no_data_at_all
      } finally {
        this.isElementHidden = isEmpty(this.dm.rows)
        this.warningText = isEmpty(this.dm.rows)
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
      let {rows, cols} = this.dm
      let chart = ChartLib.getInstance(this.config.library)
      chart.isChartSupported(this.config)
        ? chart.render(this.id, this.$el, this.config, {rows, cols})
        : this.showElementHidden(`${upperFirst(this.config.library || '')} doesn’t support this chart type`)
    },
    fetchAndRender() {
      this.fetch().then(() => {
        this.render()
        this.shouldShowElement()
      })
    },
    widgetConfig(config) {
      makeDefaultGaugeConfig(config)
      this.id = uuidv4()
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id), () => {
        const library = this.config.library
        // check visible
        const isSmallerThanMinSize = this.$refs.gaugeChartElement.clientWidth < this.config.sizeSettings.defaultMinSize
        const isNoData = isEmpty(this.dm.rows)
        this.isElementHidden = isSmallerThanMinSize || isEmpty(this.dm.rows)
        this.$emit('checkHeaderWidget', this.isElementHidden)
        if (this.isElementHidden) {
          isNoData
            ? this.shouldShowElement()
            : (this.warningText = this.config.sizeSettings.warningText)
        }
        if (library === 'highcharts') {
          ChartLib.getInstance(library).updateSizeChart(this.id, this.config)
        }
      })
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id), (config) => {
        this.$set(this, 'config', config)
        this.widgetInit()
      })
      CBPO.$bus.$on(BUS_EVENT.EXPORT_WIDGET(this.config.id), async(widget, handleResponse) => {
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
    /**
     * @override
     */
    widgetExport (fileType, fileName, polling, pollingInterval, isMulti = false) {
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
      return CBPO
        .dsManager()
        .getDataSource(this.config.dataSource)
        /**
         * Export table data with optional polling support
         * @param {Object} queryParams - The query parameters for export
         * @param {String} fileName - Name of the exported file
         * @param {String} fileType - Type of export (csv, xlsx, etc.)
         * @param {Array} columns - Columns to include in export
         * @param {Boolean} polling - Whether to use polling mode for large exports
         * @param {Number} pollingInterval - How often to check export status in ms
         */
        .export(this._buildMainQueryParams(), fileName, fileType, [], polling, pollingInterval)
        .then(blob => {
          if (!isMulti) toast.goAway(1500)
          this.widgetDownloadFile(blob, fileName)
          return true
        },
        /* eslint handle-callback-err: ["error", "error"] */
        (err) => {
          if (!isMulti) toast.goAway(1500)
          return false
        })
    },
    widgetInit() {
      this.config.filter = this.filterObj
      this.fetchAndRender()
    },
    calculateElementHeight() {
      let numberOfPadding = 1
      let sizeOfPadding = 8
      return ($(this.$el).height() || 0) + (numberOfPadding * sizeOfPadding)
    },
    /**
     * Calculated and hide element if table's size is too small
     * Default min size is 250
     * Will be called inside mounted hook
     * **/
    shouldShowElement() {
      // grid item in widget layout delay this element rendered with full size
      setTimeout(() => {
        this.isElementHidden = $(this.$el).width() < this.config.sizeSettings.defaultMinSize
        this.warningText = this.config.sizeSettings.warningText
      }, 0)
    },
    showElementHidden(message) {
      setTimeout(() => {
        this.isElementHidden = true
        this.warningText = message
      }, 0)
    },
    changeColor() {
      const { library, id } = this.config
      let colorData = {color: '#333333'}
      if (!isEmpty(this.colorStyle)) {
        colorData = {...this.colorStyle}
      }
      if (library === 'highcharts') {
        ChartLib.getInstance(library).updateColor(colorData, id)
      }
    }
  },
  created() {
    this.dm = new DataManager()
  },
  mounted() {
    this.dm.reset()
  },
  destroyed() {
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.EXPORT_WIDGET(this.config.id))
  }
}
</script>
<style scoped lang="scss">
@import './Gauge';
</style>
