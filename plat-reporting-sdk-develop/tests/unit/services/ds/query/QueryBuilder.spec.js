import QueryBuilder from '@/services/ds/query/QueryBuilder.js'

describe('QueryBuilder', () => {
  it('Check class QueryBuilder', () => {
    // setup
    let queryBuilder = new QueryBuilder()
    // excute
    queryBuilder.setDistinct()
    queryBuilder.resetPaging()
    queryBuilder.addOrder()
    queryBuilder.setOrder()
    queryBuilder.resetOrder()
    queryBuilder.hasOrder()
    queryBuilder.resetGroup()
    queryBuilder.hasGroup()
    queryBuilder.setFilter()
    queryBuilder.setGroup([], [])
  })
})
