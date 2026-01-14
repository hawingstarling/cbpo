<template>
  <div>
    <div
      v-if="getSelectionList.length"
    >
      <template v-for="(option, idx) in getSelectionList">
        <b-button
          :key="idx"
          v-if="option.type === 'item' && option.value && !option.link && !widgetInfo.is_programmed"
          @click="selected(option.value)"
          size="sm"
          class="mr-1"
          :variant="option.variant ? option.variant : 'secondary'"
        >
          <i v-if="option.icon" :class="option.icon" class="pr-1" aria-hidden="true"></i>
          <span v-if="option.label">{{option.label}}</span>
        </b-button>
        <b-button
          :key="idx"
          v-else-if="option.type === 'item' && option.value && !option.link && widgetInfo.is_programmed && option.value !== 'save_widget'"
          @click="selected(option.value)"
          size="sm"
          class="mr-1"
          :variant="option.variant ? option.variant : 'secondary'"
        >
          <i v-if="option.icon" :class="option.icon" class="pr-1" aria-hidden="true"></i>
          <span v-if="option.label">{{option.label}}</span>
        </b-button>
        <b-button
          :key="idx"
          v-else-if="option.type === 'item' && option.value && option.link"
          :href="option.value"
          target="_blank"
          size="sm"
          class="mr-1"
          :variant="option.variant ? option.variant : 'secondary'"
        >
          <i v-if="option.icon" :class="option.icon" class="pr-1" aria-hidden="true"></i>
          <span v-if="option.label">{{option.label}}</span>
        </b-button>
      </template>
    </div>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'

export default {
  name: 'TemplateMenuControlSelect',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins
  ],
  props: {
    builder: {
      type: Boolean,
      default: false
    },
    isVisualize: {
      type: Boolean,
      default: false
    },
    widgetInfo: {
      type: Object
    }
  },
  computed: {
    getSelectionList() {
      return this.config.selection.options.filter(op => {
        return this.builder
          ? op.value && op.value !== 'csv' && op.type !== 'divider'
          : (op.value === 'csv' || (op.value && op.link)) && op.type !== 'divider'
      })
    },
    getWidgetInfo() {
      return this.widgetInfo
    }
  },
  methods: {
    selected($event) {
      this.$emit('click', $event)
    }
  }
}
</script>
