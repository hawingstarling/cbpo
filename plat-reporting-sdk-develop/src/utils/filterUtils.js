import { defaultSelectControlConfig } from '@/components/widgets/form/FilterControlConfig'
import { SUPPORT_OPERATORS } from '@/services/ds/filter/FilterDefinitions'
import { moveElement } from '@/utils/arrayUtil'
import { isBoolean, isEmpty, get, reduce, some, isString } from 'lodash'
import CBPO from '@/services/CBPO'
import moment from 'moment'

let decreaseIndex = false

export const SUPPORT_LOGIC = {
  AND: 'AND',
  OR: 'OR'
}

export const convertColumnObjectToColumnName = (queries) => {
  if (isEmpty(queries)) {
    return queries
  }
  queries.conditions = queries.conditions.map(query => {
    if (query.conditions) {
      return convertColumnObjectToColumnName(query)
    } else {
      query.column = query.column.name || query.column
      return query
    }
  })
  return queries
}

export const convertColumnObjectToColumnDisplayName = (queries, columns) => {
  if (isEmpty(queries)) {
    return queries
  }
  const updatedColumnsState = columns && Array.isArray(columns) ? columns : CBPO.channelManager().getChannel().getColumnSvc().getColumns()
  queries.conditions = queries.conditions.map(query => {
    if (query.conditions) {
      return convertColumnObjectToColumnDisplayName(query, columns)
    } else {
      const foundColumn = updatedColumnsState.find(col => col.name === query.column)
      query.column = get(foundColumn, 'displayName', query.column.displayName || query.column.name || query.column)
      return query
    }
  })
  return queries
}

export const convertColumnNameToColumnObject = (queries, fields) => {
  if (isEmpty(queries)) {
    return queries
  }
  queries.conditions = queries.conditions.map(query => {
    if (query.conditions && query.conditions.length) {
      return convertColumnNameToColumnObject(query, fields)
    } else {
      if (isString(query.column)) {
        const column = fields.find(f => f.name === query.column)
        query.column = column || { name: query.column }
      } else {
        const column = fields.find(f => f.name === query.column.name)
        query.column.displayName = column.displayName || query.column.displayName
      }
      return query
    }
  })
  return queries
}

/**
 *
 * @param {Object} dsColumns List columns
 * @param {string} globalFilterObj The object filter
 * @return {Object} the object filter
 */
export const refineGlobalFilterByDSColumns = (dsColumns, globalFilterObj) => {
  let conditions = get(globalFilterObj, 'conditions', [])
  if (isEmpty(dsColumns) || isEmpty(conditions)) {
    return {}
  }

  conditions = reduce(conditions, function(result, value) {
    if (some(dsColumns, ['name', value.column])) {
      result.push(value)
    }
    return result
  }, [])

  return isEmpty(conditions) ? {} : { ...globalFilterObj, conditions }
}

export const changeFlag = (value) => {
  if (!isBoolean(value)) {
    decreaseIndex = !decreaseIndex
  } else {
    decreaseIndex = value
  }
}

export const getFlag = () => {
  return decreaseIndex
}

export const findAndRemove = (filter, node, target) => {
  if (filter.id === node.parentId) {
    filter.conditions = filter.conditions.filter(filterNode => filterNode.id !== node.id)
  } else {
    let wrappers = filter.conditions.filter(filterNode => !isEmpty(filterNode.conditions))
    wrappers.forEach(filter => {
      findAndRemove(filter, node, target)
    })
    let currentLength = filter.conditions.length
    // Remove empty group
    filter.conditions = filter.conditions.filter(filter => !filter.conditions || filter.conditions.length > 0)
    // If group length change. it means empty group has been removed then index when create will be decrease 1
    if (currentLength !== filter.conditions.length && node.level !== target.node.level) {
      changeFlag(true)
    }
  }
}

export const findAndCreate = (filter, node, target) => {
  if (filter.id === target.node.parentId) {
    // Update parent Id and level
    node.parentId = filter.id
    node.level = filter.level + 1

    // Move node to new location
    filter.conditions.push(node)
    filter.conditions = moveElement(filter.conditions, filter.conditions.length - 1, getFlag() && target.index !== 0 ? target.index - 1 : target.index)
  } else {
    let wrappers = filter.conditions.filter(filterNode => !isEmpty(filterNode.conditions))
    wrappers.forEach(filter => {
      findAndCreate(filter, node, target)
    })
  }
}

export const updateLevel = (node, newLevel) => {
  node.level = newLevel
  if (!isEmpty(node.conditions)) {
    node.conditions.forEach(filter => updateLevel(filter, newLevel + 1))
  }
}

export const parseOperators = (queries) => {
  if (isEmpty(queries)) {
    return queries
  }
  queries.conditions = queries.conditions.reduce((conditions, query) => {
    if (query.conditions) {
      const parsedQuery = parseOperators(query)
      conditions = [...conditions, parsedQuery]
    } else {
      if (query.operator === SUPPORT_OPERATORS.date_in.value) {
        const format = get(query, 'options.format') || defaultSelectControlConfig.common.options.format
        const startQuery = {
          column: query.column,
          operator: SUPPORT_OPERATORS.$gte.value,
          value: moment(query.value).format(format.start)
        }
        const endQuery = {
          column: query.column,
          operator: SUPPORT_OPERATORS.$lte.value,
          value: moment(query.value).format(format.end)
        }
        conditions.push({
          type: SUPPORT_LOGIC.AND,
          conditions: [startQuery, endQuery]
        })
      } else {
        conditions.push(query)
      }
    }
    return conditions
  }, [])
  return queries
}
