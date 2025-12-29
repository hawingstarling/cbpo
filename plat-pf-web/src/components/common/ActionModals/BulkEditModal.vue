<template>
  <ValidationObserver ref="bulkEditObserver" slim>
    <b-modal
      :id="id"
      size="lgx"
      title="Bulk Edit Sale Item"
      modal-class="editable-modal"
      v-model="isOpen"
      centered
    >
      <ErrorMessages
        :showErrorAlert="showErrorAlert"
        :errorMessages="errorMessages"
      />
      <b-container fluid class="bulk-edit-modal">
        <b-row>
          <b-card no-body class="w-100">
            <b-card-header
              header-tag="header"
              v-b-toggle.accordion-fields
              class="bulk-edit-modal__header"
              role="tab"
            >
              <span>Fields</span>
              <b-btn variant="secondary" size="sm" class="icon-collapsible">
                <span class="when-opened">
                  <i class="fa fa-minus"/>
                </span>
                <span class="when-closed">
                  <i class="fa fa-plus"/>
                </span>
              </b-btn>
            </b-card-header>

            <b-collapse id="accordion-fields" visible role="tabpanel">
              <b-card-body>
                <b-card-group class="bulk-card-group">
                  <b-card
                    v-for="(dataGroup, index) in dataRenderUI"
                    :key="index"
                    :header="dataGroup.group | filterGroupname"
                    header-class="text-uppercase font-weight-bold"
                  >
                    <b-row class="edit-modal__row-group">
                      <b-col
                        md="12"
                        v-for="(dataField, dataKey) in dataGroup.data"
                        :key="dataKey"
                      >
                        <div class="edit-modal__heading">
                          <b-btn
                            v-if="isFieldVisible(dataField.format) && !isEmptyValue(dataField.name)"
                            @click="toggleBulkDataState(dataField)"
                            :variant="buttonVariant(dataField.id)"
                            class="mb-1 w-100"
                            size="sm"
                            pill
                          >
                            {{
                              getColumnName(dataField.name) | filterColumnName
                            }}
                          </b-btn>
                        </div>
                      </b-col>
                    </b-row>
                    <template v-if="dataGroup.subGroup">
                      <b-card
                        v-for="(subGroup, index) in dataGroup.subGroup"
                        :key="index"
                        :header="subGroup.group | filterGroupname"
                        header-class="text-uppercase font-weight-bold"
                      >
                        <b-row class="edit-modal__row-group">
                          <b-col
                            md="12"
                            v-for="(subGroupData, subGroupKey) in subGroup.data"
                            :key="subGroupKey"
                          >
                            <div class="edit-modal__heading">
                              <b-btn
                                v-if="isFieldVisible(subGroupData.format) && !isEmptyValue(subGroupData.name)"
                                @click="toggleBulkDataState(subGroupData)"
                                :variant="buttonVariant(subGroupData.id)"
                                class="mb-1 w-100"
                                size="sm"
                                pill
                              >
                                {{
                                  getColumnName(subGroupData.name)
                                    | filterColumnName
                                }}
                              </b-btn>
                            </div>
                          </b-col>
                        </b-row>
                      </b-card>
                    </template>
                  </b-card>
                </b-card-group>
              </b-card-body>
            </b-collapse>
          </b-card>

          <b-card no-body class="w-100">
            <b-card-header
              header-tag="header"
              v-b-toggle.accordion-actions
              class="bulk-edit-modal__header"
              role="tab"
            >
              <span>Actions</span>
              <b-btn variant="secondary" size="sm" class="icon-collapsible">
                <span class="when-opened">
                  <i class="fa fa-minus"/>
                </span>
                <span class="when-closed">
                  <i class="fa fa-plus"/>
                </span>
              </b-btn>
            </b-card-header>

            <b-collapse id="accordion-actions" visible role="tabpanel">
              <b-card-body v-if="isAnyFieldsSelected">
                <div class="mb-2">
                  <div class="row align-items-start m-0">
                    <div class="col-sm col-sm-1/5">
                      <div class="text-uppercase font-weight-bold">Field</div>
                    </div>
                    <div class="col-sm col-sm-1/5">
                      <div class="text-uppercase font-weight-bold">Action</div>
                    </div>
                    <div class="col-sm-3">
                      <div class="text-uppercase font-weight-bold">Value</div>
                    </div>
                    <div class="col-sm"></div>
                  </div>
                </div>
                <div
                  v-for="(dataField, index) in flattenedData"
                  :key="index"
                  class="mb-2"
                >
                  <div
                    class="row align-items-start m-0"
                    v-if="bulkDataState[dataField.id]"
                  >
                    <div class="col-sm col-sm-1/5">
                      <b-btn
                        variant="success"
                        size="sm"
                        class="w-100 cursor-none"
                        pill
                      >
                        {{ getColumnName(dataField.name) | filterColumnName }}
                      </b-btn>
                    </div>
                    <div class="col-sm col-sm-1/5">
                      <b-select
                        :id="'action-option-' + dataField.id"
                        v-model="bulkActionsForApi[dataField.id]"
                        :options="
                          actionOptions(dataField.type, dataField.format)
                        "
                        value-field="value"
                        text-field="label"
                        size="sm"
                      />
                    </div>
                    <div class="col-sm-3">
                      <FormInput
                        v-if="dataField.type === 'input'"
                        :name="getColumnName(dataField.name)"
                        v-model="bulkDataForApi[dataField.id]"
                        :format="handleFormat(dataField.id, dataField.format)"
                        :type="dataField.type"
                        :rules="
                          handleActionRules(dataField.id, dataField.rules)
                        "
                        :placeholder="placeholderBulkEdit(dataField.name)"
                        :disabled="!bulkDataState[dataField.id]"
                        size="sm"
                      />
                      <Textarea
                        v-if="dataField.type === 'textarea'"
                        :name="getColumnName(dataField.name)"
                        v-model="bulkDataForApi[dataField.id]"
                        :rules="
                          handleActionRules(dataField.id, dataField.rules)
                        "
                        :placeholder="placeholderBulkEdit(dataField.name)"
                        :disabled="!bulkDataState[dataField.id]"
                        size="sm"
                      ></Textarea>
                      <Datepicker
                        v-if="dataField.type === 'datepicker'"
                        :name="getColumnName(dataField.name)"
                        v-model="bulkDataForApi[dataField.id]"
                        type="datetime"
                        :rules="
                          handleActionRules(dataField.id, dataField.rules)
                        "
                        :placeholder="placeholderBulkEdit(dataField.name)"
                        :disabled="!bulkDataState[dataField.id]"
                        size="sm"
                      ></Datepicker>
                      <ComboBox
                        v-if="dataField.type === 'combobox'"
                        :name="getColumnName(dataField.name)"
                        v-model="bulkDataForApi[dataField.id]"
                        :options="selectOption[dataField.id]"
                        :params="paramOption[dataField.id]"
                        :type="isSelect(dataField.format) ? 'select' : null"
                        :optionType="dataField.id"
                        :rules="
                          handleActionRules(dataField.id, dataField.rules)
                        "
                        :placeholder="placeholderBulkEdit(dataField.name)"
                        :disabled="!bulkDataState[dataField.id]"
                        size="sm"
                        @keyup="handleGetVariations"
                        @changeParam="handleChangeParams"
                      ></ComboBox>
                      <CheckBox
                      v-if="dataField.type === 'checkbox'"
                      v-model="bulkDataForApi[dataField.id]"
                      :type="isCheckBox(dataField.format) ? 'checkbox' : null"
                      ></CheckBox>
                    </div>
                    <div class="col-sm">
                      <b-btn
                        @click="bulkDataState[dataField.id] = false"
                        variant="danger"
                        class="rounded-circle bulk-edit-modal__remove-button"
                      >
                        <i class="fa fa-minus" />
                      </b-btn>
                    </div>
                  </div>
                  <b-alert v-if="bulkDataState.cog && dataField.name === 'cog'" class="mt-1" variant="info" show dismissible>COGs = Unit COGs * Quantity</b-alert>
                </div>
              </b-card-body>
              <b-card-body v-else>
                <div class="row align-items-start m-0">
                  <div class="col-sm">
                    Nothing has been changed.
                  </div>
                </div>
              </b-card-body>
            </b-collapse>
          </b-card>
        </b-row>
      </b-container>
      <div slot="modal-footer">
        <b-btn
          class="mr-2"
          variant
          @click="handleCloseModal()"
          :disabled="isUpdating"
        >
          Cancel
        </b-btn>
        <b-btn
          v-if="!isCustomExport"
          variant="warning"
          type="submit"
          @click.prevent="handleUpdateBulkSale()"
          :disabled="isUpdating || !isAnyFieldsSelected"
        >
          Update {{ itemsCount }}
        </b-btn>
        <b-btn
          v-else
          variant="warning"
          type="submit"
          @click.prevent="handleUpdateBulkEditUi()"
          :disabled="isUpdating || !isAnyFieldsSelected"
        >
          Export
        </b-btn>
      </div>
      <b-modal
        id="save-custom-export"
        title="Save Custom CSV Export"
        centered
      >
        <label class="mb-2">Name</label>
        <b-form-input class="mb-2" placeholder="Enter name" v-model="exportName" @keypress.enter="handleCustomExport"></b-form-input>
        <template v-slot:modal-footer>
          <div class="w-100">
            <b-button class="float-right" variant="primary" @click="handleCustomExport" :disabled="exportName ? false : true">Save</b-button>
            <b-button class="float-left" @click="closeModalSave">Cancel</b-button>
          </div>
        </template>
      </b-modal>
    </b-modal>
  </ValidationObserver>
</template>

<script>
import '@/plugins/vee-validate'
import { mapActions, mapGetters } from 'vuex'
import editSaleItemMixins from '@/mixins/editMixins/editSaleItemMixins'
import errorsHandlerMixins from '@/mixins/editMixins/errorsHandlerMixins'
import variationsMixins from '@/mixins/editMixins/variationsMixins'
import toastMixin from '@/components/common/toastMixin'
import { checkFieldFormatMixins } from '@/shared/utils'
import {
  UPDATE_ACTIONS,
  CHANGE_TO_ACTION,
  NUMERIC_ACTIONS
} from '@/shared/constants'

import ComboBox from '@/components/common/ComboBox/ComboBox'
import Datepicker from '@/components/common/Datepicker/Datepicker'
import ErrorMessages from '@/components/common/ActionModals/ErrorMessages'
import FormInput from '@/components/common/FormInput/FormInput'
import Textarea from '@/components/common/Textarea/Textarea'
import CheckBox from '@/components/common/CheckBox/CheckBox'
import _ from 'lodash'

export default {
  name: 'EditModal',
  components: { ComboBox, Datepicker, ErrorMessages, FormInput, Textarea, CheckBox },
  props: {
    id: {
      type: String,
      required: true
    },
    dataRow: {
      type: [Object, Array]
    },
    columns: {
      type: Array
    },
    isCustomExport: {
      type: Boolean
    }
  },
  data() {
    return {
      bulkDataForApi: {},
      bulkDataState: {},
      bulkActionsForApi: {},
      updateActions: UPDATE_ACTIONS,
      isUpdating: false,
      exportName: '',
      isOpen: false
    }
  },
  mixins: [
    checkFieldFormatMixins,
    editSaleItemMixins,
    errorsHandlerMixins,
    toastMixin,
    variationsMixins
  ],
  computed: {
    ...mapGetters({
      getUserId: `ps/userModule/GET_USER_ID`,
      currentCustomExportId: `pf/analysis/currentCustomExportId`
    }),
    placeholderBulkEdit() {
      return columnName =>
        'Enter new ' + this.$options.filters.filterColumnName(columnName)
    },
    isFieldVisible() {
      return format => !this.isReadonly(format)
    },
    buttonVariant() {
      return field => (this.bulkDataState[field] ? 'success' : 'secondary')
    },
    itemsCount() {
      return `${this.numberFormat(this.totalItems)} Sale Items`
    },
    isAnyFieldsSelected() {
      for (const value of Object.values(this.bulkDataState)) {
        if (value) return true
      }
      return false
    },
    userId() {
      return this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
    },
    isEmptyValue() {
      return (value) => {
        return _.isEmpty(this.getColumnName(value))
      }
    }
  },
  methods: {
    ...mapActions({
      updateSaleItem: `pf/analysis/updateSaleItem`,
      updateBulkSaleItems: `pf/bulk/updateBulkSaleItems`,
      getBulkListProgress: `pf/bulk/getBulkListProgress`,
      createCustomExport: `pf/bulk/createCustomExport`,
      setCurrentCustomExportId: 'pf/analysis/setCurrentCustomExportId'
    }),
    toggleBulkDataState(field) {
      this.$set(this.bulkDataState, field.id, !this.bulkDataState[field.id])
      if (field.type === 'checkbox') {
        this.$set(this.bulkDataForApi, field.id, false)
      }
    },
    actionOptions(type, format) {
      if (type === 'input' || type === 'textarea') {
        if (this.isCurrency(format)) {
          return this.updateActions.numberic
        } else if (this.isPercent(format)) {
          return this.updateActions.default
        } else {
          return this.updateActions.text
        }
      } else {
        return this.updateActions.default
      }
    },
    handleActionRules(fieldID, rules) {
      switch (this.bulkActionsForApi[fieldID]) {
        case NUMERIC_ACTIONS.DIVIDE_BY:
          return ['is_not:0', 'currency', 'required']
        case CHANGE_TO_ACTION:
        case NUMERIC_ACTIONS.ADD:
        case NUMERIC_ACTIONS.SUBTRACT:
        case NUMERIC_ACTIONS.MULTIPLY_BY:
        case NUMERIC_ACTIONS.PERCENT_INCREASE:
        case NUMERIC_ACTIONS.PERCENT_DECREASE:
        case NUMERIC_ACTIONS.UNDO_PERCENT_INCREASE:
        case NUMERIC_ACTIONS.UNDO_PERCENT_DECREASE:
          const newRules = rules
            ? rules.includes('required')
              ? rules
              : rules.push('required')
            : ['required']
          return newRules
        default:
          return ['required']
      }
    },
    handleFormat(fieldID, format) {
      switch (this.bulkActionsForApi[fieldID]) {
        case CHANGE_TO_ACTION:
          return format
        case NUMERIC_ACTIONS.ADD:
        case NUMERIC_ACTIONS.SUBTRACT:
          return ['currency']
        case NUMERIC_ACTIONS.PERCENT_INCREASE:
        case NUMERIC_ACTIONS.PERCENT_DECREASE:
        case NUMERIC_ACTIONS.UNDO_PERCENT_INCREASE:
        case NUMERIC_ACTIONS.UNDO_PERCENT_DECREASE:
          return ['percent']
        default:
          return []
      }
    },

    handleUpdateBulkSale() {
      this.$refs.bulkEditObserver.validate().then(success => {
        if (!success) {
          return
        }
        this.isUpdating = true
        const data = {
          params: {
            client_id: this.clientID
          },
          payload: this.latestBulkDataForApi('edit')
        }

        this.updateBulkSaleItems(data).then(resp => {
          if (resp.status === 200 || resp.status === 201) {
            this.$CBPO.$bus.$emit(`BULK_EDIT_UPDATE_${this.sdkID}`)
            this.$bus.$emit('updateBulkProgress')
            this.errorMessages = {}
            this.handleCloseModal()
            this.vueToast('success', this.BULK_PROGRESS.editCreated)
            this.isUpdating = false
          } else {
            this.errorMessages = this.filterErrorMessage(resp.data)
            this.isUpdating = false
          }
        })
      })
    },
    handleUpdateBulkEditUi() {
      this.$refs.bulkEditObserver.validate().then(success => {
        if (!success) {
          return
        }
        this.$bvModal.show('save-custom-export')
      })
    },
    closeModalSave() {
      this.$bvModal.hide('save-custom-export')
    },
    async handleCustomExport() {
      this.setCurrentCustomExportId({clientId: this.$route.params.client_id, userId: this.userId, id: null})
      this.$bvModal.hide('save-custom-export')
      this.$bvModal.hide('bulk-edit-modal')
      try {
        const payload = this.buildPayloadCustomExport()
        const data = {
          params: {
            clientID: this.clientID,
            userID: this.userId
          },
          payload: payload
        }
        this.createCustomExport(data).then(response => {
          this.exportName = ''
          this.setCurrentCustomExportId({clientId: this.$route.params.client_id, userId: this.userId, id: response.data.id})
          this.bulkDataState = {}
          this.bulkDataForApi = {}
        })
      } catch (error) {
        this.vueToast('error', error.response.data.message)
      }
    }
  },
  filters: {
    filterGroupname: function(str) {
      return str ? str.replace(/([A-Z])/g, ' $1').toUpperCase() : str
    }
  },
  watch: {
    dataRow(newValue) {
      this.bulkDataForApi = {}
      this.bulkDataState = {}
      this.bulkActionsForApi = {}
      this.errorMessages = {}
    },
    bulkDataState(newValue) {
      Object.keys(newValue).map(key => {
        if (newValue[key]) {
          if (!this.bulkActionsForApi.hasOwnProperty(key)) {
            this.$set(this.bulkActionsForApi, key, CHANGE_TO_ACTION)
          }
        }
      })
    },
    isOpen(val) {
      // variations mixin
      if (val) {
        this.initialVariations()
      }
    }
  }
}
</script>

<style lang="scss">
@import "./ActionModals.scss";
</style>
