<template>
  <b-modal
    id="setting-goal-modal"
    v-model="computeIsOpen"
    variant="danger"
    hide-header
    centered
    :no-close-on-backdrop="isLoading"
    @hidden="resetValue">
    <div class="title">Setting Goal</div>

    <div role="group" class="mb-2 mt-2">
      <label>Goal Value</label>
      <b-form-input v-model="value" v-mask="currencyMask" :disabled="isLoading"></b-form-input>
    </div>

    <template v-slot:modal-footer>
      <b-button :disabled="isLoading" variant="primary" @click="saveSettings()">
        Save
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions } from 'vuex'
import { VueMaskDirective } from 'v-mask'
import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import ToastMixin from '@/components/common/toastMixin'

export default {
  name: 'SettingGoal',
  mixins: [ToastMixin],
  directives: {
    mask: VueMaskDirective
  },
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    default: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      value: 0,
      isLoading: false,
      currencyMask: createNumberMask({
        prefix: '',
        allowDecimal: true,
        includeThousandsSeparator: true,
        allowNegative: false
      })
    }
  },
  computed: {
    computeIsOpen: {
      get() { return this.isOpen },
      set(isOpen) { this.$emit('update:isOpen', isOpen) }
    }
  },
  methods: {
    ...mapActions({
      saveWidgetsDashboard: `pf/manageWidgetDashboard/saveWidgetsDashboard`
    }),
    async saveSettings() {
      const parseValue = this.value ? Number.parseFloat(this.value.replace(/,/g, '')) : 0
      if ([NaN].includes(parseValue)) {
        return this.vueToast('error', 'Invalid goal value. Accept positive number only.')
      }

      try {
        this.isLoading = true
        const params = {
          client_id: this.$route.params.client_id,
          dashboard: 'overview',
          payload: {
            data: [{
              widget: 'total_sales_tracker',
              settings: {goal: parseValue}
            }]
          }
        }
        await this.saveWidgetsDashboard(params)
        this.$emit('updateSettingsGoal', parseValue)
        this.computeIsOpen = false
      } catch (e) {
        this.vueToast('error', 'Failed to load settings. Please try again!!!')
      } finally {
        this.isLoading = false
      }
    },
    resetValue() {
      this.value = this.default
    }
  },
  watch: {
    default: {
      immediate: true,
      handler() {
        this.resetValue()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';
</style>
