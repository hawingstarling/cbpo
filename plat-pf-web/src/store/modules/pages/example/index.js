// import mtAxios from '@/services/mtAxios'
// import authSvc from '@/services/authSvc'
import _ from 'lodash'

const state = {
  items: [],
  pageCount: 0,
  pageSize: 10,
  pageCurrent: 1,
  total: 0,
  dashboardFields: [
  ],
  dashboard: {}
}

const getters = {
  getDashboardItems: (state) => state.items,
  getDashboardFields: (state) => state.dashboardFields,
  getDashboardPageSize: (state) => state.pageSize,
  getDashboardPageCurrent: (state) => state.pageCurrent,
  getDashboardPageTotal: (state) => state.total,
  getDashboardPageCount: (state) => state.pageCount,
  getOneDashboard: (state) => state.dashboard
}

const mutations = {
  setDashboardData: (state, payload) => {
    state.pageCount = payload.page_count
    state.pageSize = payload.page_size
    state.pageCurrent = payload.page_current
    state.total = payload.total
    state.items = payload.items
    state.items = _.map(payload.items, (i) => ({ ...i }))
  },
  saveOneDashboard(state, payload) {
    state.dashboard = { ...payload }
  }
}

const actions = {
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
