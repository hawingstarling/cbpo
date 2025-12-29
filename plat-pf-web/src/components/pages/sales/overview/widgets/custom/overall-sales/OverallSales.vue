<template>
  <div class="widget-overall-sales d-flex flex-column position-relative h-100 overflow-hidden">
    <widget-header title="Overall Sales" :lastUpdated="lastUpdated">
      <template #menu-control>
        <cbpo-widget-menu-control class="custom-menu" :config-obj="mixinsWidgetMenuConfig"
        @click="menuEventHandler" />
      </template>
    </widget-header>
    <div class="widget-overall-sales-body h-100" v-cbpo-loading="{ loading: isLoading }">
      <overall-sales-data :key="renderKey" ref="dataWidget" @changed="buildAndRefreshWidget" :config-obj="config" />
      <template v-if="isShowContent">
        <div class="overall-sales-segments">
          <template>
            <b-card-group deck>
              <b-card v-for="(data, index) in listSectionOverallSales" :key="index" class="mb-3" :class="{'columns-template': listSectionOverallSales.length === overallSalesLimit}">
                <template #header>
                  <div class="title">{{ data.title }}</div>
                </template>
                <b-card-text>
                  <div :class="{ [data.className]: listSectionOverallSales.length < overallSalesLimit, 'trend': listSectionOverallSales.length < overallSalesLimit }">
                    <div class="main-data">
                      {{ data.main | number(data.slug !== totalUnitsSoldSlug) }}
                      <div v-if="listSectionOverallSales.length === overallSalesLimit" class="columns-item" :class="[data.className]" />
                    </div>
                    <div v-for="(child, indexChild) in data.childData" :key="indexChild">
                      <div class="child" :class="{ 'w-100': listSectionOverallSales.length === overallSalesLimit }">
                        <i :class="[child.className]"></i>
                        <span>{{ child.data }}</span>&nbsp;
                        <span class="w-100">{{ child.text }}</span>
                      </div>
                    </div>
                  </div>
                </b-card-text>
              </b-card>
            </b-card-group>
          </template>
        </div>
      </template>
    </div>
    <SettingOverallSales v-if="!isLoadingSetting" :is-open.sync="isModelOpened" @loading="isLoading = true"
      :dashboard="dashboard" :widget-name="widgetName" :widget-slug="widgetSlug" @refresh="refreshWidget" />
  </div>

</template>

<script>
import OverallSalesData from './OverallSalesData'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import SettingOverallSales from '@/components/pages/sales/views/modal/SettingOverallSales'
import { isArray, isUndefined, floor } from 'lodash'
import { isInvalidNumber } from '@/shared/filters'
import { mapActions, mapGetters } from 'vuex'
import { slugify } from '@/shared/utils'
import moment from 'moment-timezone'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'

export default {
  name: 'OverallSalesWidget',
  components: { OverallSalesData, SettingOverallSales, WidgetHeader },
  props: {
    config: Object,
    dashboard: String
  },
  mixins: [
    WidgetMenu
  ],
  data() {
    return {
      isLoading: true,
      dataTable: [],
      renderKey: Date.now(),
      compareRowData: [],
      localDsId: null,
      widgetName: 'OverallSales',
      widgetSlug: 'overall-sales',
      totalUnitsSoldSlug: 'Total-Units-Sold',
      isModelOpened: false,
      mixinsWidgetMenuConfig: {
        selection: {
          options: [
            {
              label: 'Edit Overall Sales',
              icon: 'fa fa-pencil',
              value: 'edit-divisions',
              type: 'item'
            },
            {
              label: 'Export CSV',
              icon: 'fa fa-download',
              value: 'csv',
              type: 'item'
            }
          ]
        }
      },
      noDataMessage: this.config.elements[0].config.messages.no_data_at_all || 'No data',
      overallSalesLimit: 5,
      timezone: 'America/Los_Angeles',
      lastUpdated: null
    }
  },
  async created() {
    this.isLoading = true
    await this.fetchListOfWidgetByUser({
      dashboard: this.dashboard,
      clientId: this.$route.params.client_id,
      widgetName: this.widgetName,
      widgetSlug: this.widgetSlug
    })
  },
  filters: {
    number(value, addDollarSign = true) {
      if (isInvalidNumber(value)) return '-'
      const dollarSign = addDollarSign ? '$' : ''
      return `${dollarSign}${Number(value).toLocaleString('en')}`
    }
  },
  computed: {
    ...mapGetters({
      listOfOverallSalesByUser: `pf/settings/getListOfOverallSalesByUser`,
      isLoadingSetting: `pf/settings/isLoadingSetting`
    }),
    widgetRef() {
      return this.$refs.dataWidget
    },
    listSectionOverallSales() {
      if (!this.dataTable.length) return []
      const data = []
      const convertDashToUnderScoreFn = name => name.toLowerCase().replace(/-/g, '-')
      const convertDashToSpaceFn = name => name.replace(/-/g, ' ')
      this.listOfOverallSalesByUser.forEach(key => {
        data.push(this.convertData(convertDashToUnderScoreFn(key), convertDashToSpaceFn(key)))
      })
      return data
    },
    isShowContent() {
      return !this.isLoading && Boolean(this.listSectionOverallSales.length)
    },
    beforeTodayFormat() {
      // The date of current data is yesterday, which is why two days have been subtracted in this format.
      return moment.tz(this.timezone).subtract(2, 'days').format('M/D')
    }
  },
  methods: {
    refreshWidget() {
      this.isLoading = true
      this.renderKey = Date.now() + 1 // force re-render
    },
    ...mapActions({
      fetchListOfWidgetByUser: `pf/settings/fetchListOfWidgetByUser`
    }),
    getClassName(compareRowData) {
      return isArray(compareRowData)
        ? compareRowData.some(d => d && d.data && d.data.includes('-')) ? 'decrease' : 'increase'
        : !isUndefined(compareRowData) && compareRowData.includes('-') ? 'custom-arrow-down' : 'custom-arrow-up'
    },
    convertData(columnName, title) {
      const data = this.dataTable.find(col => col.division.base.toLowerCase() === columnName)
      const childData = this.compareRowData.map(
        ({ text, value }) => ({
          text,
          data: data[value].format,
          className: this.getClassName(data[value].format)
        }))
      return {
        title: title,
        slug: slugify(title),
        main: floor(data.total.base),
        childData: childData,
        className: this.getClassName(childData)
      }
    },
    menuEventHandler(event) {
      event === 'csv' ? this.widgetRef.exportCSV() : this.isModelOpened = true
    },
    buildAndRefreshWidget(dataSource) {
      if (!dataSource.length) {
        this.isLoading = false
        return
      }
      this.lastUpdated = dataSource[0].modified ? dataSource[0].modified.base : null
      this.dataTable = [...dataSource]
      this.compareRowData = [
        {
          value: 'percent_vs_yesterday',
          text: `vs Yesterday (${this.beforeTodayFormat})`
        },
        {
          value: 'percent_vs_last_week',
          text: 'vs last week'
        },
        {
          value: 'percent_vs_last_month',
          text: 'vs last month'
        }
      ]
      this.localDsId = `id_overall_sale_${Date.now()}`
      this.isLoading = false
    }
  }
}
</script>

<style scoped lang="scss">
.widget-overall-sales {
  border: solid 1px #d9d9d9;

  ::v-deep .menu-control-select {
    position: absolute;
    right: calc(0px + 0.5rem);
    top: 19px;
    right: 32px;
    z-index: 50;
  }
}

.overall-sales-segments {
  display: flex;
  padding: 20px 0px 20px 15px;

  .group {
    width: calc(100% / 3);
  }
  .columns-template {
    .card-body {
      padding: 20px 15px;
    }
  }
  .trend {
    position: relative;
    height: 100%;

    &:before {
      position: absolute;
      bottom: 1px;
      left: 80%;
    }

    &.increase::before {
      content: url("~@/assets/img/icon/up-trend.svg");
    }

    &.decrease::before {
      content: url("~@/assets/img/icon/down-trend.svg");
    }
  }
  .columns-item {
    position: relative;
    height: 100%;
    &:before {
      position: absolute;
      bottom: -15px;
      left: 75%;
    }
    &.increase::before {
      content: url("~@/assets/img/icon/up-trend.svg");
      transform: scale(0.75)
    }

    &.decrease::before {
      content: url("~@/assets/img/icon/down-trend.svg");
      transform: scale(0.75)
    }
  }

  .title {
    font-family: Inter, serif;
    font-size: 14px;
    line-height: 16px;
    font-weight: 700;
  }

  .main-data {
    font-family: Inter, serif;
    font-weight: 700;
    font-size: 24px;
    line-height: 32px;
    margin: 5px 0;
  }

  .child {
    font-family: Inter, serif;
    font-weight: 400;
    font-size: 14px;
    line-height: 20px;
    margin-bottom: 5px;

    span {
      display: inline-block;
    }

    i.custom-arrow-up+span {
      color: #027A48;
    }

    i.custom-arrow-down+span {
      color: #D92D20;
    }
  }
  .custom-arrow-down, .custom-arrow-up {
    width: 15px;
  }
}

.overall-sales-empty {
  text-align: center;
  font-size: 1rem;
  margin-top: 1rem;
}

.title {
  font-weight: bold;
}

.card {
  margin-right: 0px !important;
}

.child {
  display: flex;
  align-items: center;
  width: 85%;
}

.child {
  i {
    margin-right: 5px;
  }

  span:last-child {
    width: 67%;
    z-index: 1;
  }
}

.card-deck {
  width: 100%;
}

@media (max-width: 1060px) {
  .card-deck {
    flex-flow: column;

    .card {
      margin-bottom: 11px !important;
    }
  }
}

@media (min-width: 1061px) and (max-width: 1260px) {
  .card-text {
    .child {
      width: 100%;
    }
  }

  .card-body {
    padding: 8px 18px 12px 13px !important
  }
}

.card,
.card-header {
  border-top-left-radius: 8px !important;
  border-top-right-radius: 8px !important;
}

.bg-white {
  background-color: #fff;
}

::v-deep .dropdown-item {
  font-size: 0.875rem;

  &:hover {
    color: #fff;
    background: #5897fb;
    border-radius: 0;
  }
}
</style>
