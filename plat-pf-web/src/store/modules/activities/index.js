import pfAxios from '@/services/pfAxios'

const state = {
  activitiesList: []
}

const getters = {
  activitiesList: (state) => { return state.activitiesList }
}

const mutations = {
  setActivitiesList(state, payload) {
    state.activitiesList = payload
  }
}

const actions = {
  getActivitiesList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    let key = params.key || ''
    return (
      pfAxios.get(`/v1/clients/${clientId}/activity?page=${page}&limit=${limit}&key=${key}`).then(res => {
        commit('setActivitiesList', res.data)
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
