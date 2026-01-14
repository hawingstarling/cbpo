import segmentsFormatConfig from './segmentsFormatConfig'
import dataFormatManager from '@/services/dataFormatManager'
import _ from 'lodash'
/**
 * @param {Object} formatConfig object format config
 */
const templateHTML = `<i class="{iconClass}" style="{iconStyle}"></i>`
const CONDITION = {
  eq: '==',
  lt: '<',
  gt: '>',
  lte: '<=',
  gte: '>='
}
export default (formatConfig, isHtml) => {
  _.defaults(formatConfig, segmentsFormatConfig)
  const {segmentType, segments, value: {format}} = formatConfig
  const DATA_SEGMENTS = {
    custom: segments,
    trend: segmentsFormatConfig.segments
  }
  const getLabelSegments = (dataIcon, value) => {
    value = `${dataFormatManager.format(value, format, true)}`
    const {iconClass, iconStyle} = dataIcon
    let styleStr = Object.keys(iconStyle).reduce((str, key) => (str += `${key}:${iconStyle[key]}; `), '')
    const icon = templateHTML.replace('{iconClass}', iconClass).replace('{iconStyle}', styleStr)
    return `${icon} ${value}`
  }

  const funEval = (str) => {
    // eslint-disable-next-line no-eval
    return eval(str)
  }

  const buildCondition = (obj, value) => {
    let keys = Object.keys(obj)
    return keys.reduce((str, key, index) => {
      if (CONDITION[key] && !_.isNil(obj[key])) {
        str += `${value} ${CONDITION[key]} ${obj[key]} ${((index === keys.length - 1) ? '' : '&& ')}`
      }
      return str
    }, '')
  }

  const formatSegments = (value) => {
    let labelSegments = `${dataFormatManager.format(value, format, true)}`
    DATA_SEGMENTS[segmentType].forEach((item) => {
      let objCondition = {}
      Object.keys(item.conditions).forEach(k => (objCondition[k] = item.conditions[k]))
      let conditionStr = buildCondition(objCondition, value)
      if (funEval(conditionStr)) {
        labelSegments = getLabelSegments(item, value)
      }
    })
    return labelSegments
  }
  const formatNum = (value) => {
    value = `${dataFormatManager.format(value, format, false)}`
    return value
  }
  return (value) => {
    return isHtml ? formatSegments(value) : formatNum(value)
  }
}
