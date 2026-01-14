<template>
  <div v-cbpo-lazy-load="{...lazyLoadConfig, enabled: lazyLoadConfig.enabled && !enabled}">
    <template v-if="enabled">
      <vue-custom-scrollbar
        v-cbpo-lazy-load="lazyLoadConfig"
        :settings="settings"
        @ps-scroll-y="$emit('scroll-x')"
        class="scrollable">
        <slot></slot>
      </vue-custom-scrollbar>
    </template>
    <template v-else>
      <slot></slot>
    </template>
  </div>
</template>

<script>
import lazyLoadDirective from '@/directives/lazyLoadDirective'
import vueCustomScrollbar from 'vue-custom-scrollbar'
import 'vue-custom-scrollbar/dist/vueScrollbar.css'

export default {
  name: 'CustomScrollbar',
  directives: {
    'cbpo-lazy-load': lazyLoadDirective
  },
  props: {
    enabled: {
      type: Boolean,
      default: false
    },
    lazyLoadConfig: Object
  },
  components: {
    vueCustomScrollbar
  },
  data() {
    return {
      settings: {
        suppressScrollY: false,
        suppressScrollX: false,
        wheelPropagation: true
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.scrollable {
  position: relative;
  margin: auto;
  width: 100%;
  height: 100%;

  ::v-deep {
    .ps__rail-y, .ps__rail-x {
      z-index: 500;
    }
  }
}
</style>
