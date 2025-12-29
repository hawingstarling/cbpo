import pfAxios from '@/services/pfAxios'

const state = {
  appEagleProfileList: []
}

const getters = {
  appEagleProfileList: (state) => { return state.appEagleProfileList }
}

const mutations = {
  setAppEagleProfileList(state, payload) {
    state.appEagleProfileList = payload
  }
}

const actions = {
  getAppEagleProfileList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    let keyword = params.key || ''
    return (
      pfAxios.get(`/v1/clients/${clientId}/app-eagle-profile/`, {params: {limit: limit, page: page, keyword: keyword}}).then(res => {
        commit('setAppEagleProfileList', res.data)
      })
    )
  },
  removeProfile({ commit, dispatch }, params) {
    let clientId = params.client_id
    let profileId = params.profile_id
    return (
      pfAxios.delete(`/v1/clients/${clientId}/app-eagle-profile/${profileId}`).then(() => {
        dispatch('getAppEagleProfileList', params)
      })
    )
  },
  editProfile({ commit }, params) {
    let clientId = params.client_id
    let profileId = params.profile_id
    let payload = {
      profile_name: params.profile_edit.profile_name,
      profile_id_link: params.profile_edit.profile_id_link
    }
    return (
      pfAxios.patch(`/v1/clients/${clientId}/app-eagle-profile/${profileId}/`, payload)
    )
  },
  exporProfile({ commit }, params) {
    let clientId = params.client_id
    let query = params.query
    return (
      pfAxios.get(`/v1/clients/${clientId}/app-eagle-profile/export/`, {params: query})
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
