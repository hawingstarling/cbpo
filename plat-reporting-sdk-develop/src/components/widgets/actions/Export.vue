<template>
  <div class="cbpo-action-item">
    <b-dropdown class="cbpo-action-export" right size="sm" toggle-class="text-decoration-none" no-caret no-flip>
      <template v-slot:button-content>
        <i v-if="config.icons && config.icons.css" :class="config.icons.css" aria-hidden="true"></i>
        <span v-if="config.label && config.label.text"> {{config.label.text}}</span>
      </template>
      <b-dropdown-item
        v-for="(option, idx) in config.selection.options"
        :key="idx"
        :value="option.value"
        @click="clickExport(option.value)">{{option.label}}</b-dropdown-item>
    </b-dropdown>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'

export default {
  name: 'Export',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins
  ],
  methods: {
    clickExport (filetype) {
      this.$emit('widgetExport', filetype)
    }
  }
}
</script>
<style scoped lang="scss">
  @import './Export.scss';
</style>
