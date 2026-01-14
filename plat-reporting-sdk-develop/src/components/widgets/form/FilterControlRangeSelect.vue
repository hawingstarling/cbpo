<template>
  <div class="cbpo-s form-group cbpo-filter-control-range-select">
    <label v-if="control.config.label && control.config.label.text">{{control.config.label.text}}: </label>
    <cbpo-filter-control-range
      v-show="control.config.range.visible"
      :control="rangeControl"
      :key="reRenderRange"
      @input="rangeChange"
    />
    <cbpo-filter-control-select
      :control="selectControl"
      @input="selectChange"
    />
  </div>
</template>
<script>

import {
  CONTROL_TYPE,
  makeDefaultInRangeControlConfig,
  makeDefaultSelectControlConfig,
  makeDefaultInRangeSelectControlConfig, buildSpecialValuesKey
} from '@/components/widgets/form/FilterControlConfig'
import FilterControlRange from '@/components/widgets/form/FilterControlRange'
import FilterControlSelect from '@/components/widgets/form/FilterControlSelect'
import cloneDeep from 'lodash/cloneDeep'
import _ from 'lodash'
import { StaticExpression } from 'plat-sdk'

export default {
  name: 'FilterControlRange',
  data() {
    return {
      rangeControl: null,
      selectControl: null,
      reRenderRange: 0
    }
  },
  components: {
    'cbpo-filter-control-range': FilterControlRange,
    'cbpo-filter-control-select': FilterControlSelect
  },
  props: {
    control: Object
  },
  methods: {
    widgetConfig (config) {
      this.control.config = Object.assign({}, makeDefaultInRangeSelectControlConfig(config))
    },
    rangeChange(rangeControl) {
      this.control.config.common.value = rangeControl.config.common.value
      this.$emit('input', this.control)
    },
    selectChange(control) {
      // update input range
      let dataSelected = this.control.config.selection.options.find(option => this.selectControl.config.common.value === buildSpecialValuesKey(option.value)) || [undefined, undefined]
      this.rangeControl.config.common.value = dataSelected.value
      // set value
      this.reRenderRange++
      // emit event with empty value
      if (_.every(dataSelected.value, _.isNull)) {
        this.$emit('input', this.control)
      }
    },
    createRangeSelect(defaultOption) {
      let config = makeDefaultInRangeControlConfig({
        range: this.control.config.range
      })
      config.common.column = this.control.config.common.column
      if (defaultOption) config.common.value = defaultOption.value
      this.rangeControl = {
        type: CONTROL_TYPE.RANGE,
        config
      }
    },
    buildOptionsSelect(options) {
      return options.map(option => {
        option.value = buildSpecialValuesKey(option.value)
        return option
      })
    },
    createControlSelect(defaultOption) {
      let config = makeDefaultSelectControlConfig({})
      config.common.column = this.control.config.common.column
      // order options
      this.control.config.selection.options = _.map(this.control.config.selection.options, (item) => {
        item['dateFormatForSort'] = item.value[0] ? StaticExpression.eval(item.value[0]) : '0'
        return item
      })
      config.selection.options = this.buildOptionsSelect(cloneDeep(this.control.config.selection.options))
      config.selection.empty.label = this.control.config.selection.empty.label
      config.selection.options = _.orderBy(_.uniqWith([ ...config.selection.options ], _.isEqual), ['dateFormatForSort'], ['desc'])
      if (defaultOption) config.common.value = buildSpecialValuesKey(defaultOption.value)
      this.selectControl = {
        type: CONTROL_TYPE.SELECT,
        config
      }
    },
    findDefaultOption() {
      return this.control.config.selection.options.find(option => option.isDefault)
    }
  },
  created() {
    this.widgetConfig(this.control.config)
    const defaultOption = this.findDefaultOption()
    this.createRangeSelect(defaultOption)
    this.createControlSelect(defaultOption)
  }
}
</script>
<style lang="scss" scoped>
  @import './FilterControlRangeSelect.scss';
</style>
