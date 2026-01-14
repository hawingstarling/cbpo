import findIndex from 'lodash/findIndex'
import KPIGradient from '@/services/ds/expression/cbpoChartLibs/KPIGradient'
import { getStyle } from '@/utils/chartUtil'

// get background color
const COLOR = {
  MAX_COLOR_CURRENT_FAIL: '#F45E40',
  MAX_COLOR_CURRENT_PASS: '#7CAB2E',
  MAX_COLOR_TARGET: '#3A6CF5',
  MAX_COLOR_MAX_POINT: '#DADBDC',
  MIN_COLOR_CURRENT_FAIL: '#FF9C00',
  MIN_COLOR_CURRENT_PASS: '#A6D950',
  MIN_COLOR_TARGET: '#669FFE',
  MIN_COLOR_MAX_POINT: '#B2B6BC',
  DEFAULT_COLOR: '#3A4464'
}

export default class RadialKPIGradientConfig {
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
    let maxValue = values[maxIndex] || 0
    let max = Math.max(maxValue, target, current) || 0
    let maxPoint = max === 0 ? max + 1 : max

    const formatValue = (value) => {
      return formatObject.prefix + formatFn(value, formatObject.formatType, formatObject.formatString) + formatObject.suffix
    }

    return {
      data: [
        {
          label: 'Current_Value',
          value: current,
          formatValue: formatValue(current),
          color: current >= target
            ? { min: COLOR.MIN_COLOR_CURRENT_PASS, max: COLOR.MAX_COLOR_CURRENT_PASS }
            : { min: COLOR.MIN_COLOR_CURRENT_FAIL, max: COLOR.MAX_COLOR_CURRENT_FAIL }
        },
        {
          label: 'Target_Value',
          formatValue: formatValue(target),
          value: target,
          color: { min: COLOR.MIN_COLOR_TARGET, max: COLOR.MAX_COLOR_TARGET }
        },
        {
          label: 'Max_Value',
          formatValue: formatValue(maxValue),
          value: maxValue,
          color: { min: COLOR.MIN_COLOR_MAX_POINT, max: COLOR.MAX_COLOR_MAX_POINT }
        }
      ],
      config: {
        background: themeStyles.mainColor,
        size: {
          x: parseInt(options.width),
          y: parseInt(options.height) - 80
        },
        angle: {
          max: 130,
          min: -130
        },
        radius: {
          padding: 4,
          inner: 85,
          outer: 100,
          corner: 15 / 2
        },
        max: {
          label: 'Max',
          value: maxPoint,
          color: COLOR.DEFAULT_COLOR
        },
        needle: {
          pointValue: (current / maxPoint) * 100 / 100,
          length: 115,
          color: current >= target ? COLOR.MAX_COLOR_CURRENT_PASS : COLOR.MAX_COLOR_CURRENT_FAIL
        }
      }
    }
  }

  drawChart(id, columns, values, formatObject, formatFn, options) {
    // get config
    let chartConfig = this.getConfig(id, columns, values, formatObject, formatFn, options)
    // draw chart
    KPIGradient
      .renderRadialKPI(
        `#${id}`,
        { ...chartConfig }
      )
  }
}
