<template>
  <div class="cbpo-s form-group cbpo-filter-control-input">
    <label v-if="control.config.label && control.config.label.text">{{control.config.label.text}}: </label>
    <template v-if="getType === 'temporal'">
      <cbpo-datetime-picker
        :value="control.config.common.value"
        :config="getFormatConfig"
        @input="dateChange"
      ></cbpo-datetime-picker>
    </template>
    <template v-else>
      <input
        class="form-control cbpo-custom-text"
        :type="getType"
        v-model.trim="control.config.common.value"
        @input="debounceChange"
      />
    </template>
  </div>
</template>
<script>
import { makeDefaultInputControlConfig } from './FilterControlConfig'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import datetimePicker from '@/components/datetimePicker/DatetimePicker'
import debounce from 'lodash/debounce'

export default {
  name: 'FilterControlInput',
  components: {
    'cbpo-datetime-picker': datetimePicker
  },
  props: {
    control: Object
  },
  methods: {
    widgetConfig (config) {
      this.control.config = Object.assign({}, makeDefaultInputControlConfig(config))
    },
    dateChange(date) {
      this.control.config.common.value = date || undefined
      this.$emit('input', this.control)
    },
    debounceChange: debounce(function($event) {
      this.$emit('input', this.control)
    }, 1000)
  },
  computed: {
    getType() {
      let type = this.control.config.common.column.type
      if (DataTypeUtil.isTemporal(type)) return 'temporal'
      return DataTypeUtil.isNumeric(type) ? 'number' : 'text'
    },
    getFormatConfig: function() {
      let config = this.control.config
      return config.input ? config.input : {
        type: 'date',
        formatLabel: 'MM/DD/YYYY',
        formatValue: 'YYYY-MM-DD'
      }
    }
  },
  created() {
    this.widgetConfig(this.control.config)
  }
}
</script>
<style lang="scss" scoped>
  @import './FilterControlInput.scss';
</style>
