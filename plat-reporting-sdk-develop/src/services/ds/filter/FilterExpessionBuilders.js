import _ from 'lodash'
import precond from 'precond'
import { checkFeColumn } from '@/utils/precondUtil'
import { SUPPORT_OPERATORS } from './FilterDefinitions'
import moment from 'moment'

class AbstractFilterExpressionBuilder {
  constructor() {
    this.AND = 'AND'
    this.OR = 'OR'
  }
  /**
   * Quote the value for the filter expression.
   * @param {Object} column Standard column object
   * @param {*} value Base value
   */
  quoteValue(column, value) {
    throw Error('Not implemented')
  }
  quoteColumn(column) {
    throw Error('Not implemented')
  }
  /**
   * Quote the value for the filter expression.
   * @param quotedColumn: string - Column value
   */
  getDefaultString(quotedColumn) {
    throw Error('Not implemented')
  }
  /**
   * Build filter expression
   * @param {Object} filter Filter nested object
   */
  buildExpression(filter) {
    precond.checkIsObject(filter, 'Invalid filter')
    if (!_.isEmpty(filter.conditions)) {
      // recursively build the expression
      let type = _.toLower(filter.type) === 'or' ? this.OR : this.AND
      return `( ${_.map(filter.conditions, (cond) => {
        return this.buildExpression(cond)
      }).join(type)} )`
    } else {
      // build it as a condition
      return this.buildCondition(filter)
    }
  }
  /**
   * @override
   * @param {Object} aCondition filter condition object
   */
  buildCondition(aCondition) {
    precond.checkIsObject(aCondition, 'Invalid condition')
    let quotedColumn = this.quoteColumn(aCondition.column)
    let quotedValue = this.quoteValue(aCondition.column, aCondition.value)
    switch (aCondition.operator) {
      // Equal
      case SUPPORT_OPERATORS['=='].value:
      case SUPPORT_OPERATORS.eq.value:
      case SUPPORT_OPERATORS.$eq.value:
      case SUPPORT_OPERATORS.$i_eq.value:
        return this.makeEqualExpression(quotedColumn, quotedValue)
      // Not equal
      case SUPPORT_OPERATORS['!='].value:
      case SUPPORT_OPERATORS.ne.value:
      case SUPPORT_OPERATORS.$ne.value:
      case SUPPORT_OPERATORS.$i_ne.value:
        return this.makeNotEqualExpression(quotedColumn, quotedValue)
      // Less
      case SUPPORT_OPERATORS['<'].value:
      case SUPPORT_OPERATORS.lt.value:
      case SUPPORT_OPERATORS.$lt.value:
        return this.makeLessThanExpression(quotedColumn, quotedValue)
      // Less or equal
      case SUPPORT_OPERATORS['<='].value:
      case SUPPORT_OPERATORS.lte.value:
      case SUPPORT_OPERATORS.$lte.value:
        return this.makeLessThanOrEqualExpression(quotedColumn, quotedValue)
      // Great
      case SUPPORT_OPERATORS['>'].value:
      case SUPPORT_OPERATORS.gt.value:
      case SUPPORT_OPERATORS.$gt.value:
        return this.makeGreaterThanExpression(quotedColumn, quotedValue)
      // Great or equal
      case SUPPORT_OPERATORS['>='].value:
      case SUPPORT_OPERATORS.gte.value:
      case SUPPORT_OPERATORS.$gte.value:
        return this.makeGreaterThanOrEqualExpression(quotedColumn, quotedValue)
      // Contains
      case SUPPORT_OPERATORS.contains.value:
        return this.makeContainsExpression(quotedColumn, quotedValue)
      // Not contains
      case SUPPORT_OPERATORS.not_contain.value:
        return this.makeNotContainsExpression(quotedColumn, quotedValue)
      // Null
      case SUPPORT_OPERATORS.null.value:
        return this.makeIsNullExpression(quotedColumn)
      // Not null
      case SUPPORT_OPERATORS.not_null.value:
        return this.makeIsNotNullExpression(quotedColumn)
      // Empty
      case SUPPORT_OPERATORS.empty.value:
        return this.makeIsEmptyExpression(quotedColumn)
      // Not empty
      case SUPPORT_OPERATORS.not_empty.value:
        return this.makeIsNotEmptyExpression(quotedColumn)
      // Is true
      case SUPPORT_OPERATORS.is_true.value:
        return this.makeIsTrueExpression(quotedColumn)
      // Is False
      case SUPPORT_OPERATORS.is_false.value:
        return this.makeIsFalseExpression(quotedColumn)
      // Starts with
      case SUPPORT_OPERATORS.starts_with.value:
        return this.makeStartsWithExpression(quotedColumn, quotedValue)
      // Not start with
      case SUPPORT_OPERATORS.not_start_with.value:
        return this.makeNotStartWithExpression(quotedColumn, quotedValue)
      // Ends with
      case SUPPORT_OPERATORS.ends_with.value:
        return this.makeEndsWithExpression(quotedColumn, quotedValue)
      // Not end with
      case SUPPORT_OPERATORS.not_end_with.value:
        return this.makeNotEndsWithExpression(quotedColumn, quotedValue)
      // In
      case SUPPORT_OPERATORS.in.value:
        return this.makeInWithExpression(aCondition.column, quotedColumn, aCondition.value)
      // Not In
      case SUPPORT_OPERATORS.not_in.value:
        return this.makeNotInWithExpression(aCondition.column, quotedColumn, aCondition.value)
      // In Range
      case SUPPORT_OPERATORS.time_range.value:
      case SUPPORT_OPERATORS.in_range.value:
        return this.makeInRangeWithExpression(aCondition.column, quotedColumn, aCondition.value)
      // Throw error
      default:
        throw Error(`Operator ${aCondition.operator} has not been supported`)
    }
  }
  /**
   * @override
   * @param quotedColumn: string - Value of Column
   * @param quotedValue: string - Base value
   */
  makeEqualExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeNotEqualExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeContainsExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeNotContainsExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeLessThanExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeLessThanOrEqualExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeGreaterThanExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeGreaterThanOrEqualExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeIsNullExpression(quotedColumn) {
    throw Error('Not implemented')
  }
  makeIsNotNullExpression(quotedColumn) {
    throw Error('Not implemented')
  }
  makeIsTrueExpression(quotedColumn) {
    throw Error('Not implemented')
  }
  makeIsFalseExpression(quotedColumn) {
    throw Error('Not implemented')
  }
  makeIsEmptyExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeIsNotEmptyExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeStartsWithExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeNotStartWithExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeEndsWithExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeNotEndsWithExpression(quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
  makeInWithExpression(column, quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }

  makeNotInWithExpression(column, quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }

  makeInRangeWithExpression(column, quotedColumn, quotedValue) {
    throw Error('Not implemented')
  }
}

export class LocalFilterExpressionBuilder extends AbstractFilterExpressionBuilder {
  constructor() {
    super()
    this.AND = '&&'
    this.OR = '||'
  }
  /**
   * Quote column for expression
   * @override
   * @param {Object} column Standard column
   * @param {*} value Base value
   */
  quoteValue(column, value) {
    checkFeColumn(column)
    // TODO need checking DS columns type
    let isNum = _.isNumber(value)
    if (isNum) {
      return '`' + value + '`'
    }
    let isTemporal = value && moment(value).isValid()
    return '`' + (isTemporal ? moment(value).format() : value) + '`'
  }
  quoteColumn(columnName) {
    checkFeColumn(columnName)
    // __colValue is method name that will be used with eval
    return `__colValue(${JSON.stringify(columnName)})`
  }
  getDefaultString(quotedColumn) {
    return `__getString(${quotedColumn})`
  }
  /**
   * Define rules for expression
   * @override
   * @param quotedColumn: string - Value of column
   * @param quotedValue:string - Base value
   */
  makeEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} == ${quotedValue}`
  }
  makeNotEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} != ${quotedValue}`
  }
  makeContainsExpression(quotedColumn, quotedValue) {
    return `${this.getDefaultString(quotedColumn)}.includes(${quotedValue})`
  }
  makeNotContainsExpression(quotedColumn, quotedValue) {
    return `!${this.getDefaultString(quotedColumn)}.includes(${quotedValue})`
  }
  makeLessThanExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} < ${quotedValue}`
  }
  makeLessThanOrEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} <= ${quotedValue}`
  }
  makeGreaterThanExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} > ${quotedValue}`
  }
  makeGreaterThanOrEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} >= ${quotedValue}`
  }
  makeIsNullExpression(quotedColumn) {
    return `${quotedColumn} == null`
  }
  makeIsNotNullExpression(quotedColumn) {
    return `${quotedColumn} != null`
  }
  makeIsTrueExpression(quotedColumn) {
    return `${quotedColumn} === true`
  }
  makeIsFalseExpression(quotedColumn) {
    return `${quotedColumn} == false`
  }
  makeIsEmptyExpression(quotedColumn, quotedValue) {
    return `${quotedColumn}`
  }
  makeIsNotEmptyExpression(quotedColumn, quotedValue) {
    return `!${quotedColumn}`
  }
  makeStartsWithExpression(quotedColumn, quotedValue) {
    return `${this.getDefaultString(quotedColumn)}.startsWith(${quotedValue})`
  }
  makeNotStartWithExpression(quotedColumn, quotedValue) {
    return `!${this.getDefaultString(quotedColumn)}.startsWith(${quotedValue})`
  }
  makeEndsWithExpression(quotedColumn, quotedValue) {
    return `${this.getDefaultString(quotedColumn)}.endsWith(${quotedValue})`
  }
  makeNotEndsWithExpression(quotedColumn, quotedValue) {
    return `!${this.getDefaultString(quotedColumn)}.endsWith(${quotedValue})`
  }
  makeInWithExpression(column, quotedColumn, quotedValue) {
    let stringfilter = ''
    if (_.isArray(quotedValue)) {
      _.map(quotedValue, (value, index) => {
        stringfilter += this.makeEqualExpression(quotedColumn, this.quoteValue(column, value))
        if (index + 1 < quotedValue.length) {
          stringfilter += this.OR
        }
      })
    }
    return stringfilter
  }
  makeNotInWithExpression(column, quotedColumn, quotedValue) {
    let stringfilter = ''
    if (_.isArray(quotedValue)) {
      _.map(quotedValue, (value, index) => {
        stringfilter += this.makeNotEqualExpression(quotedColumn, this.quoteValue(column, value))
        console.log(stringfilter)
        if (index + 1 < quotedValue.length) {
          stringfilter += this.AND
        }
      })
    }
    return stringfilter
  }
  makeInRangeWithExpression(column, quotedColumn, quotedValue) {
    let value = _.cloneDeep(quotedValue)
    value.sort()
    return this.makeGreaterThanOrEqualExpression(quotedColumn, this.quoteValue(column, value[0])) + this.AND + this.makeLessThanOrEqualExpression(quotedColumn, this.quoteValue(column, value[1]))
  }
}

export class ReadableFilterExpression extends AbstractFilterExpressionBuilder {
  constructor() {
    super()
    this.AND = '<span class="exp-filter"> AND </span>'
    this.OR = '<span class="exp-filter"> OR </span>'
  }
  /**
   * Quote column for expression
   * @override
   * @param {Object} column Standard column
   * @param {*} value Base value
   */
  buildExpression(filter) {
    precond.checkIsObject(filter, 'Invalid filter')
    if (!_.isEmpty(filter.conditions)) {
      // recursively build the expression
      let type = _.toLower(filter.type) === 'or' ? this.OR : this.AND
      return `<span class="value-filter">(</span>${_.map(filter.conditions, (cond) => {
        return this.buildExpression(cond)
      }).join(type)}<span class="value-filter">)</span>`
    } else {
      // build it as a condition
      if (!filter.column || !filter.operator) return ''
      return this.buildCondition(filter)
    }
  }
  quoteValue(column, value) {
    checkFeColumn(column)
    // TODO need checking DS columns type
    let isNum = _.isNumber(value)
    if (isNum) {
      return `<span class="value-filter">${value}</span>`
    }
    const numberRegex = new RegExp('^[0-9.,]*$')
    let isTemporal = value && _.isString(value) && !numberRegex.test(value) && (moment(value, 'YYYY-MM-DD', true).isValid() || moment(value, 'YYYY-MM-DDTHH:mm:ss', true).isValid())
    return (isTemporal ? `<span class="value-filter">${moment(value).format('MM/DD/YYYY').toString()}</span>` : `<span class="value-filter">${value}</span>`)
  }
  quoteColumn(columnName) {
    checkFeColumn(columnName)
    // __colValue is method name that will be used with eval
    return `<span class="column-filter">@${columnName}</span>`
  }
  getDefaultString(quotedColumn) {
    return `${quotedColumn}`
  }
  /**
   * Define rules for expression
   * @override
   * @param quotedColumn: string - Value of column
   * @param quotedValue:string - Base value
   */
  makeEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} <span class="text-primary"> = </span> ${quotedValue}`
  }
  makeNotEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} <span class="text-primary"> != </span> ${quotedValue}`
  }
  makeContainsExpression(quotedColumn, quotedValue) {
    return `${this.getDefaultString(quotedColumn)}<span class="text-primary"> Contains </span>${quotedValue}`
  }
  makeNotContainsExpression(quotedColumn, quotedValue) {
    return `${this.getDefaultString(quotedColumn)}<span class="text-primary"> Not Contains </span>${quotedValue}`
  }
  makeLessThanExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} <span class="text-primary"> < </span> ${quotedValue}`
  }
  makeLessThanOrEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} <span class="text-primary"> <= </span> ${quotedValue}`
  }
  makeGreaterThanExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} <span class="text-primary"> > </span> ${quotedValue}`
  }
  makeGreaterThanOrEqualExpression(quotedColumn, quotedValue) {
    return `${quotedColumn} <span class="text-primary"> >= </span> ${quotedValue}`
  }
  makeIsNullExpression(quotedColumn) {
    return `${quotedColumn} <span class="text-primary">= null</span>`
  }
  makeIsNotNullExpression(quotedColumn) {
    return `${quotedColumn} <span class="text-primary">!= null</span>`
  }
  makeIsTrueExpression(quotedColumn) {
    return `${quotedColumn} <span class="text-primary">= true</span>`
  }
  makeIsFalseExpression(quotedColumn) {
    return `${quotedColumn} <span class="text-primary">= false</span>`
  }
  makeIsEmptyExpression(quotedColumn, quotedValue) {
    return `${quotedColumn}`
  }
  makeIsNotEmptyExpression(quotedColumn, quotedValue) {
    return `<span class="text-primary"> !</span>${quotedColumn}`
  }
  makeStartsWithExpression(quotedColumn, quotedValue) {
    return `${this.getDefaultString(quotedColumn)} <span class="text-primary">Starts With</span> ${quotedValue}`
  }
  makeNotStartWithExpression(quotedColumn, quotedValue) {
    return `<span class="text-primary"> !</span>${this.getDefaultString(quotedColumn)} <span class="text-primary">Starts With</span> ${quotedValue}`
  }
  makeEndsWithExpression(quotedColumn, quotedValue) {
    return `${this.getDefaultString(quotedColumn)} <span class="text-primary">Ends With</span> ${quotedValue}`
  }
  makeNotEndsWithExpression(quotedColumn, quotedValue) {
    return `<span class="text-primary"> !</span>${this.getDefaultString(quotedColumn)} <span class="text-primary">Ends With</span> ${quotedValue}`
  }
  makeInWithExpression(column, quotedColumn, quotedValue) {
    let stringfilter = quotedColumn + ' <span class="condition-filter">IN</span> '
    if (_.isArray(quotedValue)) {
      _.map(quotedValue, (value, index) => {
        stringfilter += this.quoteValue(column, value)
        if (index + 1 < quotedValue.length) {
          stringfilter += ', '
        }
      })
    } else {
      stringfilter += this.quoteValue(column, quotedValue)
    }
    return stringfilter
  }
  makeNotInWithExpression(column, quotedColumn, quotedValue) {
    let stringfilter = quotedColumn + ' <span class="condition-filter">NOT IN</span> '
    if (_.isArray(quotedValue)) {
      _.map(quotedValue, (value, index) => {
        stringfilter += this.quoteValue(column, value)
        if (index + 1 < quotedValue.length) {
          stringfilter += ', '
        }
      })
    } else {
      stringfilter += this.quoteValue(column, quotedValue)
    }
    return stringfilter
  }
  makeInRangeWithExpression(column, quotedColumn, quotedValue) {
    let value = _.cloneDeep(quotedValue)
    value.sort()
    return `${quotedColumn} <span class="condition-filter">BETWEEN</span> ${this.quoteValue(column, value[0])} <span class="condition-filter">AND</span> ${this.quoteValue(column, value[1])}`
  }
}
