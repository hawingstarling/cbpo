import pfAxios from '@/services/pfAxios'

const state = {
  listTagByClient: [],
  viewsByClient: [],
  brandList: []
}

const getters = {
  listTagByClient: (state) => { return state.listTagByClient },
  viewsByClient: (state) => { return state.viewsByClient },
  brandList: (state) => { return state.brandList }
}

const mutations = {
  setTagByClient(state, payload) {
    state.listTagByClient = payload
  },
  setViewsByClient(state, payload) {
    state.viewsByClient = payload
  },
  setBrandList(state, payload) {
    state.brandList = payload
  }
}

const actions = {
  async getTagByClient({ commit }, params) {
    try {
      let clientId = params.client_id
      let page = params.page || 1
      let limit = params.limit || 100
      let keyword = params.keyword || ''
      const res = await pfAxios.get(`/v1/clients/${clientId}/tags`, {params: { limit: limit, page: page, keyword }})
      commit('setTagByClient', res.data.results)
    } catch (err) {
      throw new Error(err)
    }
  },
  async fetchViewsByClient({ commit }, params) {
    try {
      let clientId = params.clientId
      let page = params.page || 1
      let limit = params.limit || 10
      let keyword = params.keyword || ''
      const data = await pfAxios.get(`/v1/clients/${clientId}/custom-views/dropdown`, {params: { limit: limit, page: page, search: keyword }})
      commit('setViewsByClient', data.data.results)
    } catch (err) {
      throw new Error(err)
    }
  },
  createNewTag({ commit }, payload) {
    return pfAxios.post(`/v1/clients/${payload.clientId}/tags`, payload)
  },
  editTagView({ commit }, payload) {
    return pfAxios.put(`/v1/clients/${payload.clientId}/tags/${payload.tagId}`, payload)
  },
  addTagsToBulkView({ commit }, params) {
    let clientId = params.clientId
    const payload = {
      tag_ids: params.tagIds,
      custom_view_ids: params.customViewIds
    }
    return pfAxios.post(`/v1/clients/${clientId}/tags/bulk-views`, payload)
  },
  deleteBrand({ commit }, payload) {
    const clientId = payload.client_id
    const id = payload.id
    return (
      pfAxios.delete(`/v1/clients/${clientId}/brands/${id}`).then(res => {
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
