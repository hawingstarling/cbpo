import _ from 'lodash'

export const defaultPaging = {
  limit: 30,
  current: 1
}

export const defaultOrder = {
  column: '',
  direction: 'asc'
}

export const defaultAggregation = {
  column: null,
  aggregation: 'distinct'
}

export const defaultGroup = {
  columns: [],
  aggregations: []
}

export const defaultBins = []

export const defaultFilter = {}

export const defaultParams = {
  distinct: false,
  paging: Object.assign({}, defaultPaging),
  orders: [],
  group: Object.assign({}, defaultGroup),
  filter: Object.assign({}, defaultFilter),
  fields: []
}

export default class QueryBuilder {
  constructor () {
    this.reset()
  }
  getParams () {
    return this.params
  }
  reset () {
    this.params = _.cloneDeep(defaultParams)
    return this
  }
  setDistinct (d) {
    this.params.distinct = d
    return this
  }
  setPaging (d) {
    Object.assign(this.params.paging, d)
    return this
  }
  setBins(bins = []) {
    this.params.bins = Object.assign(bins)
  }
  resetPaging () {
    this.params.paging = Object.assign({}, defaultPaging)
    return this
  }
  resetBins () {
    this.params.bins = Object.assign({}, defaultBins)
    return this
  }
  addOrder (column, direction) {
    this.params.orders.push({column, direction})
    return this
  }
  setOrder (column, direction) {
    this.params.orders = [{column, direction}]
    return this
  }
  resetOrder () {
    this.params.orders.length = 0
    return this
  }
  hasOrder () {
    return this.params.orders.length > 0
  }
  setGroup (columns, aggregations) {
    Object.assign(this.params.group, {
      columns: [...columns],
      aggregations: [...aggregations]
    })
    return this
  }
  resetGroup () {
    this.params.group = Object.assign(this.params.group, defaultGroup)
    return this
  }
  hasGroup () {
    return this.params.group.length > 0
  }
  setFilter (filter) {
    Object.assign(this.params.filter, filter && !_.isEmpty(filter.conditions) ? filter : {})
  }
  getFilter () {
    return {...this.params.filter}
  }

  setFields (fields) {
    if (fields) {
      this.params.fields = [...fields]
    }
  }
  setTimezone (timezone) {
    if (timezone) {
      this.params.timezone = timezone
    }
  }
}
