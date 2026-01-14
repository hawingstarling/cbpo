<template>
  <div class="select-calendar" v-on-clickaway="{ callback: checkAndCloseDatepicker, except: '.mx-datepicker-main' }">
    <template v-if="isModeExpression">
      <input v-if="isFocus"
             @blur="isFocus = false"
             @keyup.enter="change(datetime)"
             class="input-expression"
             :placeholder="`Select a ${getTypeDatetimePicker}`"
             v-model="datetime">
      <input v-else
             @focus="isFocus = true"
             class="input-expression"
             :placeholder="`Select a ${getTypeDatetimePicker}`"
             :title="getParseValue"
             :value="getParseValue">
    </template>
    <template v-else>
      <!-- For time picker -->
      <template v-if="config.type === 'time'">
        <date-picker
          ref="dp"
          placeholder="Select a time"
          class="cbpo-custom-date"
          :type="getTypeDatetimePicker"
          v-model="localDatetime"
          :format="config.formatLabel"
          :value-type="config.formatValue"
          :editable="canOpen"
          :open="canOpen"
          :title="localDatetime"
        >
          <template v-slot:footer>
            <div style="text-align: right">
              <button class="ml-1 cbpo-btn btn-success" @click="change(localDatetime)">
                Apply
              </button>
              <button class="ml-1 cbpo-btn btn-danger" @click="change('', false)">
                Clear
              </button>
              <button class="ml-1 cbpo-btn" @click="closeDatePicker">
                Cancel
              </button>
            </div>
          </template>
        </date-picker>
      </template>
      <!-- For Date picker -->
      <template v-if="config.type === 'date'">
        <date-picker
          ref="dp"
          placeholder="Select a date"
          class="cbpo-custom-date"
          type="date"
          :value="datetime"
          :format="config.formatLabel"
          :value-type="config.formatValue"
          :editable="canOpen"
          :open="canOpen"
          :title="datetime"
          @change="change"
        >
          <template v-slot:footer>
            <div style="text-align: right">
              <button class="ml-1 cbpo-btn btn-danger" @click="change('', false)">
                Clear
              </button>
              <button class="ml-1 cbpo-btn" @click="closeDatePicker">
                Cancel
              </button>
            </div>
          </template>
        </date-picker>
      </template>
      <!-- For Datetime picker -->
      <template v-if="config.type === 'datetime'">
        <date-picker
          ref="dp"
          placeholder="Select a date"
          class="cbpo-custom-date"
          type="datetime"
          v-model="localDatetime"
          :format="config.formatLabel"
          :value-type="config.formatValue"
          :editable="canOpen"
          :open="canOpen"
          :title="localDatetime"
        >
          <template v-slot:footer>
            <div style="text-align: right">
              <button class="ml-1 cbpo-btn btn-success" @click="change(localDatetime)">
                Apply
              </button>
              <button class="ml-1 cbpo-btn btn-danger" @click="change('', false)">
                Clear
              </button>
              <button class="ml-1 cbpo-btn" @click="closeDatePicker">
                Cancel
              </button>
            </div>
          </template>
        </date-picker>
      </template>
    </template>
    <i @click="showDropdown" v-if="config.type !== 'time'" class="fa fa-bolt text-center icon-flast-dd"></i>
    <i @click="showCalendar" class="fa fa-calendar text-center"></i>
    <dropdown-expression v-if="config.type !== 'time'" @setValueNodeData="setValueNodeData" ref="de"></dropdown-expression>
  </div>
</template>
<script>
import DatePicker from 'vue2-datepicker'
import 'vue2-datepicker/index.css'
import dropdownExpression from '@/components/common/dropdown'
import { getLabelOfExpressionFromSyntax } from '@/services/ds/filter/FilterDefinitions'
import moment from 'moment'
import VueClickawayCustom from '@/directives/clickAwayDatepicker'

export default {
  name: 'DatetimePicker',
  props: {
    value: {
      type: String,
      default: ''
    },
    config: {
      type: Object,
      default: function () {
        return {
          type: 'date',
          formatLabel: 'MM/DD/YYYY',
          formatValue: 'YYYY-MM-DD'
        }
      }
    }
  },
  directives: {
    onClickaway: VueClickawayCustom
  },
  components: {
    DatePicker,
    'dropdown-expression': dropdownExpression
  },
  data() {
    return {
      // with datetime picker, only apply value when apply button is clicked
      localDatetime: null,
      datetime: '',
      propsChange: false,
      canOpen: false,
      isModeExpression: false,
      isFocus: false
    }
  },
  beforeMount() {
    // format data with default format
    let dateFormat = moment(this.value, this.config.formatValue, true).format(this.config.formatValue)
    // check data is valid with default format
    if (this.value && !moment(dateFormat, this.config.formatValue, true).isValid()) {
      this.setDatetime(this.value)
    }
    this.datetime = this.value
    this.localDatetime = this.value
  },
  computed: {
    getParseValue() {
      if (!this.datetime) return this.datetime
      return getLabelOfExpressionFromSyntax(this.datetime)
    },
    getTypeDatetimePicker() {
      return this.config.type === 'time' ? 'time' : 'date'
    }
  },
  methods: {
    checkAndCloseDatepicker() {
      if (['datetime', 'time'].includes(this.config.type) && this.datetime !== this.localDatetime) {
        this.change(this.localDatetime, false)
      }
      this.closeDatePicker()
    },
    closeDatePicker() {
      this.localDatetime = this.datetime
      this.canOpen = false
    },
    change(datetime, isClose = true) {
      this.datetime = datetime
      this.localDatetime = datetime
      this.$emit('input', datetime)
      isClose && this.closeDatePicker()
    },
    setValueNodeData({value}) {
      this.setDatetime(value)
    },
    showDropdown() {
      this.canOpen = false
      this.closeDatePicker()
      this.$nextTick(() => {
        this.$refs.de.showDropdown()
      })
    },
    showCalendar() {
      if (this.config.type === 'time' && this.datetime === '') {
        this.setDatetime(moment().startOf('day').format(this.config.formatValue))
      }
      this.isModeExpression = false
      this.$nextTick(() => {
        this.localDatetime = this.datetime
        this.canOpen = !this.canOpen
      })
    },
    setDatetime(value) {
      this.isModeExpression = true
      this.$emit('input', value)
    }
  },
  watch: {
    value(val) {
      this.datetime = val
    }
  }
}
</script>
<style lang="scss" scoped>
@import "DatetimePicker";
</style>
