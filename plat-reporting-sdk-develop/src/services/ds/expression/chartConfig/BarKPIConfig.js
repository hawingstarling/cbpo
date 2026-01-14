import findIndex from 'lodash/findIndex'
import { getStyle, invertColor } from '@/utils/chartUtil'
import KPIChart from '@/services/ds/expression/cbpoChartLibs/KPIChart'

// get background color
const COLOR = {
  DANGER_COLOR: '#e14d58',
  SUCCESS_COLOR: '#71b37c',
  INFO_COLOR: '#5290e9',
  DEFAULT_COLOR: '#aaaaaa'
}

export default class BarKPIConfig {
  /**
   * Build config with data from Expression
   * @param {string} id: id of container highcharts
   * @param {Object[]} columns: columns in data from expression
   * @param {Number[]} values: values in data from expression
   * @param {formatString, formatType, formatToolTip, suffix, prefix} formatObject: Format Object
   * @param {Function} formatFn: Format callback
   * **/
  getConfig = (id, columns, values, formatObject, formatFn, options) => {
    const themeStyles = getStyle()
    // find index of all required value
    const targetIndex = findIndex(columns, col => col.alias === 'target' || col.name === 'target')
    const currentIndex = findIndex(columns, col => col.alias === 'current' || col.name === 'current')
    const maxIndex = findIndex(columns, col => col.alias === 'max' || col.name === 'max')

    // get all required value with index
    let current = values[currentIndex] || 0
    let target = values[targetIndex] || 0
    let max = values[maxIndex] || null

    const bulletGaugeSeries = [
      {
        label: options.legend.current,
        fillColor: current >= target ? COLOR.SUCCESS_COLOR : COLOR.INFO_COLOR,
        value: current,
        opacity: 1
      },
      {
        label: options.legend.target,
        fillColor: current < target ? COLOR.DANGER_COLOR : COLOR.INFO_COLOR,
        value: target,
        opacity: 1
      }
    ].sort((v1, v2) => v1.value - v2.value)

    // const themeStyles = getStyle()
    return {
      size: {
        width: options.width,
        height: options.height
      },
      margin: {
        top: 15,
        left: 15,
        right: 15,
        bottom: 5
      },
      options: {
        labels: {
          formatter: function() {
            return formatObject.prefix + formatFn(this.value, formatObject.formatType, formatObject.formatString) + formatObject.suffix
          }
        },
        background: themeStyles.mainColor,
        needle: {
          fillColor: invertColor(themeStyles.mainColor || '#ffffff', true)
        },
        marker: {
          width: 2
        },
        bar: {
          height: 30,
          labelHeight: options.labelHeight
        },
        sum: {},
        legend: {
          enabled: true,
          height: 40,
          color: themeStyles.accentColor
        },
        style: options.style || 'gradiant'
      },
      max: {
        enabled: max !== null,
        value: max,
        label: options.legend.goal,
        fillColor: COLOR.DEFAULT_COLOR,
        opacity: max > current && max > target ? 1 : 0
      },
      percentage: {
        enabled: current !== target,
        value: Math.round((current - target) / (target || 1) * 10000) / 100,
        fillColor: current > target ? COLOR.SUCCESS_COLOR : (target > current ? COLOR.DANGER_COLOR : COLOR.DEFAULT_COLOR),
        reversed: current < target
      },
      series: bulletGaugeSeries
    }
  }

  drawChart(id, columns, values, formatObject, formatFn, options) {
    // get config
    let chartConfig = this.getConfig(id, columns, values, formatObject, formatFn, options)

    // draw chart
    KPIChart
      .renderBarKPI(
        `#${id}`,
        {...chartConfig}
      )
  }
}
