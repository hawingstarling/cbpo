import pfAxios from '@/services/pfAxios'
import get from 'lodash/get'
import forEach from 'lodash/forEach'
import cloneDeep from 'lodash/cloneDeep'
import exprUtil from '@/services/exprUtil'
import { DEFAULT_CHANNEL } from '@/shared/constants'
import { DSType } from '@/shared/constants/ds.constant'
import { filterColumnName, orderColumn } from '@/shared/filters'

const BASE_FILTER_QUERY = {
  type: 'AND',
  conditions: [
    {
      column: 'sale_date',
      operator: '$gte',
      value: "DATE_START_OF(DATE_LAST(30,'day'), 'day')"
    },
    {
      column: 'sale_date',
      operator: '$lte',
      value: "DATE_END_OF(TODAY(), 'day')"
    },
    {
      column: 'channel_name',
      operator: '$eq',
      value: DEFAULT_CHANNEL
    }
  ]
}

const DEFAULT_FILTER = {
  ds_filter: {
    base: {
      config: {
        query: cloneDeep(BASE_FILTER_QUERY)
      }
    },
    builder: {
      enabled: true,
      config: {
        query: {
        },
        ignore: {
          global: {
            visible: false,
            value: false
          },
          base: {
            visible: true,
            value: false
          }
        }
      }
    }
  }
}

const state = {
  dsColumns: [],
  viewList: [],
  configFilterList: [],
  viewQuickSelectList: null,
  favoriteViewQuickSelectList: null,
  originalFilter: cloneDeep(DEFAULT_FILTER),
  filter: null,
  // SDK won't reload new data or configuration if this key keep the same value
  sdkUniqueState: 0,
  sdkConfig: null,
  // a key => value mapping of all the data source
  allDataSourceMap: null,
  allDataSourceLoaded: false,
  currentCustomExportId: null
}

const buildFilterExpr = (sdkConfig) => {
  const cols = state.dsColumns
  return exprUtil.buildFilterExpr(sdkConfig, cols)
}

const getters = {
  viewList: (state) => { return state.viewList },
  configFilterList: (state) => { return state.configFilterList },
  originalFilter: (state) => { return state.originalFilter },
  dsColumns: (state) => { return state.dsColumns },

  filter: (state) => { return state.filter },
  dsIdOfStandardView: (state) => { return state.allDataSourceMap ? state.allDataSourceMap[DSType.STANDARD_LAYOUT].data_source_id : null },
  allDataSourceMap: (state) => { return state.allDataSourceMap },
  allDataSourceLoaded: (state) => { return state.allDataSourceLoaded },
  sdkUniqueState: (state) => { return state.sdkUniqueState },
  sdkConfig: (state) => { return state.sdkConfig },
  filterRenewable: (state) => {
    return buildFilterExpr({ filter: DEFAULT_FILTER.ds_filter }) !== getters.filterCurrentExpression(state)
  },
  filterCurrentExpression: (state) => {
    return buildFilterExpr(state.sdkConfig)
  },
  filterExpression: (state) => {
    // eslint-disable-next-line no-undef
    return buildFilterExpr({ filter: get(state.filter, 'ds_filter', {}) })
  },
  originalFilterExpression: (state) => {
    return buildFilterExpr({ filter: get(state.originalFilter, 'ds_filter', {}) })
  },
  filterCopiable: (state) => {
    return get(state.filter, 'id')
  }
}

const mutations = {
  setDSColumns(state, payload) {
    state.dsColumns = orderColumn(payload)
    forEach(state.dsColumns, column => {
      column.checked = false
      // column.displayName = column.name === 'warehouse_processing_fee'
      //   ? 'Dropship Fee'
      //   : filterColumnName(column.name)
      column.displayName = filterColumnName(column.name)
    })
  },
  changeSDKUniqueState(state) {
    state.sdkUniqueState++
  },
  setConfigFilterList(state, payload) {
    state.configFilterList = payload
  },
  setFilter(state, payload) {
    state.filter = payload
  },
  setOriginalFilter(state, payload) {
    state.originalFilter = payload
  },
  setSDKConfig(state, payload) {
    state.sdkConfig = payload
  },
  setViewList(state, payload) {
    state.viewList = payload
  },
  setViewQuickSelectList(state, payload) {
    state.viewQuickSelectList = payload
  },
  setFavoriteViewQuickSelectList(state, payload) {
    state.favoriteViewQuickSelectList = payload
  },

  setColumnSet(state, payload) {
    state.columnSet = payload
  },
  setOriginalColumnSet(state, payload) {
    state.originalColumnSet = payload
  },
  setOriginalViewDSColumns(state, payload) {
    state.originalView.ds_column = payload
  },
  setOriginalView(state, payload) {
    state.originalView = payload
  },
  setView(state, payload) {
    state.view = payload
  },
  setAllDataSourceMap(state, payload) {
    state.allDataSourceMap = payload
  },
  setAllDataSourceLoaded(state, payload) {
    state.allDataSourceLoaded = payload
  }
}

const actions = {
  fetchDSColumns: async ({ commit, dispatch, state, getters }, params) => {
    let id = getters.dsIdOfStandardView
    return pfAxios.get(`/ds-proxy/v1/ds/${id}/columns`).then(res => {
      commit('setDSColumns', res.data.columns)
    })
  },
  fetchAllDataSourceIDs: async ({ commit, state }, params) => {
    if (!params.client_id) throw Error('params.client_id is required')
    commit('setAllDataSourceLoaded', false)
    return pfAxios.get(`/v1/clients/${params.client_id}/sale-items/ds/connection`).then(res => {
      commit('setAllDataSourceMap', res.data)
      commit('setAllDataSourceLoaded', true)
    }, () => {
      commit('setAllDataSourceLoaded', true)
    })
  },
  async getListFilterByTag ({commit, dispatch}, params) {
    try {
      let clientId = params.client_id
      let tag = params.tag
      let res = await pfAxios.get(`/v1/clients/${clientId}/custom-views/tags-filters`, {params: {tag}})
      commit('setConfigFilterList', res.data)
    } catch (error) {
      return error
    }
  },
  async initCompareTable({ dispatch, commit }, payload) {
    // this is required and need fetching synchronously
    await dispatch('fetchDSColumns', payload)
  },
  setFilter({ commit }, item) {
    commit('setFilter', item)
  },
  setOriginalFilter({ commit }, item) {
    commit('setOriginalFilter', item)
  },
  setReloadKeySDK({ commit }, id) {
    commit('changeSDKUniqueState')
  },
  setSDKConfig({ commit }, payload) {
    commit('setSDKConfig', payload)
  },
  async getAllTags({ commit }, payload) {
    try {
      const { data } = await pfAxios.get(`/v1/clients/${payload.client_id}/custom-views/tags-user-access`)
      return data
    } catch (err) {
      throw err
    }
  }
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
