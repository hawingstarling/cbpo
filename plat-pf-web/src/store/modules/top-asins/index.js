import pfAxios from '@/services/pfAxios'

const keyCurrentListTopASINsExportId = 'currentListTopASINsExportId'

const state = {
  topASINsList: [],
  topASIN: null,
  currentListTopASINsExportId: localStorage.getItem(keyCurrentListTopASINsExportId)
}

const getters = {
  topASINsList: (state) => { return state.topASINsList },
  topASIN: (state) => { return state.topASIN },
  currentListTopASINsExportId: (state) => { return state.currentListTopASINsExportId }
}

const mutations = {
  setTopASINsList(state, payload) {
    state.topASINsList = payload
  },
  setTopASIN(state, payload) {
    state.topASIN = payload
  },
  setCurrentListTopASINsExportId(state, payload) {
    state.currentListTopASINsExportId = payload
  }
}

const actions = {
  getTopASINsList({ commit }, { clientId, page = 1, limit = 10, key = '', channel, sortDirection = null, sortField = null }) {
    let search = key

    return (
      pfAxios.get(`/v1/clients/${clientId}/top-asins/`, {
        params: {
          limit: limit,
          page: page,
          search: search,
          channel: channel || null,
          sort_field: sortField,
          sort_direction: sortDirection
        }}).then(res => {
        commit('setTopASINsList', res.data)
      })
    )
  },
  editTopASIN({ commit }, params) {
    let clientId = params.client_id
    let id = params.id
    let payload = {
      channel: params.item_edit.channel,
      parent_asin: params.item_edit.parent_asin,
      child_asin: params.item_edit.child_asin,
      client: params.item_edit.client,
      segment: params.item_edit.segment
    }
    return (
      pfAxios.patch(`/v1/clients/${clientId}/top-asins/${id}/`, payload)
    )
  },
  async exportTopASINs({ commit, dispatch }, params) {
    const { clientId, payload } = params
    const customReportType = 'TopASINs'
    try {
      const res = await pfAxios.post(`/v1/clients/${clientId}/custom-reports/${customReportType}/export`, payload)
      const currentExportId = res.data.id
      dispatch('setCurrentListTopASINsExportId', currentExportId)
    } catch (err) {
      dispatch('setCurrentListTopASINsExportId', null)
      throw err
    }
  },
  async deleteTopASIN({ commit }, payload) {
    const {clientId, id} = payload
    try {
      return pfAxios.delete(`/v1/clients/${clientId}/top-asins/${id}`)
    } catch (err) {
      throw err
    }
  },
  async getListTopASINsExportPercent({ commit }, params) {
    const {clientId, userId, id} = params
    try {
      const res = await pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`)
      return res.data
    } catch (err) {
      throw err
    }
  },
  setCurrentListTopASINsExportId({ commit }, payload) {
    if (payload) {
      commit('setCurrentListTopASINsExportId', payload)
      localStorage.setItem(keyCurrentListTopASINsExportId, payload)
    } else {
      commit('setCurrentListTopASINsExportId', null)
      localStorage.removeItem(keyCurrentListTopASINsExportId)
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
