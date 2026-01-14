import findIndex from 'lodash/findIndex'
import KPIGradient from '@/services/ds/expression/cbpoChartLibs/KPIGradient'
import { getStyle } from '@/utils/chartUtil'

const COLOR = {
  MAX_COLOR_CURRENT_FAIL: '#D24A03',
  MAX_COLOR_CURRENT_PASS: '#429420',
  MAX_COLOR_TARGET: '#3A6CF5',
  MAX_COLOR_MAX_POINT: '#DADBDC',
  MIN_COLOR_CURRENT_FAIL: '#FF9C00',
  MIN_COLOR_CURRENT_PASS: '#A6D950',
  MIN_COLOR_TARGET: '#669FFE',
  MIN_COLOR_MAX_POINT: '#B2B6BC',
  DEFAULT_COLOR: '#3A4464'
}

export class BarKPIGradientConfig {
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
    let max = Math.max(values[maxIndex], target, current) || 0
    let maxPoint = max === 0 ? max + 1 : max
    const percentage = Math.round((current - target) / (target || 1) * 10000) / 100

    const formatValue = (value) => {
      return formatObject.prefix + formatFn(value, formatObject.formatType, formatObject.formatString) + formatObject.suffix
    }

    return {
      data: [
        {
          label: 'Max_Value',
          formatLabel: options && options.legend ? options.legend.goal : 'Max',
          formatValue: formatValue(max),
          value: max,
          position: 'bottom',
          color: { min: COLOR.MIN_COLOR_MAX_POINT, max: COLOR.MAX_COLOR_MAX_POINT }
        },
        {
          label: 'Target_Value',
          formatLabel: options && options.legend ? options.legend.target : 'Target',
          formatValue: formatValue(target),
          value: target,
          position: 'bottom',
          color: { min: COLOR.MIN_COLOR_TARGET, max: COLOR.MAX_COLOR_TARGET }
        },
        {
          label: 'Current_Value',
          formatLabel: options && options.legend ? options.legend.current : 'Current',
          value: current,
          formatValue: formatValue(current),
          position: 'top',
          color: current >= target
            ? { min: COLOR.MIN_COLOR_CURRENT_PASS, max: COLOR.MAX_COLOR_CURRENT_PASS }
            : { min: COLOR.MIN_COLOR_CURRENT_FAIL, max: COLOR.MAX_COLOR_CURRENT_FAIL }
        }
      ],
      config: {
        background: themeStyles.mainColor,
        point: {
          enabled: options.percentNumber === 'on' && target !== current,
          label: percentage + '%',
          color: current >= target ? COLOR.MAX_COLOR_CURRENT_PASS : COLOR.MAX_COLOR_CURRENT_FAIL,
          direction: current >= target ? 'top' : 'bottom',
          targetPoint: current
        },
        bar: {
          padding: 50,
          height: 15
        },
        max: {
          value: maxPoint,
          color: COLOR.DEFAULT_COLOR
        },
        legendColor: '#bdc0c4',
        size: {
          x: parseInt(options.width),
          y: parseInt(options.height) + 80
        }
      }
    }
  }

  drawChart(id, columns, values, formatObject, formatFn, options) {
    // get config
    let chartConfig = this.getConfig(id, columns, values, formatObject, formatFn, options)
    // draw chart
    KPIGradient
      .renderBarKPI(
        `#${id}`,
        { ...chartConfig }
      )
  }
}
