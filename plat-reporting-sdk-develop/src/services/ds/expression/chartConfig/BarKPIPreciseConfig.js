import KPIPreciseChart from '@/services/ds/expression/cbpoChartLibs/KPIPrecise'
import { getStyle } from '@/utils/chartUtil'
import findIndex from 'lodash/findIndex'

const COLOR = {
  TARGET_COLOR: '#91E4AB',
  CURRENT_COLOR: '#52C0E1',
  GOAL_COLOR: '#D0DDE7',
  PERCENT_COLOR: '#080E2C'
}

export default class BarKPIPreciseConfig {
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
    let maxPoint = Math.max(current, target, max)
    const roundValue = (value) => value.toFixed(2)
    const percentageWithTarget = roundValue(((current - target) / target * 100) || 0)
    const percentageWithGoal = max && Math.abs(roundValue(100 - ((max - current) / max * 100)))

    const formatValue = (value) => formatObject.prefix + formatFn(value, formatObject.formatType, formatObject.formatString) + formatObject.suffix
    const availablePosition = {
      top: true,
      left: true,
      bottom: true
    }
    const calcPosition = (value) => {
      const compareValues = [current, target, max].filter(v => v !== null)
      let key = 'bottom'
      if (value === Math.max(...compareValues) && availablePosition.left) {
        key = 'left'
      } else if (value === Math.min(...compareValues) && availablePosition.top) {
        key = 'top'
      }
      availablePosition[key] = false
      return key
    }

    return {
      data: [
        {
          label: 'Max_Value',
          formatLabel: options && options.legend ? options.legend.goal : 'Max',
          formatValue: max ? formatValue(max) : null,
          value: max,
          position: calcPosition(max),
          color: COLOR.GOAL_COLOR
        },
        {
          label: 'Target_Value',
          formatLabel: options && options.legend ? options.legend.target : 'Target',
          formatValue: formatValue(target),
          value: target,
          position: calcPosition(target),
          color: COLOR.TARGET_COLOR
        },
        {
          label: 'Current_Value',
          formatLabel: options && options.legend ? options.legend.current : 'Current',
          value: current,
          formatValue: formatValue(current),
          position: calcPosition(current),
          color: COLOR.CURRENT_COLOR
        }
      ],
      config: {
        background: themeStyles.mainColor,
        point: {
          enabled: options.percentNumber === 'on',
          label: `${percentageWithTarget}%` + (max ? ` (${percentageWithGoal}% Goal)` : ''),
          color: COLOR.PERCENT_COLOR,
          direction: current >= target ? 'top' : 'bottom',
          targetPoint: current
        },
        bar: {
          padding: 50,
          height: 15
        },
        max: {
          value: maxPoint,
          color: COLOR.GOAL_COLOR
        },
        legendColor: COLOR.PERCENT_COLOR,
        size: {
          x: parseInt(options.width),
          y: Math.max(parseInt(options.height), 160)
        }
      }
    }
  }

  drawChart(id, columns, values, formatObject, formatFn, options) {
    // get config
    let chartConfig = this.getConfig(id, columns, values, formatObject, formatFn, options)

    // draw chart
    KPIPreciseChart
      .renderBarKPI(
        `#${id}`,
        {...chartConfig}
      )
  }
}
