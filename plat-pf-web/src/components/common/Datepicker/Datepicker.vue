<template>
  <ValidationProvider
    :name="filteredName(name)"
    immediate
    :rules="validateRules"
    v-slot="{ errors }"
    :vid="name"
  >
    <div
      class="pf-datepicker"
      :class="[
        errors.length ? 'error' : '',
        specializedComponent,
        `pf-datepicker--${size}`
      ]"
    >
      <date-picker
        v-model="dataValue"
        :type="type"
        :value-type="valueType"
        :format="format"
        :range="range"
        :shortcuts="shortcuts"
        :disabled-date="disabledDate"
        :placeholder="placeholder"
        :disabled="disabled"
        @change="$emit('change')"
        :editable="editable"
        :clearable="clearable"
      >
        <template slot="icon-calendar">
          <i class="fa fa-calendar" />
        </template>
      </date-picker>
      <div class="pf-datepicker__feedback" v-if="errors.length">
        {{ errors[0] }}
      </div>
    </div>
  </ValidationProvider>
</template>

<script>
import DatePicker from 'vue2-datepicker'
import 'vue2-datepicker/index.css'
import moment from 'moment-timezone'
import { checkFieldFormatMixins, validateMixins } from '@/shared/utils'

export default {
  name: 'Datepicker',
  components: {
    DatePicker
  },
  props: {
    name: String,
    value: [String, Date, Array],
    timezone: String,
    type: {
      type: String,
      default: 'date'
    },
    valueType: String,
    specializedComponent: {
      type: String,
      default: ''
    },
    range: { type: Boolean, default: false },
    shortcuts: Array,
    placeholder: String,
    disabled: Boolean,
    editable: { type: Boolean, default: true },
    clearable: { type: Boolean, default: true },
    rules: Array,
    validateIf: {
      validator: prop => typeof prop === 'boolean' || prop === null,
      default: true
    },
    size: {
      type: String,
      default: 'md'
    },
    notAfterTime: String
  },
  mixins: [checkFieldFormatMixins, validateMixins],
  methods: {
    convertToFormattedDate(value, timezone, format = 'MM/DD/YYYY hh:mm A') {
      // because old datepicker doesn't support date with timezone so we need to convert it to date with timezone (format MM/DD/YYYY hh:mm A)
      // example: "2024-07-26T00:06:47-07:00" to "07/26/2024 00:06 AM"
      const formattedString = moment.tz(value, timezone).format(format)
      return moment(formattedString).toDate()
    },
    toISOWithTZ(value, timezone) {
      return moment(value).parseZone().tz(timezone, true).toISOString(true)
    }
  },
  computed: {
    disabledDate() {
      if (this.notAfterTime) {
        return date => date > new Date() || date < new Date(this.notAfterTime)
      }
      return date => date > new Date()
    },
    dataValue: {
      get() {
        if (this.range) {
          return this.value || null
        }
        return this.value ? this.convertToFormattedDate(this.value, this.timezone, this.format) : null
      },
      set(val) {
        if (this.range) {
          this.$emit('input', val)
          return
        }
        this.$emit('input', this.toISOWithTZ(val, this.timezone))
      }
    },
    format() {
      return this.type === 'datetime' ? 'MM/DD/YYYY hh:mm A' : 'MM/DD/YYYY'
    },
    validateRules() {
      return this.validateIf ? this.stringRules(this.rules) : null
    }
  }
}
</script>

<style lang="scss">
.pf-datepicker {
  &--sm {
    .mx-input {
      font-size: 12px;
      height: 28px;
      box-shadow: none;
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-radius: 3px;
    }
  }
  &.error {
    input {
      border-color: #f86c6b;
      &:focus {
        box-shadow: 0 0 0 0.2rem rgba(248, 108, 107, 0.25);
      }
    }
  }
  &__feedback {
    width: 100%;
    margin-top: 0.25rem;
    font-size: 80%;
    color: #f86c6b;
  }
  .mx-datepicker {
    width: 100%;
  }
  .mx-input:disabled {
    background-color: #e4e7ea;
    border-color: #ccc;
    cursor: default;
  }
}
.pf-analysis {
  .mx-input-wrapper {
    margin-top: 24px;
    .mx-input {
      font-size: 12px;
      height: 36px;
      min-width: 200px;
      font-size: 12px;
      background: #FFFFFF;
      border: 1px solid #D0D5DD;
      box-shadow: 0px 1px 2px rgba(16, 24, 40, 0.05);
      border-radius: 1px;
    }
    .mx-icon-calendar {
      right: 4px;
    }
  }
}
</style>
