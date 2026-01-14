<template>
  <div class="cbpo-s form-group cbpo-filter-control-range">
    <label v-if="control.config.label && control.config.label.text">{{control.config.label.text}}: </label>
    <template v-for="(control, idx) in controls">
      <cbpo-filter-control-input
        :class="{ 'cbpo-cs-pr': idx === 0 }"
        :key="idx"
        :control="control"
        @input="controlChange($event, idx)"
      ></cbpo-filter-control-input>
    </template>
  </div>
</template>
<script>

import {
  CONTROL_TYPE,
  makeDefaultInputControlConfig,
  makeDefaultInRangeControlConfig
} from './FilterControlConfig'
import range from 'lodash/range'
import cloneDeep from 'lodash/cloneDeep'
import { SUPPORT_OPERATORS } from '@/services/ds/filter/FilterDefinitions'
import FilterControlInput from '@/components/widgets/form/FilterControlInput'

export default {
  name: 'FilterControlRange',
  data() {
    return {
      controls: []
    }
  },
  components: {
    'cbpo-filter-control-input': FilterControlInput
  },
  props: {
    control: Object
  },
  methods: {
    widgetConfig (config) {
      this.control.config = Object.assign({}, makeDefaultInRangeControlConfig(config))
    },
    createTwoControlInputs() {
      this.controls = range(2).map((value, idx) => {
        let config = makeDefaultInputControlConfig({})
        config.label.text = ''
        config.input = this.control.config.range
        // only change column and operator, keep value
        config.common.column = cloneDeep(this.control.config.common.column)
        config.common.operator = SUPPORT_OPERATORS.$eq.value // set any
        config.common.value = cloneDeep(this.control.config.common.value[idx])
        return {
          type: CONTROL_TYPE.INPUT,
          config
        }
      })
    },
    controlChange(control, idx) {
      this.control.config.common.value[idx] = control.config.common.value !== '' ? control.config.common.value : undefined
      let isEmptyValue = this.control.config.common.value.every(value => value !== undefined)
      let isValidValue = this.control.config.common.value.every(value => value === undefined)
      if (isEmptyValue || isValidValue) {
        this.$emit('input', this.control)
      }
    }
  },
  created() {
    this.widgetConfig(this.control.config)
    this.createTwoControlInputs()
  }
}
</script>
<style lang="scss" scoped>
  @import './FilterControlRange.scss';
</style>
