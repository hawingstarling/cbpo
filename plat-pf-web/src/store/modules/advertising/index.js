import pfAxios from '@/services/pfAxios'

const state = {
  advertisingDsId: ''
}

const getters = {
  advertisingdsId: (state) => { return state.advertisingDsId }
}

const mutations = {
  setAdvertisingDsId(state, payload) {
    if (payload['ADVERTISING']) {
      state.advertisingDsId = payload['ADVERTISING'].data_source_id
    } else {
      state.advertisingDsId = ''
    }
  }
}

const actions = {
  fetchAdvertisingDSId: async ({ commit }, params) => {
    let clientId = params.client_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/sale-items/ds/connection?ds_type=ADVERTISING`).then(res => {
        commit('setAdvertisingDsId', res.data)
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
