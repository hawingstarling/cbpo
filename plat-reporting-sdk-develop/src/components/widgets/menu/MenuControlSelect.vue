<template>
  <b-dropdown class="menu-control-select" right size="sm" toggle-class="text-decoration-none" no-caret no-flip v-if="getSelectionList.length">
    <template v-slot:button-content>
      <div class="precise-theme-menu-icon" v-if="preciseTheme"></div>
      <i v-else-if="configObj.icons && configObj.icons.css" :class="configObj.icons.css" aria-hidden="true"></i>
      <span v-if="configObj.label && configObj.label.text"> {{configObj.label.text}}</span>
    </template>
    <template v-for="(option, idx) in getSelectionList">
      <b-dropdown-item
        :key="idx"
        v-if="option.type === 'item' && option.value && !option.link"
        @click="selected(option)"
      >
        <i v-if="option.icon" :class="option.icon" class="pr-1" aria-hidden="true"></i>
        <span v-if="option.label">{{option.label}}</span>
      </b-dropdown-item>
      <b-dropdown-item
        :key="idx"
        v-else-if="option.type === 'item' && option.value && option.link"
        :href="option.value"
        target="_blank"
      >
        <i v-if="option.icon" :class="option.icon" class="pr-1" aria-hidden="true"></i>
        <span v-if="option.label">{{option.label}}</span>
      </b-dropdown-item>
      <b-dropdown-divider
        v-else-if="option.type === 'divider'"
        :key="idx">
      </b-dropdown-divider>
    </template>
  </b-dropdown>
</template>
<script>
// import WidgetBaseMixins from '@/components/WidgetBaseMixins'
// import WidgetBase from '@/components/WidgetBase'
import CBPO from '@/services/CBPO'

export default {
  name: 'MenuControlSelect',
  props: {
    builder: {
      type: Boolean,
      default: false
    },
    isVisualize: {
      type: Boolean,
      default: false
    },
    allowCustomOptions: {
      type: Boolean,
      default: true
    },
    configObj: Object
  },
  computed: {
    getSelectionList() {
      return this.configObj.selection.options.filter(op => {
        if (this.allowCustomOptions) return true
        return this.builder
          ? op.value && op.value !== 'csv' && op.type !== 'divider'
          : (op.value === 'csv' || (op.value && op.link) || op.value === 'custom-csv' || op.value === 'template-csv') && op.type !== 'divider'
      })
    },
    preciseTheme() {
      return CBPO.channelManager().getChannel().getThemeSvc().getCurrentTheme() === 'cbpo-sdk-precise-theme'
    }
  },
  methods: {
    selected($event) {
      if ($event.value === 'template-csv') this.$emit('click', {type: $event.value, templateName: $event.templateName})
      else this.$emit('click', $event.value)
    }
  }
}
</script>

<style lang="scss" scoped>
::v-deep .dropdown-toggle {
  width: auto;
  font-size: 12px;
  margin: 0;
  border-radius: 3px;
  >span {
    padding-left: 7px;
  }
}
::v-deep .dropdown-menu {
  transform: translate3d(-129px, 29px, 0px) !important;
  will-change: inherit !important;
  .dropdown-item {
    font-size: $text-font-size;
  }
}
</style>
