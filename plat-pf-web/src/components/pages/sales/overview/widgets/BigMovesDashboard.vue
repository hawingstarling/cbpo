<template>
  <b-card class="card-big-moves rounded-0 h-100">
    <div class="h-100 d-flex flex-column overflow-hidden">
      <widget-header title="Big Moves" :lastUpdated="lastUpdated" />

      <div class="card-movement-filer d-flex justify-content-start align-items-end flex-wrap flex-grow-1">
        <div class="d-flex align-items-center flex-grow-1">
          <div class="position-relative w-25 flex-column align-items-start mr-2">
            <label class="label-name mb-2 fulfillment-label">Movement</label>
            <v-select :options="percentOptions" :clearable="false" v-model="selectedPercentOptions"
              class="custom-v-select" placeholder="Search percent option">
              <template #open-indicator="{ attributes }">
                <i class="fa fa-angle-down" v-bind="attributes"></i>
              </template>
              <span slot="no-options">
                This percent option does not exist.
              </span>
            </v-select>
          </div>
          <div class="position-relative w-25 flex-column align-items-start mr-1">
            <label class="label-name mb-2 fulfillment-label">Average Comparison</label>
            <v-select :options="dayOptions" :clearable="false" v-model="selectedDayOptions" class="custom-v-select"
              placeholder="Search day option">
              <template #open-indicator="{ attributes }">
                <i class="fa fa-angle-down" v-bind="attributes"></i>
              </template>
              <span slot="no-options">
                This day option does not exist.
              </span>
            </v-select>
          </div>
          <div class="position-relative flex-column align-items-start">
            <div class="submit" @click.prevent="handleSubmit($event)"></div>
          </div>
        </div>
      </div>

      <div class="mt-1 card-big-moves-table" style="display: flex; padding: 0; background: white; border-radius: 6px;">
        <cbpo-widget class="border-right-0 border-bottom-0 border-left-0 up" :key="reloadKeyUp" style="width: 50%;" @getLastUpdated="getLastUpdatedUp"
          :config-obj="bigMovesUpConfig.config"></cbpo-widget>
        <cbpo-widget class="border-right-0 border-bottom-0 down" :key="reloadKeyDown" style="width: 50%" @getLastUpdated="getLastUpdatedDown"
          :config-obj="bigMovesDownConfig.config"></cbpo-widget>
      </div>
    </div>
  </b-card>
</template>

<script>
import { PERCENT_BIGMOVES_OPTIONS, DAY_BIGMOVES_OPTIONS } from '@/shared/constants'
import WidgetHeader from '../common/WidgetHeader.vue'

export default {
  components: { WidgetHeader },
  name: 'BigMovesDashboard',
  props: {
    bigMovesUp: {
      type: Object,
      required: true
    },
    bigMovesDown: {
      type: Object,
      required: true
    },
    dsId: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      percentOptions: PERCENT_BIGMOVES_OPTIONS,
      dayOptions: DAY_BIGMOVES_OPTIONS,
      selectedPercentOptions: PERCENT_BIGMOVES_OPTIONS[3],
      selectedDayOptions: DAY_BIGMOVES_OPTIONS[0],
      bigMovesUpConfig: this.$props.bigMovesUp,
      bigMovesDownConfig: this.$props.bigMovesDown,
      reloadKeyUp: 'up_1',
      reloadKeyDown: 'down_1',
      submitCount: 0,
      lastUpdated: null
    }
  },
  created() {
    this.bigMovesUpConfig.config.elements[0].config.dataSource = this.dsId.data_source_id
    this.bigMovesDownConfig.config.elements[0].config.dataSource = this.dsId.data_source_id
  },
  methods: {
    handleSubmit(event) {
      event.preventDefault()
      // Increment the submitCount
      this.submitCount++
      const daySelected = this.selectedDayOptions.value
      const percentSelected = this.selectedPercentOptions.value
      let upConditions = {
        'column': daySelected,
        'operator': '$gt',
        'value': percentSelected
      }
      let downConditions = {
        'column': daySelected,
        'operator': '$gt',
        'value': percentSelected
      }
      const dayCompare = (daySelected === 'quantity_d_vs_quantity_avg_30d') ? 'total_quantity_day' : 'total_quantity_30d'
      const avgCompare = (daySelected === 'quantity_d_vs_quantity_avg_30d') ? 'total_avg_quantity_30d' : 'total_avg_quantity_12m'
      const distanceCompare = (daySelected === 'quantity_d_vs_quantity_avg_30d') ? 'distance_day_vs_avg_30d' : 'distance_30d_vs_avg_12m'

      // change order column
      this.bigMovesUpConfig.config.elements[0].config.columns[1].name = dayCompare
      this.bigMovesDownConfig.config.elements[0].config.columns[1].name = dayCompare

      // change AVG column
      this.bigMovesUpConfig.config.elements[0].config.columns[2].name = avgCompare
      this.bigMovesDownConfig.config.elements[0].config.columns[2].name = avgCompare

      // change percent column
      this.bigMovesUpConfig.config.elements[0].config.columns[3].name = daySelected
      this.bigMovesDownConfig.config.elements[0].config.columns[3].name = daySelected

      // change sorting column
      this.bigMovesUpConfig.config.elements[0].config.sorting[0].column = daySelected
      this.bigMovesDownConfig.config.elements[0].config.sorting[0].column = daySelected

      // change config for both up and down
      this.bigMovesUpConfig.config.filter.base.config.query.conditions[1] = upConditions
      this.bigMovesDownConfig.config.filter.base.config.query.conditions[1] = downConditions
      this.bigMovesUpConfig.config.filter.base.config.query.conditions[2].column = distanceCompare
      this.bigMovesDownConfig.config.filter.base.config.query.conditions[2].column = distanceCompare

      // force reload & Use the submitCount to generate unique keys
      this.reloadKeyUp = new Date().getTime() + '_' + this.submitCount
      this.reloadKeyDown = new Date().getTime() + '_' + (this.submitCount + 1)
    },
    getLastUpdatedUp(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    },
    getLastUpdatedDown(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

.card-big-moves {
  background-color: #f9fbfb;

  .card-body {
    padding: 0 0;
    height: 100%;
    overflow: hidden;
  }

  .card-header {
    height: 37.8px;
    padding: .7rem;
    background: #ebebeb;
    text-align: center;
    font-size: 12px;
  }

  .card-big-moves-filter {
    height: 10%;
  }

  .card-big-moves-table {
    height: 90%;
  }

  ::v-deep .precise-theme-menu-icon {
    position: relative;
    top: 9px;
  }

  .up {
    /deep/ .cbpo-widget-title {
      background-color: white;
      padding: 5px 11px;
    }
  }

  .down {
    /deep/ .cbpo-widget-title {
      background-color: white;
      padding: 5px 11px;
    }
  }
}

.card-movement-filer {
  margin-top: 8px;
  padding: 8px 8px;
}

.fulfillment-label {
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.33;
  letter-spacing: 0.12px;
  font-size: 12px;
  color: #667085;
}

.submit {
  min-width: 35px;
  position: absolute;
  background-size: contain;
  content: '';
  height: 35px;
  background-repeat: no-repeat;
  top: 100%;
  left: 0;
  transform: translateY(-3px);
  background-size: contain;
  background-image: url('~@/assets/img/icon/submit.svg');

  &:focus {
    box-shadow: none !important;
  }

  &:hover {
    cursor: pointer;
    filter: invert(66%) sepia(18%) saturate(3000%) hue-rotate(150deg) brightness(108%) contrast(24%);

  }
}

::v-deep .title-up {
  color: green;
  font-size: 27px;
  position: relative;
  top: 3px;
}

::v-deep .title-down {
  color: red;
  font-size: 27px;
  position: relative;
  top: 4px;
}

::v-deep .fa-check {
  color: green;
}

::v-deep .fa-times {
  color: red;
}

::v-deep .custom-v-select ul {
  min-width: 50px;
}

::v-deep .custom-v-select ul li {
  min-width: 50px;
}

::v-deep .custom-v-select {
  width: 100%;
  height: 36px;

  .vs__dropdown-toggle {
    height: 100%;
  }

  .vs__dropdown-menu {
    max-height: 185px !important;
    margin: 0.125rem 0 0;
    border-top: 1px solid rgba(60, 60, 60, .26);
  }
}

::v-deep .vs__selected {
  padding: 0 0 0 2px;
}

::v-deep .vs__search {
  padding: 0 0 0 1px;
}

::v-deep .vs__actions {
  padding: 4px 4px 0px 0px;
}

.average-comparison {
  width: 164px;
}

::v-deep .menu-position .cbpo-widget-menu {
  right: 32px !important;
}

::v-deep .fa-caret-down,
::v-deep .fa-caret-up {
  font-size: 20px;
  position: relative;
  top: 3px;
}

::v-deep .fa-minus {
  position: relative;
  font-size: 14px;
  top: 2px;
}

::v-deep .cbpo-pagination {
  display: flex !important;
  justify-content: center !important;
}

::v-deep .cbpo-pagination-sizing {
  width: 60% !important;
  align-items: center;

  button {
    border-color: #D0D5DD !important;
    color: #1D2939 !important;
  }

  button {
    &[data-button="page"]:is(*) {
      padding: 6px !important;
      font-weight: 600;
      font-size: 12px;
      max-width: 32px !important;
      height: 32px !important;
      border: 1px 1px 1px 0 !important;
    }

    &:hover {
      color: $primary !important;
      text-decoration: none;
      background-color: #F9FAFB !important;
      border-color: #D0D5DD;
    }

    &[data-button="prev"]:is(*) {
      @include button-icon(true, 'arrow-right.svg', 20px, 20px);
      border-top-left-radius: 6px !important;
      border-bottom-left-radius: 6px !important;
      color: #73818f;
      padding: 10px 16px !important;
      max-height: 32px !important;

      &::before {
        transform: rotate(180deg);
        background-color: $primary !important;
      }
    }

    &[data-button="prev"]:disabled {
      background-color: #fff !important;
      color: #73818f !important;

      &::before {
        transform: rotate(180deg);
        background-color: #73818f !important;
      }
    }

    &[data-button="next"]:is(*) {
      @include button-icon(false, 'arrow-right.svg', 20px, 20px);
      border-top-right-radius: 6px !important;
      border-bottom-right-radius: 6px !important;
      border-right: 1px solid #d9d9d9 !important;
      color: #73818f;
      padding: 10px 16px !important;
      max-height: 32px !important;

      &::after {
        background-color: $primary !important;
      }
    }

    &[data-button="next"]:disabled {
      background-color: #fff !important;
      color: #73818f !important;

      &::after {
        background-color: #73818f !important;
      }
    }

    &:disabled {
      background-color: #d9d9d9 !important;
      opacity: 1 !important;
    }
  }
}

::v-deep .cbpo-widget {
  border-radius: 0 0 6px 6px !important;
}

::v-deep .cbpo-table {
  border-bottom: none !important;
}

::v-deep .vue-recycle-scroller {
  margin-bottom: -3px;
}

.last-updated {
  position: absolute !important;
  right: calc(25px + 2.5rem);
  margin-top: 3px;
}
</style>
