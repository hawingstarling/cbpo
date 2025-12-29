import pfAxios from '@/services/pfAxios'

const state = {
  brandSettingList: [],
  countUpdateSales: 0,
  brandList: []
}

const getters = {
  brandSettingList: (state) => { return state.brandSettingList },
  countUpdateSales: (state) => { return state.countUpdateSales },
  brandList: (state) => { return state.brandList }
}

const mutations = {
  setBrandSettingList(state, payload) {
    state.brandSettingList = payload
  },
  setCountUpdateSales(state, payload) {
    state.countUpdateSales = payload
  },
  setBrandList(state, payload) {
    state.brandList = payload
  }
}

const actions = {
  getBrandSettingList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    let keyword = params.key || ''
    let channel = params.channel
    return (
      pfAxios.get(`/v1/clients/${clientId}/brand-settings/`, {params: {limit: limit, page: page, keyword: keyword, channel: channel || null}}).then(res => {
        commit('setBrandSettingList', res.data)
      })
    )
  },
  postBrandSettingUpdateSales({ commit }, params) {
    let clientId = params.client_id
    let brandSettingId = params.brand_setting_id
    let payload = {
      sale_date_from: params.sale_date_from,
      sale_date_to: params.sale_date_to,
      recalculate: params.recalculate
    }
    return (
      pfAxios.post(`/v1/clients/${clientId}/brand-settings/${brandSettingId}/update-sales/`, payload)
    )
  },
  postCountUpdateSales({ commit }, params) {
    let clientId = params.client_id
    let brandSettingId = params.brand_setting_id
    let payload = {
      sale_date_from: params.sale_date_from,
      sale_date_to: params.sale_date_to,
      recalculate: params.recalculate
    }
    return (
      pfAxios.post(`/v1/clients/${clientId}/brand-settings/${brandSettingId}/count-sales/`, payload).then(res => {
        commit('setCountUpdateSales', res.data)
      })
    )
  },
  editBrandSetting({ commit }, params) {
    let clientId = params.client_id
    let brandSettingId = params.brand_setting_id
    let payload = {
      est_first_item_shipcost: params.item_edit.est_first_item_shipcost,
      est_add_item_shipcost: params.item_edit.est_add_item_shipcost,
      est_fba_fees: params.item_edit.est_fba_fees,
      po_dropship_method: params.item_edit.po_dropship_method,
      po_dropship_cost: params.item_edit.po_dropship_cost,
      mfn_formula: params.item_edit.mfn_formula,
      auto_update_sales: params.item_edit.auto_update_sales,
      segment: params.item_edit.segment,
      est_unit_inbound_freight_cost: params.item_edit.est_unit_inbound_freight_cost,
      est_unit_outbound_freight_cost: params.item_edit.est_unit_outbound_freight_cost,
      add_user_provided_cost: params.item_edit.add_user_provided_cost,
      add_user_provided_method: params.item_edit.add_user_provided_method,
      channel: params.item_edit.channel,
      brand: params.item_edit.brand
    }
    return (
      pfAxios.patch(`/v1/clients/${clientId}/brand-settings/${brandSettingId}/`, payload)
    )
  },
  exportBrandSetting({ commit }, params) {
    let clientId = params.client_id
    let query = params.query
    return (
      pfAxios.get(`/v1/clients/${clientId}/brand-settings/export/`, {params: query})
    )
  },
  getBrandList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.key || ''
    let sortDirection = params.sortDirection || null
    let sortField = params.sortField || null
    return (
      pfAxios.get(`/v1/clients/${clientId}/brands`, {
        params: {
          limit: limit, page: page, search: search, sort_field: sortField, sort_direction: sortDirection
        }
      }).then(res => {
        commit('setBrandList', res.data)
      })
    )
  },
  fetchBrandList({ commit }, params) {
    let clientId = params.client_id
    let page = params.page || 1
    let limit = params.limit || 10
    let search = params.key || ''
    let sortDirection = params.sortDirection || null
    let sortField = params.sortField || null
    return (
      pfAxios.get(`/v1/clients/${clientId}/brands`, {
        params: {
          limit: limit, page: page, search: search, sort_field: sortField, sort_direction: sortDirection
        }
      }).then(res => {
        return res.data
      })
    )
  },
  exportBrands({ commit }, payload) {
    const clientId = payload.client_id
    const query = payload.query
    return (
      pfAxios.get(`/v1/clients/${clientId}/brands/export`, {params: {...query}}).then(res => {
        return res
      })
    )
  },
  editBrand({ commit }, payload) {
    const clientId = payload.client_id
    const name = payload.name
    const id = payload.id
    const isObsolete = payload.is_obsolete
    return (
      pfAxios.put(`/v1/clients/${clientId}/brands/${id}`, {name: name, is_obsolete: isObsolete}).then(res => {
      })
    )
  },
  fetchAddBrandSetting({ commit }, payload) {
    const clientId = payload.client_id
    const data = payload.item_add
    return pfAxios.post(`/v1/clients/${clientId}/brand-settings/`, data)
  },
  async deleteBrandAsync({ commit }, payload) {
    const {clientId, brandId} = payload
    try {
      return pfAxios.delete(`/v1/clients/${clientId}/brands/${brandId}`)
    } catch (err) {
      throw err
    }
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
