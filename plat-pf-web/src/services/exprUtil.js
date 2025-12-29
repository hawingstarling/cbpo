import _ from 'lodash'

/**
 *
 * @param {Array} columns list of column definition with visibility
 */
const buildColumnSetExpr = (columns) => {
  let hiddenExpr = columns.reduce((listColumn, column) => {
    if (column.visible === false) listColumn = [...listColumn, `<span class="column-label">@${column.displayName}</span>`]
    return listColumn
  }, []).join(', ')
  if (hiddenExpr) {
    hiddenExpr = '<span class="column-set-expr"><span class="hide-label"><i class="fa fa-eye-slash"></i></span> ' + hiddenExpr + '</span>'
  } else {
    hiddenExpr = '<span class="column-set-expr">Default set</span>'
  }
  return hiddenExpr
}

const buildFilterExpr = (sdkConfig, columns) => {
  const baseQuery = _.get(sdkConfig, 'filter.base.config.query', {})
  const builderQuery = _.get(sdkConfig, 'filter.builder.config.query', {})
  const ignoreBase = _.get(sdkConfig, 'filter.builder.config.ignore.base.value', false)
  const query = { type: 'AND', conditions: [] }
  if (!_.isEmpty(baseQuery) && !_.isEmpty(baseQuery.conditions) && !ignoreBase) {
    query.conditions.push(baseQuery)
  }
  if (!_.isEmpty(builderQuery) && !_.isEmpty(builderQuery.conditions)) {
    query.conditions.push(builderQuery)
  }
  // eslint-disable-next-line no-undef
  let queryStr = CBPO.dataQueryManager().getFilterReadableFromFilter(query, columns)
  if (!queryStr) {
    queryStr = '<span class="text-primary">No filter</span>'
  }
  return `<span class="filter-expr">${queryStr}</span>`
}
const buildReportExpr = (query, columns) => {
  // eslint-disable-next-line no-undef
  let queryStr = CBPO.dataQueryManager().getFilterReadableFromFilter(query, columns)
  if (!queryStr) {
    queryStr = '<span class="text-primary">No filter</span>'
  }
  return `<span class="filter-expr">${queryStr}</span>`
}
export default {
  buildColumnSetExpr,
  buildFilterExpr,
  buildReportExpr
}
