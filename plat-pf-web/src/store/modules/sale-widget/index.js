import pfAxios from '@/services/pfAxios'
import { BRAND_ALL_OPTION, SKU_ALL_OPTION, FULFILLMENT_ALL_OPTION, WIDGET_NAME } from '@/shared/constants'

const convertResultToOptions = (results = []) => {
  return [
    ...results.map(item => ({ label: item.name || item.label, value: item.value || item.name }))
  ]
}
const convertResultToSkuOptions = (results = []) => {
  return [
    ...results.map(item => ({
      label: item.sku || item.label, value: item.sku || item.value
    }))
  ]
}

const state = {
  isLoading: false,
  fulfillmentOptions: [FULFILLMENT_ALL_OPTION],
  brandOptions: [BRAND_ALL_OPTION],
  skuAllSellerOptions: [SKU_ALL_OPTION],
  skuSalesBy$AmountOptions: [SKU_ALL_OPTION]
}

const getters = {
  isLoading: state => state.isLoading,
  fulfillmentOptions: state => convertResultToOptions(state.fulfillmentOptions),
  brandOptions: state => convertResultToOptions(state.brandOptions),
  skuAllSellerOptions: state => convertResultToSkuOptions(state.skuAllSellerOptions),
  skuSalesBy$AmountOptions: state => convertResultToSkuOptions(state.skuSalesBy$AmountOptions)
}

const mutations = {
  setFulfillmentOptions(state, payload) {
    state.fulfillmentOptions = [FULFILLMENT_ALL_OPTION, ...payload.data.results]
  },
  setBrandOptions(state, payload) {
    state.brandOptions = [...state.brandOptions, ...payload.data.results]
  },
  setSkuAllSellerOptions(state, payload) {
    state.skuAllSellerOptions = [SKU_ALL_OPTION, ...payload.data.results]
  },
  setSkuSalesBy$AmountOptions(state, payload) {
    state.skuSalesBy$AmountOptions = [SKU_ALL_OPTION, ...payload.data.results]
  },
  setIsLoading(state, payload) {
    state.isLoading = payload
  }
}

const actions = {
  async getAllBrandsAndFulfillment({ dispatch, state, commit }, params) {
    try {
      dispatch('getAllSKUs', params)
      if (state.isLoading) {
        return
      }
      commit('setIsLoading', true)
      dispatch('getAllBrands', params)
      dispatch('getSaleItemVariation', params)
    } catch (err) {
      throw err
    }
  },
  async getAllBrands({ commit }, params) {
    try {
      let clientId = params.clientId
      let limit = 9999
      const res = await pfAxios.get(`/v1/clients/${clientId}/brands`, { params: { limit, sort_direction: 'asc', sort_field: 'name' } })
      commit('setBrandOptions', res)
      commit('setIsLoading', false)
    } catch (err) {
      throw err
    }
  },
  async getAllSKUs({ commit }, params) {
    try {
      let clientId = params.clientId
      let widget = params.widget
      let limit = 9999
      const res = await pfAxios.get(`/v1/clients/${clientId}/${widget}/sale-by-sku`, { params: { limit, sort_direction: 'asc', sort_field: 'name' } })
      if (widget === WIDGET_NAME.dollar) {
        commit('setSkuSalesBy$AmountOptions', res)
      }
      if (widget === WIDGET_NAME.unit) {
        commit('setSkuAllSellerOptions', res)
      }
      commit('setIsLoading', false)
    } catch (err) {
      throw err
    }
  },
  getUserTrack({ commit }, payload) {
    try {
      let clientId = payload.clientId
      return pfAxios.get(`/v1/clients/${clientId}/user-track`)
    } catch (err) {
      throw err
    }
  },
  async updateUserTrack({ commit }, payload) {
    try {
      let clientId = payload.clientId
      await pfAxios.post(`/v1/clients/${clientId}/user-track`, payload.data)
    } catch (err) {
      throw err
    }
  },
  async getSaleItemVariation({ commit }, data) {
    try {
      let { clientId, hasVariation, type, keyword, queries } = data
      let url = `/v1/clients/${clientId}`
      hasVariation ? url = `${url}/variations/${type}` : url = `${url}/${type}`
      const res = await pfAxios.get(url, { params: { search: keyword, ...queries } })
      commit('setFulfillmentOptions', res)
      commit('setIsLoading', false)
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
