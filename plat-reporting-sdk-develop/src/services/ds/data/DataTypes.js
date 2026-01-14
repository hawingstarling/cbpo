import _ from 'lodash'

export const COUNT_AGG = {aggregation: 'count', label: 'Count', abbr: 'Cnt'}
export const DISTINCT_AGG = {aggregation: 'distinct', label: 'Distinct', abbr: 'Dist'}
export const SUM_AGG = {aggregation: 'sum', label: 'Sum'}
export const AVG_AGG = {aggregation: 'avg', label: 'Average', abbr: 'Avg'}
export const MIN_AGG = {aggregation: 'min', label: 'Min', abbr: 'Min'}
export const MAX_AGG = {aggregation: 'max', label: 'Max', abbr: 'Max'}
export const CONCAT_AGG = {aggregation: 'concat', label: 'Concat', abbr: 'Cat'}

export const DATA_AGGREGATIONS = [
  COUNT_AGG,
  DISTINCT_AGG,
  SUM_AGG,
  AVG_AGG,
  MIN_AGG,
  MAX_AGG,
  CONCAT_AGG
]

export const MAP_DATA_AGGREGATIONS = _.keyBy(DATA_AGGREGATIONS, 'aggregation')

export const TEXT_TYPE = {
  type: 'text',
  defaultAggregation: COUNT_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG, MIN_AGG, MAX_AGG, CONCAT_AGG]
}

export const INT_TYPE = {
  type: 'int',
  defaultAggregation: SUM_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG, SUM_AGG, AVG_AGG, MIN_AGG, MAX_AGG]
}

export const NUM_TYPE = {
  type: 'num',
  defaultAggregation: SUM_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG, SUM_AGG, AVG_AGG, MIN_AGG, MAX_AGG]
}

export const BOOL_TYPE = {
  type: 'bool',
  defaultAggregation: COUNT_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG]
}

export const BIN_TYPE = {
  type: 'bin',
  defaultAggregation: COUNT_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG, MIN_AGG, MAX_AGG]
}

export const TEMPORAL_BIN_TYPE = {
  type: 'temporal_bin',
  defaultAggregation: COUNT_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG, MIN_AGG, MAX_AGG]
}

export const NUMERIC_BIN_TYPE = {
  type: 'numeric_bin',
  defaultAggregation: COUNT_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG, MIN_AGG, MAX_AGG]
}

export const DOC_TYPE = {
  type: 'doc',
  defaultAggregation: COUNT_AGG,
  aggregations: [COUNT_AGG]
}

export const TEMPORAL_TYPE = {
  type: 'temporal',
  defaultAggregation: MAX_AGG,
  aggregations: [COUNT_AGG, DISTINCT_AGG, MIN_AGG, MAX_AGG]
}

export const MAP_OF_DATA_TYPES = {
  // string
  'text': TEXT_TYPE,
  'string': TEXT_TYPE,
  'varchar': TEXT_TYPE,
  'char': TEXT_TYPE,
  // bool
  'boolean': BOOL_TYPE,
  'bool': BOOL_TYPE,
  // integer
  'integer': INT_TYPE,
  'int': INT_TYPE,
  'long': INT_TYPE,
  // numeric
  'num': NUM_TYPE,
  'numeric': NUM_TYPE,
  'number': NUM_TYPE,
  'float': NUM_TYPE,
  'double': NUM_TYPE,
  // binary
  'binary': BIN_TYPE,
  'bin': BIN_TYPE,
  // document
  'doc': DOC_TYPE,
  'document': DOC_TYPE,
  // temporal
  'temporal': TEMPORAL_TYPE,
  'date': TEMPORAL_TYPE,
  'datetime': TEMPORAL_TYPE,
  'time': TEMPORAL_TYPE,
  // bin aggregation type
  'integer_bin': NUMERIC_BIN_TYPE,
  'int_bin': NUMERIC_BIN_TYPE,
  'long_bin': NUMERIC_BIN_TYPE,
  'num_bin': NUMERIC_BIN_TYPE,
  'numeric_bin': NUMERIC_BIN_TYPE,
  'number_bin': NUMERIC_BIN_TYPE,
  'float_bin': NUMERIC_BIN_TYPE,
  'double_bin': NUMERIC_BIN_TYPE,
  'temporal_bin': TEMPORAL_BIN_TYPE,
  'date_bin': TEMPORAL_BIN_TYPE,
  'datetime_bin': TEMPORAL_BIN_TYPE,
  'time_bin': TEMPORAL_BIN_TYPE,
  // null
  'null': TEXT_TYPE
}

export const getDataTypeFromType = (sourceDataType) => {
  let type = MAP_OF_DATA_TYPES[sourceDataType]
  if (!type) {
    console.error(`${sourceDataType} is not valid platform data type`)
    return TEXT_TYPE
  }
  return type
}

export const findNumericAggregations = (sourceDataType) => {
  if (!DataTypeUtil.isNumeric(sourceDataType)) {
    return [COUNT_AGG, DISTINCT_AGG]
  }
  return getDataTypeFromType(sourceDataType).aggregations || []
}

export const getDataAggregationFromType = (aggregationType) => {
  let type = MAP_DATA_AGGREGATIONS[aggregationType]
  if (!type) {
    throw Error(`"${aggregationType}" is not a valid platform aggregation type`)
  }
  return type
}

/**
 * @param {string} formatType Format Type as string
 * @param {string} aggrType Aggr Type as string
 * @return {boolean} true when this is int data
 */
export const isThisFormatSupportedByThisAggr = (formatType, aggrType) => {
  const DATA_TYPE = {
    stars: [AVG_AGG.aggregation, MIN_AGG.aggregation, MAX_AGG.aggregation],
    segments: [AVG_AGG.aggregation, MIN_AGG.aggregation, MAX_AGG.aggregation, SUM_AGG.aggregation]
  }
  if (!DATA_TYPE[formatType]) return true
  return _.includes(DATA_TYPE[formatType], aggrType)
}

export const getDefaultAggregation = (sourceDataType) => {
  return getDataTypeFromType(sourceDataType).defaultAggregation
}

export const getDefaultAggregationsOfDataType = (sourceDataType) => {
  let aggregation = null
  if (!DataTypeUtil.isNumeric(sourceDataType)) {
    aggregation = COUNT_AGG
  } else {
    aggregation = getDefaultAggregation(sourceDataType)
  }
  return aggregation
}

export const getAggregationDataTypeObj = (sourceDataType, aggregationType) => {
  let aggr = getDataAggregationFromType(aggregationType)
  let type = getDataTypeFromType(sourceDataType)
  switch (aggr.aggregation) {
    case COUNT_AGG.aggregation:
    case DISTINCT_AGG.aggregation:
      return INT_TYPE
    case SUM_AGG.aggregation:
      return type.type === INT_TYPE.type ? INT_TYPE : NUM_TYPE
    case AVG_AGG.aggregation:
      return NUM_TYPE
    case MIN_AGG.aggregation:
    case MAX_AGG.aggregation:
      return type
    case CONCAT_AGG.aggregation:
      return TEXT_TYPE
  }
}

export const getBinTypeFromSourceType = (sourceType) => {
  if (!MAP_OF_DATA_TYPES[sourceType]) {
    throw new Error('We do not support bin type for ' + sourceType)
  }
  return MAP_OF_DATA_TYPES[sourceType].type
}

export const getAggregationObjFromAggregationName = (name) => {
  switch (name) {
    case COUNT_AGG.aggregation:
      return COUNT_AGG
    case DISTINCT_AGG.aggregation:
      return DISTINCT_AGG
    case SUM_AGG.aggregation:
      return SUM_AGG
    case AVG_AGG.aggregation:
      return AVG_AGG
    case MIN_AGG.aggregation:
      return MIN_AGG
    case MAX_AGG.aggregation:
      return MAX_AGG
    case CONCAT_AGG.aggregation:
      return COUNT_AGG
    default: {
      throw Error(`There is no aggregation with name ${name}`)
    }
  }
}

export const getAggregationDataTypeStr = (sourceDataType, aggregationType) => {
  return getAggregationDataTypeObj(sourceDataType, aggregationType).type
}

export const calculateAggregationOfAnArrayOfFlatValues = (flatValues, aggregation) => {
  switch (aggregation) {
    case COUNT_AGG.aggregation:
      return flatValues.length
    case DISTINCT_AGG.aggregation:
      return _.keys(_.countBy(flatValues)).length
    case SUM_AGG.aggregation:
      return _.sum(flatValues)
    case AVG_AGG.aggregation:
      return flatValues.length > 0 ? _.sum(flatValues) / flatValues.length : 0
    case MIN_AGG.aggregation:
      return _.min(flatValues)
    case MAX_AGG.aggregation:
      return _.max(flatValues)
    case CONCAT_AGG.aggregation:
      return _.truncate(_.join(flatValues, ', '), {length: 500})
  }
}

const _aggregationInstances = {}
export class AggregationType {
  /**
   * Create aggregation type class.
   * @param {*} aggr Aggregation (count, min, max, avg)
   */
  constructor (aggr) {
    this._aggr = aggr
    this._aggConfig = MAP_DATA_AGGREGATIONS[aggr]
  }
  isText () {
    return this._aggr === CONCAT_AGG.aggregation
  }
  isInt () {
    return this._aggr === COUNT_AGG.aggregation || this._aggr === DISTINCT_AGG.aggregation
  }
  isFloat () {
    return this._aggr === AVG_AGG.aggregation
  }
  static getInstance (aggr) {
    if (!_aggregationInstances[aggr]) {
      _aggregationInstances[aggr] = new AggregationType(aggr)
    }
    return _aggregationInstances[aggr]
  }
}

export class DataTypeUtil {
  /**
   * @param {string} dataType Data type as string
   * @return {boolean} true when this is text data
   */
  static isText (dataType) {
    return getDataTypeFromType(dataType).type === TEXT_TYPE.type
  }
  /**
   * @param {string} dataType Data type as string
   * @return {boolean} true when this is temporal data
   */
  static isTemporal (dataType) {
    return getDataTypeFromType(dataType).type === TEMPORAL_TYPE.type
  }
  /**
   * @param {string} dataType Data type as string
   * @return {boolean} true when this is int data
   */
  static isInt (dataType) {
    return getDataTypeFromType(dataType).type === INT_TYPE.type
  }
  /**
   * @param {string} dataType Data type as string
   * @return {boolean} true when this is numeric data
   */
  static isNumeric (dataType) {
    return getDataTypeFromType(dataType).type === NUM_TYPE.type || DataTypeUtil.isInt(dataType)
  }
  static isSame (dataType1, dataType2) {
    return getDataTypeFromType(dataType1).type === getDataTypeFromType(dataType2).type
  }
  static isNumericBin(dataType) {
    return getDataTypeFromType(dataType).type === NUMERIC_BIN_TYPE.type
  }
  static isTemporalBin(dataType) {
    return getDataTypeFromType(dataType).type === TEMPORAL_BIN_TYPE.type
  }
}

export const SUPPORT_COLUMN_TYPES = {
  STRING: 'string',
  DATE: 'date',
  DATE_TIME: 'datetime',
  BOOLEAN: 'boolean',
  NUM: 'num',
  NUMBER: 'number',
  INT: 'int',
  LONG: 'long',
  FLOAT: 'float',
  DOUBLE: 'double',
  TEXT: 'text'
}
