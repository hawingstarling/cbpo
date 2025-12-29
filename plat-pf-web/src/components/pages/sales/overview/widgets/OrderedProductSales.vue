<template>
  <div class="ordered-product-sales">
    <widget-header title="Ordered Product Sales" :lastUpdated="lastUpdated">
      <template #menu-control>
        <cbpo-widget-menu-control :config-obj="mixinsWidgetMenuConfig" @click="menuEventHandler"/>
      </template>
    </widget-header>
    <div class="ordered-product-sales-header-body">
      <div class="col-6 px-0">
        <cbpo-widget class="--with-placement-right" ref="widget" :config-obj="configThirtyDays" @getLastUpdated="getLastUpdated30Days"/>
      </div>
      <div class="col-6 px-0">
        <cbpo-widget :config-obj="configToday" class="order-product-today" @getLastUpdated="getLastUpdatedToday"/>
      </div>
    </div>
  </div>
</template>

<script>
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'

export default {
  components: { WidgetHeader },
  name: 'OrderedProductSales',
  props: {
    configThirtyDays: Object,
    configToday: Object
  },
  data() {
    return {
      lastUpdated: null
    }
  },
  mixins: [WidgetMenu],
  methods: {
    menuEventHandler(type) {
      if (type !== 'csv' || !this.$refs.widget) return
      this.$refs.widget.widgetExport(type)
    },
    getLastUpdated30Days(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    },
    getLastUpdatedToday(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    }
  }
}
</script>
<style lang="scss" scoped>
.ordered-product-sales {
  height: 100%;
  display: flex;
  flex-direction: column;
}

::v-deep .widget-header {
  border-radius: 6px 6px 0 0;
  border: solid 1px #d9d9d9;
  border-bottom: none;
  background-color: #fff;
}

@mixin text($fontSize, $color: #667085) {
  font-family: 'Inter'!important;
  font-style: normal!important;
  font-size: $fontSize!important;
  line-height: 20px!important;
  color: $color!important;
}

.ordered-product-sales-header-body {
  display: flex;
  flex: 1 0 auto;

  .cbpo-widget {
    border-top: none;
  }

  .col-6 {
    &:first-child .cbpo-widget {
      border-right: none;
    }

    &:last-child .cbpo-widget {
      border-left: none;
    }
  }

  .--with-placement-right ::v-deep .chart-container {
    position: relative;

    &:after {
      content: '';
      position: absolute;
      display: block;
      height: calc(100% - 15px);
      width: 1px;
      top: 0;
      right: 5px;
      background: #E6E8F0;
    }
  }

  ::v-deep .cbpo-widget-title h4 {
    @include text(14px, #232F3E);
    line-height: 16px!important;
  }

  ::v-deep .cbpo-chart-widget .highcharts-container {
   .highcharts-legend {
     .highcharts-legend-item {
       &:nth-child(2):nth-last-child(2) {
         transform: translate(8px, 33px);
       }
       &:nth-child(3):last-child {
         transform: translate(8px, 63px);
       }
     }

     text {
       @include text(14px);
     }
   }

    .highcharts-axis-labels text {
      @include text(14px);
    }
  }
}
.--with-placement-right {
  border-radius: 0 0 0 6px !important;
}
.order-product-today {
  border-radius: 0 0 6px 0 !important;
}
</style>
