<template>
  <div class="align-middle d-flex justify-content-center">
    <div class="spinner-border thin-spinner spinner-border-sm cls-loading-oauth"></div>&nbsp;Loading...
  </div>
</template>

<script>
import LS from '@/services/_localStorage'
import get from 'lodash/get'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'PFSCOAuthRedirect',
  computed: {
    ...mapGetters({
      redirectToken: `pf/settings/redirectToken`
    })
  },
  methods: {
    ...mapActions({
      spAccountConnection: `pf/settings/spAccountConnection`,
      getRedirectToken: `pf/settings/getRedirectToken`
    }),
    async getToken(clientID) {
      let payload = {
        client_id: clientID,
        selling_partner_id: this.$route.query.selling_partner_id,
        spapi_oauth_code: this.$route.query.spapi_oauth_code,
        state: this.$route.query.state
      }
      await this.getRedirectToken(payload)
    },
    async saveToken(clientID) {
      try {
        let payload = {
          client_id: clientID,
          ac_spapi_enabled: true,
          ac_spapi_state: this.$route.query.state,
          ac_spapi_selling_partner_id: this.$route.query.selling_partner_id,
          ac_spapi_token_expired: this.redirectToken.expires_in,
          ac_spapi_refresh_token: this.redirectToken.refresh_token,
          ac_spapi_access_token: this.redirectToken.access_token,
          ac_spapi_auth_code: this.$route.query.spapi_oauth_code,
          ac_spapi_need_reconnect: false
        }
        await this.spAccountConnection(payload)
        this.$router.replace({
          name: 'PFSettings',
          params: { client_id: clientID }
        })
      } catch {
        this.vueToast('error', 'Saving token failed. Please retry or contact administrator.')
      }
    }
  },
  async created() {
    let clientID = localStorage.getItem('auth') ? get(JSON.parse(localStorage.getItem('auth')), 'ps.userModule.current_client.id', '') : LS.getCurrentClientId()
    const state = this.$route.query.state
    const oauthClientId = state ? state.split('_')[1] : ''
    // Users can open multiple tabs with different clients,
    // which may cause confusion or mismatch of client_id during OAuth authentication.
    // Always check and use the correct client_id from the state.
    if (oauthClientId && clientID !== oauthClientId) {
      clientID = oauthClientId
    }
    await this.getToken(clientID)
    await this.saveToken(clientID)
  }
}
</script>

<style scoped>
.cls-loading-oauth {
  border-width: 0.1em !important
}
</style>
