import { mapGetters, mapActions } from 'vuex'

const key = 'SPAPI_NEED_RECONNECT_ALERT'

export default {
  computed: {
    ...mapGetters({ settingOption: 'pf/settings/settingOption' }),
    settingsLink() {
      return this.$router.resolve({ name: 'PFSettings', params: { client_id: this.$route.params.client_id } }).href
    },
    spapiReconnectAlert() {
      const messages = {
        'rotation_date_line': `Token expired (rotation dateline). Please <a href="${this.settingsLink}">reconnect</a> your Selling Central account to continue integration.`,
        'lwa_secret_key': `LWA Secret Key changed. Please <a href="${this.settingsLink}">reconnect</a> your Selling Central account to continue integration.`
      }

      const typeReconnect = this.settingOption && this.settingOption.ac_spapi_type_reconnect
      const message = messages[typeReconnect] ||
        `Please <a href="${this.settingsLink}">reconnect</a> your Selling Central account to continue integration`

      return {
        type: 'danger',
        message
      }
    },
    isSPAPINeedReconnect() {
      return this.settingOption && this.settingOption.ac_spapi_need_reconnect === true
    }
  },
  watch: {
    isSPAPINeedReconnect(newVal) {
      if (newVal) {
        this.showMainAlert(this.spapiReconnectAlert)
      } else if (newVal === false) {
        this.removeMainAlert()
      }
    },
    '$route.params.client_id'(newVal) {
      this.getSettingOption({ client_id: newVal })
    }
  },
  methods: {
    ...mapActions({ getSettingOption: 'pf/settings/getSettingOption' }),
    showMainAlert({ type = 'info', message = '' }) {
      if (this.$bus && message) {
        this.$bus.$emit('show-main-alert', { type, message, key })
      }
    },
    removeMainAlert() {
      this.$bus.$emit('remove-main-alert', key)
    }
  },
  mounted() {
    if (this.$route && this.$route.params && this.$route.params.client_id) {
      this.getSettingOption({ client_id: this.$route.params.client_id }).then(() => {
        if (this.isSPAPINeedReconnect) {
          this.showMainAlert(this.spapiReconnectAlert)
        }
      })
    }
  }
}
