<template>
  <div :class="getClassBaseOnIgnoreState" class="complex-range-datepicker">
    <SelectInput
      label="Date"
      v-model="dataValue"
      default="Select date filter"
      :options="dataDateOptions"
      isDataRange
      @change="onChangeDate"
    />
    <div class="date-filter ml-2" v-if="isAbsoluteDate">
      <Datepicker
        v-model="dataValue"
        valueType="YYYY-MM-DD"
        specializedComponent="pf-analysis"
        range
        placeholder="Select date filter"
        :shortcuts="datePickerShortcuts"
        :clearable="false"
        @change="onChangeDate"
        :notAfterTime=notAfterTime
      ></Datepicker>
    </div>
  </div>
</template>

<script>
import _ from 'lodash'
import Datepicker from '@/components/common/Datepicker/Datepicker'
import SelectInput from '@/components/common/SelectInput/SelectInput'

import {DATE_QUERY_OPTIONS, CUSTOM_LABEL, ALL_OPTION} from '@/shared/constants/date.constant'
// eslint-disable-next-line
const OLD_LAST_30d_EXPRESSIONS = ["DATE_LAST(30,'days')", 'TODAY()']
export default {
  name: 'ComplexRangeDatepicker',
  props: {
    value: Array,
    absoluteDate: Array,
    ignoreState: Object,
    currentQueryObj: Object,
    notAfterTime: String,
    dateOptions: {
      type: Array,
      default: () => DATE_QUERY_OPTIONS
    },
    isShowOptionAll: {
      type: Boolean,
      default: false
    }
  },
  components: {
    Datepicker,
    SelectInput
  },
  data() {
    return {
      isAbsoluteDate: false,
      internalRelativeDate: [
        'DATE_START_OF(DATE_LAST(30,\'day\'), \'day\')',
        'DATE_END_OF(TODAY(), \'day\')'
      ]
    }
  },
  methods: {
    checkAbsoluteDate(data) {
      return (
        Array.isArray(data) &&
        data.length === 2 &&
        (data.every(item => this.$moment(item).isValid()) ||
          data.every(_.isNull))
      )
    },
    onChangeDate(value) {
      this.$emit('onChangeDate', value)
    },
    makeDynamicOption() {
      if (this.isAbsoluteDate) {
        this.dateOptions.map((option, index) => {
          if (option.text === CUSTOM_LABEL) {
            this.$set(this.dateOptions[index], 'value', this.dataValue)
          }
        })
      }
    },
    migrateDate() {
      if (_.isEqual(this.dataValue, OLD_LAST_30d_EXPRESSIONS)) {
        this.dataValue = ["DATE_START_OF(DATE_LAST(30,'day'), 'day')", "DATE_END_OF(TODAY(), 'day')"]
      }
    }
  },
  computed: {
    dataDateOptions() {
      if (this.isShowOptionAll) {
        return this.dateOptions.filter(item => item.id !== ALL_OPTION.id)
      }
      return this.dateOptions
    },
    getClassBaseOnIgnoreState() {
      return this.ignoreState && this.ignoreState.base.value ? 'disabled-non-hover' : ''
    },
    dataValue: {
      get() {
        return this.value || null
      },
      set(val) {
        this.$emit('input', val)
      }
    },
    datePickerShortcuts() {
      return [
        {
          text: 'Today',
          onClick: () => {
            return [
              new Date(this.$moment().startOf('day')),
              new Date(this.$moment().endOf('day'))
            ]
          }
        },
        {
          text: 'Yesterday',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .subtract(1, 'days')
                  .startOf('day')
              ),
              new Date(
                this.$moment()
                  .subtract(1, 'days')
                  .endOf('day')
              )
            ]
          }
        },
        {
          text: 'Last 30 days',
          onClick: () => [
            new Date(
              this.$moment()
                .add(-30, 'day')
                .startOf('day')
            ),
            new Date(this.$moment().endOf('day'))
          ]
        },
        {
          text: 'This week',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .day(0)
                  .startOf('day')
              ),
              new Date(
                this.$moment()
                  .day(6)
                  .endOf('day')
              )
            ]
          }
        },
        {
          text: 'Last week',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .day(-7)
                  .startOf('day')
              ),
              new Date(
                this.$moment()
                  .day(-1)
                  .endOf('day')
              )
            ]
          }
        },
        {
          text: 'This month',
          onClick: () => {
            return [
              new Date(this.$moment().startOf('month')),
              new Date(this.$moment().endOf('month'))
            ]
          }
        },
        {
          text: 'Last month',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .subtract(1, 'months')
                  .startOf('month')
              ),
              new Date(
                this.$moment()
                  .subtract(1, 'months')
                  .endOf('month')
              )
            ]
          }
        },
        {
          text: 'This year',
          onClick: () => {
            return [
              new Date(this.$moment().startOf('year')),
              new Date(this.$moment().endOf('year'))
            ]
          }
        },
        {
          text: 'Last year',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .subtract(1, 'years')
                  .startOf('year')
              ),
              new Date(
                this.$moment()
                  .subtract(1, 'years')
                  .endOf('year')
              )
            ]
          }
        }
      ]
    }
  },
  mounted() {
    this.$nextTick(() => {
      if (this.currentQueryObj) {
        if (
          this.currentQueryObj.selectedFilter ||
          this.currentQueryObj.selectedView ||
          this.currentQueryObj.q
        ) {
          this.isAbsoluteDate = this.checkAbsoluteDate(this.dataValue)
          this.makeDynamicOption()
        }
      }
    })
  },
  watch: {
    dataValue(newVal) {
      this.isAbsoluteDate = this.checkAbsoluteDate(newVal)
      this.makeDynamicOption()
      this.migrateDate()
    }
  },
  created() {
    this.migrateDate()
  }
}
</script>

<style lang="scss" scoped>
.complex-range-datepicker {
  display: flex;
  align-items: center;

  .date-switch {
    padding-left: 2rem;

    /deep/ label {
      padding-top: 3px;
      font-size: 11px;
      color: grey;

      &::before {
        left: -2rem;
      }

      &::after {
        left: calc(-2rem + 2px);
      }
    }
  }
}

.disabled-non-hover:not(:hover) {
  ::v-deep select, ::v-deep input.mx-input {
    background-color: #e9ecef;
    transition: 0s all !important;
    color: #6c757d;
  }

  ::v-deep .mx-icon-calendar .fa {
    color: #6c757d;
  }
}

::v-deep .select-input .dropdown-toggle {
  padding: 10px 8px 10px 40px;
  background: url('~@/assets/img/icon/date-icon.png') no-repeat left 0.75rem center/18px 20px;
}
</style>
