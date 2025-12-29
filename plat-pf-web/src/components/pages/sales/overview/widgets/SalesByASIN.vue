<template>
  <b-card class="sales-by-asin rounded-0 h-100">
    <div class="h-100 d-flex flex-column overflow-hidden">
      <widget-header title="Sales By ASIN">
        <template #menu-control>
          <cbpo-widget-menu-control :config-obj="mixinsWidgetMenuConfig"
            @click="menuEventHandler"/>
        </template>
      </widget-header>

      <div class="sales-by-asin-cta d-flex justify-content-start align-items-end flex-wrap flex-grow-1">
        <div class="sales-by-asin-filter flex-column align-items-start mr-2">
          <label class="label mb-2 fulfillment-label">Fulfillment Methods</label>
          <v-select :options="fulfillment_methods.options" :clearable="false" v-model="fulfillment_methods.selected"
            class="custom-v-select">
            <template #open-indicator="{ attributes }">
              <i class="fa fa-angle-down" v-bind="attributes"></i>
            </template>
          </v-select>
        </div>
        <div class="sales-by-asin-filter flex-column align-items-start mr-2">
          <ComplexRangeDatepicker class="d-flex justify-content-center select-date" v-model="currentDateQuery"
            :dateOptions="this.dateOptions"></ComplexRangeDatepicker>
        </div>

      </div>
      <div class="mt-1">
        <cbpo-widget ref="widget" class="border-right-0 border-bottom-0 border-left-0 sales-by-asin-table"
          :key="reloadKey" :config-obj="salesByAsin.config"></cbpo-widget>
      </div>
    </div>
  </b-card>
</template>

<script>
import _ from 'lodash'
import { FULFILLMENT_METHODS_ALL, FULFILLMENT_METHODS_FBA, FULFILLMENT_METHODS_MFN_DS } from '@/shared/constants'
import { DATE_QUERY_SALES_BY_ASIN_OPTIONS } from '@/shared/constants/date.constant'
import ComplexRangeDatepicker from '@/components/common/ComplexRangeDatepicker/ComplexRangeDatepicker.vue'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'

export default {
  name: 'SalesByASIN',
  components: {
    ComplexRangeDatepicker,
    WidgetHeader
  },
  mixins: [WidgetMenu],
  props: {
    salesByAsin: Object
  },
  data() {
    return {
      fulfillment_methods: {
        options: [
          FULFILLMENT_METHODS_ALL,
          FULFILLMENT_METHODS_FBA,
          FULFILLMENT_METHODS_MFN_DS
        ],
        selected: FULFILLMENT_METHODS_ALL
      },
      currentDateQuery: [],
      dateOptions: DATE_QUERY_SALES_BY_ASIN_OPTIONS,
      reloadKey: 0
    }
  },
  methods: {
    queryData() {
      let baseQuery = {
        config: {
          query: {
            type: 'AND',
            conditions: [
              {
                'column': 'fulfillment_type',
                'operator': 'in',
                'value': ['MFN-DS', 'FBA']
              }
            ]
          }
        }
      }
      if (
        Array.isArray(this.currentDateQuery) &&
        this.currentDateQuery.length &&
        !this.currentDateQuery.every(_.isNull) // case: null absolute date
      ) {
        baseQuery.config.query.conditions.push(
          {
            column: 'sale_date',
            operator: '$gte',
            value: this.currentDateQuery[0]
          },
          {
            column: 'sale_date',
            operator: '$lte',
            value: this.currentDateQuery[1]
          }
        )
      }
      if (this.fulfillment_methods.selected.value) {
        baseQuery.config.query.conditions.push(
          {
            'column': 'fulfillment_type',
            'operator': '$eq',
            'value': this.fulfillment_methods.selected.value
          }
        )
      }
      this.salesByAsin.config.filter.base = baseQuery
      this.salesByAsin.config.elements[0].config.pagination.current = 1
      this.reloadKey = new Date().getTime() + 1
    },
    menuEventHandler(type) {
      if (type !== 'csv' || !this.$refs.widget) return
      this.$refs.widget.widgetExport(type)
    }
  },
  watch: {
    'fulfillment_methods.selected'() {
      this.queryData()
    },
    'currentDateQuery'() {
      this.queryData()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

::v-deep {
  .cbpo-table-container {
    min-height: 300px;
    background-color: #d9d9d9
  }

  .custom-v-select {
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

  .mx-input {
    min-height: 36px;
  }

  .btn-primary.disabled,
  .btn-primary {
    padding: .3rem .5rem !important;
    font-size: 12px;
  }

  .dropdown-toggle {
    font-size: 0.875rem !important;

    i {
      font-size: 14px !important;
      font-weight: normal;
      color: #23282c !important;
    }
  }

  .dropdown-item {
    font-size: 0.875rem;

    &:hover {
      color: #fff;
      background: #5897fb;
      border-radius: 0;
    }
  }

  .overview__menu-control .menu-control-select {
    margin: 0 23px !important;

    .btn:not(.not-button).btn-secondary.btn-secondary:not(.disabled):not(:disabled):hover {
      background-color: #fff !important;
    }
  }

  .custom-v-select {
    height: 36px;
  }
}

.sales-by-asin {
  background-color: #f9fbfb;
}

.sales-by-asin-cta {
  margin-top: 8px;
  padding: 0 8px;

  .sales-by-asin-filter {
    min-width: 25%;
  }
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

.card-body {
  height: 100%;
  padding: 0 0;
  overflow: hidden;
}

.cbpo-sdk-precise-theme .cbpo-dashboard,
.cbpo-sdk-precise-theme .cbpo-widget,
.cbpo-sdk-precise-theme .cbpo-widget .cbpo-crosstab-table-container {
  border: none;
}

::v-deep .cbpo-pagination {
  display: flex !important;
  justify-content: center !important;
}

::v-deep .cbpo-pagination-sizing {
  width: 40% !important;
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

::v-deep .select-dropdown {
  background-color: #fff !important;
}

::v-deep .cbpo-control-features,
.sales-by-asin-table {
  background-color: #f9fbfb !important;
}
::v-deep .dropdown-toggle-no-caret {
  &:active, &:hover {
    box-shadow: none !important;
    border-color: #e1e1e1db !important;
  }
}
</style>
