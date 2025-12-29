import pfAxios from '@/services/pfAxios'

import { isArray } from 'lodash'

const formatDataDropdown = (items, idx = 0) => {
  if (!items) return []
  return items.map(item => {
    if (isArray(item.sub_categories) && item.sub_categories.length > 0) {
      const listChildItem = formatDataDropdown(item.sub_categories, idx + 1)
      return {
        text: item.name,
        key: item.value,
        children: listChildItem,
        hasChildren: true,
        defaultOption: listChildItem[0].value,
        value: item.id,
        index: idx
      }
    }
    if (isArray(item.report_types) && item.report_types.length > 0) {
      const listChildItem = formatDataDropdown(item.report_types, idx + 1)
      return {
        text: item.name,
        key: item.value,
        children: listChildItem,
        hasChildren: true,
        defaultOption: listChildItem[0].value,
        value: item.id,
        index: idx
      }
    }
    return {
      text: item.name,
      key: item.value,
      value: item.id,
      hasChildren: false,
      index: idx
    }
  })
}

const state = {
  customReportsList: [],
  reportsList: [],
  reportCategoriesList: [],
  reportsCount: null
}

const getters = {
  customReportsList: (state) => { return state.customReportsList },
  reportCategoriesList: (state) => { return formatDataDropdown(state.reportCategoriesList.results) },
  reportsCount: (state) => { return state.reportsCount }
}

const mutations = {
  setCustomReportsList(state, payload) {
    state.customReportsList = payload
  },
  setReportsList(state, payload) {
    state.reportsList = payload
  },
  setReportCategoriesList(state, payload) {
    state.reportCategoriesList = payload
  },
  setReportsCount(state, payload) {
    state.reportsCount = payload
  }
}

const actions = {
  getCustomReportsList({ commit }, payload) {
    const { params, query } = payload
    const clientId = params.clientId
    const userId = params.userId
    return (
      pfAxios.get(`/v1/clients/${clientId}/users/${userId}/custom-reports`, {params: query}).then(res => {
        commit('setReportsCount', res.data.count)
        commit('setCustomReportsList', res.data.results)
      })
    )
  },
  async getReportsList({ commit }, payload) {
    const { params, query } = payload
    const clientId = params.clientId
    const result = await pfAxios.get(`/v1/clients/${clientId}/sp-reports`, {params: query})
    commit('setReportsList', result.data)
  },
  async generateReports({ commit }, payload) {
    const { params, query } = payload
    const clientId = params.clientId
    await pfAxios.post(`/v1/clients/${clientId}/sp-reports`, query)
  },
  async getReportCategoriesList({ commit }, payload) {
    const result = await pfAxios.get(`/v1/clients/${payload.clientId}/sp-report-categories`)
    commit('setReportCategoriesList', result.data)
  },
  deleteReport({ commit, dispatch }, payload) {
    const { params, id } = payload
    const clientId = params.clientId
    const userId = params.userId
    return (
      pfAxios.delete(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`)
    )
  },
  cancelReport({ commit, dispatch }, payload) {
    const { params, id } = payload
    const clientId = params.clientId
    const userId = params.userId
    return (
      pfAxios.put(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}/cancellation`)
    )
  },
  editReport({ commit, dispatch }, payload) {
    const { params, id, name } = payload
    const clientId = params.clientId
    const userId = params.userId
    return (
      pfAxios.put(`/v1/clients/${clientId}/users/${userId}/custom-reports/${id}`, {name: name})
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
