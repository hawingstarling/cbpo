<template>
  <b-card class="card-average px-0 rounded-0 h-100">
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-12">
          <span>
            <strong>Average Sales Price</strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <div class="h-100 d-flex flex-column overflow-hidden">
      <div class="average-yesterday">
        <cbpo-widget class="border-0" :config-obj="averageSalesPriceYesterdayConfig.config"/>
      </div>
      <div class="h-100 average-last-month">
        <cbpo-widget class="border-0 widget" :config-obj="averageSalesPriceConfig.config"/>
      </div>
    </div>
  </b-card>
</template>

<script>
export default {
  name: 'AverageSalesPrice',
  props: {
    averageSalesPriceYesterday: Object,
    averageSalesPrice: Object
  },
  data() {
    return {
      averageSalesPriceYesterdayConfig: this.$props.averageSalesPriceYesterday,
      averageSalesPriceConfig: this.$props.averageSalesPrice
    }
  }
}
</script>

<style lang="scss" scoped>
.card-average{
  .card-body {
    height: 100%;
    padding: 0 0;
    overflow: hidden;
  }

  .card-header {
    height: 37.8px;
    padding: .7rem;
    background: #ebebeb;
    text-align: center;
    font-size: 12px;
  }
  .average-yesterday {
    height: 25%;
  }
  .widget {
    /deep/ .highcharts-legend {
      display: none;
    }
  }
}
</style>
