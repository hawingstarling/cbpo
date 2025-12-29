import pfAxios from '@/services/pfAxios'
import _ from 'lodash'

const state = {
  settingOption: {},
  spapiSetting: {},
  shopifyPartnerSetting: {},
  redirectToken: {},
  divisionsConfig: [],
  listOfDivisionsByUser: [],
  listOfDivisions: [],
  listOfOverallSalesByUser: [],
  listOfOverallSales: [],
  isLoadingSetting: true
}

const getters = {
  settingOption: (state) => { return state.settingOption },
  spapiSetting: (state) => { return state.spapiSetting },
  shopifyPartnerSetting: (state) => { return state.shopifyPartnerSetting },
  redirectToken: (state) => { return state.redirectToken },
  getListOfDivisionsByUser: (state) => { return state.listOfDivisionsByUser },
  getListOfDivisions: (state) => { return state.listOfDivisions },
  getListOfOverallSalesByUser: (state) => { return state.listOfOverallSalesByUser },
  getListOfOverallSales: (state) => { return state.listOfOverallSales },
  isLoadingSetting: (state) => { return state.isLoadingSetting },
  divisionsConfig: (state) => { return state.divisionsConfig }
}

const mutations = {
  setSettingOption(state, payload) {
    state.settingOption = payload
  },
  setSpapiSetting(state, payload) {
    state.spapiSetting = payload
  },
  setShopifyPartnerSetting(state, payload) {
    state.shopifyPartnerSetting = payload
  },
  setRedirectToken(state, payload) {
    state.redirectToken = payload
  },
  setIsLoadingSetting(state, payload) {
    state.isLoadingSetting = payload
  },
  setListOfDivisionsByUser(state, payload) {
    state.listOfDivisionsByUser = payload
  },
  setListOfDivisions(state, payload) {
    state.listOfDivisions = payload
  },
  setListOfOverallSalesByUser(state, payload) {
    state.listOfOverallSalesByUser = payload
  },
  setListOfOverallSales(state, payload) {
    state.listOfOverallSales = payload
  },
  setDivisionsConfig(state, payload) {
    state.divisionsConfig = payload.data
  }
}

const actions = {
  getSettingOption({ commit }, params) {
    let clientId = params.client_id
    commit('setIsLoadingSetting', true)
    return (
      pfAxios.get(`/v1/clients/${clientId}/settings/details/`).then(res => {
        commit('setSettingOption', res.data)
        commit('setIsLoadingSetting', false)
      })
    )
  },
  fetchListOfWidgetByUser({ commit }, params) {
    const { widgetName, widgetSlug, dashboard, clientId } = params
    commit('setIsLoadingSetting', true)
    return (
      pfAxios.get(`/v1/clients/${clientId}/dashboard/${dashboard}/users/widget-${widgetSlug}`).then(res => {
        commit(`setListOf${widgetName}`, res.data)
        commit(`setListOf${widgetName}ByUser`, _.chain(res.data)
          .filter('enabled')
          .map('key')
          .value())
        commit('setIsLoadingSetting', false)
      }).catch(err => {
        throw err
      })
    )
  },
  saveWidgetOptionByUser({ state, commit }, params) {
    return (
      pfAxios.put(`/v1/clients/${params.clientId}/dashboard/${params.dashboard}/users-widget-${params.widgetSlug}`, params.updateData)
        .then(() => {
          commit(`setListOf${params.widgetName}ByUser`, params.currentData)
        })
        .catch(err => { throw err })
    )
  },
  fetchDivisionsConfig({ state, commit }, params) {
    return (
      pfAxios.get(`/v1/clients/${params.clientId}/dashboard/${params.dashboard}/users/${params.widgetName}-widget-settings`)
        .then((result) => {
          commit(`setDivisionsConfig`, result.data)
        })
        .catch(err => { throw err })
    )
  },
  saveDivisionsConfig({ state, commit }, params) {
    const newDivisionsConfig = state.divisionsConfig.map((item) => {
      if (item.key === params.dataConfig.key) {
        item = params.dataConfig
      }
      return item
    })
    commit(`setDivisionsConfig`, { data: newDivisionsConfig })
    return (pfAxios.put(`/v1/clients/${params.clientId}/dashboard/${params.dashboard}/users/${params.widgetName}-widget-settings`, params.dataConfig))
  },
  saveBulkDivisionsConfig({ state, commit }, params) {
    commit(`setDivisionsConfig`, params.dataConfig)
    commit(`setListOf${params.widgetName}ByUser`, _.chain(params.dataConfig.data)
      .filter('enabled')
      .map('key')
      .value())
    return (pfAxios.put(`/v1/clients/${params.clientId}/dashboard/${params.dashboard}/users/${params.widgetSlug}-widget-bulk-settings`, params.dataConfig))
  },
  putSettingOption({ commit }, params) {
    let clientId = params.client_id
    let payload = {
      allow_sale_data_update_from: params.allow_sale_data_update_from,
      is_remove_cogs_refunded: params.is_remove_cogs_refunded,
      ac_mws_access_key: params.ac_mws_access_key,
      ac_mws_secret_key: params.ac_mws_secret_key,
      ac_mws_merchant_id: params.ac_mws_merchant_id,
      ac_mws_merchant_name: params.ac_mws_merchant_name,
      ac_mws_enabled: params.ac_mws_enabled,
      ac_spapi_enabled: params.ac_spapi_enabled,
      ac_spapi_state: params.ac_spapi_state,
      ac_spapi_selling_partner_id: params.ac_spapi_selling_partner_id,
      ac_spapi_token_expired: params.ac_spapi_token_expired,
      ac_spapi_refresh_token: params.ac_spapi_refresh_token,
      ac_spapi_access_token: params.ac_spapi_access_token,
      ac_spapi_auth_code: params.ac_spapi_auth_code,
      // CartRover
      ac_cart_rover_enabled: params.ac_cart_rover_enabled,
      ac_cart_rover: params.ac_cart_rover,
      // COGS
      cog_use_extensiv: params.cog_use_extensiv,
      cog_extensiv_token: params.cog_extensiv_token,
      cog_use_dc: params.cog_use_dc,
      cog_use_pf: params.cog_use_pf,
      cog_priority_source: params.cog_priority_source
    }
    return (
      pfAxios.put(`/v1/clients/${clientId}/settings/details/`, payload)
    )
  },
  patchSettingOption({ state, commit }, params) {
    const { client_id: clientId, payload } = params || {}
    return (
      pfAxios.patch(`/v1/clients/${clientId}/settings/details/`, payload)
        .then(() => commit('setSettingOption', {...state.settingOption, ...payload}))
        .catch(err => { throw err })
    )
  },

  getSpapiSetting({ commit }, params) {
    let clientId = params.client_id
    return (
      pfAxios.get(`/v1/clients/${clientId}/spapi-setting`).then(res => {
        commit('setSpapiSetting', res.data)
      })
    )
  },
  getShopifyPartnerSetting({ commit }, params) {
    return pfAxios.get(`/v1/clients/${params.client_id}/sp-setting`)
      .then(response => {
        commit('setShopifyPartnerSetting', response.data)
      })
      .catch(err => {
        if (err.response.status === 404) {
          commit('setShopifyPartnerSetting', {})
        }
      })
  },
  getOauthUrlShopifyPartner({ commit }, params) {
    return pfAxios.post(`/v1/clients/${params.client_id}/sp-oauth/o2/token`,
      params)
  },
  revokeShopifyPartner({ commit }, params) {
    return pfAxios.post(`v1/clients/${params.client_id}/sp/revoke-access`,
      params)
  },
  getRedirectToken({ commit }, params) {
    let clientId = params.client_id
    let payload = {
      selling_partner_id: params.selling_partner_id,
      spapi_oauth_code: params.spapi_oauth_code,
      state: params.state
    }
    return (
      pfAxios.post(`v1/clients/${clientId}/sc-oauth/o2/token`, payload).then(res => {
        commit('setRedirectToken', res.data)
      })
    )
  },
  async registerMerchantShopUrl({ commit }, params) {
    const clientId = params.client_id
    const payload = {
      shop_url: params.shop_url,
      client_id: clientId
    }
    try {
      const res = await pfAxios.post(`v1/clients/${clientId}/register-merchant`, payload)
      return res.data
    } catch (err) {
      throw err
    }
  },
  async spAccountConnection({ commit }, params) {
    let clientId = params.client_id
    let payload = {
      ac_spapi_access_token: params.ac_spapi_access_token,
      ac_spapi_refresh_token: params.ac_spapi_refresh_token,
      ac_spapi_token_expired: params.ac_spapi_token_expired,
      ac_spapi_selling_partner_id: params.ac_spapi_selling_partner_id,
      ac_spapi_auth_code: params.ac_spapi_auth_code,
      ac_spapi_enabled: params.ac_spapi_enabled,
      ac_spapi_state: params.ac_spapi_state,
      ac_spapi_need_reconnect: params.ac_spapi_need_reconnect
    }
    try {
      await pfAxios.post(`v1/clients/${clientId}/sp-account-connection`, payload)
    } catch (err) {
      throw err
    }
  },
  async revokeAccountConnection({ commit }, params) {
    const clientId = params.client_id
    try {
      await pfAxios.delete(`v1/clients/${clientId}/sp-account-revoke`)
    } catch (err) {
      throw err
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
