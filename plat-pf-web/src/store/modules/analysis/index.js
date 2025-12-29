import pfAxios from '@/services/pfAxios'
import {makeDefaultColumnConfig, makeDefaultFilterConfig} from '@/shared/utils'
import _ from 'lodash'
import exprUtil from '@/services/exprUtil'
import { filterColumnName, orderColumn } from '@/shared/filters'
import { DEFAULT_CHANNEL } from '@/shared/constants'
import { DSType } from '@/shared/constants/ds.constant'
// import { set } from 'core-js/core/dict'

// limit num of quick select item in dropdown
const QUICK_ITEM_LIMIT_VIEW = 20
// const QUICK_ITEM_LIMIT_COLUMN_SET = 10
// const QUICK_ITEM_LIMIT_FILTER = 10
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
        query: _.cloneDeep(BASE_FILTER_QUERY)
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

const DEFAULT_COLUMN_SET = {
  ds_column: {
    config: {
      columns: []
    }
  }
}

const DEFAULT_VIEW = {
  ds_filter: {
    base: {
      config: {
        query: _.cloneDeep(BASE_FILTER_QUERY)
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
  },
  ds_column: {
    config: {
      columns: []
    }
  }
}

let BASE_QUERY_CHANNEL_SALE_ID = {
  query: {
    filter: {
      type: 'AND',
      conditions: [
        {
          column: 'channel_id',
          operator: '$eq',
          value: ''
        }
      ]
    }
  }
}

const state = {
  viewList: [],
  // columnSetList: [],
  // filterList: [],
  // columnSetQuickSelectList: null,
  viewQuickSelectList: null,
  favoriteViewQuickSelectList: null,
  // favoriteColumnSetQuickSelectList: null,
  // filterQuickSelectList: null,
  // favoriteFilterQuickSelectList: null,
  // keep the original filter object so we can compare to know if the data has been changed
  // its structure is the filter model from backend
  originalFilter: _.cloneDeep(DEFAULT_FILTER),
  filter: null,
  originalColumnSet: _.cloneDeep(DEFAULT_COLUMN_SET),
  columnSet: null,
  originalView: {
    ds_filter: _.cloneDeep(DEFAULT_FILTER.ds_filter),
    ds_column: null
  },
  view: null,
  dsColumns: [],
  // SDK won't reload new data or configuration if this key keep the same value
  sdkUniqueState: 0,
  sdkConfig: null,
  listBreakdownListing: [],
  listBreakdownOther: [],
  listBreakdownTaxCharged: [],
  listBreakdownShippingCost: [],
  listBreakdownReimbursementCosts: [],
  listBreakdownChannelTaxWithheld: [],
  listBreakdownSaleCharged: [],
  listBreakdownReturnPostageBilling: [],
  channelList: [],
  formFilterOptions: [],
  // a key => value mapping of all the data source
  allDataSourceMap: null,
  allDataSourceLoaded: false,
  currentCustomExportId: null,
  customObject: {}
}

const buildFilterExpr = (sdkConfig) => {
  const cols = state.dsColumns
  return exprUtil.buildFilterExpr(sdkConfig, cols)
}

const buildColumnSetExpr = (sdkConfig, hiddenColumns = []) => {
  const cols = _.get(sdkConfig, 'config.columns', {})
  const noneHiddenColumns = cols.filter(col => !hiddenColumns.find(hiddenCol => hiddenCol.name === col.name))
  return exprUtil.buildColumnSetExpr(noneHiddenColumns)
}

const getters = {
  // filterList: (state) => { return state.filterList },
  // columnSetList: (state) => { return state.columnSetList },
  // quickSelectFilters: (state) => {
  //   return _.get(state.filterQuickSelectList, 'results', []).slice(0, QUICK_ITEM_LIMIT_FILTER)
  // },
  // quickSelectColumnSets: (state) => {
  //   return _.get(state.columnSetQuickSelectList, 'results', []).slice(0, QUICK_ITEM_LIMIT_COLUMN_SET)
  // },
  // quickFavoriteSelectColumnSets: (state) => {
  //   return _.get(state.favoriteColumnSetQuickSelectList, 'results', []).slice(0, QUICK_ITEM_LIMIT_VIEW)
  // },
  // quickFavoriteSelectFilters: (state) => {
  //   return _.get(state.favoriteFilterQuickSelectList, 'results', []).slice(0, QUICK_ITEM_LIMIT_VIEW)
  // },
  viewList: (state) => { return state.viewList },
  quickSelectViews: (state) => {
    return _.get(state.viewQuickSelectList, 'results', []).slice(0, QUICK_ITEM_LIMIT_VIEW)
  },
  quickFavoriteSelectViews: (state) => {
    return _.get(state.favoriteViewQuickSelectList, 'results', []).slice(0, QUICK_ITEM_LIMIT_VIEW)
  },
  originalFilter: (state) => { return state.originalFilter },

  filter: (state) => { return state.filter },
  columnSet: (state) => { return state.columnSet },
  view: (state) => { return state.view },

  dsColumns: (state) => { return state.dsColumns },
  dsIdOfStandardView: (state) => { return state.allDataSourceMap ? state.allDataSourceMap[DSType.STANDARD_LAYOUT].data_source_id : null },
  dsIdOfFinancialView: (state) => { return state.allDataSourceMap ? state.allDataSourceMap[DSType.FINANCIAL_LAYOUT].data_source_id : null },
  allDataSourceMap: (state) => { return state.allDataSourceMap },
  allDataSourceLoaded: (state) => { return state.allDataSourceLoaded },
  sdkUniqueState: (state) => { return state.sdkUniqueState },
  sdkConfig: (state) => { return state.sdkConfig },
  currentCustomExportId: (state) => {
    return state.currentCustomExportId
  },

  // UI computation

  // Filter
  // filterName: (state) => { return _.get(state.filter, 'name') },
  // filterDiscardable: (state) => {
  //   return _.get(state.filter, 'id') && getters.originalFilterExpression(state) !== getters.filterCurrentExpression(state)
  // },
  filterRenewable: (state) => {
    return buildFilterExpr({ filter: DEFAULT_FILTER.ds_filter }) !== getters.filterCurrentExpression(state)
  },
  // columnSetName: (state) => { return _.get(state.columnSet, 'name') },
  filterCurrentExpression: (state) => {
    return buildFilterExpr(state.sdkConfig)
  },
  filterExpression: (state) => {
    // eslint-disable-next-line no-undef
    return buildFilterExpr({ filter: _.get(state.filter, 'ds_filter', {}) })
  },
  originalFilterExpression: (state) => {
    return buildFilterExpr({ filter: _.get(state.originalFilter, 'ds_filter', {}) })
  },
  filterCopiable: (state) => {
    return _.get(state.filter, 'id')
  },

  // Column Set
  columnSetCurrentExpression: (state) => {
    const hiddenColumns = _.get(state.sdkConfig, 'columnManager.config.hiddenColumns', [])
    return buildColumnSetExpr(state.sdkConfig.elements[0], hiddenColumns)
  },
  originalColumnSetExpression: (state) => {
    const hiddenColumns = _.get(state.sdkConfig, 'columnManager.config.hiddenColumns', [])
    return buildColumnSetExpr(_.get(state.originalColumnSet, 'ds_column', {}), hiddenColumns)
  },
  // columnSetDiscardable: (state) => {
  //   return _.get(state.columnSet, 'id') && getters.originalColumnSetExpression(state) !== getters.columnSetCurrentExpression(state)
  // },
  // columnSetCopiable: (state) => {
  //   return _.get(state.columnSet, 'id')
  // },
  columnSetRenewable: (state) => {
    return buildColumnSetExpr(DEFAULT_COLUMN_SET.ds_column) !== getters.columnSetCurrentExpression(state)
  },

  // View
  viewName: (state) => { return _.get(state.view, 'name') },
  viewCurrentExpression: (state) => {
    const hiddenColumns = _.get(state.sdkConfig, 'columnManager.config.hiddenColumns', [])
    return buildColumnSetExpr(state.sdkConfig.elements[0], hiddenColumns) + buildFilterExpr(state.sdkConfig)
  },
  originalViewExpression: (state) => {
    const hiddenColumns = _.get(state.sdkConfig, 'columnManager.config.hiddenColumns', [])
    return buildColumnSetExpr(_.get(state.originalView, 'ds_column', {}), hiddenColumns) + buildFilterExpr({ filter: _.get(state.originalView, 'ds_filter', {}) })
  },
  viewDiscardable: (state) => {
    return _.get(state.view, 'id') && getters.originalViewExpression(state) !== getters.viewCurrentExpression(state)
  },
  viewCopiable: (state) => {
    return _.get(state.view, 'id')
  },
  viewRenewable: (state) => {
    return _.get(state.view, 'id') && buildColumnSetExpr(DEFAULT_COLUMN_SET.ds_column) + buildFilterExpr({ filter: DEFAULT_FILTER }) !== getters.columnSetCurrentExpression(state) + getters.filterCurrentExpression(state)
  },
  listBreakdownListing: (state) => { return state.listBreakdownListing },
  listBreakdownOther: (state) => { return state.listBreakdownOther },
  listBreakdownTaxCharged: (state) => { return state.listBreakdownTaxCharged },
  listBreakdownShippingCost: (state) => { return state.listBreakdownShippingCost },
  listBreakdownChannelTaxWithheld: (state) => { return state.listBreakdownChannelTaxWithheld },
  listBreakdownReimbursementCosts: (state) => { return state.listBreakdownReimbursementCosts },
  listBreakdownSaleCharged: (state) => { return state.listBreakdownSaleCharged },
  listBreakdownReturnPostageBilling: (state) => { return state.listBreakdownReturnPostageBilling },
  // Channel
  channelList: (state) => { return state.channelList },
  formFilterOptions: (state) => { return state.formFilterOptions },
  // Custom Object
  getCustomObject: (state) => { return state.customObject }
}

const mutations = {
  // setColumnSetList(state, payload) {
  //   state.columnSetList = payload
  // },
  // setFilterList(state, payload) {
  //   state.filterList = payload
  // },
  // setColumnSetQuickSelectList(state, payload) {
  //   state.columnSetQuickSelectList = payload
  // },
  setViewList(state, payload) {
    state.viewList = payload
  },
  setViewQuickSelectList(state, payload) {
    state.viewQuickSelectList = payload
  },
  setFavoriteViewQuickSelectList(state, payload) {
    state.favoriteViewQuickSelectList = payload
  },
  // setFavoriteColumnSetQuickSelectList(state, payload) {
  //   state.favoriteColumnSetQuickSelectList = payload
  // },
  // setFilterQuickSelectList(state, payload) {
  //   state.filterQuickSelectList = payload
  // },
  // setFavoriteFilterQuickSelectList(state, payload) {
  //   state.favoriteFilterQuickSelectList = payload
  // },
  setFilter(state, payload) {
    state.filter = payload
  },
  setOriginalFilter(state, payload) {
    state.originalFilter = payload
  },
  setSDKConfig(state, payload) {
    state.sdkConfig = payload
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
  setDSColumns(state, payload) {
    state.dsColumns = orderColumn(payload)
    _.forEach(state.dsColumns, column => {
      column.checked = false
      column.displayName = filterColumnName(column.name)
    })
  },
  setAllDataSourceMap(state, payload) {
    state.allDataSourceMap = payload
  },
  setAllDataSourceLoaded(state, payload) {
    state.allDataSourceLoaded = payload
  },
  changeSDKUniqueState(state) {
    state.sdkUniqueState++
  },
  setListBreakdownListing(state, payload) {
    state.listBreakdownListing = payload
  },
  setListBreakdownOther(state, payload) {
    state.listBreakdownOther = payload
  },
  setListBreakdownTaxCharged(state, payload) {
    state.listBreakdownTaxCharged = payload
  },
  setListBreakdownReimbursementCosts(state, payload) {
    state.listBreakdownReimbursementCosts = payload
  },
  setListBreakdownShippingCost(state, payload) {
    state.listBreakdownShippingCost = payload
  },
  setListBreakdownChannelTaxWithheld(state, payload) {
    state.listBreakdownChannelTaxWithheld = payload
  },
  setListBreakdownSaleCharged(state, payload) {
    state.listBreakdownSaleCharged = payload
  },
  setListBreakdownReturnPostageBilling(state, payload) {
    state.listBreakdownReturnPostageBilling = payload
  },
  setChannelList(state, payload) {
    state.channelList = payload
  },
  setFormFilterOptions(state, payload) {
    state.formFilterOptions = payload
  },
  setCurrentCustomExportId(state, payload) {
    state.currentCustomExportId = payload
  },
  setCustomObject(state, payload) {
    state.customObject = payload
  }
}

const actions = {
  /**
   * This init all the state of the analysis table.
   *
   * 1. Preload filter
   * 2. Preload column set
   * 3. Preload view
   *
   * @param { [commit] } param0 Vuejx params
   * @param { any } payload Option to init the analysis table
   *  [client_id] current client id
   *  [user_id] current user id
   */
  resetAllConditions({ dispatch, commit }, payload) {
    dispatch('newFilter', payload)
    dispatch('newColumnSet', payload)
    dispatch('newView', payload)
  },
  async initSaleItemAnalyisTable({ dispatch, commit }, payload) {
    // this is required and need fetching synchronously
    await Promise.all([
      dispatch('fetchDSColumns', payload),
      dispatch('getChannelList', payload)
    ])
    // TODO should be done like this await dispatch('setDefaultColumnSet')
    // can load these stuffs asynchronously
    // concern these are not used anymore
    // data return not commit
    //
    // dispatch('getFilters', payload)
    // dispatch('getQuickSelectColumnSets', payload)
    // dispatch('getFavoriteQuickSelectColumnSets', payload)
    // dispatch('getQuickSelectFilters', payload)
    // dispatch('getFavoriteQuickSelectFilters', payload)
    // ##########################################
    // seem it's relevant, there is an interval action for this type
    // dispatch('pf/bulk/getBulkList', payload, { root: true })
    // ##########################################
    dispatch('getViews', payload)
    dispatch('getQuickSelectViews', payload)
    dispatch('getFavoriteQuickSelectViews', payload)
  },
  setFilter({ commit }, item) {
    commit('setFilter', item)
  },
  setOriginalFilter({ commit }, item) {
    commit('setOriginalFilter', item)
  },
  setColumnSet({ commit }, item) {
    commit('setColumnSet', item)
  },
  setOriginalColumnSet({ commit }, item) {
    commit('setOriginalColumnSet', item)
  },
  setView({ commit }, item) {
    commit('setView', item)
  },
  setOriginalView({ commit }, item) {
    commit('setOriginalView', item)
  },
  setReloadKeySDK({ commit }, id) {
    commit('changeSDKUniqueState')
  },
  setSDKConfig({ commit }, payload) {
    commit('setSDKConfig', payload)
  },
  discardFilter({ commit, state }) {
    commit('setFilter', _.cloneDeep(state.originalFilter))
  },
  discardColumnSet({ commit, state }) {
    commit('setColumnSet', _.cloneDeep(state.originalColumnSet))
  },
  discardView({ commit, state }) {
    commit('setView', _.cloneDeep(state.originalView))
  },
  newFilter({ commit, state }) {
    commit('setFilter', _.cloneDeep(DEFAULT_FILTER))
    commit('setOriginalFilter', _.cloneDeep(DEFAULT_FILTER))
  },
  newColumnSet({ commit, state }) {
    commit('setColumnSet', _.cloneDeep(DEFAULT_COLUMN_SET))
    commit('setOriginalColumnSet', _.cloneDeep(DEFAULT_COLUMN_SET))
  },
  newView({ commit }) {
    commit('setView', _.cloneDeep(DEFAULT_VIEW))
    commit('setOriginalView', _.cloneDeep(DEFAULT_VIEW))
  },
  fetchAllDataSourceIDs: async ({ commit }, params) => {
    if (!params.client_id) {
      throw Error('params.client_id is required')
    }
    commit('setAllDataSourceLoaded', false)
    return pfAxios.get(`/v1/clients/${params.client_id}/sale-items/ds/connection`).then(res => {
      commit('setAllDataSourceMap', res.data)
      commit('setAllDataSourceLoaded', true)
    }, () => {
      commit('setAllDataSourceLoaded', true)
    })
  },
  fetchDSColumns: async ({ commit, dispatch, state, getters }, params) => {
    let id = getters.dsIdOfStandardView
    return pfAxios.get(`/ds-proxy/v1/ds/${id}/columns`).then(res => {
      commit('setDSColumns', res.data.columns)
    })
  },
  setCurrentCustomExportId({ commit }, payload) {
    if (payload.id) localStorage.setItem(`customExportId-${payload.clientId}-${payload.userId}`, payload.id)
    else localStorage.removeItem(`customExportId-${payload.clientId}-${payload.userId}`)
    commit('setCurrentCustomExportId', payload.id)
  },
  createCustomObject({ commit }, payload) {
    return pfAxios.post(`/v1/clients/${payload.clientId}/custom-objects`, {content: payload.data}).then(res => {
      return res
    })
  },
  async fetchCustomObject({ commit }, payload) {
    try {
      const res = await pfAxios.get(`/v1/clients/${payload.clientId}/custom-objects/${payload.id}`)
      commit('setCustomObject', res.data.content)
    } catch (err) {
      return {}
    }
  },
  /**
   * TODO for now we need this because we don't have a sufficient way to mimic the table column config
   * So this method is to "reuse" the column config built by SDK table.
   * @param {*} {  commit } Vuex std arg
   * @param {*} tableConfig of the SDK and hiddenColumns
   */
  setDefaultColumnSet({ commit }, { tableConfig, hiddenColumns }) {
    const defaultTableConfig = _.cloneDeep(tableConfig)
    defaultTableConfig.columns = defaultTableConfig.columns.filter(column => {
      const isHiddenColumnManagerExist = hiddenColumns.columnManager.find(col => col.name === column.name)
      const isHiddenQueryBuilderExist = hiddenColumns.queryBuilder.find(col => col.name === column.name)
      return !isHiddenColumnManagerExist && !isHiddenQueryBuilderExist
    })
    DEFAULT_COLUMN_SET.ds_column.config = defaultTableConfig
    DEFAULT_VIEW.ds_column.config = defaultTableConfig
    commit('setOriginalColumnSet', _.cloneDeep(DEFAULT_COLUMN_SET))
    commit('setOriginalViewDSColumns', _.cloneDeep(DEFAULT_VIEW.ds_column))
  },
  // filter
  getFilters({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.search || ''
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-filters?page=${page}&limit=${limit}&search=${search}`).then(res => {
        res.data.results.map(configFilter => makeDefaultFilterConfig(configFilter.ds_filter))
        // commit('setFilterList', res.data)
      })
    )
  },
  getQuickSelectFilters({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.search || ''
    let featured = false
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-filters?page=${page}&limit=${limit}&search=${search}&featured=${featured}`).then(res => {
        res.data.results.map(configFilter => makeDefaultFilterConfig(configFilter.ds_filter))
        // commit('setFilterQuickSelectList', res.data)
      })
    )
  },
  getFavoriteQuickSelectFilters({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.search || ''
    let featured = true
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-filters?page=${page}&limit=${limit}&search=${search}&featured=${featured}`).then(res => {
        res.data.results.map(configFilter => makeDefaultFilterConfig(configFilter.ds_filter))
        // commit('setFavoriteFilterQuickSelectList', res.data)
      })
    )
  },
  createFilter({ commit, dispatch }, params) {
    let payload = {
      name: params.name,
      ds_filter: params.data,
      featured: params.featured
    }
    let clientId = params.client_id
    let userId = params.user_id
    return (
      pfAxios.post(`/v1/clients/${clientId}/users/${userId}/custom-filters`, payload).then((res) => {
        commit('setOriginalFilter', _.cloneDeep(res.data))
        commit('setFilter', res.data)
        dispatch('getFilters', params)
        dispatch('getQuickSelectFilters', params)
        dispatch('getFavoriteQuickSelectFilters', params)
      })
    )
  },
  updateFilter({ commit, dispatch }, params) {
    let payload = {
      name: params.name,
      ds_filter: params.data,
      featured: params.featured
    }
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.put(`/v1/clients/${clientId}/users/${userId}/custom-filters/${idItem}`, payload).then((res) => {
        commit('setOriginalFilter', _.cloneDeep(res.data))
        commit('setFilter', res.data)
        dispatch('getFilters', params)
        dispatch('getQuickSelectFilters', params)
        dispatch('getFavoriteQuickSelectFilters', params)
      })
    )
  },
  updateCurrentFilter({ commit, dispatch }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-filters/${idItem}`).then((res) => {
        commit('setFilter', res.data)
      })
    )
  },
  updateCurrentColumnSet({ commit, dispatch }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let columnId = params.item_id
    return pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-columns/${columnId}`).then(res => {
      commit('setColumnSet', res.data)
      commit('setOriginalColumnSet', _.cloneDeep(res.data))
    })
  },
  updateCurrentView({ commit, dispatch }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idView = params.item_id
    return pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-views/${idView}`).then(res => {
      commit('setView', res.data)
      commit('setOriginalView', _.cloneDeep(res.data))
    })
  },
  removeFilter({ commit, dispatch }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.delete(`/v1/clients/${clientId}/users/${userId}/custom-filters/${idItem}`)
    )
  },
  // columns
  getColumnSets({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.search || ''
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-columns?page=${page}&limit=${limit}&search=${search}`).then(res => {
        res.data.results.map(config => makeDefaultColumnConfig(config.ds_column))
        // commit('setColumnSetList', res.data)
      })
    )
  },
  getQuickSelectColumnSets({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.search || ''
    let featured = false
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-columns?page=${page}&limit=${limit}&search=${search}&featured=${featured}`).then(res => {
        res.data.results.map(config => makeDefaultColumnConfig(config.ds_column))
        // commit('setColumnSetQuickSelectList', res.data)
      })
    )
  },
  getFavoriteQuickSelectColumnSets({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.search || ''
    let featured = true
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-columns?page=${page}&limit=${limit}&search=${search}&featured=${featured}`).then(res => {
        res.data.results.map(config => makeDefaultColumnConfig(config.ds_column))
        // commit('setFavoriteColumnSetQuickSelectList', res.data)
      })
    )
  },
  createColumnSet({ commit, dispatch }, params) {
    let payload = {
      name: params.name,
      ds_column: params.data,
      featured: params.featured
    }
    let clientId = params.client_id
    let userId = params.user_id
    return (
      pfAxios.post(`/v1/clients/${clientId}/users/${userId}/custom-columns`, payload).then((res) => {
        commit('setOriginalColumnSet', _.cloneDeep(res.data))
        commit('setColumnSet', res.data)
        dispatch('getColumnSets', params)
        dispatch('getQuickSelectColumnSets', params)
        dispatch('getFavoriteQuickSelectColumnSets', params)
      })
    )
  },
  removeColumnSet({ commit, dispatch }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.delete(`/v1/clients/${clientId}/users/${userId}/custom-columns/${idItem}`).then(() => {
        dispatch('getColumnSets', params)
      })
    )
  },
  updateColumnSet({ commit, dispatch }, params) {
    let payload = {
      name: params.name,
      ds_column: params.data,
      featured: params.featured
    }
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.put(`/v1/clients/${clientId}/users/${userId}/custom-columns/${idItem}`, payload).then((res) => {
        commit('setOriginalColumnSet', _.cloneDeep(res.data))
        commit('setColumnSet', res.data)
        dispatch('getColumnSets', params)
        dispatch('getQuickSelectColumnSets', params)
        dispatch('getFavoriteQuickSelectColumnSets', params)
      })
    )
  },
  // view
  async getViews({ commit }, params) {
    try {
      let clientId = params.client_id
      let userId = params.user_id
      let page = params.page || 1
      let limit = params.limit || 20
      let search = params.search || ''
      let tag = params.tag || ''

      const res = await pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-views?page=${page}&limit=${limit}&search=${search}&tag=${tag}`)
      res.data.results.map(config => {
        makeDefaultFilterConfig(config.ds_filter)
        makeDefaultColumnConfig(config.ds_column)
      })
      commit('setViewList', res.data)
    } catch (err) {
      throw new Error(err)
    }
  },
  updateCustomView({ commit }, params) {
    const clientId = params.clientId
    const userId = params.userId
    const id = params.id
    const data = params.data
    return (
      pfAxios.put(`/v1/clients/${clientId}/users/${userId}/custom-views/${id}`, data).then(res => {
        return res
      })
    )
  },
  createAlertForView({ commit }, params) {
    const clientId = params.clientId
    const payload = params.payload
    return (
      pfAxios.post(`/v1/clients/${clientId}/alerts`, payload).then((res) => {
        return res
      })
    )
  },
  editAlertForView({ commit }, params) {
    const clientId = params.clientId
    const payload = params.payload
    const alertId = params.alertId
    return (
      pfAxios.put(`/v1/clients/${clientId}/alerts/${alertId}`, payload).then((res) => {
        return res
      })
    )
  },
  deleteAlertForView({ commit }, params) {
    const clientId = params.clientId
    const alertId = params.alertId
    return (
      pfAxios.delete(`/v1/clients/${clientId}/alerts/${alertId}`).then((res) => {
        return res
      })
    )
  },
  getQuickSelectViews({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 20
    let search = params.search || ''
    let featured = false
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-views?page=${page}&limit=${limit}&search=${search}&featured=${featured}`).then(res => {
        commit('setViewQuickSelectList', res.data)
      })
    )
  },
  getFavoriteQuickSelectViews({ commit }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let page = params.page || 1
    let limit = params.limit || 20
    let search = params.search || ''
    let featured = true
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-views?page=${page}&limit=${limit}&search=${search}&featured=${featured}`).then(res => {
        commit('setFavoriteViewQuickSelectList', res.data)
      })
    )
  },
  createView({ commit, dispatch }, params) {
    let payload = {
      name: params.name,
      ds_column: params.data.elements[0],
      ds_filter: params.data.filter,
      featured: params.featured
    }
    let clientId = params.client_id
    let userId = params.user_id
    return (
      pfAxios.post(`/v1/clients/${clientId}/users/${userId}/custom-views`, payload).then((res) => {
        commit('setOriginalView', _.cloneDeep(res.data))
        commit('setView', res.data)
        dispatch('getViews', params)
        dispatch('getQuickSelectViews', params)
        dispatch('getFavoriteQuickSelectViews', params)
      }).catch((err) => {
        throw err.response.data
      })
    )
  },
  removeView({ commit, dispatch }, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.delete(`/v1/clients/${clientId}/users/${userId}/custom-views/${idItem}`).then(() => {
        dispatch('getViews', params)
      })
    )
  },
  updateView({ commit, dispatch }, params) {
    let payload = {
      name: params.name,
      ds_column: params.data.elements[0],
      ds_filter: params.data.filter,
      featured: params.featured
    }
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.put(`/v1/clients/${clientId}/users/${userId}/custom-views/${idItem}`, payload).then((res) => {
        commit('setOriginalView', _.cloneDeep(res.data))
        commit('setView', res.data)
        dispatch('getViews', params)
        dispatch('getQuickSelectViews', params)
        dispatch('getFavoriteQuickSelectViews', params)
      })
    )
  },
  updateSaleItem({ commit }, data) {
    const { params, payload } = data
    let clientId = params.client_id
    let id = params.id
    return pfAxios.put(`/v1/clients/${clientId}/sale-items/${id}`, payload).then((data) => {
      return data
    }).catch((err) => {
      return err.response
    })
  },
  deleteSaleItem({ commit }, data) {
    let clientId = data.client_id
    let id = data.id
    return pfAxios.delete(`/v1/clients/${clientId}/sale-items/${id}`).then((data) => {
      return data
    }).catch((err) => {
      return err.response
    })
  },
  getAuditLogs({ commit }, data) {
    let clientId = data.client_id
    let { id, page, keyword } = data
    let url = `/v1/clients/${clientId}/sale-items/${id}/audit-logs?limit=5&page=${page}`
    if (keyword) {
      url = url + `&keyword=${keyword}`
    }
    return pfAxios.get(url).then((data) => {
      return data
    }).catch((err) => {
      return err
    })
  },
  // Event
  getListBreakdownListing({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=channel_listing_fee`).then((res) => {
        commit('setListBreakdownListing', res.data)
      })
    )
  },
  getListBreakdownOther({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=other_channel_fees`).then((res) => {
        commit('setListBreakdownOther', res.data)
      })
    )
  },
  getListBreakdownTaxCharged({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=tax_charged`).then((res) => {
        commit('setListBreakdownTaxCharged', res.data)
      })
    )
  },
  getListBreakdownReimbursementCosts({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=reimbursement_costs`).then((res) => {
        commit('setListBreakdownReimbursementCosts', res.data)
      })
    )
  },
  getListBreakdownShippingCost({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=shipping_cost`).then((res) => {
        commit('setListBreakdownShippingCost', res.data)
      })
    )
  },
  getListBreakdownChannelTaxWithheld({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=channel_tax_withheld`).then((res) => {
        commit('setListBreakdownChannelTaxWithheld', res.data)
      })
    )
  },
  getListBreakdownSaleCharged({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=sale_charged`).then((res) => {
        commit('setListBreakdownSaleCharged', res.data)
      })
    )
  },
  getListBreakdownReturnPostageBilling({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/${itemId}/events?column=return_postage_billing`).then((res) => {
        commit('setListBreakdownReturnPostageBilling', res.data)
      })
    )
  },

  getChannelList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    return (
      pfAxios.get(`/v1/clients/${clientId}/channels/`, { params: { page, limit } }).then(res => {
        commit('setChannelList', res.data)
      })
    )
  },
  setFormFilterOptions({ commit }, data) {
    commit('setFormFilterOptions', data)
  },
  getDataRowByChannelSaleId({ commit, state }, params) {
    BASE_QUERY_CHANNEL_SALE_ID.query.filter.conditions[0].value = params.channel_sale_id
    const id = getters.dsIdOfStandardView(state)
    return (
      pfAxios.post(`ds-proxy/v1/ds/${id}/exec`, BASE_QUERY_CHANNEL_SALE_ID).then(res => {
        return res.data
      })
    )
  },
  getTagSuggestions: async ({ commit }, payload) => {
    try {
      let clientId = payload.clientId
      const keyword = payload.keyword
      let res = await pfAxios.get(`/v1/clients/${clientId}/tags`, {params: { keyword }})
      return res.data
    } catch (err) {
      return err.response.data.statusCode
    }
  },
  getSaleItemVariation({ commit }, data) {
    let { clientId, hasVariation, type, keyword, queries } = data
    const page = data.page || 1
    const limit = ['brands'].includes(type) ? 9999 : data.limit || 20
    let url = `/v1/clients/${clientId}`
    url = hasVariation ? `${url}/variations/${type}` : `${url}/${type}`
    return pfAxios.get(url, { params: { search: keyword, ...queries, page, limit } }).then((data) => {
      return data
    }).catch((err) => {
      return err
    })
  },
  getAllBrands({ commit }, params) {
    let clientId = params.clientId
    let limit = 9999
    return pfAxios.get(`/v1/clients/${clientId}/brands`, { params: { limit, sort_direction: 'asc', sort_field: 'name' } }).then((data) => {
      return data
    }).catch((err) => {
      throw new Error(err)
    })
  }
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
