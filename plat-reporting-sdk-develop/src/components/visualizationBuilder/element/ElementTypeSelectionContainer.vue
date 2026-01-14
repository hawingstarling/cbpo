<template>
  <div class="cbpo-visualization-element">
    <div class="cbpo-element-header">
      <h4>Elements</h4>
    </div>
    <div class="cbpo-element-content">
      <div class="cbpo-grid-row">
        <div :class="{'active': isChartType(TYPES.PIE)}" @click="createNewElementConfig(ELEMENT.CHART, TYPES.PIE)"
             class="cbpo-grid-item">
          <i class="fa fa-pie-chart" />
        </div>
        <div :class="{'active': isChartType(TYPES.BAR)}" @click="createNewElementConfig(ELEMENT.CHART, TYPES.BAR)"
             class="cbpo-grid-item">
          <i class="fa fa-bar-chart" />
        </div>
        <div :class="{'active': isChartType(TYPES.LINE)}" @click="createNewElementConfig(ELEMENT.CHART, TYPES.LINE)"
             class="cbpo-grid-item">
          <i class="fa fa-line-chart" />
        </div>
        <div :class="{'active': isChartType(TYPES.AREA)}" @click="createNewElementConfig(ELEMENT.CHART, TYPES.AREA)"
             class="cbpo-grid-item">
          <i class="fa fa-area-chart" />
        </div>
        <div :class="{'active': isChartType(TYPES.SCATTER)}"
             @click="createNewElementConfig(ELEMENT.CHART, TYPES.SCATTER)" class="cbpo-grid-item">
          <svg version="1.1" id="scatter_svg" xmlns="http://www.w3.org/2000/svg"
               xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
               viewBox="0 0 17.455 17.455" style="enable-background:new 0 0 17.455 17.455;" xml:space="preserve">
            <polygon points="1.658,15.667 1.658,0.13 0,0.13 0,17.325 17.455,17.325 17.455,15.667" />
            <circle cx="5.134" cy="11.843" r="1.519" />
            <circle cx="6.147" cy="7.631" r="1.519" />
            <circle cx="8.331" cy="10.496" r="1.52" />
            <circle cx="9.851" cy="6.557" r="1.519" />
            <circle cx="13.859" cy="6.558" r="1.52" />
            <circle cx="11.97" cy="9.595" r="1.52" />
            <circle cx="11.971" cy="3.519" r="1.519" />
          </svg>
        </div>
        <div :class="{'active': isChartType(TYPES.BUBBLE)}" @click="createNewElementConfig(ELEMENT.CHART, TYPES.BUBBLE)"
             class="cbpo-grid-item">
          <svg version="1.1" id="bubble_svg" xmlns="http://www.w3.org/2000/svg"
               xmlns:xlink="http://www.w3.org/1999/xlink" x="0px"
               y="0px"
               viewBox="0 0 511.999 511.999" style="enable-background:new 0 0 511.999 511.999;" xml:space="preserve">
            <path d="M346.094,210.952c-82.997,0-150.523,67.527-150.523,150.523s67.527,150.523,150.523,150.523
              s150.523-67.527,150.523-150.523S429.091,210.952,346.094,210.952z" />
            <path d="M135.874,0C69.433,0,15.382,54.05,15.382,120.492s54.05,120.492,120.492,120.492s120.492-54.05,120.492-120.492
              S202.315,0,135.874,0z" />
            <path d="M391.141,0c-41.602,0-75.445,33.844-75.445,75.445s33.844,75.445,75.445,75.445c41.601,0,75.445-33.844,75.445-75.445
              S432.742,0,391.141,0z" />
          </svg>
        </div>
        <div :class="{'active': isChartType(TYPES.PARETO)}" @click="createNewElementConfig(ELEMENT.CHART, TYPES.PARETO)"
             class="cbpo-grid-item">
          <svg height="512pt" viewBox="0 0 512 512" width="512pt" xmlns="http://www.w3.org/2000/svg">
            <path
              d="m76 240c12.101562 0 23.054688-4.855469 31.148438-12.652344l44.402343 22.199219c-.222656 1.808594-.550781 3.585937-.550781 5.453125 0 24.8125 20.1875 45 45 45s45-20.1875 45-45c0-6.925781-1.703125-13.410156-4.511719-19.277344l60.234375-60.234375c5.867188 2.808594 12.351563 4.511719 19.277344 4.511719 24.8125 0 45-20.1875 45-45 0-4.671875-.917969-9.089844-2.246094-13.328125l52.335938-39.242187c7.140625 4.769531 15.699218 7.570312 24.910156 7.570312 24.8125 0 45-20.1875 45-45s-20.1875-45-45-45-45 20.1875-45 45c0 4.671875.917969 9.089844 2.246094 13.328125l-52.335938 39.242187c-7.140625-4.769531-15.699218-7.570312-24.910156-7.570312-24.8125 0-45 20.1875-45 45 0 6.925781 1.703125 13.410156 4.511719 19.277344l-60.234375 60.234375c-5.867188-2.808594-12.351563-4.511719-19.277344-4.511719-12.101562 0-23.054688 4.855469-31.148438 12.652344l-44.402343-22.199219c.222656-1.808594.550781-3.585937.550781-5.453125 0-24.8125-20.1875-45-45-45s-45 20.1875-45 45 20.1875 45 45 45zm0 0" />
            <path
              d="m497 482h-16v-317c0-8.289062-6.710938-15-15-15h-60c-8.289062 0-15 6.710938-15 15v317h-30v-227c0-8.289062-6.710938-15-15-15h-60c-8.289062 0-15 6.710938-15 15v227h-30v-107c0-8.289062-6.710938-15-15-15h-60c-8.289062 0-15 6.710938-15 15v107h-30v-167c0-8.289062-6.710938-15-15-15h-60c-8.289062 0-15 6.710938-15 15v167h-16c-8.289062 0-15 6.710938-15 15s6.710938 15 15 15h482c8.289062 0 15-6.710938 15-15s-6.710938-15-15-15zm0 0" />
          </svg>
        </div>
        <div :class="{'active': isChartType(TYPES.BULLETGAUGE)}"
             @click="createNewElementConfig(ELEMENT.GAUGE, TYPES.BULLETGAUGE)" class="cbpo-grid-item">
          <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 100 100">
            <path fill="#333"
                  d="M68.9 5H5v24.2h90V5H68.9zM28.5 8.4v3.4H9V8.4h19.5zM9 25.8v-3.4h19.5v3.4H9zm23.5 0v-3.4h18.1V11.7H32.5V8.4h32.9v17.5H32.5zm59.1 0H68.8V8.4h22.8v17.4z" />
            <path fill="#333"
                  d="M32.4 37.9H5v24.2h90V37.9H32.4zM9 58.7v-3.4h16.1V44.6H9v-3.4h19.5v17.5H9zm23.5 0V41.3h32.9v17.5H32.5zm59.1-17.4v17.5H68.8V41.3h22.8z" />
            <path fill="#333"
                  d="M32.4 70.8H5V95h90V70.8H32.4zm33 3.4v3.4H32.5v-3.4h32.9zm-36.9 0v3.4H9v-3.4h19.5zM9 91.6v-3.4h19.5v3.4H9zm23.5 0v-3.4h32.9v3.4H32.5zm59.1-17.4v17.5H68.8v-3.4h10.1V77.5H68.8v-3.4h22.8z" />
          </svg>
        </div>
        <div :class="{'active': isChartType(TYPES.SOLIDGAUGE)}"
             @click="createNewElementConfig(ELEMENT.GAUGE, TYPES.SOLIDGAUGE)" class="cbpo-grid-item">
          <i class="fa fa-tachometer" />
        </div>
        <div :class="{'active': isChartType(TYPES.HEAT_MAP)}"
             @click="createNewElementConfig(ELEMENT.HEAT_MAP, TYPES.HEAT_MAP)" class="cbpo-grid-item">
          <svg viewBox="-21 -90 682.66669 682" xmlns="http://www.w3.org/2000/svg">
            <path d="m391.28125 260.042969h-18.75v-18.75h18.75zm-31.25 0h-18.75v-18.75h18.75zm0 0" />
            <path
              d="m156.34375 419.929688c0-18.128907 0-168.660157 0-191.253907h82.207031v213.140625h-67.867187v18.75h431.816406v-358.523437h-424.28125v18.75h60.328125v51.632812h-82.203125v-98.507812c0-43.097657-35.070312-78.167969-78.175781-78.167969-43.097657 0-78.167969 35.070312-78.167969 78.167969v346.015625c0 43.277344 35.1875 78.210937 78.167969 78.210937 42.933593-.007812 78.175781-34.890625 78.175781-78.214843zm138.453125 21.886718v-66.277344h142.960937v66.277344zm288.953125 0h-89.742188v-213.140625h89.742188zm0-321.023437v51.632812h-89.742188v-51.632812zm-145.992188 0v198.496093h-142.960937v-198.496093zm-281.414062 70.382812h100.953125v-70.382812h18.75v217.246093h180.460937v-217.246093h18.75v70.382812h108.492188v18.75h-108.492188v231.890625h-18.75v-85.027344h-180.460937v85.027344h-18.75v-231.890625h-100.953125zm-78.175781 288.140625c-32.746094 0-59.394531-26.636718-59.417969-59.382812.023438-32.746094 26.671875-59.382813 59.417969-59.382813 32.753906 0 59.402343 26.636719 59.425781 59.382813-.023438 32.746094-26.671875 59.382812-59.425781 59.382812zm-59.417969-405.398437c0-32.761719 26.65625-59.417969 59.417969-59.417969 32.769531 0 59.425781 26.65625 59.425781 59.417969v295.34375c-31.324219-36.65625-87.578125-36.582031-118.84375 0zm0 0" />
            <path
              d="m78.167969 379.300781c-22.421875 0-40.667969 18.242188-40.667969 40.667969s18.246094 40.667969 40.667969 40.667969c22.425781 0 40.675781-18.242188 40.675781-40.667969s-18.25-40.667969-40.675781-40.667969zm0 62.585938c-12.082031 0-21.917969-9.828125-21.917969-21.917969s9.835938-21.917969 21.917969-21.917969c12.089843 0 21.925781 9.828125 21.925781 21.917969s-9.835938 21.917969-21.925781 21.917969zm0 0" />
            <path d="m171.96875 64.542969v18.75h449.28125v396.023437h-474.28125v18.75h493.03125v-433.523437zm0 0" />
          </svg>
        </div>
        <div :class="{'active': (element ? element.type : '') === ELEMENT.TABLE}"
             @click="createNewElementConfig(ELEMENT.TABLE, 'pie')" class="cbpo-grid-item">
          <i class="fa fa-table" />
        </div>
        <div :class="{'active': (element ? element.type : '') === ELEMENT.CROSSTAB_TABLE}"
             @click="createNewElementConfig(ELEMENT.CROSSTAB_TABLE)" class="cbpo-grid-item">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path
              d="M 4 2 C 2.9 2 2 2.9 2 4 L 2 20 C 2 21.1 2.9 22 4 22 L 20 22 C 21.1 22 22 21.1 22 20 L 22 4 C 22 2.9 21.1 2 20 2 L 4 2 z M 8 4 L 10 4 L 10 8 L 20 8 L 20 20 L 8 20 L 8 10 L 4 10 L 4 8 L 8 8 L 8 4 z M 16 9 L 12.998047 12 L 15.001953 12 L 15 14 C 15 14.56503 14.56503 15 14 15 L 12 15 L 12 13 L 9 16 L 12 19 L 12 17 L 14 17 C 15.64497 17 17 15.64497 17 14 L 17.001953 12 L 18.998047 12 L 16 9 z" />
          </svg>
        </div>
        <div :class="{'active': (element ? element.type : '') === ELEMENT.GLOBAL_FILTER}"
             @click="createNewElementConfig(ELEMENT.GLOBAL_FILTER)" class="cbpo-grid-item">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
            <path
              style="line-height:normal;text-indent:0;text-align:start;text-decoration-line:none;text-decoration-style:solid;text-decoration-color:#000;text-transform:none;block-progression:tb;isolation:auto;mix-blend-mode:normal"
              d="M 3 2 L 3 2.5 L 3 3.9746094 C 3 4.4677431 3.242869 4.9291272 3.6484375 5.2089844 L 7 7.7480469 L 7 14 L 9 12 L 9 7.7480469 L 12.351562 5.2089844 C 12.757131 4.9291272 13 4.4677431 13 3.9746094 L 13 2 L 3 2 z M 4 3 L 12 3 L 12 3.9746094 C 12 4.1394756 11.91963 4.2925759 11.783203 4.3867188 L 11.773438 4.3925781 L 8.3320312 7 L 7.6679688 7 L 4.2265625 4.3925781 L 4.2167969 4.3867188 C 4.0803654 4.292576 4 4.1394756 4 3.9746094 L 4 3 z"
              font-weight="400" font-family="sans-serif" white-space="normal" overflow="visible" />
          </svg>
        </div>
        <div :class="{'active': (element ? element.type : '') === ELEMENT.HTML_EDITOR}"
             @click="createNewElementConfig(ELEMENT.HTML_EDITOR, 'pie')" class="cbpo-grid-item">
          <i class="fa fa-code" />
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { makeDefaultHeatMapConfig } from '@/components/widgets/elements/heat-map/HeatMapConfig'
import { makeTableDefaultConfig } from '@/components/widgets/elements/table/TableConfig'
import { makeDefaultChartConfig, TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import { makeDefaultHtmlEditorConfig } from '@/components/widgets/elements/htmlEditor/HtmlEditorConfig'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import {
  DEFAULT_CHART_CONFIG_CHARTJS, DEFAULT_CHART_CONFIG_HEAT_MAP,
  DEFAULT_CONFIG_X_AXIS,
  DEFAULT_CONFIG_Y_AXIS,
  DEFAULT_SERIES_CONFIG,
  getDefaultOptionsConfigFromChartTypeChartJs
} from '@/components/widgets/elements/chart/types/ChartTypes'
import { isEmpty, cloneDeep, defaultsDeep, get } from 'lodash'
import { createBinColumnAlias, buildBinObj, hasBinningAccept } from '@/utils/binUtils'
import { makeCrosstabTableDefaultConfig } from '@/components/widgets/elements/crosstab-table/CrosstableTableConfig'
import {
  handleUngrouping, GROUPING_TYPE
} from '@/utils/visualizationUtil'
import { getDataTypeFromType } from '@/services/ds/data/DataTypes'
import { makeDefaultGlobalConfig } from '@/components/widgets/elements/globalFilter/GlobalFilterConfig'
import { generateIdIfNotExist } from '@/utils/configUtil'

export default {
  name: 'VisualizationElement',
  props: {
    element: Object,
    selectedElement: Object,
    dataSource: String
  },
  data() {
    return {
      ELEMENT: ELEMENT,
      TYPES: cloneDeep(TYPES),
      configData: null
    }
  },
  computed: {
    isChartType() {
      return chartType => {
        if (!this.element || (![ELEMENT.CHART, ELEMENT.GAUGE, ELEMENT.HEAT_MAP].includes(this.element.type))) {
          return false
        }
        return this.selectedElement.chartType === chartType
      }
    }
  },
  methods: {
    createNewElementConfig(type, chartType = null, isExtended = true) {
      let prevSelectedType = cloneDeep(this.selectedElement)
      let selectedType = chartType
      this.selectedElement.elementType = type
      this.selectedElement.chartType = chartType
      chartType = chartType === TYPES.PARETO ? TYPES.BAR : chartType
      let config = { dataSource: this.dataSource }
      switch (type) {
        case ELEMENT.TABLE:
          makeTableDefaultConfig(config)
          config.detailView.enabled = true
          break
        case ELEMENT.GLOBAL_FILTER:
          makeDefaultGlobalConfig(config)
          break
        case ELEMENT.CROSSTAB_TABLE:
          makeCrosstabTableDefaultConfig(config)
          break
        case ELEMENT.CHART:
          makeDefaultChartConfig(config)
          generateIdIfNotExist(config)

          let defaultConfig = defaultsDeep({}, DEFAULT_CHART_CONFIG_CHARTJS)
          let defaultSeriesConfig = defaultsDeep({ type: selectedType === TYPES.PARETO ? TYPES.BAR : chartType }, DEFAULT_SERIES_CONFIG)
          defaultSeriesConfig.id = Date.now()

          // Mapping axis
          let defaultAxisX = { ...{ id: `x_${defaultSeriesConfig.id}` }, ...cloneDeep(DEFAULT_CONFIG_X_AXIS) }
          let defaultAxisY = { ...{ id: `y_${defaultSeriesConfig.id}` }, ...cloneDeep(DEFAULT_CONFIG_Y_AXIS) }
          defaultSeriesConfig.axis = {
            x: `x_${defaultSeriesConfig.id}`,
            y: `y_${defaultSeriesConfig.id}`
          }

          // Mapping Options
          defaultConfig.options = defaultsDeep(defaultConfig.options, getDefaultOptionsConfigFromChartTypeChartJs(chartType))
          defaultConfig.axis.x = [...defaultConfig.axis.x, defaultAxisX]
          defaultConfig.axis.y = [...defaultConfig.axis.y, defaultAxisY]
          defaultConfig.series = [defaultSeriesConfig]
          if (chartType === TYPES.PIE) {
            defaultConfig.options.legend.position = 'right'
            defaultConfig.options.legend.isHorizontal = false
          } else {
            defaultConfig.options.legend.position = 'bottom'
            defaultConfig.options.legend.isHorizontal = true
          }
          config.charts = [defaultConfig]
          break
        case ELEMENT.HTML_EDITOR:
          makeDefaultHtmlEditorConfig(config)
          break
        case ELEMENT.GAUGE:
          makeDefaultChartConfig(config)
          generateIdIfNotExist(config)

          let bulletGaugeConfig = defaultsDeep({}, DEFAULT_CHART_CONFIG_CHARTJS)
          let bulletGaugeSeriesConfig = defaultsDeep({ type: chartType }, DEFAULT_SERIES_CONFIG)
          defaultSeriesConfig.id = Date.now()

          // Mapping axis
          let bulletGaugeAxisY = { ...{ id: `y_${bulletGaugeSeriesConfig.id}` }, ...cloneDeep(DEFAULT_CONFIG_Y_AXIS) }
          bulletGaugeSeriesConfig.axis = {
            y: `y_${bulletGaugeSeriesConfig.id}`
          }

          // Mapping Options
          bulletGaugeConfig.options = defaultsDeep(bulletGaugeConfig.options, getDefaultOptionsConfigFromChartTypeChartJs(chartType))
          bulletGaugeConfig.axis.y = [...bulletGaugeConfig.axis.y, bulletGaugeAxisY]
          bulletGaugeConfig.series = [bulletGaugeSeriesConfig]
          config.library = 'highcharts'
          config.charts = [bulletGaugeConfig]
          break
        case ELEMENT.HEAT_MAP:
          makeDefaultHeatMapConfig(config)
          generateIdIfNotExist(config)
          config.charts.push(DEFAULT_CHART_CONFIG_HEAT_MAP())
          break
        default:
          throw new Error(`We have not supported type ${type} yet.`)
      }
      if (!isExtended) {
        this.$emit('update:element', { type, config })
        this.$emit('update:selectedElement', this.selectedElement)
        return
      }
      // Save filter and grouping from the previous selection
      if (this.element && this.element.type === type) {
        if (type === ELEMENT.CHART) {
          let prevItemType
          config.library = this.element.config.library
          config.charts[0].series = this.element.config.charts[0].series.map((item, i) => {
            if (selectedType === TYPES.PARETO) {
              if (!i) {
                item.type = item.type !== TYPES.BAR || item.type !== TYPES.LINE ? TYPES.BAR : item.type
                prevItemType = item.type
              } else {
                item.type = prevItemType === TYPES.BAR ? TYPES.LINE : TYPES.BAR
              }
            } else {
              item.type = chartType
            }
            return item
          })
          config.charts[0].axis = cloneDeep(this.element.config.charts[0].axis)
        }
        if (type === ELEMENT.CHART) {
          if (chartType === TYPES.BUBBLE && prevSelectedType.chartType !== TYPES.BUBBLE) {
            // remove from series and aggregations
            config.charts[0].series.forEach(item => {
              if (this.checkColumnInSeries(config.charts[0].series, item.data.y) <= 1) {
                if (this.element.config.columns && this.element.config.columns.length) {
                  this.element.config.columns = this.element.config.columns.filter(col => col.name !== item.data.y)
                }
              }
              const name = item.data.y
              handleUngrouping(this.element, item, { name }, GROUPING_TYPE.AGGREGATIONS)
              item.data.y = ''
            })
            config.charts[0].series.slice(0, 1)
            config.grouping.aggregations = []
          }
          if (chartType !== TYPES.BUBBLE && prevSelectedType.chartType === TYPES.BUBBLE) {
            config.charts[0].series.forEach(item => {
              if (this.checkColumnInSeries(config.charts[0].series, item.data.y) <= 1) {
                if (this.element.config.columns && this.element.config.columns.length) {
                  this.element.config.columns = this.element.config.columns.filter(col => col.name !== item.data.y)
                }
              }
              if (this.checkColumnInSeries(config.charts[0].series, item.data.z) <= 1) {
                if (this.element.config.columns && this.element.config.columns.length) {
                  this.element.config.columns = this.element.config.columns.filter(col => col.name !== item.data.z)
                }
              }
              const yName = item.data.y
              handleUngrouping(this.element, item, { name: yName }, GROUPING_TYPE.COLUMNS)
              const zName = item.data.z
              handleUngrouping(this.element, item, { name: zName }, GROUPING_TYPE.AGGREGATIONS)
              item.data.y = ''
              delete item.data.z
            })
            config.charts[0].series.slice(0, 1)
          }
        }

        // auto binning for BAR and PARETO with numeric or temporal
        config.bins = cloneDeep(this.element.config.bins)
        const autoBinningCharts = [TYPES.PARETO, TYPES.BAR, TYPES.PIE]
        const xAxis = get(this.element.config, 'charts[0].series[0].data.x', null)
        const columns = cloneDeep(this.element.config.columns)
        let hasAutoBinning = false
        // find x column
        const xColumn = columns.find(col => col.name === xAxis)
        if (autoBinningCharts.includes(chartType)) {
          if (xColumn && !config.bins.find(bin => bin.alias === createBinColumnAlias(xColumn.name)) && hasBinningAccept(xColumn)) {
            const binObj = buildBinObj(xColumn)
            if (!isEmpty(binObj)) {
              config.bins.push(binObj)
              hasAutoBinning = true
            }
          }
        }
        // remove binning column that isn't in columns
        if (!isEmpty(config.bins)) {
          config.bins = config.bins.filter(bin => bin.alias === createBinColumnAlias(bin.column.name) &&
            this.element.config.columns.findIndex(col => col.name.includes(bin.column.name)) !== -1)
        }

        if (!isEmpty(this.element.config.grouping) && chartType !== TYPES.SCATTER) {
          config.grouping = cloneDeep(this.element.config.grouping)
          // if has auto binning, update group columns and aggregation
          if (hasAutoBinning) {
            config.grouping.columns = config.grouping.columns.map(col => {
              if (col.name === xColumn.name) col.name = createBinColumnAlias(col.name)
              return col
            })
            const aggregationData = getDataTypeFromType(xColumn.type).defaultAggregation
            const xAggr = {
              column: xColumn.name,
              aggregation: aggregationData.aggregation,
              alias: xColumn.name
            }
            config.grouping.aggregations = [...config.grouping.aggregations, xAggr]
          }
        }

        if (!isEmpty(this.element.config.columns)) {
          config.columns = cloneDeep(this.element.config.columns)
        }

        if (!isEmpty(this.element.config.filter)) {
          config.filter = cloneDeep(this.element.config.filter)
        }
      }

      this.$emit('update:element', { type, config })
      this.$emit('update:selectedElement', this.selectedElement)
      if (type === ELEMENT.CHART && chartType !== TYPES.SCATTER && prevSelectedType.chartType === TYPES.SCATTER) {
        this.$emit('createGroupingFromConfig')
      }
    },
    checkColumnInSeries(series, name) {
      // check series
      let columnInSeries = 0
      this.element.config.charts[0].series.forEach(ser => {
        columnInSeries += Object.values(ser.data).reduce((total, val) => {
          return val === name ? ++total : total
        }, 0)
      })
      return columnInSeries
    }
  },
  created() {
    // Default selected is pie chart
    if (!this.element) {
      this.createNewElementConfig(ELEMENT.CHART, TYPES.PIE)
      this.$emit('createFirstSeries')
    }
  }
}
</script>
<style lang="scss" scoped>
@import "ElementTypeSelectionContainer";
</style>
