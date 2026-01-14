import { convertColumnObjectToColumnDisplayName } from '@/utils/filterUtils'
import { ReadableFilterExpression } from '@/services/ds/filter/FilterExpessionBuilders'
import cloneDeep from 'lodash/cloneDeep'

let cached = {}

class DataQueryManager {
  filterBuilder = new ReadableFilterExpression()

  getQuery(id) {
    return cached[id] || {}
  }

  setQuery(id, query) {
    cached[id] = query
  }

  getFilterReadableFromFilter(filter, columns) {
    let builtBuilder = convertColumnObjectToColumnDisplayName(cloneDeep(filter), columns)
    let exp = this.filterBuilder.buildExpression(builtBuilder)
    exp = exp.slice(0, -35)
    return exp.substring(35)
  }
}

export default new DataQueryManager()
