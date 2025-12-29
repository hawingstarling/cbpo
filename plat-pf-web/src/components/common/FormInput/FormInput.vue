<template>
  <ValidationProvider
    :name="filteredName(name)"
    immediate
    :rules="validateRules"
    v-slot="{ errors }"
    :vid="name"
  >
    <b-input-group
      :size="size"
      class="pf-input"
      :class="{ 'is-invalid': errors.length }"
      :prepend="isCurrency(format) ? '$' : null"
      :append="isPercent(format) ? '%' : null"
      v-if="type === 'input'"
    >
      <b-form-input
        v-if="isDatetime(format)"
        :value="value | moment('MM/DD/YYYY hh:mm A')"
        :placeholder="placeholder"
        :disabled="disabled"
      ></b-form-input>
      <b-form-input
        v-else
        v-model="dataValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :state="isHasError(errors)"
        @keypress.native="onKeyPress"
        trim
      ></b-form-input>
      <b-input-group-append v-if="allowBreakDown(id)">
        <b-button class="btn-no-hover" :disabled="isGettingListBreakdown || disableBreakdown" @click="$emit('open-modal')" variant="primary">
          <div class="spinner-border thin-spinner spinner-border-sm" v-if="isGettingListBreakdown"></div><i class="fa fa-pie-chart" v-else></i>
        </b-button>
      </b-input-group-append>
    </b-input-group>
    <b-form-invalid-feedback v-if="errors.length">
      {{ errors[0] }}
    </b-form-invalid-feedback>
  </ValidationProvider>
</template>

<script>
import '@/plugins/vee-validate'
import { checkFieldFormatMixins, validateMixins } from '@/shared/utils'

export default {
  name: 'FormInput',
  props: {
    value: [String, Number, Array, Boolean],
    name: String,
    type: String,
    format: Array,
    rules: Array,
    placeholder: String,
    disabled: Boolean,
    isGettingListBreakdown: Boolean,
    id: String,
    validateIf: {
      validator: prop => typeof prop === 'boolean' || prop === null,
      default: true
    },
    size: {
      type: String,
      default: 'md'
    }
  },
  mixins: [checkFieldFormatMixins, validateMixins],
  computed: {
    dataValue: {
      get() {
        return this.$props.value
      },
      set(val) {
        this.$emit('input', val)
      }
    },
    validateRules() {
      return this.validateIf ? this.stringRules(this.rules) : null
    },
    disableBreakdown() {
      let listBreakdownId = ['channel_listing_fee', 'other_channel_fees', 'tax_charged', 'actual_shipping_cost', 'reimbursement_costs', 'channel_tax_withheld', 'return_postage_billing']
      return (listBreakdownId.includes(this.$props.id) && (!this.dataValue || this.dataValue === 0))
    }
  },
  methods: {
    onKeyPress(e) {
      const keyCode = e.which
      /*
      8 - (backspace)
      48-57 - (0-9)Numbers
      96-105 - (0-9)Keypad - KeyPress doesn't care Keypad
      44 - (comma) - just with KeyPress
      45 - (minus)
      46 - (dot) - just with KeyPress
      */
      if (
        (this.isCurrency(this.rules) || this.isPercent(this.format)) &&
        keyCode !== 8 &&
        keyCode !== 45 &&
        keyCode !== 46 &&
        (keyCode < 48 || keyCode > 57)
      ) {
        e.preventDefault()
      }
    },
    allowBreakDown(id) {
      let listId = [
        'channel_listing_fee',
        'other_channel_fees',
        'tax_charged',
        'actual_shipping_cost',
        'reimbursement_costs',
        'channel_tax_withheld',
        'sale_charged',
        'return_postage_billing'
      ]
      if (listId.includes(id)) {
        return true
      }
    }
  }
}
</script>

<style lang="scss">
.pf-input {
  .form-control {
    &:placeholder-shown {
      text-overflow: ellipsis;
      padding-right: 30px;
    }
  }
  .was-validated .form-control:invalid,
  .form-control.is-invalid {
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='none' stroke='%23dc3545' viewBox='0 0 12 12'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
    padding-right: 30px;
  }
  &.is-invalid {
    ~ .invalid-feedback {
      display: block;
    }
  }
  .thin-spinner {
    border-width: .14em;
  }

  .btn-no-hover.disabled:hover {
    background-color: #254164 !important;
    color: #FFFFFF !important;
  }
  .btn-no-hover:hover {
    background-color: #254164 !important;
    color: #FFFFFF !important;
  }
}
</style>
