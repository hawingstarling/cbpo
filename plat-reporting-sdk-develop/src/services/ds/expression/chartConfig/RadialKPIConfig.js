import findIndex from 'lodash/findIndex'
import { getStyle, invertColor } from '@/utils/chartUtil'
import KPIChart from '@/services/ds/expression/cbpoChartLibs/KPIChart'

// get background color
const COLOR = {
  DANGER_COLOR: '#e14d58',
  SUCCESS_COLOR: '#71b37c',
  INFO_COLOR: '#5290e9'
}

export default class RadialKPIConfig {
  /**
   * Build config with data from Expression
   * @param {string} id: id of container highcharts
   * @param {Object[]} columns: columns in data from expression
   * @param {Number[]} values: values in data from expression
   * @param {formatString, formatType, formatToolTip, prefix, suffix} formatObject: Format Object
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
        label: 'Current',
        fillColor: current >= target ? COLOR.SUCCESS_COLOR : COLOR.DANGER_COLOR,
        value: current,
        markerWidth: 3,
        needle: true,
        opacity: 1
      },
      {
        label: 'Target',
        fillColor: COLOR.INFO_COLOR,
        value: target,
        markerWidth: 1,
        needle: false,
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
        needle: {
          fillColor: invertColor(themeStyles.mainColor || '#ffffff', true),
          width: 3
        },
        marker: {
          width: 1
        },
        background: themeStyles.mainColor,
        bar: {
          height: 30,
          labelHeight: options.labelHeight
        },
        sum: {},
        legend: {
          enabled: false,
          height: 40,
          color: themeStyles.accentColor
        },
        dialRadiusOffset: 2
      },
      max: {
        enabled: max !== null,
        value: max,
        label: 'Goal',
        markerWidth: 1,
        opacity: max > current && max > target ? 1 : 0,
        fillColor: COLOR.DEFAULT_COLOR
      },
      percentage: {
        enabled: false
      },
      series: bulletGaugeSeries
    }
  }

  drawChart(id, columns, values, formatObject, formatFn, options) {
    // get config
    let chartConfig = this.getConfig(id, columns, values, formatObject, formatFn, options)

    // draw chart
    KPIChart
      .renderRadialKPI(
        `#${id}`,
        {...chartConfig}
      )
  }
}
