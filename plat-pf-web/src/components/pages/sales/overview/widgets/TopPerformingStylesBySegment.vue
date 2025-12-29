<template>
  <b-card class="top-performing-styles rounded-0 h-100">
    <div class="h-100 d-flex flex-column overflow-hidden">
      <widget-header title="Top Performing Styles by Segment" :lastUpdated="lastUpdated">
        <template #menu-control>
          <cbpo-widget-menu-control :config-obj="mixinsWidgetMenuConfig"
            @click="menuEventHandler"/>
        </template>
      </widget-header>

      <div class="top-performing-styles-cta d-flex justify-content-start align-items-end flex-wrap flex-grow-1">
        <div class="top-performing-styles-filter flex-column align-items-start mr-2">
          <label class="label mb-2 fulfillment-label">Group by</label>
          <v-select :options="segmentsOptions" :clearable="false" v-model="segmentsSelected"
            class="custom-v-select">
            <template #open-indicator="{ attributes }">
              <i class="fa fa-angle-down" v-bind="attributes" aria-label="Open dropdown"></i>
            </template>
          </v-select>
        </div>
        <div class="top-performing-styles-filter flex-column align-items-start mr-2">
          <label class="label mb-2 fulfillment-label">Date</label>
          <v-select :options="dateOptions" :clearable="false" v-model="dateSelected" label="text"
            class="custom-v-select">
            <template #open-indicator="{ attributes }">
              <i class="fa fa-angle-down" v-bind="attributes" aria-label="Open dropdown"></i>
            </template>
          </v-select>
        </div>
        <div class="top-performing-styles-filter flex-column align-items-start mr-2">
          <label class="label mb-2 fulfillment-label">Search by ASIN</label>
          <CommonFilter v-model="currentCommonFilter" @change="onSearchChange()"/>
        </div>
      </div>
      <div class="mt-1">
        <cbpo-widget ref="widget" class="border-right-0 border-bottom-0 border-left-0 top-performing-styles-table"
          :key="reloadKey" :config-obj="topPerformingStylesBySegment.config" @getLastUpdated="lastUpdated = $event"/>
      </div>
    </div>
  </b-card>
</template>

<script>
import { DATE_QUERY_TOP_PERFORMING_STYLES_OPTIONS } from '@/shared/constants/date.constant'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'
import CommonFilter from '@/components/common/CommonFilter/CommonFilter.vue'

// mixin
import baseQueryMixins from '@/mixins/baseQueryMixins'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'

// data
import { SEGMENT_OPTIONS_FOR_TOP_PERFORMING } from '@/shared/constants'

export default {
  name: 'TopPerformingStylesBySegment',
  components: {
    WidgetHeader,
    CommonFilter
  },
  mixins: [WidgetMenu, baseQueryMixins],
  props: {
    topPerformingStylesBySegment: Object,
    dsId: Object
  },
  data() {
    return {
      segmentsOptions: SEGMENT_OPTIONS_FOR_TOP_PERFORMING,
      segmentsSelected: SEGMENT_OPTIONS_FOR_TOP_PERFORMING[0],
      dateSelected: DATE_QUERY_TOP_PERFORMING_STYLES_OPTIONS[0],
      dateOptions: DATE_QUERY_TOP_PERFORMING_STYLES_OPTIONS,
      currentCommonFilter: '',
      reloadKey: 0,
      lastUpdated: null
    }
  },
  methods: {
    menuEventHandler(type) {
      if (type !== 'csv' || !this.$refs.widget) return
      try {
        this.$refs.widget.widgetExport(type)
      } catch (error) {
        console.error('Failed to export widget data:', error)
        this.$bvToast.toast('Failed to export data. Please try again.', {
          title: 'Export Failed',
          variant: 'danger'
        })
      }
    },
    onSearchChange() {
      let filter = {
        type: 'AND',
        conditions: [
          {
            column: 'parent_asin',
            operator: 'contains',
            value: this.currentCommonFilter
          }
        ]
      }
      this.topPerformingStylesBySegment.config.filter.base.config.query = filter
      this.$nextTick(() => {
        this.reloadKey = new Date().getTime() + 1
      })
    },
    getLastUpdated(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    }
  },
  watch: {
    'dateSelected'(val) {
      this.topPerformingStylesBySegment.config.elements[0].config.dataSource = this.dsId[val.type].data_source_id
      this.topPerformingStylesBySegment.config.elements[0].config.crossTab.data = [...val.value]
      this.topPerformingStylesBySegment.config.elements[0].config.pagination.current = 1
      this.$nextTick(() => {
        this.reloadKey = new Date().getTime() + 1
      })
    },
    'segmentsSelected'(newVal, oldVal) {
      const config = this.topPerformingStylesBySegment.config
      const grouping = config.elements[0].config.grouping
      const pagination = config.elements[0].config.pagination

      grouping.columns = [{ name: newVal.value }]
      grouping.aggregations = grouping.aggregations.filter(item => item.column !== newVal.value)
      pagination.current = 1

      this.$nextTick(() => {
        this.reloadKey = new Date().getTime() + 1
      })
    }
  },
  created() {
    this.topPerformingStylesBySegment.config.elements[0].config.crossTab.data = [...this.dateSelected.value]
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

  .cbpo-table-action {
    background: #f9fbfb;
    border: none !important;
  }
  .tbl-col-header {
    .name {
      margin: 0 calc(16px + .5rem) !important;
    }
  }
}

.top-performing-styles {
  background-color: #f9fbfb;
}

.top-performing-styles-cta {
  margin-top: 8px;
  padding: 0 8px;

  .top-performing-styles-filter {
    min-width: 15%;
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
.top-performing-styles-table {
  background-color: #f9fbfb !important;
}
::v-deep .dropdown-toggle-no-caret {
  &:active, &:hover {
    box-shadow: none !important;
    border-color: #e1e1e1db !important;
  }
}
</style>
