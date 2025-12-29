import _ from 'lodash'
import pfAxios from '@/services/pfAxios'

// limit num of quick select item in dropdown
const QUICK_ITEM_LIMIT = 5

const state = {
  bulkList: [],
  currentBulkProgressDetail: null,
  importItems: null,
  lastListAPICallAt: null,
  bulkTypeFilterList: []
}

const getters = {
  bulkList: (state) => { return state.bulkList },
  currentBulkProgressDetail: (state) => { return state.currentBulkProgressDetail },
  importItems: (state) => { return state.importItems },
  lastListAPICallAt: (state) => { return state.lastListAPICallAt },
  bulkTypeFilterList: (state) => { return state.bulkTypeFilterList },

  quickSelectBulks: (state) => {
    return _.get(state.bulkList, 'results', []).slice(0, QUICK_ITEM_LIMIT)
  }
}

const mutations = {
  setBulkList(state, payload) {
    state.bulkList = payload
    state.lastListAPICallAt = new Date()
  },
  setBulkProgressDetail(state, payload) {
    state.currentBulkProgressDetail = payload
  },
  setImportItems(state, payload) {
    state.importItems = payload
  },
  setBulkTypeFilterList(state, payload) {
    state.bulkTypeFilterList = payload
  }
}

const actions = {
  updateBulkSaleItems({ commit }, data) {
    const { params, payload } = data
    let clientId = params.client_id
    return pfAxios.post(`/v1/clients/${clientId}/sale-items/bulk-edit`, payload).then((data) => {
      return data
    }).catch((err) => {
      return err.response
    })
  },
  deleteBulkSaleItems({ commit }, data) {
    const { params, payload } = data
    let clientId = params.client_id
    return pfAxios.post(`/v1/clients/${clientId}/sale-items/bulk-delete`, payload).then((data) => {
      return data
    }).catch((err) => {
      return err.response
    })
  },
  getBulkList({ commit }, params) {
    let clientId = params.client_id
    const ignoreLoading = params.ignoreLoading || false
    const bulkListParams = {
      page: params.page || 1,
      limit: params.limit || 10,
      status: params.status,
      search: params.search
    }
    return pfAxios.get(`/v1/clients/${clientId}/sale-items/bulk`, { ignoreLoading: ignoreLoading, params: bulkListParams }).then((res) => {
      commit('setBulkList', res.data)
    })
  },
  cancelBulkProgress({ commit }, data) {
    const { clientId, id } = data
    return pfAxios.put(`/v1/clients/${clientId}/bulk-progress/${id}/cancellation`).then((res) => { console.log('res', res) })
  },
  getBulkProgressDetail({ commit }, params) {
    let clientId = params.client_id
    let bulkId = params.bulk_id
    let page = params.page || 1
    let limit = params.limit || 10
    return pfAxios.get(`/v1/clients/${clientId}/sale-items/bulk/${bulkId}?page=${page}&limit=${limit}`).then((res) => {
      commit('setBulkProgressDetail', res.data)
    })
  },
  getImportItems({ commit }, params) {
    let bulkId = params.bulk_id
    let module = params.module
    let search = params.search || ''
    let page = params.page || 1
    return pfAxios.get(`/v1/imports/${module}/${bulkId}/items`, { params: { s: search, page: page } }).then((res) => {
      commit('setImportItems', res.data)
    })
  },
  createBulkSync({ commit }, data) {
    const { params, payload } = data
    let clientId = params.client_id
    return pfAxios.post(`/v1/clients/${clientId}/sale-items/bulk-sync`, payload).then((data) => {
      return data
    }).catch((err) => {
      return err.response
    })
  },
  getListBulkTypeFilter({ commit }, data) {
    const clientId = data.client_id
    return pfAxios.get(`/v1/clients/${clientId}/sale-items/bulk-filter-type`).then((res) => {
      commit('setBulkTypeFilterList', res.data.status)
    }).catch((err) => {
      return err.response
    })
  },
  revertBulkEdit({ commit }, data) {
    const clientId = data.client_id
    const bulkId = data.bulk_id
    return pfAxios.post(`/v1/clients/${clientId}/sale-items/revert-bulk-edit/${bulkId}`).then((res) => {
      return res
    })
  },
  createCustomExport({ commit }, data) {
    const { params, payload } = data
    let clientID = params.clientID
    let userID = params.userID
    return pfAxios.post(`/v1/clients/${clientID}/users/${userID}/custom-reports`, payload).then((res) => {
      return res
    })
  },
  getCustomExport({ commit }, data) {
    const { params, id } = data
    let clientID = params.clientID
    let userID = params.userID
    return pfAxios.get(`/v1/clients/${clientID}/users/${userID}/custom-reports/${id}`, {ignoreLoading: true}).then((res) => {
      return res
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
