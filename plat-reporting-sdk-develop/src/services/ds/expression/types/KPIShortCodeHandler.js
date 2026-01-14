import { AbtractShortcodeHandler } from '@/services/ds/expression/types/AbtractShortcodeHandler'
import { generateIdIfNotExist } from '@/utils/configUtil'
import { DsQueryExecService } from '@/services/ds/expression/DsQueryExec'
import { DsQueryExpr } from 'plat-expr-sdk'
import dsFormatManager, { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import BarKPIConfig from '@/services/ds/expression/chartConfig/BarKPIConfig'
import get from 'lodash/get'
import * as d3 from 'd3'
import RadialKPIGradientConfig from '@/services/ds/expression/chartConfig/RadialKPIGradientConfig'
import RadialKPIConfig from '@/services/ds/expression/chartConfig/RadialKPIConfig'
import { BarKPIGradientConfig } from '@/services/ds/expression/chartConfig/BarKPIGradientConfig'
import BarKPIPreciseConfig from '@/services/ds/expression/chartConfig/BarKPIPreciseConfig'

const VALUE_TYPE = {
  HALF_EXPRESSION: 'half_expression',
  FULL_EXPRESSION: 'full_expression',
  NUMBER: 'number'
}

const CHART_TYPE = {
  RADIAL: 'radial',
  BAR: 'bar'
}

export class KPIShortCodeHandler extends AbtractShortcodeHandler {
  /**
   * Declare callback function
   *  @param {Object} parsedShortcode: shortCode result
   *  @param {Object} config: config of element HTML
   * **/
  async evalFormat(parsedShortcode, config) {
    const attributes = get(parsedShortcode, 'attributes', {})
    const {
      width = 500,
      height = 500,
      prefix = '',
      suffix = '',
      'goal-legend': goalLegend = 'Goal',
      'current-legend': currentLegend = 'Current',
      'target-legend': targetLegend = 'Target',
      'class-css': classCss = '',
      'version': version = '2',
      'chart-type': chartType = CHART_TYPE.RADIAL,
      'format-type': formatType = FORMAT_DATA_TYPES.NUMERIC,
      'format-string': formatString = '',
      'format-tooltip': formatToolTip = '',
      'percent-number': percentNumber = 'on'
    } = attributes

    // throw error if chartType is invalid
    if (!Object.values(CHART_TYPE).includes(chartType)) {
      let typesSupported = Object.values(CHART_TYPE).join(', ')
      throw new Error(`Invalid type of kpi shortcode. Support only ${typesSupported}. Current is ${chartType}`)
    }

    const { dataSource, filter, timezone } = config
    const shortCode = get(parsedShortcode, 'shortCode', '')
    const dataExpression = this.buildExpressionData(attributes)
    // get data from query server
    const dataServer = await this.getDataQueryFromExpression(
      dataExpression,
      dataSource,
      {filter: get(filter, 'base.config.query'), timezone: get(timezone, 'utc')}
    )
    // get data from query server
    const dataLocal = this.getDataQueryFromLocal(dataExpression)
    // merge 2 data sources
    const mergeData = {
      cols: [...dataServer.cols, ...dataLocal.cols],
      rows: [[...(dataServer.rows[0] || []), ...(dataLocal.rows[0] || [])]]
    }
    const configShortCode = {
      chartType,
      shortCode,
      formatObject: { formatString, formatType, formatToolTip, prefix, suffix },
      value: mergeData.rows[0] || [],
      columns: mergeData.cols,
      options: { width, height, classCss, version, legend: { goal: goalLegend, target: targetLegend, current: currentLegend }, percentNumber }
    }
    return configShortCode
  }

  /**
   * Format value in expression
   * **/
  format(value, formatType, formatString) {
    if (!value && value !== 0) return ''
    if (formatString && !formatType) return value
    switch (formatType) {
      case FORMAT_DATA_TYPES.NUMERIC: {
        return d3.format(formatString || '.2f')(value)
      }
      case FORMAT_DATA_TYPES.TEMPORAL: {
        let formatObj = {
          type: FORMAT_DATA_TYPES.TEMPORAL,
          config: {
            format: formatString
          }
        }
        return dsFormatManager.create(formatObj, true)(value)
      }
      case FORMAT_DATA_TYPES.SEGMENTS:
        // current do not do anything
        return value
      default: {
        console.error('Invalid format type. Solid Chart only support segment and numeric format type. Current format type is "' + formatType + '"')
        return value
      }
    }
  }

  /**
   *  get data query from expression
   *  @param {Object} itemOfEvalData: item of data of evalFormat function
   *  @param {string} parsingContent: template short code
   **/
  replaceShortcode(itemOfEvalData, parsingContent) {
    generateIdIfNotExist(itemOfEvalData)
    let {options} = itemOfEvalData
    let chartContainer = parsingContent
      .replace(itemOfEvalData.shortCode, `<div class="${options.classCss}" style="width: ${options.width}px; height: ${options.height}px" id="${this.getChartId(itemOfEvalData.id)}"></div>`)
    return {
      data: itemOfEvalData,
      content: chartContainer
    }
  }

  /**
   * this callback is building solid chart
   * @param {Object} data: must contain id which was generate by uuidv4
   * **/
  callback(data) {
    let {columns, chartType, value, id = '', formatObject, options} = data
    this.getChartInstance(chartType, options.version).drawChart(this.getChartId(id), columns, value, formatObject, this.format, options)
  }

  getChartId(id) {
    return `cbpo_shortcode_handler_html_editor_${id}`
  }

  getChartInstance(chartType, version) {
    switch (true) {
      // version default
      case chartType === CHART_TYPE.RADIAL && parseInt(version) === 1: return new RadialKPIConfig()
      case chartType === CHART_TYPE.BAR && parseInt(version) === 1: return new BarKPIConfig()
      // version gradient
      case chartType === CHART_TYPE.RADIAL && parseInt(version) === 2: return new RadialKPIGradientConfig()
      case chartType === CHART_TYPE.BAR && parseInt(version) === 2: return new BarKPIGradientConfig()
      // version precise
      case chartType === CHART_TYPE.BAR && version === 'precise': return new BarKPIPreciseConfig()
    }
  }

  /**
   *  get data query from expression
   *  @param {Array} dataExpression: values which were parsed from buildExpressionData()
   *  @param {string} dataSource: data source id
   *  @param {Object} additionalConfig: additional timezone and filters
   **/
  async getDataQueryFromExpression(dataExpression, dataSource, additionalConfig) {
    const emptyData = { cols: [], rows: [] }
    const { filter = [], timezone = null } = additionalConfig
    const stringExpr = dataExpression
      .filter(expObj => [VALUE_TYPE.FULL_EXPRESSION, VALUE_TYPE.HALF_EXPRESSION].includes(expObj.type))
      .map(expObj => expObj.value)
      .join(',')
    if (!stringExpr) return emptyData
    try {
      const dsQueryExec = new DsQueryExecService(filter, timezone)
      const dsQueryExpr = new DsQueryExpr(dsQueryExec)
      return await dsQueryExpr.eval(dataSource, stringExpr)
    } catch (err) {
      console.error(err)
      // return default result
      return emptyData
    }
  }

  /**
   *  get data query from expression
   *  @param {Array} dataExpression: values which were parsed from buildExpressionData()
   **/
  getDataQueryFromLocal(dataExpression) {
    const data = dataExpression.filter(expObj => expObj.type === VALUE_TYPE.NUMBER)
    return {
      cols: data.map(dt => ({ type: 'number', name: dt.columnName, alias: dt.columnName, column: dt.columnName })),
      rows: [data.map(dt => dt.value)]
    }
  }

  // Build expression for all data value, min, max into same
  buildExpressionData(attributes) {
    return Object
      .keys(attributes)
      .filter(key => ['target', 'current', 'min', 'max'].includes(key))
      .map(key => {
        return this.getExpressionFromAttributeValue(attributes[key], key)
      })
  }

  // Check type of Expression and return suitable value
  getExpressionFromAttributeValue(value, columnName) {
    let fullExp = /^{(.*?)}$/
    let resultFullExp = fullExp.exec(value)
    if (resultFullExp) {
      return {
        type: VALUE_TYPE.FULL_EXPRESSION,
        columnName,
        value: `${resultFullExp[1].trim()} as ${columnName}`
      }
    } else {
      return {
        type: VALUE_TYPE.NUMBER,
        columnName,
        value: isNaN(value) ? value : Number.parseFloat(value)
      }
    }
  }

  // parse expression
  getIDsFn(parsedExpr) {
    if ((parsedExpr.type === 'exec' || parsedExpr.type === 'count') && parsedExpr.dv) {
      return [parsedExpr.dv]
    }
    if (parsedExpr.type === 'combined') {
      const queries = parsedExpr.queries || []
      const dvs = queries.map((query) => query.dv)
      return [...dvs]
    }
    return []
  }

  // get datasource IDs
  getDataSourceIDs(shortCode) {
    let dataSources = []
    const dataExpression = this.buildExpressionData(shortCode.attributes)
    if (dataExpression && dataExpression.length) {
      for (let index = 0; index < dataExpression.length; index++) {
        try {
          const expr = dataExpression[index]
          if (expr.type !== 'full_expression') continue
          const parsedData = DsQueryExpr.parse(expr.value)
          if (!get(parsedData, 'parsedExprs', []).length) continue
          for (let i = 0; i < parsedData.parsedExprs.length; i++) {
            const parsedExpr = parsedData.parsedExprs[i] || {}
            const ids = this.getIDsFn(parsedExpr)
            dataSources = [...dataSources, ...ids]
          }
        } catch (err) {
          console.log('Expression is invalid!')
        }
      }
    }
    return dataSources
  }
}
