import { DsQueryExecAbstract } from 'plat-expr-sdk'
import CBPO from '@/services/CBPO'
import isEmpty from 'lodash/isEmpty'
import cloneDeep from 'lodash/cloneDeep'
import get from 'lodash/get'

export class DsQueryExecService extends DsQueryExecAbstract {
  /**
   * DS query process excution
   * @param dvOrDsId Datasource ID or Dataview ID to query
   * @param query ds-api standard query object https://mayoretailinternetservices.atlassian.net/wiki/spaces/DSP/pages/3932256/Queries
   * @param column expected response column info {type, alias}
   */
  customFilter = null

  constructor (filter, timezone) {
    super()
    this.customFilter = filter
    this.customTimezone = timezone
  }

  async exec(dvOrDsId, query, column) {
    try {
      let queryFilter = cloneDeep(query.filter)
      if (!isEmpty(this.customFilter)) {
        let finalFilter = {
          type: 'AND',
          conditions: []
        }
        finalFilter.conditions = [
          ...finalFilter.conditions,
          ...get(query, 'filter.conditions', [])
        ]
        finalFilter.conditions.push({...this.customFilter})
        queryFilter = cloneDeep(finalFilter)
      }
      query.timezone = this.customTimezone
      query.filter = cloneDeep(queryFilter)
      if (column.type === 'count') {
        let total = await CBPO.dsManager().getDataSource(dvOrDsId).total(query)
        return { rows: [[total]], cols: [{name: column.alias, type: 'number'}] }
      }
      return await CBPO.dsManager().getDataSource(dvOrDsId).query(query)
    } catch (e) {
      console.log('get datasource', e)
      return ''
    }
  }
}
