<template>
  <div class="cbpo-visualization-widget">
    <div class="cbpo-visualization">
      <div class="cbpo-element-header">
        <h4>Visualization</h4>
      </div>
    </div>
    <div class="cbpo-visualization-content">
      <div v-show="widgetStatus.isValidate" class="widget-content">
        <div id="cbpo-visualization-widget" style="height: 100%">
          <Widget v-if="widgetStatus.isValidate && !widgetStatus.reset"
                  :builder="true"
                  :config-obj="widgetInnerConfig"
                  :visualizationProps="{ elementSettingMethod: applyElementConfig, widgetSettingMethod: applyWidgetConfig, resetAllConfig: resetAllConfig }"
          />
        </div>
      </div>
      <div v-show="!widgetStatus.isValidate" class="widget-content-invalid-config">
        <div class="errors-container">
          <span :key="index" v-for="(msg, index) of widgetStatus.errorMsg" class="error-msg">{{msg}}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { ELEMENT, ERROR_MSG_VISUALIZATION } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import {cloneDeep, get, isEmpty, debounce} from 'lodash'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import Widget from '@/components/widgets/Widget'

export default {
  name: 'Visualization',
  props: {
    widgetConfig: Object,
    filterAlignment: String,
    selected: Object
  },
  components: {
    'Widget': Widget
  },
  data() {
    return {
      widgetData: null,
      widgetInnerConfig: null,
      applyFilter: null,
      widgetStatus: {
        reset: true,
        isValidate: false,
        errorMsg: []
      },
      ELEMENT: ELEMENT
    }
  },
  methods: {
    applyWidgetConfig(config) {
      let { elements } = this.widgetConfig
      config.elements = elements
      this.$emit('widgetConfigChange', cloneDeep(config))
    },
    applyElementConfig(config) {
      this.$emit('elementConfigChange', cloneDeep(config))
    },
    resetAllConfig() {
      this.$emit('resetAllConfig')
    },
    _debounceInitWidget: debounce(function () { this.initWidget() }, 50),
    initWidget() {
      this.$nextTick(() => {
        this.widgetInnerConfig = this.clearEmptySeriesIfExist(cloneDeep(this.widgetConfig))
        this.widgetStatus.reset = false
      })
    },
    /**
     * Clear empty with data is empty in chart
     * Will be call before init widget (initWidget function)
     * @params {Object} config - widget config
     * */
    clearEmptySeriesIfExist(config) {
      if (get(config, 'elements[0].config.charts[0].series', null)) {
        if (![TYPES.PIE, TYPES.BAR].includes(this.selected.chartType)) {
          config.elements[0].config.charts[0].series = config.elements[0].config.charts[0].series
            .filter(item => (config.elements[0].type === ELEMENT.GAUGE ? isEmpty(item.data.x) : !isEmpty(item.data.x)) && !isEmpty(item.data.y))
        }
      }
      return config
    },
    changeGlobalFilter(filter) {
      this.$set(this.widgetData.filter.base.config, 'query', cloneDeep(filter.builder))
      this.$emit('update:widgetConfig', this.widgetData)
    },
    resetValidate() {
      this.widgetStatus = {
        reset: true,
        isValidate: false,
        errorMsg: []
      }
    },
    validateWidget(widget) {
      if (!widget.elements || !widget.elements[0]) {
        this.widgetStatus = {
          reset: true,
          isValidate: false,
          errorMsg: []
        }
        return
      }
      switch (widget.elements[0].type) {
        case ELEMENT.CHART: {
          this.validateChart(widget.elements[0].config)
          break
        }
        case ELEMENT.TABLE: {
          this.validateTable(widget.elements[0].config)
          break
        }
        case ELEMENT.HTML_EDITOR: {
          this.validateHTMLEditor(widget.elements[0].config)
          break
        }
        case ELEMENT.GAUGE: {
          this.validateBulletGauge(widget.elements[0].config)
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          this.validateCrosstabTable(widget.elements[0].config)
          break
        }
        case ELEMENT.GLOBAL_FILTER: {
          this.validateGlobalFilter(widget.elements[0].config)
          break
        }
        case ELEMENT.HEAT_MAP: {
          this.validateHeatMap(widget.elements[0].config)
          break
        }
      }
    },
    validateHTMLEditor(elementConfig) {
      // Nothing to validate with this right now
      this.widgetStatus.errorMsg = []
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateTable(tableConfig) {
      if (!tableConfig.columns || !tableConfig.columns.length) {
        this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateChart(elementConfig) {
      switch (elementConfig.charts[0].series[0].type) {
        case TYPES.PIE: {
          this.validatePieChart(elementConfig.charts[0])
          break
        }
        case TYPES.SCATTER: {
          this.validateScatterChart(elementConfig.charts[0])
          break
        }
        case TYPES.AREA:
        case TYPES.LINE:
        case TYPES.BAR: {
          this.validateBarLineChart(elementConfig.charts[0])
          break
        }
        case TYPES.BUBBLE: {
          this.validateBubbleChart(elementConfig.charts[0])
          break
        }
      }
    },
    validateBulletGauge(elementConfig) {
      switch (elementConfig.charts[0].series[0].type) {
        case TYPES.BULLETGAUGE:
        case TYPES.SOLIDGAUGE: {
          this.validateBulletGaugeChart(elementConfig.charts[0])
          break
        }
      }
    },
    validatePieChart(chartConfig) {
      if (!chartConfig.series[0].data.y) {
        this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateScatterChart(chartConfig) {
      if (!chartConfig.series[0].data.y || !chartConfig.series[0].data.x) {
        this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateBarLineChart(chartConfig) {
      if (this.selected.chartType === TYPES.BAR) {
        if (!chartConfig.series[0].data.y) {
          this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
        }
      } else {
        if (!chartConfig.series[0].data.y || !chartConfig.series[0].data.x) {
          this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
        }
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateBubbleChart(chartConfig) {
      if (!chartConfig.series[0].data.y || !chartConfig.series[0].data.x || !chartConfig.series[0].data.z) {
        this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateBulletGaugeChart(chartConfig) {
      if (!chartConfig.series[0].data.y) {
        this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateCrosstabTable(tableConfig) {
      if (isEmpty(tableConfig.xColumns) || isEmpty(tableConfig.yColumns) || isEmpty(tableConfig.tColumns)) {
        this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    },
    validateGlobalFilter(tableConfig) {
      this.widgetStatus.isValidate = true
    },
    validateHeatMap(elementConfig) {
      const {x, y} = get(elementConfig, 'charts[0].series[0].data', {})
      if (!x || !y) {
        this.$set(this.widgetStatus, 'errorMsg', [...this.widgetStatus.errorMsg, ...ERROR_MSG_VISUALIZATION.GUILD_MESSAGE])
      }
      this.widgetStatus.isValidate = this.widgetStatus.errorMsg.length === 0
    }
  },
  watch: {
    widgetConfig: {
      immediate: true,
      deep: true,
      handler: function(val) {
        if (val) {
          this.widgetStatus.reset = true
          this.widgetData = val
          if (!val.elements || val.elements.filter(element => element).length === 0) {
            this.widgetStatus = {
              isValidate: false,
              errorMsg: [ERROR_MSG_VISUALIZATION.NO_CONFIG]
            }
          }
          this.resetValidate()
          this.validateWidget(val)
          if (this.widgetStatus.isValidate) {
            this._debounceInitWidget()
          }
        }
      }
    }
  }
}
</script>
<style scoped lang="scss">
  .cbpo-visualization-widget{
    height: 100%;
  }
  .widget-content {
    position: relative;
    .chart-options-setting {
      position: absolute;
      top: 12px;
      right: 15px;
      z-index: 9999;
      font-size: 1rem;
      cursor: pointer;
    }
  }
  .cbpo-visualization-content {
    height: calc(100% - 32px);
  }
  .widget-content, .widget-content-invalid-config {
    height: calc(100% - .5rem);
  }
  .widget-content {
    /deep/ {
      .cbpo-table-container,.cbpo-chart-widget {
        max-height: 100%;
        overflow: hidden;
      }
    }
  }
  .widget-content-invalid-config {
    display: flex;
    flex-direction: column;
    flex-wrap: wrap;
    width: 100%;
    justify-content: center;
    align-items: center;

    .error-msg {
      display: block;
      width: 100%;
      font-size: 13px;
      margin-bottom: 10px;
    }
  }
</style>
