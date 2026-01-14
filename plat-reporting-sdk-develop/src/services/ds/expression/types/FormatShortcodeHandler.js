import { DsQueryExecService } from '@/services/ds/expression/DsQueryExec'
import { DsQueryExpr } from 'plat-expr-sdk'
import { AbtractShortcodeHandler } from '@/services/ds/expression/types/AbtractShortcodeHandler'
import { StaticExpression } from 'plat-sdk'
import { Parser } from 'expr-eval'
import dsFormatManager, { FORMAT_DATA_TYPES, getDefaultFormatConfigBaseOnFormatType } from '@/services/dataFormatManager'
import * as d3 from 'd3'
import get from 'lodash/get'
import isObject from 'lodash/isObject'
import defaultsDeep from 'lodash/defaultsDeep'
import cloneDeep from 'lodash/cloneDeep'
import isNumber from 'lodash/isNumber'
import merge from 'lodash/merge'
import moment from 'moment'
var parser = new Parser()

/**
 *
 * **/
export class FormatShortcodeHandler extends AbtractShortcodeHandler {
  evalBySdk (expression) {
    return StaticExpression.eval(expression)
  }

  async evalByExpr (expression, dsId, filter = {}, timezone = '') {
    const dsQueryExec = new DsQueryExecService(filter, timezone)
    const dsQueryExpr = new DsQueryExpr(dsQueryExec)
    const evaluated = await dsQueryExpr.eval(dsId, expression)
    return get(evaluated, 'rows[0][0]', 0)
  }

  async evalFormat (parsedShortcode, config) {
    const shortCode = get(parsedShortcode, 'shortCode', '')
    const dataExpr = get(parsedShortcode, 'attributes.expression', '')
    const value = get(parsedShortcode, 'attributes.value', '')
    const formatType = get(parsedShortcode, 'attributes.type', '')
    const colorStyle = get(parsedShortcode, 'attributes.color', '')
    const replaceInvalidValue = get(parsedShortcode, 'attributes.replace_invalid_value')
    try {
      let evaluatedValue = ''
      if (value) {
        evaluatedValue = value
      } else {
        if (StaticExpression.isValid(dataExpr)) {
          evaluatedValue = this.evalBySdk(dataExpr)
        } else {
          const tableFilter = config.filter || {}
          evaluatedValue = await this.evalByExpr(dataExpr, config.dataSource, tableFilter, get(config, 'timezone.utc'))
        }
      }
      if ([Infinity, NaN].includes(evaluatedValue) && replaceInvalidValue) evaluatedValue = Number.parseInt(replaceInvalidValue)
      // exec format
      let formatData = null
      if (evaluatedValue) {
        formatData = this.formatFn(get(parsedShortcode, 'attributes', {}), evaluatedValue)
      }
      return {
        shortCode,
        value: isNumber(formatData) ? formatData : formatData || evaluatedValue,
        color: this.getColor(colorStyle, formatType, evaluatedValue),
        prefix: get(parsedShortcode, 'attributes.prefix', ''),
        suffix: get(parsedShortcode, 'attributes.suffix', '')
      }
    } catch (err) { // catch is needed
      console.error(err)
      return { shortCode, value: '#Error', color: '' }
    }
  }

  getColor (colorAttr, typeAttr, value) {
    let color = ''
    if (!colorAttr) return ''
    switch (typeAttr) {
      case FORMAT_DATA_TYPES.TEMPORAL:
        value = moment(value).format('YYYY-MM-DD')
        break
    }
    const parsedColor = JSON.parse(colorAttr)
    for (let prop in parsedColor) {
      if (parsedColor[prop]) {
        const colorCondition = parsedColor[prop].replace('value', value)
        if (parser.evaluate(colorCondition)) color = prop
      }
    }
    return color
  }

  // Build to platform format structure
  buildFormatObject (attributes) {
    const formatType = attributes.type || get(attributes, 'format.type', '')
    const defaultConfig = getDefaultFormatConfigBaseOnFormatType(formatType)
    const formatConfig = cloneDeep(attributes).format || {}
    if (isObject(formatConfig)) return defaultsDeep(formatConfig, {config: defaultConfig})
    let formatObj = { type: formatType, config: defaultConfig }
    // check formatConfig string
    if (formatType === FORMAT_DATA_TYPES.TEMPORAL) {
      formatObj.config.format = formatConfig
    } else if (formatType === FORMAT_DATA_TYPES.SEGMENTS) {
      // Format attribute
      const parsedFormatStr = formatConfig ? JSON.parse(formatConfig) : {}
      if (isObject(parsedFormatStr)) merge(formatObj, parsedFormatStr)
      // Segments attribute
      for (let attr in attributes) {
        if (attributes.hasOwnProperty(attr)) {
          const segmentRegrex = /segment\d$/i
          if (segmentRegrex.test(attr)) {
            const matchedSegment = attr.match(/\d$/)
            if (attributes[attr] && matchedSegment && matchedSegment.length) {
              const segmentIndex = +matchedSegment[0] - 1
              const segment = {...formatObj.config.segments[segmentIndex]}
              formatObj.config.segments[segmentIndex] = merge(segment, JSON.parse(attributes[attr]))
            }
          }
        }
      }
    }
    return formatObj
  }

  /**
   * Format data with format object config
   * @param {object} attributes: config contains format config, format config is in platform format structure
   * @param {any} value: data to format
   */
  formatFn (attributes, value) {
    const formatType = attributes.type || get(attributes, 'format.type', '')
    if (!formatType) return value
    let formatted = null
    const formatConfig = attributes.format || {}
    // format value if it is d3 format string
    if (formatType === FORMAT_DATA_TYPES.NUMERIC && !isObject(formatConfig)) {
      try {
        formatted = d3.format(formatConfig)(value)
      } catch {
        formatted = value
      }
      return formatted
    }
    // format value if it is another case
    // call buildFormatObject
    const formatObj = this.buildFormatObject(attributes)
    // exec in dataFormatManager
    formatted = dsFormatManager.create(formatObj, true)(value)
    return formatted
  }

  replaceShortcode(itemOfEvalData, parsingContent) {
    let content = parsingContent
    const fullContent = `${itemOfEvalData.prefix || ''}${itemOfEvalData.value}${itemOfEvalData.suffix || ''}`
    content = content.replace(itemOfEvalData.shortCode, `<span style="color: ${itemOfEvalData.color}">${fullContent}</span>`)
    return {
      data: itemOfEvalData,
      content
    }
  }

  callback() {
    // Do nothing
  }

  // parse expression
  parseExpression(expression) {
    let result = []
    const getIDsFn = (parsedExpr) => {
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

    const parsedData = DsQueryExpr.parse(expression)
    if (!get(parsedData, 'parsedExprs', []).length) return []
    for (let i = 0; i < parsedData.parsedExprs.length; i++) {
      const ids = getIDsFn(parsedData.parsedExprs[i] || {})
      result = [...result, ...ids]
    }
    return result
  }

  // get datasource IDs
  getDataSourceIDs(shortCode) {
    const expression = get(shortCode, 'attributes.expression')
    if (!expression) return []
    let dataSources = []
    try {
      dataSources = this.parseExpression(expression)
    } catch (err) {
      console.log('Expression is invalid!')
    }
    return dataSources
  }
}
