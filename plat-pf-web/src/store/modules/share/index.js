import pfAxios from '@/services/pfAxios'

const state = {
  listIdSharedFilter: [],
  listIdSharedColumns: [],
  listIdSharedViews: []
}

const getters = {
  listIdSharedFilter: (state) => { return state.listIdSharedFilter },
  listIdSharedColumns: (state) => { return state.listIdSharedColumns },
  listIdSharedViews: (state) => { return state.listIdSharedViews }
}

const mutations = {
  setListIdSharedFilter (state, payload) {
    state.listIdSharedFilter = payload
  },
  setListIdSharedColumns (state, payload) {
    state.listIdSharedColumns = payload
  },
  setListIdSharedViews (state, payload) {
    state.listIdSharedViews = payload
  }
}

const actions = {
  // filter
  getListIdSharedFilter ({commit}, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-filters/${idItem}/share-mode`).then(res => {
        commit('setListIdSharedFilter', res.data)
      })
    )
  },
  postFilterShareMode ({commit, dispatch}, params) {
    let payload = {
      share_mode: params.share_mode,
      shared_users: params.shared_users
    }
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.post(`/v1/clients/${clientId}/users/${userId}/custom-filters/${idItem}/share-mode`, payload).then(() => {
        dispatch('getListIdSharedFilter', params)
      })
    )
  },
  // columns
  getListIdSharedColumns ({commit}, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-columns/${idItem}/share-mode`).then(res => {
        commit('setListIdSharedColumns', res.data)
      })
    )
  },
  postColumnsShareMode ({commit, dispatch}, params) {
    let payload = {
      share_mode: params.share_mode,
      shared_users: params.shared_users
    }
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.post(`/v1/clients/${clientId}/users/${userId}/custom-columns/${idItem}/share-mode`, payload).then(() => {
        dispatch('getListIdSharedColumns', params)
      })
    )
  },
  // views
  getListIdSharedViews ({commit}, params) {
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-views/${idItem}/share-mode`).then(res => {
        commit('setListIdSharedViews', res.data)
      })
    )
  },
  postViewsShareMode ({commit, dispatch}, params) {
    let payload = {
      share_mode: params.share_mode,
      shared_users: params.shared_users
    }
    let clientId = params.client_id
    let userId = params.user_id
    let idItem = params.id_item
    return (
      pfAxios.post(`/v1/clients/${clientId}/users/${userId}/custom-views/${idItem}/share-mode`, payload).then(() => {
        dispatch('getListIdSharedViews', params)
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
