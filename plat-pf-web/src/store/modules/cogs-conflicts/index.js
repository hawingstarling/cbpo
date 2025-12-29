import pfAxios from '@/services/pfAxios'

const keyCurrentCogsConflictsExportId = 'currentCogsConflictsExportId'

const state = {
  cogsConflictsList: [],
  cogsConflictsCount: 0,
  channelList: [],
  currentCogsConflictsExportId: localStorage.getItem(keyCurrentCogsConflictsExportId)
}

const mutations = {
  setCogsConflictsList(state, payload) {
    state.cogsConflictsList = payload.results || []
    state.cogsConflictsCount = payload.count || 0
  },
  setCurrentCogsConflictsExportId(state, payload) {
    state.currentCogsConflictsExportId = payload
  },
  setChannelList(state, payload) {
    state.channelList = payload
  }
}

const actions = {
  async getCogsConflictsList(
    { commit },
    { clientId, page = 1, limit = 20, channel = '', status = '', usedCog = '', search = '', sortDirection = '', sortField = '' }
  ) {
    try {
      const params = {
        page: page,
        limit: limit,
        status: status
      }
      if (channel) params.channel = channel
      if (usedCog) params.used_cog = usedCog
      if (search) params.search = search
      if (sortField) {
        params.sort_field = sortField
        params.sort_direction = sortDirection || 'desc'
      }

      const res = await pfAxios.get(`/v1/clients/${clientId}/extensiv-cogs-conflict`, {params})
      commit('setCogsConflictsList', res.data)
    } catch (e) {
      commit('setCogsConflictsList', { results: [], count: 0 })
      throw e
    }
  },
  async exportCogsConflicts({ commit, dispatch }, params) {
    const { clientId, payload } = params
    const customReportType = 'COGSConflict'
    try {
      const res = await pfAxios.post(`/v1/clients/${clientId}/custom-reports/${customReportType}/export`, payload)
      const currentExportId = res.data.id
      dispatch('setCurrentCogsConflictsExportId', currentExportId)
    } catch (err) {
      dispatch('setCurrentCogsConflictsExportId', null)
      throw err
    }
  },
  async getCogsConflictsExportPercent({ commit }, params) {
    const {clientId, userId, id} = params
    try {
      const res = await pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`)
      return res.data
    } catch (err) {
      throw err
    }
  },
  setCurrentCogsConflictsExportId({ commit }, payload) {
    if (payload) {
      commit('setCurrentCogsConflictsExportId', payload)
      localStorage.setItem(keyCurrentCogsConflictsExportId, payload)
    } else {
      commit('setCurrentCogsConflictsExportId', null)
      localStorage.removeItem(keyCurrentCogsConflictsExportId)
    }
  },
  async getChannelList({ commit }, { clientId }) {
    try {
      const response = await pfAxios.get(`/v1/clients/${clientId}/channels/`)
      if (response.data && response.data.results) {
        commit('setChannelList', response.data.results)
        return response.data.results
      }
      commit('setChannelList', [])
      return []
    } catch (error) {
      console.error('Error fetching channels:', error)
      commit('setChannelList', [])
      throw error
    }
  }
}

const getters = {
  cogsConflictsList: state => state.cogsConflictsList,
  cogsConflictsCount: state => state.cogsConflictsCount,
  currentCogsConflictsExportId: state => state.currentCogsConflictsExportId,
  channelList: state => state.channelList
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
