import {SUPPORT_COLUMN_TYPES} from '@/services/ds/data/DataTypes'

export const SUPPORT_OPERATORS = {
  '==': {
    label: 'Equal',
    value: '=='
  },
  eq: {
    label: 'Equal',
    value: 'eq'
  },
  $eq: {
    label: 'Equal',
    value: '$eq'
  },
  $i_eq: {
    label: 'Equal (ignore case)',
    value: '$i_eq'
  },
  '!=': {
    label: 'Not equal',
    value: '!='
  },
  ne: {
    label: 'Not equal',
    value: 'ne'
  },
  $ne: {
    label: 'Not equal',
    value: '$ne'
  },
  '$i_ne': {
    label: 'Not equal (ignore case)',
    value: '$i_ne'
  },
  '<': {
    label: 'Less than',
    value: '<'
  },
  lt: {
    label: 'Less than',
    value: 'lt'
  },
  $lt: {
    label: 'Less than',
    value: '$lt'
  },
  '>': {
    label: 'Greater than',
    value: '>'
  },
  gt: {
    label: 'Greater than',
    value: 'gt'
  },
  $gt: {
    label: 'Greater than',
    value: '$gt'
  },
  '<=': {
    label: 'Less than or equal',
    value: '<='
  },
  lte: {
    label: 'Less than or equal',
    value: 'lte'
  },
  $lte: {
    label: 'Less than or equal',
    value: '$lte'
  },
  '>=': {
    label: 'Greater than or equal',
    value: '>='
  },
  gte: {
    label: 'Greater than or equal',
    value: 'gte'
  },
  $gte: {
    label: 'Greater than or equal',
    value: '$gte'
  },
  contains: {
    label: 'Contains',
    value: 'contains'
  },
  not_contain: {
    label: 'Not contain',
    value: 'not_contain'
  },
  null: {
    label: 'Is null',
    value: 'null'
  },
  not_null: {
    label: 'Is not null',
    value: 'not_null'
  },
  empty: {
    label: 'Is empty',
    value: 'empty'
  },
  not_empty: {
    label: 'Is not empty',
    value: 'not_empty'
  },
  is_true: {
    label: 'Is true',
    value: 'is_true'
  },
  is_false: {
    label: 'Is false',
    value: 'is_false'
  },
  starts_with: {
    label: 'Starts with',
    value: 'starts_with'
  },
  not_start_with: {
    label: 'Not start with',
    value: 'not_start_with'
  },
  ends_with: {
    label: 'Ends with',
    value: 'ends_with'
  },
  not_end_with: {
    label: 'Not end with',
    value: 'not_end_with'
  },
  in: {
    label: 'In',
    value: 'in'
  },
  not_in: {
    label: 'Not in',
    value: 'not_in'
  },
  in_range: {
    label: 'In range',
    value: 'in_range'
  },
  date_in: {
    label: 'Date in',
    value: 'date_in'
  },
  time_range: {
    label: 'Time range',
    value: 'time_range'
  }
}

export const logicWithoutValue = [
  SUPPORT_OPERATORS.not_null.value,
  SUPPORT_OPERATORS.not_empty.value,
  SUPPORT_OPERATORS.null.value,
  SUPPORT_OPERATORS.empty.value,
  SUPPORT_OPERATORS.is_true.value,
  SUPPORT_OPERATORS.is_false.value
]

export const getConditionBaseOnDataType = (dataType) => {
  switch (dataType) {
    case SUPPORT_COLUMN_TYPES.STRING:
    case SUPPORT_COLUMN_TYPES.TEXT:
      return [
        SUPPORT_OPERATORS.in,
        SUPPORT_OPERATORS.not_in,
        SUPPORT_OPERATORS.$eq,
        SUPPORT_OPERATORS.$i_eq,
        SUPPORT_OPERATORS.$ne,
        SUPPORT_OPERATORS.$i_ne,
        SUPPORT_OPERATORS.contains,
        SUPPORT_OPERATORS.not_contain,
        SUPPORT_OPERATORS.starts_with,
        SUPPORT_OPERATORS.not_start_with,
        SUPPORT_OPERATORS.ends_with,
        SUPPORT_OPERATORS.not_end_with,
        SUPPORT_OPERATORS.not_null,
        SUPPORT_OPERATORS.not_empty,
        SUPPORT_OPERATORS.null,
        SUPPORT_OPERATORS.empty
      ]
    case SUPPORT_COLUMN_TYPES.FLOAT:
    case SUPPORT_COLUMN_TYPES.DOUBLE:
    case SUPPORT_COLUMN_TYPES.INT:
    case SUPPORT_COLUMN_TYPES.NUM:
    case SUPPORT_COLUMN_TYPES.NUMBER:
    case SUPPORT_COLUMN_TYPES.LONG:
      return [
        SUPPORT_OPERATORS.in,
        SUPPORT_OPERATORS.not_in,
        SUPPORT_OPERATORS.in_range,
        SUPPORT_OPERATORS.$eq,
        SUPPORT_OPERATORS.$ne,
        SUPPORT_OPERATORS.$lt,
        SUPPORT_OPERATORS.$lte,
        SUPPORT_OPERATORS.$gt,
        SUPPORT_OPERATORS.$gte,
        SUPPORT_OPERATORS.not_null,
        SUPPORT_OPERATORS.null
      ]
    case SUPPORT_COLUMN_TYPES.BOOLEAN:
      return [
        SUPPORT_OPERATORS.is_false,
        SUPPORT_OPERATORS.is_true,
        SUPPORT_OPERATORS.not_null,
        SUPPORT_OPERATORS.null
      ]
    case SUPPORT_COLUMN_TYPES.DATE:
    case SUPPORT_COLUMN_TYPES.DATE_TIME:
      return [
        SUPPORT_OPERATORS.in_range,
        SUPPORT_OPERATORS.$eq,
        SUPPORT_OPERATORS.$ne,
        SUPPORT_OPERATORS.$lt,
        SUPPORT_OPERATORS.$lte,
        SUPPORT_OPERATORS.$gt,
        SUPPORT_OPERATORS.$gte,
        SUPPORT_OPERATORS.not_null,
        SUPPORT_OPERATORS.null,
        SUPPORT_OPERATORS.date_in,
        SUPPORT_OPERATORS.time_range
      ]
    default:
      return []
  }
}

export const EXPRESSION_SYNTAX = {
  TODAY: 'TODAY()',
  YESTERDAY: 'YESTERDAY()',
  DATE_THIS: 'DATE_THIS("month")',
  DATE_LAST: 'DATE_LAST(30, "days")'
}

export const OPTION_DEFAULT_SELECT_RANGE = [
  {label: 'Last 7 days', value: ["DATE_LAST(7,'days')", 'TODAY()']},
  {label: 'Last 30 days', value: ["DATE_LAST(30,'days')", 'TODAY()']},
  {label: 'Last 60 days', value: ["DATE_LAST(60,'days')", 'TODAY()']},
  {label: 'This month', value: ["DATE_START_OF(TODAY(), 'month')", "DATE_END_OF(TODAY(), 'month')"]},
  {label: 'Last month', value: ["DATE_START_OF(DATE_LAST(1,'month'), 'month')", "DATE_END_OF(DATE_LAST(1,'month'), 'month')"]},
  {label: 'Lifetime', value: [undefined, undefined]}
]

export const getLabelOfExpressionFromSyntax = (syntax) => {
  // simple case
  switch (syntax) {
    case EXPRESSION_SYNTAX.TODAY:
      return 'Today'
    case EXPRESSION_SYNTAX.YESTERDAY:
      return 'Yesterday'
    case EXPRESSION_SYNTAX.DATE_THIS:
      return 'Start date of month'
    case "DATE_START_OF(TODAY(), 'month')":
      return 'Date start of this month'
    case "DATE_END_OF(TODAY(), 'month')":
      return 'Date end of this month'
    case "DATE_START_OF(DATE_LAST(1,'month'), 'month')":
      return 'Date start of last month'
    case "DATE_END_OF(DATE_LAST(1,'month'), 'month')":
      return 'Date end of last month'
    case "DATE_START_OF(TODAY(), 'days')":
      return 'Date start of this day'
    case "DATE_END_OF(TODAY(), 'days')":
      return 'Date end of this day'
    case "DATE_START_OF(DATE_LAST(1,'days'), 'days')":
      return 'Date start of Yesterday'
    case "DATE_END_OF(DATE_LAST(1,'days'), 'days')":
      return 'Date end of Yesterday'
  }
  // dynamic case
  const dateLastRegex = /DATE_LAST\((\s?)\d+(\s?),(\s?)('|")days('|")(\s?)\)/
  if (syntax.match(dateLastRegex)) {
    const numDays = syntax.replace(/DATE_LAST\((\s?)/, '').replace(/(\s?),(\s?)('|")days('|")(\s?)\)/, '')
    return `Last ${numDays} days`
  }
  return syntax
}
