<template>
  <b-card class="card-movement px-0 rounded-0 h-100">
    <div slot="header">
      <b-row align-v="center">
        <b-col>
          <span>
            <strong>Movement (Today v Last Year)</strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <div class="h-100 d-flex flex-column overflow-hidden">
      <div class="mt-1 px-1 card-movement-fitler" style="display: flex">
        <b-form-select @change="handleChangeFilterChange()" class="mr-1" v-model="selectedPercentOptions" :options="percentOptions"></b-form-select>
        <b-form-select @change="handleChangeFilterChange()" v-model="selectedDayOptions" :options="dayOptions"></b-form-select>
      </div>
      <div class="mt-1 card-movement-table" style="display: flex; padding: 0; background: white;">
        <cbpo-widget class="border-right-0 border-bottom-0 border-left-0 up" :key="reloadKeyUp" style="width: 50%" :config-obj="movementUpConfig.config"></cbpo-widget>
        <cbpo-widget class="border-right-0 border-bottom-0 down" :key="reloadKeyDown" style="width: 50%" :config-obj="movementDownConfig.config"></cbpo-widget>
      </div>
    </div>
  </b-card>
</template>

<script>
export default {
  name: 'Movement',
  props: {
    movementUp: Object,
    movementDown: Object
  },
  data() {
    return {
      percentOptions: [
        { text: '> 10%', value: 10 },
        { text: '> 20%', value: 20 },
        { text: '> 30%', value: 30 },
        { text: '> 40%', value: 40 },
        { text: '> 50%', value: 50 }
      ],
      dayOptions: [
        { text: 'Daily', value: 'total_d_vs_total_d_year_prior' },
        { text: '30Days', value: 'total_30d_vs_total_30d_year_prior' }
      ],
      selectedPercentOptions: 40,
      selectedDayOptions: 'total_d_vs_total_d_year_prior',
      movementUpConfig: this.$props.movementUp,
      movementDownConfig: this.$props.movementDown,
      reloadKeyUp: 'up_1',
      reloadKeyDown: 'down_1'
    }
  },
  methods: {
    handleChangeFilterChange() {
      let upConditions = [
        {
          'column': this.selectedDayOptions,
          'operator': '$gt',
          'value': this.selectedPercentOptions
        }
      ]
      let downConditions = [
        {
          'column': this.selectedDayOptions,
          'operator': '$lt',
          'value': -this.selectedPercentOptions
        }
      ]
      this.movementUpConfig.config.elements[0].config.columns[3].name = this.selectedDayOptions
      this.movementDownConfig.config.elements[0].config.columns[3].name = this.selectedDayOptions
      this.movementUpConfig.config.filter.base.config.query.conditions = upConditions
      this.movementDownConfig.config.filter.base.config.query.conditions = downConditions
      this.reloadKeyUp = new Date().getTime() + 1
      this.reloadKeyDown = new Date().getTime()
    }
  }
}
</script>

<style lang="scss" scoped>
.card-movement{
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
  .card-movement-fitler {
    height: 10%;
  }
  .card-movement-table {
    height: 90%;
  }
  .up {
    /deep/ .cbpo-widget-title {
      background-color: white;
    }
  }
  .down {
    /deep/ .cbpo-widget-title {
      background-color: white;
    }
  }
}
</style>
