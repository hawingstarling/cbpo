import pfAxios from '@/services/pfAxios'
import authSvc from '@/services/authSvc'

export default {
  fetchPermissions: async ({ commit }, payload = {}) => {
    try {
      let clientId = payload.clientId || authSvc.getCurrentClientId()
      const url = `/v1/clients/${clientId}/setting-permissions`
      let { data } = await pfAxios(url, { method: 'get' })
      commit('setPermissions', data)
    } catch (err) {
      commit('setPermissions', {permissions: {}})
    }
  }
}
