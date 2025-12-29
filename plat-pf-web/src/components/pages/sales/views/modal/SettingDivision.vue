<template>
  <b-modal
    id="setting-Division-modal"
    v-model="computeIsOpen"
    variant="danger"
    hide-header
    size="lg"
    centered
    :no-close-on-backdrop="isLoading"
    >
    <div class="title">Sales Division Settings</div>
    <!-- List Division option -->
    <div class="mt-3" v-if="divisionsData.length > 0">
      <b-button
        variant="primary"
        size="sm"
        @click="addDivision"
        class="mb-3"
        :disabled="isDisabledAddDivision"
      >
        Add New Division
      </b-button>
      <b-table
        show-empty
        hover
        outlined
        striped
        responsive="sm"
        :fields="fields"
        :items="divisionsData"
        :key="divisionsData.length"
        id="activity-table"
        class="tb-activity"
        sticky-header="450px"
      >
        <template v-slot:empty>
          <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm thin-spinner"></div>&nbsp;Loading...
          </div>
          <div class="align-middle d-flex justify-content-center" v-else>
            <div>There is no division to show.</div>
          </div>
        </template>
        <template v-slot:cell(check)="row">
          <b-form-checkbox
            class="d-flex justify-content-center ml-2 division-check"
            :key="`${row.item.key}`"
            v-model="row.item.enabled"
          ></b-form-checkbox>
        </template>
        <template v-slot:cell(division)="row">
          <div class="d-flex justify-content-center py-2">
            <div class="text-center input-division d-flex justify-content-center">
              <div class="w-100 d-flex justify-content-center" v-if="row.item.isEditing">
                <b-form-input
                  v-model="row.item.name"
                  placeholder="Input division name"
                  class="full-width text-center"
                  @change="changeData(row.item)"
                ></b-form-input>
              </div>
              <div class="d-name" v-else>{{row.item.name}}</div>
            </div>
          </div>
        </template>
        <template v-slot:cell(options)="row">
          <b-form-radio-group
            :options="options"
            v-model="row.item.sync_option"
            class="mr-1 d-flex justify-content-center"
          ></b-form-radio-group>
        </template>
        <template v-slot:cell(action)="row">
          <div class="d-flex justify-content-center">
            <b-button
              variant="success"
              size="sm"
              v-if="row.item.isEditing"
              @click="saveDivision(row.item.key)"
            >
              <i class="fa fa-check"></i>
            </b-button>
            <b-button
              variant="primary"
              size="sm"
              v-else
              @click="editDivision(row.item)"
            >
              <i class="fa fa-pencil"></i>
            </b-button>
            <b-button
              variant="danger"
              size="sm"
              @click="deleteDivision(row.item)"
            >
              <i class="fa fa-trash-o"></i>
            </b-button>
          </div>
        </template>
      </b-table>
      <p class="m-0">Max Limit: 5 Divisions</p>
    </div>
    <div v-else-if="isLoading" class="w-100 d-flex justify-content-center align-items-center">
      <b-spinner label="Loading..."></b-spinner>
    </div>
    <div v-else>
      <p class="text-center p-4">No data</p>
    </div>
    <template v-slot:modal-footer>
      <b-button
        class="mr-2"
        variant
        @click="handleCloseModal()"
      >
        Cancel
      </b-button>
      <b-button :disabled="isLoading" variant="primary" @click="saveListOfDivisions()">
        Save
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { VueMaskDirective } from 'v-mask'
import ToastMixin from '@/components/common/toastMixin'
import { validateMixins } from '@/shared/utils'

export default {
  name: 'SettingDivision',
  mixins: [ToastMixin, validateMixins],
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
      divisionsData: [],
      value: 0,
      isLoading: false,
      fields: [
        { key: 'check', label: '', class: 'vertical-content user-td', thClass: 'text-center align-middle', tdClass: 'justify-content-center align-middle' },
        { key: 'division', label: 'Division Name', class: 'vertical-content user-td w-100', thClass: 'w-50 text-center align-middle', tdClass: 'justify-content-center align-middle' },
        { key: 'options', label: 'Sync Options', class: 'vertical-content user-td', thClass: 'w-20 text-center align-middle', tdClass: 'justify-content-center align-middle' },
        { key: 'action', label: 'Actions', class: 'vertical-content action-td', thClass: 'w-20 text-center align-middle', tdClass: 'justify-content-center text-center align-middle' }
      ],
      options: [
        { text: 'Manual', value: 'Manual' },
        { text: 'Historical', value: 'Historical' }
      ]
    }
  },
  computed: {
    ...mapGetters({
      settingOption: `pf/settings/settingOption`,
      listOfDivisions: `pf/settings/getListOfDivisions`,
      listOfDivisionsByUser: `pf/settings/getListOfDivisionsByUser`,
      divisionsConfig: `pf/settings/divisionsConfig`
    }),
    computeIsOpen: {
      get() { return this.isOpen },
      set(isOpen) { this.$emit('update:isOpen', isOpen) }
    },
    isDisabledAddDivision() {
      return this.divisionsData.length >= 5
    }
  },
  methods: {
    ...mapActions({
      getSettingOption: `pf/settings/getSettingOption`,
      saveBulkDivisionsConfig: `pf/settings/saveBulkDivisionsConfig`,
      fetchDivisionsConfig: `pf/settings/fetchDivisionsConfig`,
      fetchListOfDivisionsByUser: `pf/settings/fetchListOfWidgetByUser`
    }),
    handleCloseModal() {
      this.$emit('update:isOpen', false)
      // Reset the data when clicking "Cancel" button
      this.divisionsData = this.divisionsConfig.map(item => {
        return {
          ...item,
          isEditing: false
        }
      })
    },
    saveDivision(key) {
      this.divisionsData = this.divisionsData.map(data => {
        if (data.key === key) {
          if (data.name === '' || !this.isValidString(data.name)) {
            this.vueToast('error', 'Division name is required.')
            return data
          } else {
            return {
              ...data,
              isEditing: false
            }
          }
        }
        return data
      })
    },
    addDivision() {
      this.divisionsData.push({
        key: '',
        name: '',
        enabled: true,
        sync_option: 'Historical',
        ytd_target_manual: 0,
        ytd_max_manual: 0,
        mtd_target_manual: 0,
        mtd_max_manual: 0,
        isEditing: true
      })
    },
    editDivision(division) {
      this.divisionsData = this.divisionsData.map(data => {
        if (data.key === division.key) {
          return {
            ...data,
            isEditing: true
          }
        }
        return data
      })
    },
    deleteDivision(division) {
      this.divisionsData = this.divisionsData.filter(data => {
        return data.key !== division.key
      })
    },
    async saveListOfDivisions() {
      const invalidDivision = this.divisionsData.find(data => !data.name || !this.isValidString(data.name))
      if (invalidDivision) {
        this.vueToast('error', 'Division name is required.')
        return
      }
      const activeDivisions = this.divisionsData.filter(data => data.enabled)
      if (activeDivisions.length > 5) {
        this.vueToast('error', 'You can only activate 5 divisions.')
        return
      }
      try {
        this.isLoading = true
        await this.saveBulkDivisionsConfig({
          clientId: this.$route.params.client_id,
          dashboard: this.dashboard,
          widgetName: this.widgetName,
          widgetSlug: this.widgetSlug,
          dataConfig: {
            data: this.divisionsData
          }
        })
        this.vueToast('success', 'Settings updated successfully.')
        this.$emit('update:isOpen', false)
        await this.fetchListOfDivisionsByUser({
          dashboard: this.dashboard,
          clientId: this.$route.params.client_id,
          widgetName: this.widgetName,
          widgetSlug: this.widgetSlug
        })
        await this.fetchDivisionsConfig({
          clientId: this.$route.params.client_id,
          dashboard: this.dashboard,
          widgetName: this.widgetSlug
        })
      } catch (e) {
        this.vueToast('error', 'Failed to update settings. Please try again!!!')
      } finally {
        this.isLoading = false
      }
    },
    changeData(divisionItem) {
      divisionItem.key = divisionItem.name
    }
  },
  watch: {
    divisionsConfig: {
      immediate: true,
      async handler() {
        this.divisionsData = this.divisionsConfig.map(item => {
          return {
            ...item,
            isEditing: false
          }
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';
.input-division{
  height: 40px;
  text-align: center;
}
.d-name{
  height: 40px;
  line-height: 40px;
}
::v-deep .division-check .custom-control-label {
 &::before {
  width: 22px;
  height: 22px;
  border-color: #E6E8F0;
  color: #FFFFFF;
 }
 &::after {
  width: 22px;
  height: 22px;
 }
}
::v-deep .table {
  border-collapse: separate;
  border-spacing: 0;
}
</style>
