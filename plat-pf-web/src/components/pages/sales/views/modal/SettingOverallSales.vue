<template>
  <b-modal
    id="setting-overall-sales-modal"
    v-model="computeIsOpen"
    variant="danger"
    hide-header
    centered
    :no-close-on-backdrop="isLoading"
    >
    <div class="title">Overall Sales Settings</div>

    <!-- List Overall Sales option -->
    <div class="list-tag-suggest d-flex flex-wrap mt-3" v-if="listOfOverallSales.length > 0">
      <b-form-group v-slot="{ ariaDescribedby }">
        <b-form-checkbox-group
          id="checkbox-tag-suggest"
          v-model="overallSalesSelected"
          :aria-describedby="ariaDescribedby"
          name="tag-suggest"
        >
          <b-form-checkbox
            v-for="(tagItem, index) in listOfOverallSales"
            :key="`${tagItem.key}_${index}`"
            :value="tagItem.key"
            @change="selectedTag(tagItem.key)"
            :class="{ 'not-full-width': index % 2 === 0 && index === listOfOverallSales.length - 1 }"
          >
            {{ tagItem.name }}
          </b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>
    </div>
    <div v-else-if="isLoading" class="w-100 d-flex justify-content-center align-items-center">
      <b-spinner label="Loading..."></b-spinner>
    </div>
    <div v-else>
      <p class="text-center p-4">No data</p>
    </div>
    <template v-slot:modal-footer>
      <b-button :disabled="isLoading" variant="primary" @click="saveListOfOverallSales()">
        Save
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { VueMaskDirective } from 'v-mask'
import ToastMixin from '@/components/common/toastMixin'
import cloneDeep from 'lodash/cloneDeep'

export default {
  name: 'OverallSalesSetting',
  mixins: [ToastMixin],
  directives: {
    mask: VueMaskDirective
  },
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    dashboard: {
      type: String
    },
    widgetName: {
      type: String
    },
    widgetSlug: {
      type: String
    }
  },
  data() {
    return {
      overallSalesData: [],
      overallSalesSelected: [],
      value: 0,
      isLoading: false
    }
  },
  computed: {
    ...mapGetters({
      listOfOverallSales: `pf/settings/getListOfOverallSales`,
      listOfOverallSalesByUser: `pf/settings/getListOfOverallSalesByUser`
    }),
    computeIsOpen: {
      get() { return this.isOpen },
      set(isOpen) { this.$emit('update:isOpen', isOpen) }
    }
  },
  methods: {
    ...mapActions({
      saveWidgetOptionByUser: `pf/settings/saveWidgetOptionByUser`
    }),
    async saveListOfOverallSales() {
      // if not selected any overall sales will not allow to save
      if (this.overallSalesData.length === 0) {
        return this.vueToast('error', 'Please select at least 1 overall sale.')
      }
      const dataUpdate = this.listOfOverallSales.map(item => {
        return {
          segment: item.key,
          enabled: this.overallSalesData.includes(item.key)
        }
      })
      try {
        this.isLoading = true
        this.$emit('loading')
        await this.saveWidgetOptionByUser({
          clientId: this.$route.params.client_id,
          dashboard: this.dashboard,
          currentData: this.overallSalesData,
          widgetName: this.widgetName,
          widgetSlug: this.widgetSlug,
          updateData: {
            data: dataUpdate
          }
        })
        this.vueToast('success', 'Settings updated successfully.')
        this.$emit('refresh')
        this.$emit('update:isOpen', false)
      } catch (e) {
        this.vueToast('error', 'Failed to update settings. Please try again!!!')
      } finally {
        this.isLoading = false
      }
    },
    selectedTag(tagItem) {
      const savedViews = this.overallSalesData.find(item => {
        return item === tagItem
      })
      if (!savedViews) {
        // if current tag is 5 item will not allow to add more
        if (this.overallSalesData.length === 5) {
          return this.vueToast('error', 'You can only select up to 5 overall sales.')
        }
        this.overallSalesData.push(tagItem)
      } else {
        this.overallSalesData = this.overallSalesData.filter(item => {
          return item !== tagItem
        })
      }
    }
  },
  watch: {
    listOfOverallSalesByUser: {
      immediate: true,
      async handler() {
        this.overallSalesSelected = cloneDeep(this.listOfOverallSalesByUser)
        this.overallSalesData = this.overallSalesSelected
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';
.list-tag-suggest {
  .form-group {
    width: 100%;
  }
  .not-full-width {
    width: 50%;
    flex: unset !important;
  }
}
</style>
