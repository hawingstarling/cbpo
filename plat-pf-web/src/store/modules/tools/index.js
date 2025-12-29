import pfAxios from '@/services/pfAxios'

const state = {
  statusWorkspace: '',
  statusDataSource: '',
  list: [
    {
      name: { title: 'Sync Workspace', icon: 'fa fa-refresh' },
      status: '',
      action: 'Sync',
      type: 'workspace'
    },
    {
      name: { title: 'Data source', icon: 'fa fa-database' },
      status: '',
      action: 'Sync',
      type: 'datasource'
    }
  ]
}

const getters = {
  statusDataSource: state => {
    return state.statusDataSource
  },
  statusGenerateWorkspace: state => {
    return state.statusWorkspace
  },
  listTools: state => {
    return state.list
  }
}

const mutations = {
  setStatus(state, payload) {
    state.list[payload.idx].status = payload.status
  }
}

const actions = {
  getStatus({ commit }, params) {
    const type = params.type
    const clientId = params.client_id
    const idx = params.idx
    let url = ``
    if (type.toLowerCase() === 'workspace') {
      url = `/v1/clients/${clientId}/sync`
    } else if (type.toLowerCase() === 'datasource') {
      url = `/v1/clients/${clientId}/sale-items/flatten/status`
    }
    return pfAxios
      .get(url)
      .then(() => {
        commit('setStatus', { idx, status: 'SUCCESS' })
      })
      .catch(() => {
        commit('setStatus', { idx, status: 'ERROR' })
      })
  },

  getSync({ commit }, params) {
    const clientId = params.client_id
    const idx = params.idx
    const type = params.type
    let url = ``
    if (type === 'workspace') {
      url = `/v1/clients/${clientId}/sync`
    } else if (type === 'datasource') {
      url = `/v1/clients/${clientId}/sale-items/flatten/generate`
    } else return
    return pfAxios
      .post(url)
      .then(() => {
        commit('setStatus', { status: 'SUCCESS', idx })
      })
      .catch(() => {
        commit('setStatus', { status: 'ERROR', idx })
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
