<template>
  <div class="cbpo-s form-group cbpo-filter-control-textarea">
    <label v-if="control.config.label && control.config.label.text">{{control.config.label.text}}: </label>
    <template>
      <textarea :value="control.config.common.value" @input="debounceChange" class="form-control cbpo-custom-textarea"/>
    </template>
  </div>
</template>
<script>
import {
  makeDefaultTextAreaControlConfig
} from '@/components/widgets/form/FilterControlConfig'
import debounce from 'lodash/debounce'

export default {
  name: 'FilterControlTextarea',
  props: {
    control: Object
  },
  methods: {
    widgetConfig (config) {
      this.control.config = Object.assign({}, makeDefaultTextAreaControlConfig(config))
    },
    debounceChange: debounce(function($event) {
      this.control.config.common.value = ($event.target.value.length) ? $event.target.value : undefined
      this.$emit('input', this.control)
    }, 1000)
  },
  created() {
    this.widgetConfig(this.control.config)
  }
}
</script>
<style lang="scss" scoped>
  @import './FilterControlTextarea.scss';
</style>
