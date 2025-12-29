import pfAxios from '@/services/pfAxios'
import _ from 'lodash'

const state = {
  importHistoryList: [],
  importModuleKeys: [],
  shippingInvoicesList: [],
  shippingInvoiceTransactionList: [],
  currentExportShipmentBreaksId: localStorage.getItem('currentExportShipmentBreaksId'),
  currentExportShippingInvoicesTransactionsBreaksId: localStorage.getItem('currentExportShippingInvoicesTransactionsBreaksId'),
  totalShippingInvoice: 0,
  currentShippingInvoiceNumber: null,
  currentExportUnmatchedTransactionsId: localStorage.getItem('currentExportUnmatchedTransactionsId')
}

const getters = {
  importHistoryList: (state) => { return state.importHistoryList },
  shippingInvoicesList: (state) => { return state.shippingInvoicesList },
  importModuleKeys: (state) => { return state.importModuleKeys },
  shippingInvoiceTransactionList: (state) => { return state.shippingInvoiceTransactionList },
  currentExportShipmentBreaksId: (state) => { return state.currentExportShipmentBreaksId },
  currentExportShippingInvoicesTransactionsBreaksId: (state) => { return state.currentExportShippingInvoicesTransactionsBreaksId },
  totalShippingInvoice: (state) => state.totalShippingInvoice,
  currentExportUnmatchedTransactionsId: (state) => state.currentExportUnmatchedTransactionsId
}

const buildParamSearch = (key, value) => {
  if (key === 'All') return { 'keyword': value }
  return {
    [_.snakeCase(key)]: value
  }
}

const mutations = {
  setImportHistoryList(state, payload) {
    const results = payload.results.map(item => {
      return {
        ...item,
        row_count: item.summary.total,
        row_processed: item.summary.completed,
        row_errors: item.summary.total - (item.summary.total - item.summary.valid) - item.summary.completed,
        entries_created: item.summary.created,
        entries_modified: item.summary.updated,
        entries_ignored: item.summary.ignored
      }
    })
    state.importHistoryList = { ...payload, results }
  },
  setEmptyImportHistoryList(state, payload) {
    state.importHistoryList.results = []
  },
  setShippingInvoicesList(state, payload) {
    state.shippingInvoicesList = payload
  },
  setImportModuleKeys(state, payload) {
    const results = [{ text: 'All', value: null }]
    for (const [key, value] of Object.entries(payload)) {
      results.push({ text: value, value: key })
    }
    state.importModuleKeys = results
  },
  setShippingInvoicesTransactionList(state, payload) {
    state.shippingInvoiceTransactionList = payload
  },
  setCurrentExportShipmentBreaksId(state, payload) {
    state.currentExportShipmentBreaksId = payload
  },
  setCurrentShippingInvoicesTransactionsBreaksId(state, payload) {
    state.currentExportShippingInvoicesTransactionsBreaksId = payload
  },
  setTotalShippingInvoice(state, payload) {
    state.totalShippingInvoice = payload
  },
  setCurrentShippingInvoiceNumber(state, payload) {
    state.currentShippingInvoiceNumber = payload
  },
  setCurrentExportUnmatchedTransactionsId(state, payload) {
    state.currentExportUnmatchedTransactionsId = payload
  }
}

const actions = {
  getshippingInvoicesList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.key || ''
    let status = params.status
    let source = params.source
    let sortDirection = params.sortDirection || 'desc'
    let sortField = params.sortField || ''
    let fromDate = params.fromDate || ''
    let toDate = params.toDate || ''
    return (
      pfAxios.get(`/v1/clients/${clientId}/shipping-invoices/`, {params: { limit: limit, page: page, keyword: search, status, source, sort_field: sortField, sort_direction: sortDirection, from_date: fromDate, to_date: toDate }}).then(res => {
        commit('setShippingInvoicesList', res.data)
      })
    )
  },
  getImportHistoryList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.key || ''
    let status = params.status
    let type = params.type
    let sortDirection = params.sortDirection || 'desc'
    let sortField = params.sortField || ''
    let fromDate = params.fromDate || ''
    let toDate = params.toDate || ''
    let fieldSearch = params.fieldSearch
    return (
      pfAxios.get(`/v1/clients/${clientId}/imports/history`, {params: { limit: limit, page: page, ...buildParamSearch(fieldSearch, search), status, module: type, sort_field: sortField, sort_direction: sortDirection, from_date: fromDate, to_date: toDate }}).then(res => {
        commit('setImportHistoryList', res.data)
      })
    )
  },
  getImportModuleKeys({ commit }, params) {
    let clientId = params.client_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/imports/modules-keys`).then(res => {
        commit('setImportModuleKeys', res.data)
      })
    )
  },
  getShippingInvoiceTransactionList({ commit }, params) {
    let clientId = params.client_id
    let shippingInvoiceId = params.shipping_invoice_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.key || ''
    let status = params.status
    let source = params.source
    let sortDirection = params.sortDirection || 'desc'
    let sortField = params.sortField || ''
    let fromDate = params.fromDate || ''
    let toDate = params.toDate || ''
    return (
      pfAxios.get(`/v1/clients/${clientId}/shipping-invoices/${shippingInvoiceId}/transactions`, {params: { limit: limit, page: page, keyword: search, status, source, sort_field: sortField, sort_direction: sortDirection, from_date: fromDate, to_date: toDate }}).then(res => {
        commit('setShippingInvoicesTransactionList', res.data)
      })
    )
  },
  async getMatchedSales({ commit }, params) {
    let clientId = params.client_id
    let shippingInvoiceId = params.shipping_invoice_id
    const res = await pfAxios.get(`/v1/clients/${clientId}/shipping-invoices/${shippingInvoiceId}/matched-sales`)
    debugger
    return res.data.sale_ids
  },
  createshippingInvoicesExport({ commit, dispatch }, params) {
    const { clientId, payload } = params
    return (
      pfAxios.post(`/v1/clients/${clientId}/shipping-invoices/export/`, payload).then(res => {
        dispatch('setCurrentExportShipmentBreaksId', res.data.id)
      })
    )
  },
  async createShippingInvoiceTransactionExport({ commit, dispatch }, params) {
    const { clientId, payload } = params
    try {
      const res = await pfAxios.post(`/v1/clients/${clientId}/shipping-invoices-transactions/export/`, payload)
      dispatch('setCurrentExportShippingInvoicesTransactionsBreaksId', res.data.id)
    } catch (err) {
      dispatch('setCurrentExportShippingInvoicesTransactionsBreaksId', null)
    }
  },
  getShippingInvoicesExportPercent({ commit }, params) {
    const { clientId, userId, id } = params
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`, {ignoreLoading: true}).then(res => {
        return res
      })
    )
  },
  async getShippingInvoicesExportPercentAsync({ commit }, params) {
    const { clientId, userId, id } = params
    try {
      const res = await pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`)
      return res.data
    } catch (err) {
      throw err
    }
  },
  setCurrentExportShipmentBreaksId({ commit }, payload) {
    if (payload) localStorage.setItem('currentExportShipmentBreaksId', payload)
    else localStorage.removeItem('currentExportShipmentBreaksId')
    commit('setCurrentExportShipmentBreaksId', payload)
  },
  setCurrentExportShippingInvoicesTransactionsBreaksId({ commit }, payload) {
    if (payload) localStorage.setItem('currentExportShippingInvoicesTransactionsBreaksId', payload)
    else localStorage.removeItem('currentExportShippingInvoicesTransactionsBreaksId')
    commit('setCurrentShippingInvoicesTransactionsBreaksId', payload)
  },
  setCurrentExportUnmatchedTransactionsId({ commit }, payload) {
    if (payload) localStorage.setItem('currentExportUnmatchedTransactionsId', payload)
    else localStorage.removeItem('currentExportUnmatchedTransactionsId')
    commit('setCurrentExportUnmatchedTransactionsId', payload)
  },
  async getTotalShippingInvoice({commit}, params) {
    const clientId = params.client_id
    try {
      const res = await pfAxios.get(`/v1/clients/${clientId}/shipping-invoices/`, {params: { limit: 1 }})
      commit('setTotalShippingInvoice', res.data.count)
    } catch (err) {
      commit('setTotalShippingInvoice', 0)
    }
  },
  async createExportUnmatchedTransactions({commit, dispatch}, params) {
    const clientId = params.client_id
    const payload = params.payload
    try {
      const res = await pfAxios.post(`v1/clients/${clientId}/shipping-invoices-transactions/export/unmatched`, payload)
      dispatch('setCurrentExportUnmatchedTransactionsId', res.data.id)
      return res.data
    } catch (err) {
      dispatch('setCurrentExportUnmatchedTransactionsId', null)
      throw new Error(err)
    }
  },
  getExportUnmatchedTransactionsPercent({ commit }, params) {
    const { clientId, userId, id } = params
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`, {ignoreLoading: true}).then(res => {
        return res
      })
    )
  }
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
