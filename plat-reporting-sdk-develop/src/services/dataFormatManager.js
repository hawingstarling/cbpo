import _ from 'lodash'
import moment from 'moment'

import { DEFAULT_INT_FORMAT, DEFAULT_NUMERIC_FORMAT } from './dataFormats/numericFormatConfig'
import currencyFormatFactory from './dataFormats/currencyFormatFactory'
import temporalFormatConfig from './dataFormats/temporalFormatConfig'

import noFormat from './dataFormats/noFormat'
import namedFormatFactory from './dataFormats/namedFormatFactory'
import numericFormatFactory from './dataFormats/numericFormatFactory'
import linkFormatFactory from './dataFormats/linkFormatFactory'
import commonFormatFactory from './dataFormats/commonFormatFactory'
import booleanFormatFactory from './dataFormats/booleanFormatFactory'
import temporalFormatFactory from './dataFormats/temporalFormatFactory'
import progressFormatFactory from './dataFormats/progressFormatFactory'
import starsFormatFactory from './dataFormats/starsFormatFactory'
import segmentsFormatFactory from './dataFormats/segmentsFormatFactory'
import overrideFormatFactory from '@/services/dataFormats/overrideFormatFactory'

import {getAggregationDataTypeStr, DataTypeUtil, isThisFormatSupportedByThisAggr} from './ds/data/DataTypes'
import DEFAULT_CURRENCY_FORMAT from '@/services/dataFormats/currencyFormatConfig'
import DEFAULT_LINK_FORMAT from '@/services/dataFormats/linkFormatConfig'
import DEFAULT_BOOLEAN_FORMAT from '@/services/dataFormats/booleanFormatConfig'
import DEFAULT_TEMPORAL_FORMAT from '@/services/dataFormats/temporalFormatConfig'
import DEFAULT_PROGRESS_FORMAT from '@/services/dataFormats/progressFormatConfig'
import DEFAULT_SEGMENT_FORMAT from '@/services/dataFormats/segmentsFormatConfig'
import DEFAULT_STAR_FORMAT from '@/services/dataFormats/starsFormatConfig'
import DEFAULT_OVERRIDE_FORMAT from '@/services/dataFormats/overrideFormatConfig'
import textFormatFactory from '@/services/dataFormats/textFormatFactory'
import customFormatFactory from '@/services/dataFormats/customFormatFactory'

export const FORMAT_DATA_TYPES = {
  TEXT: 'text',
  INT: 'int',
  NUMERIC: 'numeric',
  CURRENCY: 'currency',
  LINK: 'link',
  BOOLEAN: 'bool',
  TEMPORAL: 'temporal',
  PROGRESS: 'progress',
  STARS: 'stars',
  SEGMENTS: 'segments',
  OVERRIDE: 'override',
  CUSTOM: 'custom'
}

export const getDefaultFormatConfigBaseOnFormatType = (type) => {
  switch (type) {
    case FORMAT_DATA_TYPES.NUMERIC: {
      return _.cloneDeep(DEFAULT_NUMERIC_FORMAT)
    }
    case FORMAT_DATA_TYPES.CURRENCY: {
      return _.cloneDeep(DEFAULT_CURRENCY_FORMAT)
    }
    case FORMAT_DATA_TYPES.LINK: {
      return _.cloneDeep(DEFAULT_LINK_FORMAT)
    }
    case FORMAT_DATA_TYPES.BOOLEAN: {
      return _.cloneDeep(DEFAULT_BOOLEAN_FORMAT)
    }
    case FORMAT_DATA_TYPES.TEMPORAL: {
      return _.cloneDeep(DEFAULT_TEMPORAL_FORMAT)
    }
    case FORMAT_DATA_TYPES.PROGRESS: {
      return _.cloneDeep(DEFAULT_PROGRESS_FORMAT)
    }
    case FORMAT_DATA_TYPES.SEGMENTS: {
      return _.cloneDeep(DEFAULT_SEGMENT_FORMAT)
    }
    case FORMAT_DATA_TYPES.STARS: {
      return _.cloneDeep(DEFAULT_STAR_FORMAT)
    }
    case FORMAT_DATA_TYPES.OVERRIDE: {
      return _.cloneDeep(DEFAULT_OVERRIDE_FORMAT)
    }
    default: {
      return {}
    }
  }
}

const getMomentUnitFromBinUnit = (unit) => {
  switch (unit) {
    case 'Y':
      return 'year'
    case 'Q':
      return 'quarter'
    case 'M':
      return 'month'
    case 'W':
      return 'week'
    case 'd':
      return 'day'
    case 'm':
      return 'minute'
    default:
      return ''
  }
}
const formatLabel = (min, max, unit, width, formatObj, formatFunction) => {
  if (formatObj.type === 'temporal') {
    max = moment(max).add(-1, getMomentUnitFromBinUnit(unit)).toDate()
  }
  return width > 1
    ? formatFunction(min) + ' - ' + formatFunction(max)
    : formatFunction(min)
}

// eslint-disable-next-line no-unused-vars
const DEFAULT_FORMATS = {
  [FORMAT_DATA_TYPES.TEXT]: null,
  [FORMAT_DATA_TYPES.INT]: _.defaultsDeep({}, DEFAULT_INT_FORMAT),
  [FORMAT_DATA_TYPES.NUMERIC]: _.defaultsDeep({}, DEFAULT_NUMERIC_FORMAT),
  [FORMAT_DATA_TYPES.TEMPORAL]: _.defaultsDeep({}, temporalFormatConfig)
}

/**
 * This create format method and return a function
 * @param {Object} formatObj Mix format object
 * @return {function} That accepts (value, mode)
 */
const createBasicFormatFunction = (formatObj, isHtml, isFormat) => {
  // String object => format by a global function at window scope
  if (_.isString(formatObj)) {
    return namedFormatFactory(formatObj)
  }

  // Not an object => invalid => no format
  if (!_.isObject(formatObj) || !isFormat) {
    return noFormat
  }

  // Make default config object
  _.defaultsDeep(formatObj, {config: {}})
  switch (formatObj.type) {
    case FORMAT_DATA_TYPES.TEXT:
      return textFormatFactory(formatObj.config)
    case FORMAT_DATA_TYPES.NUMERIC:
      return numericFormatFactory(formatObj.config)
    case FORMAT_DATA_TYPES.CURRENCY:
      return currencyFormatFactory(formatObj.config)
    case FORMAT_DATA_TYPES.LINK:
      return linkFormatFactory(formatObj.config, isHtml)
    case FORMAT_DATA_TYPES.BOOLEAN:
      return booleanFormatFactory(formatObj.config, isHtml)
    case FORMAT_DATA_TYPES.TEMPORAL:
      return temporalFormatFactory(formatObj.config)
    case FORMAT_DATA_TYPES.PROGRESS:
      return progressFormatFactory(formatObj.config, isHtml)
    case FORMAT_DATA_TYPES.STARS:
      return starsFormatFactory(formatObj.config, isHtml)
    case FORMAT_DATA_TYPES.SEGMENTS:
      return segmentsFormatFactory(formatObj.config, isHtml)
    case FORMAT_DATA_TYPES.OVERRIDE:
      return overrideFormatFactory(formatObj.config)
    case FORMAT_DATA_TYPES.CUSTOM:
      return customFormatFactory(formatObj.config)
    default:
      console.error(`Format ${formatObj.type} has not been supported`)
  }

  // TODO let's build it
  return noFormat
}

/**
 * Consider default aggr format
 * @param {string} dataType Original column data type
 * @param {Object} formatObj Function of the base format
 * @param {string} aggrType Aggregation type (sum, min, max, etc)
 * @param {*} aggrFormats Map object of aggrFormat, e.g integer, numeric, temporal. If no aggrFormats found, it uses the default ones.
 * @return {Object} format object
 */
const considerAggrFormatObject = (dataType, formatObj, aggrType, aggrFormats) => {
  let aggrDataType = getAggregationDataTypeStr(dataType, aggrType)
  if (DataTypeUtil.isSame(dataType, aggrDataType)) {
    return !_.isEmpty(aggrFormats[aggrDataType]) ? aggrFormats[aggrDataType] : formatObj
  }
  return aggrFormats[aggrDataType]
}

class DataFormatManager {
  /**
   * Create format function based on format configuration and render option.
   * @param {Object} formatObj Format config object
   * @param {boolean} isHtml Render html
   */
  create (formatObj, isHtml) {
    let basicFormat = createBasicFormatFunction(formatObj, isHtml, true)
    let commonConfig = _.isObject(formatObj) && _.isObject(formatObj.common) ? formatObj.common : {}
    return commonFormatFactory(commonConfig, basicFormat, isHtml)
  }
  /**
   * Create format function based on format configuration and render option.
   * @param {string} dataType Original column data type
   * @param {Object} formatObj Format for the dataType
   * @param {string} aggrType Aggregation type (sum, min, max, avg, count, distinct, concat)
   * @param {*} aggrFormats Map object of aggrFormat, e.g integer, numeric, temporal. If no aggrFormats found, it uses the default ones.
   * @param {*} isHtml Render html
   */
  createAggrFormat (dataType, formatObj, aggrType, aggrFormats, isHtml) {
    let pickedFormatObj = considerAggrFormatObject(dataType, formatObj, aggrType, aggrFormats)
    let isFormat = _.isObject(formatObj) && isThisFormatSupportedByThisAggr(formatObj.type, aggrType)
    let pickedFormat = createBasicFormatFunction(pickedFormatObj, isHtml, isFormat)
    let pickedCommonConfig = _.isObject(pickedFormatObj) && _.isObject(pickedFormatObj.common) ? pickedFormatObj.common : {}
    return commonFormatFactory(pickedCommonConfig, pickedFormat, isHtml)
  }
  format (value, formatObj, isHtml) {
    // TODO avoid creating function every format call
    return this.create(formatObj, isHtml)(value)
  }
  formatAggr (value, dataType, formatObj, aggrType, aggrFormats, isHtml) {
    return this.createAggrFormat(dataType, formatObj, aggrType, aggrFormats, isHtml)(value)
  }
  formatBin (value, formatObj, isHtml) {
    if (formatObj) {
      let binFormat = _.cloneDeep(formatObj)
      if (formatObj.type === 'temporal' && getMomentUnitFromBinUnit(value.unit)) {
        binFormat.config.format = binFormat.config.options[getMomentUnitFromBinUnit(value.unit)]
      }
      let formatFunction = this.create(binFormat, isHtml)
      if (_.isObject(value) && value.bin) {
        if (formatObj && formatObj.type && formatObj.type !== 'datetime') {
          return formatLabel(value.min, value.max, value.unit, value.width, formatObj, formatFunction)
        } else {
          return value.label
        }
      } else {
        return formatFunction(value)
      }
    }
    // aggregation bin is not an object
    return _.isObject(value) && value.bin ? value.label : value
  }
}

export default new DataFormatManager()
