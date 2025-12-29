<template>
  <ValidationObserver ref="editObserver" slim>
    <b-modal
      :id="id"
      size="lgx"
      title="Edit Sale Item"
      modal-class="editable-modal"
      v-model="isOpen"
      centered
      @hidden="handleCancel()"
    >
      <ErrorMessages
        :showErrorAlert="showErrorAlert"
        :errorMessages="errorMessages"
      />
      <b-container fluid class="edit-modal">
        <b-row>
          <b-card-group>
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
                    <span v-if="internalData && internalData.data">
                      {{ getColumnName(dataField.name) | filterColumnName }}
                    </span>
                    <span v-if="dataField.type === 'datepicker'" class="timezone-title">
                      {{ timezoneTitle }}
                    </span>
                    <i
                      v-if="shouldShowHelpText(dataField, internalData.data)"
                      v-b-tooltip.hover.bottom="{ variant: 'info', html: true }"
                      class="fa fa-info-circle ml-1 text-info"
                      :title="dataField.helpText(internalData.data)"
                    />
                  </div>
                  <!-- Single Sale Item Editing -->
                  <div
                    class="edit-modal__col"
                    v-if="hasColumnData(internalData, dataField.name)"
                  >
                    <FormInput
                      :name="getColumnName(dataField.name)"
                      v-model="internalData.data[dataField.name].base"
                      :format="dataField.format"
                      :type="dataField.type"
                      :rules="dataField.rules"
                      :disabled="disabledCases(dataField)"
                      :id="dataField.id"
                      @open-modal="openBreakdownDetailModal(dataField.id)"
                      :isGettingListBreakdown="isGettingListBreakdown"
                    />
                    <Textarea
                      v-if="dataField.type === 'textarea'"
                      :name="getColumnName(dataField.name)"
                      v-model="internalData.data[dataField.name].base"
                      :rules="dataField.rules"
                    ></Textarea>
                    <Datepicker
                      v-if="dataField.type === 'datepicker'"
                      :name="getColumnName(dataField.name)"
                      v-model="internalData.data[dataField.name].base"
                      :timezone="timezone.utc"
                      type="datetime"
                      :rules="dataField.rules"
                    ></Datepicker>
                    <ComboBox
                      v-if="dataField.type === 'combobox'"
                      v-model="internalData.data[dataField.name].base"
                      :options="selectOption[dataField.id]"
                      :params="paramOption[dataField.id]"
                      :type="isSelect(dataField.format) ? 'select' : null"
                      :optionType="dataField.id"
                      :disabled="disabledCases(dataField)"
                      @keyup="handleGetVariations"
                      @changeParam="handleChangeParams"
                    ></ComboBox>
                    <CheckBox
                      v-if="dataField.type === 'checkbox'"
                      v-model="internalData.data[dataField.name].base"
                      :type="isCheckBox(dataField.format) ? 'checkbox' : null"
                    >
                    </CheckBox>
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
                        <span v-if="internalData && internalData.data">
                          {{
                            getColumnName(subGroupData.name) | filterColumnName
                          }}
                        </span>
                      </div>
                      <!-- Single Sale Item Editing -->
                      <div
                        class="edit-modal__col"
                        v-if="hasColumnData(internalData, subGroupData.name)"
                      >
                        <FormInput
                          :name="getColumnName(subGroupData.name)"
                          v-model="internalData.data[subGroupData.name].base"
                          :format="subGroupData.format"
                          :type="subGroupData.type"
                          :rules="subGroupData.rules"
                          :disabled="disabledCases(subGroupData)"
                          :id="subGroupData.id"
                          @open-modal="
                            openBreakdownDetailModal(subGroupData.id)
                          "
                          :isGettingListBreakdown="isGettingListBreakdown"
                        />
                      </div>
                    </b-col>
                  </b-row>
                </b-card>
              </template>
            </b-card>
          </b-card-group>
        </b-row>
      </b-container>
      <div slot="modal-footer">
        <b-btn
          class="mr-2"
          variant
          @click="handleCancel()"
          :disabled="isUpdating"
        >
          <i class="icon-close"></i> Cancel
        </b-btn>
        <b-btn
          variant="warning"
          type="submit"
          v-if="internalData && internalData.data"
          @click.prevent="handleUpdateSingleSale()"
          :disabled="isUpdating || isNotChanged"
        >
          <i class="fa fa-save"></i> Save Changes
        </b-btn>
      </div>
    </b-modal>
    <BreakdownModal
      id="breakdown-modal"
      :dataRow="breakdownData"
      :typeID="breakdownTypeID"
    />
  </ValidationObserver>
</template>

<script>
import _ from 'lodash'
import '@/plugins/vee-validate'
import moment from 'moment-timezone'
import { mapActions, mapGetters } from 'vuex'
import { UNIQUE_KEY_BE } from '@/shared/constants/column.constant'
import editSaleItemMixins from '@/mixins/editMixins/editSaleItemMixins'
import errorsHandlerMixins from '@/mixins/editMixins/errorsHandlerMixins'
import toastMixin from '@/components/common/toastMixin'
import variationsMixins from '@/mixins/editMixins/variationsMixins'
import { checkFieldFormatMixins } from '@/shared/utils'

import ComboBox from '@/components/common/ComboBox/ComboBox'
import Datepicker from '@/components/common/Datepicker/Datepicker'
import ErrorMessages from '@/components/common/ActionModals/ErrorMessages'
import FormInput from '@/components/common/FormInput/FormInput'
import Textarea from '@/components/common/Textarea/Textarea'
import CheckBox from '@/components/common/CheckBox/CheckBox'
import BreakdownModal from '@/components/common/ItemsModals/BreakdownModal'

export default {
  name: 'EditModal',
  components: {
    ComboBox,
    Datepicker,
    ErrorMessages,
    FormInput,
    Textarea,
    BreakdownModal,
    CheckBox
  },
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
    timezone: {
      type: Object
    }
  },
  data() {
    return {
      isUpdating: false,
      isGettingListBreakdown: false,
      breakdownTypeID: '',
      breakdownData: {},
      isOpen: false,
      idsWithHelpTextForBreakdown: [
        'sale_charged'
      ]
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
      listBreakdownListing: `pf/analysis/listBreakdownListing`,
      listBreakdownOther: `pf/analysis/listBreakdownOther`,
      listBreakdownTaxCharged: `pf/analysis/listBreakdownTaxCharged`,
      listBreakdownShippingCost: `pf/analysis/listBreakdownShippingCost`,
      listBreakdownReimbursementCosts: `pf/analysis/listBreakdownReimbursementCosts`,
      listBreakdownChannelTaxWithheld: `pf/analysis/listBreakdownChannelTaxWithheld`,
      listBreakdownSaleCharged: `pf/analysis/listBreakdownSaleCharged`,
      listBreakdownReturnPostageBilling: `pf/analysis/listBreakdownReturnPostageBilling`
    }),
    isNotChanged() {
      return (
        JSON.stringify(this.internalData.data) ===
        JSON.stringify(this.originalInternalData.data)
      )
    },
    hasBreakdown() {
      return id =>
        (id === 'other_channel_fees' &&
          this.listBreakdownOther.results &&
          this.listBreakdownOther.results.length > 0) ||
        (id === 'channel_listing_fee' &&
          this.listBreakdownListing.results &&
          this.listBreakdownListing.results.length > 0) ||
        (id === 'tax_charged' &&
          this.listBreakdownTaxCharged.results &&
          this.listBreakdownTaxCharged.results.length > 0) ||
        (id === 'channel_tax_withheld' &&
          this.listBreakdownChannelTaxWithheld.results &&
          this.listBreakdownChannelTaxWithheld.results.length > 0) ||
        (id === 'sale_charged' &&
          this.listBreakdownSaleCharged.results &&
          this.listBreakdownSaleCharged.results.length > 0) ||
        (id === 'reimbursement_costs' &&
          this.listBreakdownReimbursementCosts.results &&
          this.listBreakdownReimbursementCosts.results.length > 0) ||
        (id === 'return_postage_billing' &&
          this.listBreakdownReturnPostageBilling.results &&
          this.listBreakdownReturnPostageBilling.results.length > 0
        )
    },
    disabledCases() {
      return dataField => {
        // Case shipping_cost_accuracy === 100
        const accurateShippingCost =
          dataField.name === 'actual_shipping_cost' &&
          this.hasColumnData(this.internalData, 'shipping_cost_accuracy') &&
          parseInt(this.internalData.data.shipping_cost_accuracy.base) === 100
        const accurateSaleCharged =
          dataField.name === 'item_sale_charged' &&
          this.hasColumnData(this.internalData, 'sale_charged_accuracy') &&
          parseInt(this.internalData.data.sale_charged_accuracy.base) === 100
        const accurateChannelListFee =
          dataField.name === 'item_channel_listing_fee' &&
          this.hasColumnData(this.internalData, 'channel_listing_fee_accuracy') &&
          parseInt(this.internalData.data.channel_listing_fee_accuracy.base) === 100
        const accurateWarehouseProcessingFee =
          dataField.name === 'warehouse_processing_fee' &&
          this.hasColumnData(this.internalData, 'warehouse_processing_fee_accuracy') &&
          parseInt(this.internalData.data.warehouse_processing_fee_accuracy.base) === 100
        const accurateFulfillmentType =
          dataField.name === 'fulfillment_type' &&
          this.hasColumnData(this.internalData, 'fulfillment_type_accuracy') &&
          parseInt(this.internalData.data.fulfillment_type_accuracy.base) === 100
        const accurateChannelTaxWithheld =
          dataField.name === 'channel_tax_withheld' &&
          this.hasColumnData(this.internalData, 'channel_tax_withheld_accuracy') &&
          parseInt(this.internalData.data.channel_tax_withheld_accuracy.base) === 100
        const accurateInboundFreightCost =
          dataField.name === 'inbound_freight_cost' &&
          this.hasColumnData(this.internalData, 'inbound_freight_cost_accuracy') &&
          parseInt(this.internalData.data.inbound_freight_cost_accuracy.base) === 100
        const accurateOutboundFreightCost =
          dataField.name === 'outbound_freight_cost' &&
          this.hasColumnData(this.internalData, 'outbound_freight_cost_accuracy') &&
          parseInt(this.internalData.data.outbound_freight_cost_accuracy.base) === 100
        return (
          this.isReadonly(dataField.format) ||
          this.hasBreakdown(dataField.id) ||
          accurateShippingCost ||
          accurateChannelListFee ||
          accurateWarehouseProcessingFee ||
          accurateFulfillmentType ||
          accurateChannelTaxWithheld ||
          accurateSaleCharged ||
          accurateInboundFreightCost ||
          accurateOutboundFreightCost
        )
      }
    },
    timezoneTitle() {
      return `@ UTC${moment.tz(this.timezone.utc).format('Z (z)')}`
    },
    shouldShowHelpText() {
      return (dataField, internalData) => {
        if (!internalData) return false
        const validMarket = 'amazon'
        // isBreakdownId checks whether this ID can have a breakdown list or not.
        const isBreakdownId = this.idsWithHelpTextForBreakdown.includes(dataField.id)
        // Check this condition to prevent the (i) icon from appearing when the last item shows it.
        if ((this.isGettingListBreakdown && isBreakdownId) || !internalData.channel_name) return false
        const isAmazonChannel = internalData.channel_name.base.toLowerCase().includes(validMarket)
        const shouldShow = dataField.helpText && ((this.hasBreakdown(dataField.id) && isAmazonChannel) || !isBreakdownId)
        return shouldShow
      }
    }
  },
  methods: {
    ...mapActions({
      updateSaleItem: `pf/analysis/updateSaleItem`,
      getListBreakdownListing: `pf/analysis/getListBreakdownListing`,
      getListBreakdownOther: `pf/analysis/getListBreakdownOther`,
      getListBreakdownTaxCharged: `pf/analysis/getListBreakdownTaxCharged`,
      getListBreakdownShippingCost: `pf/analysis/getListBreakdownShippingCost`,
      getListBreakdownReimbursementCosts: `pf/analysis/getListBreakdownReimbursementCosts`,
      getListBreakdownChannelTaxWithheld: `pf/analysis/getListBreakdownChannelTaxWithheld`,
      getListBreakdownSaleCharged: `pf/analysis/getListBreakdownSaleCharged`,
      getListBreakdownReturnPostageBilling: `pf/analysis/getListBreakdownReturnPostageBilling`
    }),
    handleCancel() {
      this.internalData.data = _.cloneDeep(this.originalInternalData.data)
      this.handleCloseModal()
    },
    handleUpdateSingleSale() {
      this.$refs.editObserver.validate().then(success => {
        if (!success) {
          return
        }
        this.isUpdating = true
        const data = {
          params: {
            client_id: this.clientID,
            id: this.internalData.data[UNIQUE_KEY_BE].base
          },
          payload: this.dataForApi
        }
        this.updateSaleItem(data).then(resp => {
          if (resp.status === 200) {
            this.$CBPO.$bus.$emit(`SINGLE_EDIT_UPDATE_${this.sdkID}`, {
              id: this.internalData.pk_id_sdk,
              updatedData: this.internalData
            })
            this.errorMessages = {}
            this.handleCloseModal()
            this.vueToast('success', 'Updated successfully')
            this.isUpdating = false
          } else {
            this.errorMessages = this.filterErrorMessage(resp.data)
            this.isUpdating = false
          }
        })
      })
    },
    openBreakdownDetailModal(id) {
      this.breakdownTypeID = id
      this.breakdownData = this.internalData
      this.$nextTick(() => {
        this.$bvModal.show('breakdown-modal')
      })
    }
  },
  filters: {
    filterGroupname: function(str) {
      return str ? str.replace(/([A-Z])/g, ' $1').toUpperCase() : str
    }
  },
  watch: {
    async dataRow(newValue) {
      this.errorMessages = {}
      if (this.internalData.data && this.hasColumnData(newValue, 'sale_item_id')) {
        this.isGettingListBreakdown = true
        let payload = {
          client_id: this.$route.params.client_id,
          item_id: newValue.data.sale_item_id.base
        }
        await this.getListBreakdownListing(payload)
        await this.getListBreakdownOther(payload)
        await this.getListBreakdownTaxCharged(payload)
        await this.getListBreakdownShippingCost(payload)
        await this.getListBreakdownReimbursementCosts(payload)
        await this.getListBreakdownChannelTaxWithheld(payload)
        await this.getListBreakdownSaleCharged(payload)
        await this.getListBreakdownReturnPostageBilling(payload)
        this.isGettingListBreakdown = false
      }
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

<style lang="scss" scoped>
@import "./ActionModals.scss";
::v-deep .tooltip-inner {
  a {
    color: black;
    font-weight: 600;
  }
}
</style>
