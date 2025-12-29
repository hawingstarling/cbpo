import pfAxios from '@/services/pfAxios'

const keyCurrentListItemExportId = 'currentListItemExportId'

const state = {
  listItems: [],
  editData: {},
  listCogs: [],
  currentListItemExportId: localStorage.getItem(keyCurrentListItemExportId)
}

let itemsPaging = {
  page: 1,
  limit: 10,
  search: ''
}

const getters = {
  listItems: (state) => { return state.listItems },
  editData: (state) => { return state.editData },
  listCogs: (state) => { return state.listCogs },
  currentListItemExportId: (state) => { return state.currentListItemExportId }
}

const mutations = {
  setListItems(state, payload) {
    state.listItems = payload
  },
  setEditData(state, payload) {
    state.editData = payload
  },
  setListCogs(state, payload) {
    state.listCogs = payload
  },
  setCurrentListItemExportId(state, payload) {
    state.currentListItemExportId = payload
  }
}

const actions = {
  setEditData({ commit }, params) {
    commit('setEditData', params.editData)
  },
  // Item
  getListItems({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || itemsPaging.page
    let limit = params.limit || itemsPaging.limit
    let search = params.key || itemsPaging.search
    let brand = params.brand || null
    let channel = params.channel
    return (
      pfAxios.get(`/v1/clients/${clientId}/items/`, {
        params: {page, limit, keyword: search, channel, brand}
      }).then(res => {
        commit('setListItems', res.data)
      })
    )
  },
  removeItem({ commit, dispatch }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    return (
      pfAxios.delete(`/v1/clients/${clientId}/items/${itemId}`).then(() => {
        dispatch('getListItems', params)
      })
    )
  },
  updateItem({ commit, dispatch }, params) {
    let payload = params.payload
    let clientId = params.client_id
    let idItem = params.id
    return (
      pfAxios.put(`/v1/clients/${clientId}/items/${idItem}/`, payload).then(() => {
        dispatch('getListItems', params)
      })
    )
  },
  // COG
  getListCogs({ commit }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    let page = 1
    let limit = 30
    return (
      pfAxios.get(`/v1/clients/${clientId}/items/${itemId}/cogs/?page=${page}&limit=${limit}`).then((res) => {
        commit('setListCogs', res.data)
      })
    )
  },
  removeCog({ commit, dispatch }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    let idCog = params.cog_id
    return (
      pfAxios.delete(`/v1/clients/${clientId}/items/${itemId}/cogs/${idCog}/`).then(() => {
        dispatch('getListCogs', params)
        dispatch('getListItems', params)
      })
    )
  },
  addCog({ commit, dispatch }, params) {
    let clientId = params.client_id
    let itemId = params.item_id
    let payload = params.payload
    return (
      pfAxios.post(`/v1/clients/${clientId}/items/${itemId}/cogs/`, payload).then(() => {
        dispatch('getListCogs', params)
        dispatch('getListItems', params)
      })
    )
  },
  // export Items
  async createListItemExport({ commit, dispatch }, params) {
    const { clientId, payload } = params
    const customReportType = 'Items'
    try {
      const res = await pfAxios.post(`/v1/clients/${clientId}/custom-reports/${customReportType}/export`, payload)
      const currentExportId = res.data.id
      dispatch('setCurrentListItemExportId', currentExportId)
    } catch (err) {
      dispatch('setCurrentListItemExportId', null)
      throw err
    }
  },
  async getListItemExportPercent({ commit }, params) {
    const {clientId, userId, id} = params
    try {
      const res = await pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`)
      return res.data
    } catch (err) {
      throw err
    }
  },
  setCurrentListItemExportId({ commit }, payload) {
    if (payload) {
      commit('setCurrentListItemExportId', payload)
      localStorage.setItem(keyCurrentListItemExportId, payload)
    } else {
      commit('setCurrentListItemExportId', null)
      localStorage.removeItem(keyCurrentListItemExportId)
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
