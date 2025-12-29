<template>
  <div>
    <b-row class="mb-2">
      <b-col md="6">
        <span>Brand name</span>
        <b-form-input :class="{'border-danger': $v.itemEdit.brand.$dirty && !$v.itemEdit.brand.required}" @input="$v.itemEdit.brand.$touch()" v-model="itemEdit.brand"></b-form-input>
        <div v-show="$v.itemEdit.brand.$dirty && !$v.itemEdit.brand.required" class="text-danger">The Brand Name is required</div>
      </b-col>
      <b-col md="6">
        <span>Channel</span>
        <b-form-select class="select-channel"
          v-model="itemEdit.channel"
          :options="channelOptions"
          :class="{'border-danger': $v.itemEdit.channel.$dirty && !$v.itemEdit.channel.required}"
        />
        <div v-show="$v.itemEdit.channel.$dirty && !$v.itemEdit.channel.required" class="text-danger">The Channel is required</div>
      </b-col>
    </b-row>
    <b-row class="mb-2">
      <b-col md="6">
        <span>Est. 1st Item Shipcost</span>
          <span :id="`question-tooltip-${tooltipInfo[0].name}-edit`" class="ml-1" v-html="tooltipInfo[0].trigger">
          </span>
          <b-popover :target="`question-tooltip-${tooltipInfo[0].name}-edit`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[0].text"></div>
          </b-popover>
        <b-form-input
          @input="$v.itemEdit.est_first_item_shipcost.$touch()"
          v-model="itemEdit.est_first_item_shipcost"
          @keypress.native="onKeyPress"
          :class="{'border-danger': $v.itemEdit.est_first_item_shipcost.$dirty && (!$v.itemEdit.est_first_item_shipcost.required || !$v.itemEdit.est_first_item_shipcost.numberValidation)}"
        >
        </b-form-input>
        <div v-show="$v.itemEdit.est_first_item_shipcost.$dirty && !$v.itemEdit.est_first_item_shipcost.required" class="text-danger">The Est. 1st Item Shipcost is required</div>
        <div v-show="$v.itemEdit.est_first_item_shipcost.$dirty && !$v.itemEdit.est_first_item_shipcost.numberValidation" class="text-danger" v-html="displayValidationMessage()"/>
      </b-col>
      <b-col md="6">
        <span>Est. Add. Item Shipcost</span>
          <span :id="`question-tooltip-${tooltipInfo[1].name}-edit`" class="ml-1" v-html="tooltipInfo[1].trigger">
          </span>
          <b-popover :target="`question-tooltip-${tooltipInfo[1].name}-edit`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[1].text"></div>
          </b-popover>
        <b-form-input
          @input="$v.itemEdit.est_add_item_shipcost.$touch()"
          v-model="itemEdit.est_add_item_shipcost"
          @keypress.native="onKeyPress"
          :class="{'border-danger': $v.itemEdit.est_add_item_shipcost.$dirty && (!$v.itemEdit.est_add_item_shipcost.required || !$v.itemEdit.est_add_item_shipcost.numberValidation)}"
        >
        </b-form-input>
        <div v-show="$v.itemEdit.est_add_item_shipcost.$dirty && !$v.itemEdit.est_add_item_shipcost.required" class="text-danger">The Est. Add. Item Shipcost is required</div>
        <div v-show="$v.itemEdit.est_add_item_shipcost.$dirty && !$v.itemEdit.est_add_item_shipcost.numberValidation" class="text-danger" v-html="displayValidationMessage()"/>
      </b-col>
    </b-row>
    <b-row class="mb-2">
      <b-col md="6">
        <span>Est. FBA Fees</span>
          <span :id="`question-tooltip-${tooltipInfo[3].name}-edit`" class="ml-1" v-html="tooltipInfo[3].trigger">
          </span>
          <b-popover :target="`question-tooltip-${tooltipInfo[3].name}-edit`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[3].text"></div>
          </b-popover>
        <b-form-input
          @input="$v.itemEdit.est_fba_fees.$touch()"
          v-model="itemEdit.est_fba_fees"
          @keypress.native="onKeyPress"
          :class="{'border-danger': $v.itemEdit.est_fba_fees.$dirty && (!$v.itemEdit.est_fba_fees.required || !$v.itemEdit.est_fba_fees.numberValidation)}"
        >
        </b-form-input>
        <div v-show="$v.itemEdit.est_fba_fees.$dirty && !$v.itemEdit.est_fba_fees.required" class="text-danger">The Est. FBA Fees is required</div>
        <div v-show="$v.itemEdit.est_fba_fees.$dirty && !$v.itemEdit.est_fba_fees.numberValidation" class="text-danger" v-html="displayValidationMessage()" />
      </b-col>
    </b-row>
    <b-row class="mb-2">
      <b-col md="6">
        <span>PO Dropship Method</span>
        <b-form-select
          v-model="itemEdit.po_dropship_method"
          :options="dropshipMethodOptions"
        />
      </b-col>
      <b-col md="6" class="clear-icon">
        <span>PO Dropship</span>
          <span :id="`question-tooltip-${tooltipInfo[2].name}-edit`" class="ml-1" v-html="tooltipInfo[2].trigger">
          </span>
          <b-popover :target="`question-tooltip-${tooltipInfo[2].name}-edit`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[2].text"></div>
          </b-popover>
        <b-form-input
          @input="$v.itemEdit.po_dropship_cost.$touch()"
          v-model="itemEdit.po_dropship_cost" @keypress.native="onKeyPress"
          :state="dropshipValidationState"
          :class="{'border-danger': $v.itemEdit.po_dropship_cost.$dirty && (!$v.itemEdit.po_dropship_cost.required || !$v.itemEdit.po_dropship_cost.numberValidation || !$v.itemEdit.po_dropship_cost.maxValue)}"
        >
        </b-form-input>
        <div v-show="$v.itemEdit.po_dropship_cost.$dirty && !$v.itemEdit.po_dropship_cost.required" class="text-danger">The PO Dropship is required</div>
        <div
          v-show="itemEdit.po_dropship_method === 'Percent' &&
          $v.itemEdit.po_dropship_cost.$dirty &&
          !$v.itemEdit.po_dropship_cost.maxValue" class="text-danger" key=""
        >
          The value must be in [0, 100].
        </div>
        <div
          v-show="$v.itemEdit.po_dropship_cost.$dirty &&
          !$v.itemEdit.po_dropship_cost.numberValidation" class="text-danger"
          v-html="displayValidationMessage(itemEdit.po_dropship_method)"
        />
      </b-col>
    </b-row>
    <b-row class="mb-2">
      <b-col md="6">
        <span>MFN Formula</span>
          <span :id="`question-tooltip-${tooltipInfo[6].name}-edit`" class="ml-1" v-html="tooltipInfo[6].trigger">
          </span>
          <b-popover :target="`question-tooltip-${tooltipInfo[6].name}-edit`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[6].text"></div>
          </b-popover>
        <b-form-select
          v-model="itemEdit.mfn_formula"
          :options="mfnOptions"
        />
      </b-col>
      <b-col md="6">
        Auto Update Sales
        <b-form-checkbox
          class="mt-2"
          v-model="itemEdit.auto_update_sales"
          switch
        />
      </b-col>
    </b-row>
    <b-row class="mb-2">
      <b-col md="6">
        <span>Est. Unit Inbound Freight Cost</span>
          <span :id="`question-tooltip-${tooltipInfo[4].name}-edit`" class="ml-1" v-html="tooltipInfo[4].trigger">
          </span>
          <b-popover :target="`question-tooltip-${tooltipInfo[4].name}-edit`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[4].text"></div>
          </b-popover>
        <b-form-input
          @input="$v.itemEdit.est_unit_inbound_freight_cost.$touch()"
          v-model="itemEdit.est_unit_inbound_freight_cost"
          type="number"
          :class="{'border-danger': !$v.itemEdit.est_unit_inbound_freight_cost.numberValidation}"
        />
        <div v-show="!$v.itemEdit.est_unit_inbound_freight_cost.numberValidation" class="text-danger" v-html="displayValidationMessage()"/>
      </b-col>
      <b-col md="6">
        <span>Est. Unit Outbound Freight Cost</span>
          <span :id="`question-tooltip-${tooltipInfo[5].name}-edit`" class="ml-1" v-html="tooltipInfo[5].trigger">
          </span>
          <b-popover :target="`question-tooltip-${tooltipInfo[5].name}-edit`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[5].text"></div>
          </b-popover>
        <b-form-input
          @input="$v.itemEdit.est_unit_outbound_freight_cost.$touch()"
          v-model="itemEdit.est_unit_outbound_freight_cost"
          type="number"
          :class="{'border-danger': !$v.itemEdit.est_unit_outbound_freight_cost.numberValidation}"
        />
        <div v-show="!$v.itemEdit.est_unit_outbound_freight_cost.numberValidation" class="text-danger" v-html="displayValidationMessage()" />
      </b-col>
    </b-row>
    <b-row class="mb-2">
      <b-col md="6">
        <span>Add. User-Provided Method</span>
        <b-form-select
          v-model="itemEdit.add_user_provided_method"
          :options="userProvidedOptions"
        />
      </b-col>
      <b-col md="6" class="clear-icon">
        <span>Add. User-Provided</span>
        <b-form-input
          @input="$v.itemEdit.add_user_provided_cost.$touch()"
          v-model="itemEdit.add_user_provided_cost" @keypress.native="onKeyPress"
          :state="userProvidedValidationState"
          :class="{'border-danger': $v.itemEdit.add_user_provided_cost.$dirty && (!$v.itemEdit.add_user_provided_cost.numberValidation || !$v.itemEdit.add_user_provided_cost.maxValue)}"
        >
        </b-form-input>
        <div
          v-show="itemEdit.add_user_provided_method === 'Percent' &&
          $v.itemEdit.add_user_provided_cost.$dirty &&
          !$v.itemEdit.add_user_provided_cost.maxValue" class="text-danger" key=""
        >
          The value must be in [0, 100].
        </div>
        <div
          v-show="$v.itemEdit.add_user_provided_cost.$dirty &&
          !$v.itemEdit.add_user_provided_cost.numberValidation" class="text-danger"
          v-html="displayValidationMessage(itemEdit.add_user_provided_method)"
        />
      </b-col>
    </b-row>
    <b-row class="mb-2">
      <b-col md="6">
        Segment
        <b-form-textarea v-model="itemEdit.segment"></b-form-textarea>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import _ from 'lodash'
import { required, minValue, maxValue } from 'vuelidate/lib/validators'

const numberValidation = (value) => value ? /^-?\d{1,4}(\.\d{0,2})?$/.test(value) : true

export default {
  name: 'EditBrandSettingModal',
  props: {
    item: Object,
    tooltipInfo: Array
  },
  data() {
    return {
      itemEdit: {},
      dropshipMethodOptions: [
        {value: 'Cost', text: 'Cost'},
        {value: 'Percent', text: 'Percent'}
      ],
      userProvidedOptions: [
        {value: 'Cost', text: 'Cost'},
        {value: 'Percent', text: 'Percent'}
      ],
      mfnOptions: [
        {value: 'Dropship', text: 'Dropship'},
        {value: 'Rapid Access', text: 'Rapid Access'},
        {value: 'Standard', text: 'Standard'},
        {value: null, text: 'None'}
      ]
    }
  },
  validations() {
    return {
      itemEdit: {
        brand: { required },
        channel: { required },
        est_add_item_shipcost: { required, numberValidation },
        est_first_item_shipcost: { required, numberValidation },
        est_fba_fees: { required, numberValidation },
        est_unit_inbound_freight_cost: { numberValidation },
        est_unit_outbound_freight_cost: { numberValidation },
        po_dropship_cost: {
          required,
          minValue: minValue(0),
          maxValue: maxValue(this.itemEdit.po_dropship_method === 'Percent' ? 100 : Infinity),
          numberValidation
        },
        add_user_provided_cost: {
          minValue: minValue(0),
          maxValue: maxValue(this.itemEdit.add_user_provided_method === 'Percent' ? 100 : Infinity),
          numberValidation
        }
      }
    }
  },
  async created() {
    this.itemEdit = _.cloneDeep(this.$props.item)
    await this.getChannelList({client_id: this.$route.params.client_id})
  },
  computed: {
    ...mapGetters({
      channelList: 'pf/analysis/channelList'
    }),
    channelOptions() {
      let channelList = []
      if (this.channelList && this.channelList.results) {
        channelList = this.channelList.results.reduce((acc, item) => {
          acc.push({ text: item.label, value: item.name })
          return acc
        }, [])
      }
      return channelList
    },
    dropshipValidationState() {
      return this.itemEdit.po_dropship_method === 'Percent' && (this.itemEdit.po_dropship_cost < 0 || this.itemEdit.po_dropship_cost > 100) ? false : null
    },
    userProvidedValidationState() {
      return this.itemEdit.add_user_provided_method === 'Percent' && (this.itemEdit.add_user_provided_cost < 0 || this.itemEdit.add_user_provided_cost > 100) ? false : null
    }
  },
  methods: {
    ...mapActions({
      getChannelList: 'pf/analysis/getChannelList'
    }),
    onKeyPress(e) {
      const keyCode = e.which
      /*
      8 - (backspace)
      48-57 - (0-9)Numbers
      96-105 - (0-9)Keypad - KeyPress doesn't care Keypad
      44 - (comma) - just with KeyPress
      46 - (dot) - just with KeyPress
      */
      if (keyCode !== 8 && keyCode !== 46 && (keyCode < 48 || keyCode > 57)) {
        e.preventDefault()
      }
    },
    displayValidationMessage(value) {
      return value === 'Percent' ? `Ensure that there are no more than 2 decimal places.`
        : `
        Ensure that:
        <ul>
          <li>There are no more than 6 digits in total.</li>
          <li>There are no more than 4 digits before the decimal point.</li>
          <li>There are no more than 2 decimal places.</li>
        </ul>
      `
    }
  }
  // mounted() {
  //   this.itemEdit = _.cloneDeep(this.$props.item)
  // }
}
</script>
<style scoped>
.custom-select {
 min-height: 36px;
}
.clear-icon .is-invalid {
  background-image: none ;
}
::v-deep .select-channel:focus {
  border: 1px solid #E6E8F0 !important;
}
::v-deep .border-danger {
  border-color: #f86c6b !important;
}
::v-deep .border-danger:focus {
  border-color: #f86c6b !important;
  box-shadow: 0 0 0 0.2rem rgba(248, 108, 107, 0.25) !important;
}
</style>
