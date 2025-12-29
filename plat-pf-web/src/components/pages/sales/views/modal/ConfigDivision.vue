<template>
  <b-modal
    id="configure-division-modal"
    v-model="computeIsOpen"
    variant="danger"
    centered
    size="lg"
    :no-close-on-backdrop="isLoading"
    >
    <template v-slot:modal-title>
      <div>Configure Sync Data ({{ division }})</div>
    </template>
    <!-- List Division option -->
    <div class="d-flex flex-wrap mt-3 row px-3 config-division justify-content-center align-items-center" v-if="form">
      <b-card header="YTD" class="col-5 p-0 mr-4">
        <b-form-group
          id="ytd_target_manual"
          label="Target value"
          label-for="ytd_target_manual"
        >
          <b-input-group prepend="$" class="">
            <b-form-input id="ytd_target_manual" v-model="form.ytd_target_manual" type="number" placeholder="Target value"></b-form-input>
          </b-input-group>
        </b-form-group>
        <b-form-group
          id="ytd_max_manual"
          label="Max value"
          label-for="ytd_max_manual"
        >
          <b-input-group prepend="$" class="mb-2 mr-sm-2 mb-sm-0">
            <b-form-input id="ytd_max_manual" v-model="form.ytd_max_manual" type="number" placeholder="Max value"></b-form-input>
          </b-input-group>
        </b-form-group>
      </b-card>
      <b-card header="MTD" class="col-5 p-0">
        <b-form-group
          id="mtd_target_manual"
          label="Target value"
          label-for="mtd_target_manual"
        >
          <b-input-group prepend="$" class="">
            <b-form-input id="mtd_target_manual" v-model="form.mtd_target_manual" type="number" placeholder="Target value"></b-form-input>
          </b-input-group>
        </b-form-group>
        <b-form-group
          id="mtd_max_manual"
          label="Max value"
          label-for="mtd_max_manual"
        >
          <b-input-group prepend="$" class="mb-2 mr-sm-2 mb-sm-0">
            <b-form-input id="mtd_max_manual" v-model="form.mtd_max_manual" type="number" placeholder="Max value"></b-form-input>
          </b-input-group>
        </b-form-group>
      </b-card>
    </div>
    <div v-if="isLoading" class="w-100 d-flex justify-content-center align-items-center">
      <b-spinner label="Loading..."></b-spinner>
    </div>
    <template v-slot:modal-footer>
      <b-button
        class="mr-2"
        variant
        @click="handleCloseModal()"
      >
        Cancel
      </b-button>
      <b-button :disabled="isLoading" variant="primary" @click="saveConfigByDivision()">
        Save
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import ToastMixin from '@/components/common/toastMixin'

export default {
  name: 'ConfigDivision',
  mixins: [ToastMixin],
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    dashboard: {
      type: String
    },
    division: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      form: {
        key: '',
        mtd_target_manual: 0,
        mtd_max_manual: 0,
        ytd_target_manual: 0,
        ytd_max_manual: 0
      },
      widgetName: 'divisions',
      isLoading: false
    }
  },
  computed: {
    ...mapGetters({
      divisionsConfig: `pf/settings/divisionsConfig`
    }),
    computeIsOpen: {
      get() { return this.isOpen },
      set(isOpen) { this.$emit('update:isOpen', isOpen) }
    }
  },
  methods: {
    ...mapActions({
      saveDivisionsConfig: `pf/settings/saveDivisionsConfig`
    }),
    handleCloseModal() {
      this.$emit('update:isOpen', false)
    },
    async saveConfigByDivision() {
      try {
        this.isLoading = true
        this.form.key = this.division
        await this.saveDivisionsConfig({
          clientId: this.$route.params.client_id,
          dashboard: this.dashboard,
          widgetName: this.widgetName,
          dataConfig: this.form
        })
        this.vueToast('success', 'Settings updated successfully.')
        this.$emit('update:isOpen', false)
      } catch (e) {
        this.vueToast('error', 'Failed to update settings. Please try again!!!')
      } finally {
        this.isLoading = false
      }
    }
  },
  watch: {
    divisionsConfig: {
      immediate: true,
      async handler() {
        this.form = this.divisionsConfig.find(item => {
          return item.key === this.division
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
// @import './Modal.scss';
.config-division {
  border-radius: 50%;
  .card {
    border-radius: 16px !important;
    .card-body {
      background-color: unset !important;
    }
    .card-header {
      border-top-left-radius: 16px !important;
      border-top-right-radius: 16px !important;
      text-align: center;
      font-weight: 700;
      font-size: 16px;
      padding-top: 6px;
      padding-bottom: 6px;
    }
  }
}
</style>
