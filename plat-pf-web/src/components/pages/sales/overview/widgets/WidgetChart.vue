<template>
  <div class="widget-chart">
    <span v-if="lastUpdated" class="last-updated">
      Last updated: {{ formatLastTime(lastUpdated) }}
    </span>
    <cbpo-widget :config-obj="configObj" @getLastUpdated="lastUpdated = $event"/>
  </div>
</template>

<script>
import { formatLastTime } from '@/shared/utils'

export default {
  name: 'WidgetChart',
  props: {
    configObj: Object
  },
  data() {
    return {
      lastUpdated: null
    }
  },
  methods: {
    formatLastTime,
    getLastUpdated(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    }
  }
}
</script>

<style scoped lang="scss">
.widget-chart {
  height: 100%;
  position: relative;

  ::v-deep .builder-on {
    text-align: left !important;
  }

  ::v-deep .menu-position .cbpo-widget-menu {
    top: 10px;
  }

  .bordered {
    position: absolute;
    border: 1px solid #c8ced3;
    left: 1rem;
    right: 1rem;
    top: 44px;
    bottom: 60px;
  }
  .last-updated {
    position: absolute;
    z-index: 9;
    right: calc(25px + 1rem);
    font-weight: 500;
    color: #C8CBD0;
    margin: 0.8rem 0;
    font-size: 14px;
    font-stretch: normal;
    font-style: normal;
    line-height: 16px;
    letter-spacing: 0.07px;
  }
}
</style>
