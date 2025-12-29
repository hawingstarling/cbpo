import pfAxios from '@/services/pfAxios'

const state = {
  dsIdForMapping: []
}

const getters = {
  dsIdForMapping: (state) => { return state.dsIdForMapping }
}

const mutations = {
  setDSIdForMapping(state, payload) {
    state.dsIdForMapping = payload
  }
}

const actions = {
  fetchDSIdForMapping: async ({ commit }, params) => {
    let clientId = params.client_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/ds/connection`).then(res => {
        commit('setDSIdForMapping', res.data)
      })
    )
  },
  fetchGetTopProductPerformance: async ({ commit }, params) => {
    try {
      let clientId = params.client_id
      const result = await pfAxios.get(`/v1/clients/${clientId}/top-product-performance`)
      return result.data
    } catch (err) {
      throw new Error(err)
    }
  },
  fetchWidgetsDashboard: async ({ commit }, params) => {
    try {
      const clientId = params.client_id
      const dashboard = params.dashboard
      const res = await pfAxios.get(`v1/clients/${clientId}/dashboard/${dashboard}/widgets`)
      return res.data.results
    } catch (err) {
      throw new Error(err)
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
