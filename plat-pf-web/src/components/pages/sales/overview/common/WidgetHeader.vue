<template>
  <div class="widget-header">
    <span>{{ title }}</span>
    <span v-if="lastUpdated" class="last-updated">
      Last updated: {{ formatLastTime(lastUpdated) }}
    </span>
    <slot name="menu-control"></slot>
  </div>
</template>
<script>
import { formatLastTime } from '@/shared/utils'

export default {
  name: 'WidgetHeader',
  props: {
    title: {
      type: String
    },
    lastUpdated: {
      type: String
    }
  },
  methods: {
    formatLastTime
  }
}
</script>
<style lang="scss" scoped>
.widget-header {
  position: relative;
  text-align: left;
  padding-top: 16px;
  padding-left: 2rem;

  span {
    margin: 0.7rem 0;
    font-size: 14px;
    font-weight: 500;
    font-stretch: normal;
    font-style: normal;
    line-height: 16px;
    letter-spacing: 0.07px;
    color: #080e2c;
  }

  ::v-deep .menu-control-select {
    position: absolute;
    right: calc(25px + 0.5rem);
    top: 17px;
  }

  .last-updated {
    position: absolute;
    right: calc(25px + 2.5rem);
    margin-top: 3px;
    // font-weight: 400;
    color: #C8CBD0;
  }
}
</style>
