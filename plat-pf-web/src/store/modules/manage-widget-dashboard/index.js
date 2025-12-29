import pfAxios from '@/services/pfAxios'

const state = {
}

const getters = {
}

const mutations = {
}

const actions = {
  fetchWidgetsDashboard: async ({ commit }, params) => {
    try {
      const clientId = params.client_id
      const dashboard = params.dashboard
      const res = await pfAxios.get(`v1/clients/${clientId}/dashboard/${dashboard}/widgets`)
      return res.data.results
    } catch (err) {
      throw new Error(err)
    }
  },
  saveWidgetsDashboard: async ({ commit }, params) => {
    try {
      const clientId = params.client_id
      const dashboard = params.dashboard
      const payload = params.payload
      const res = await pfAxios.put(`v1/clients/${clientId}/dashboard/${dashboard}/widgets-manages`, payload)
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
