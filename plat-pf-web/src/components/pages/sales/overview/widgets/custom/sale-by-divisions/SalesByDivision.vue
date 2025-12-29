<template>
  <div ref="wrapper" class="sales-by-division" :class="listOfDivisionsByUser.length > 0 ? 'list-non-empty' : 'list-empty'">
    <widget-header title="Sales By Division" :lastUpdated="lastUpdated">
      <template #menu-control>
        <cbpo-widget-menu-control v-if="!isHideMenu" :key="count" class="custom-menu"
          :class="{ disabled: isLoadingSetting }" :config-obj="mixinsWidgetMenuConfig" @click="menuEventHandler" />
      </template>
    </widget-header>
    <div class="sales-by-division-body">
      <sale-by-divisions-data ref="dataWidget" :data-source="dsId.data_source_id" @changed="buildAndRefreshWidget" />
      <template v-if="!isLoadingSetting">
        <template v-if="listOfDivisionsByUser.length > 0">
          <div class="ql-container" v-if="!isHideMenu">
            <div class="ql-editor">
              <div :key="width"
                style="margin-left: 0px; margin-right: 0px; padding-top: 10px; display: flex; flex-wrap: wrap; justify-content: center; align-items: center;">
                <div style="flex: 1 0 auto;">
                  <p class="text-center m-0 invisible" :style="{ fontSize: '15pt', color: '#23282c' }">
                    <strong>DIV</strong>
                  </p>
                </div>
                <div style="flex-grow: 1;" v-for="(division, index) in listOfDivisionsByUser" :key="index">
                  <p class="text-center m-0" :style="{ fontSize: '15pt', color: '#23282c', 'width': `${width}px` }">
                    <strong class="pr-2">{{ division | upperCase }}</strong> <i @click="handleOpenConfigure(division)"
                      v-if="isConfigureIconOpened && isConfigureIconEnabled(division)"
                      class="fa fa-cog cursor-pointer"></i>
                  </p>
                </div>
              </div>
            </div>
          </div>
          <cbpo-widget ref="widgetSaleByDivision" :key="count" :config-obj="config" />
        </template>
        <template v-else>
          <div class="d-flex justify-content-center align-items-center h-100">
            <span class="text-muted">Sales by Division is not configured in this workspace</span>
          </div>
        </template>
      </template>
    </div>

    <setting-division v-if="!isLoadingSetting" :is-open.sync="isModelOpened" :dashboard="dashboard"
      :widget-name="widgetName" :widget-slug="widgetSlug" />
    <config-division v-if="!isLoadingSetting || divisionSelected" :key="divisionSelected"
      :is-open.sync="isConfigureModelOpened" :dashboard="dashboard" :division="divisionSelected" />
  </div>
</template>

<script>
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'
import SettingDivision from '@/components/pages/sales/views/modal/SettingDivision'
import ConfigDivision from '@/components/pages/sales/views/modal/ConfigDivision'
import isEqual from 'lodash/isEqual'
import lowerCase from 'lodash/lowerCase'
import snakeCase from 'lodash/snakeCase'
import upperCase from 'lodash/upperCase'
import { mapActions, mapGetters } from 'vuex'
import cloneDeep from 'lodash/cloneDeep'
import SaleByDivisionsData from './SaleByDivisionsData'

const timePeriodFilters = {
  YTD: 'YTD',
  MTD: 'MTD'
}

export default {
  name: 'SalesByDivision',
  components: { SettingDivision, ConfigDivision, SaleByDivisionsData, WidgetHeader },
  mixins: [WidgetMenu],
  props: {
    config: Object,
    dsId: Object,
    dashboard: String
  },
  filters: {
    upperCase: (value) => upperCase(value)
  },
  data: () => ({
    count: 0,
    width: 0,
    isModelOpened: false,
    isConfigureModelOpened: false,
    isConfigureIconOpened: false,
    isHideMenu: false,
    expressionShortCode: {},
    divisionSelected: null,
    dataCalculated: null,
    configExport: {
      id: 'id-a97d6b1b-67ae-4ceb-9b46-958a0c074896',
      dataSource: 'salesByDivisionsDSLocal',
      type: 'csv',
      fileName: 'sales-by-division-widget'
    },
    widgetName: 'Divisions',
    widgetSlug: 'divisions',
    lastUpdated: null
  }),
  mounted() {
    this.updateWidth()
    window.addEventListener('resize', this.updateWidth)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateWidth)
  },
  computed: {
    ...mapGetters({
      listOfDivisionsByUser: `pf/settings/getListOfDivisionsByUser`,
      listOfDivisions: `pf/settings/getListOfDivisions`,
      isLoadingSetting: `pf/settings/isLoadingSetting`,
      divisionsConfig: `pf/settings/divisionsConfig`
    }),
    widgetData() {
      return {
        id: this.dsId.data_source_id
      }
    },
    isConfigureIconEnabled() {
      return (division) => {
        const divisionConfig = this.divisionsConfig.find(item => item.key === division)
        return divisionConfig && divisionConfig.sync_option === 'Manual'
      }
    }
  },
  methods: {
    ...mapActions({
      fetchListOfDivisionsByUser: `pf/settings/fetchListOfWidgetByUser`,
      fetchDivisionsConfig: `pf/settings/fetchDivisionsConfig`
    }),
    updateWidth() {
      const countDivision = this.listOfDivisionsByUser.length
      const elm = countDivision < 4 ? 4 : 5
      this.width = this.$refs.wrapper ? this.$refs.wrapper.clientWidth * 0.8 / elm : 320
    },
    menuEventHandler(event) {
      switch (event) {
        case 'edit-divisions':
          this.isModelOpened = true
          break
        case 'configure-divisions':
          this.isConfigureIconOpened = !this.isConfigureIconOpened
          break
        case 'csv':
          this.exportData()
          break
        default:
          break
      }
    },
    handleOpenConfigure(division) {
      this.divisionSelected = division
      this.isConfigureModelOpened = true
    },
    saveAndConfigManualExpressionShortCode(dataSourceId, shortCode, expression, division, timePeriodFilters) {
      const divisionConfig = this.divisionsConfig.find(item => item.key === division)
      // Get data from config manual if enabled and sync_option is Manual
      if (divisionConfig && divisionConfig.enabled && divisionConfig.sync_option === 'Manual' && timePeriodFilters) {
        this.expressionShortCode[shortCode] = divisionConfig[`${snakeCase(lowerCase(timePeriodFilters))}_manual`] || 0
        return divisionConfig[`${snakeCase(lowerCase(timePeriodFilters))}_manual`] || 0
      }
      // Get data from data source if end with "sale_by_divisions"
      if (dataSourceId.endsWith('sale_by_divisions')) {
        this.expressionShortCode[shortCode] = this.dataCalculated[shortCode] || 0
        return this.dataCalculated[shortCode] || 0
      }
      this.expressionShortCode[shortCode] = expression
      return expression
    },
    getConfigManualExpressionShortCode(expression, division, timePeriodFilters) {
      const divisionConfig = this.divisionsConfig.find(item => item.key === division)
      if (divisionConfig && divisionConfig.enabled && divisionConfig.sync_option === 'Manual' && timePeriodFilters) {
        return divisionConfig[`${snakeCase(lowerCase(timePeriodFilters))}_manual`] || 0
      }
      return expression
    },
    replaceExpressionKPIChart(dsId, conditionDay, division) {
      this.updateWidth()
      let contentKpiChartYTD = `[kpi chart-type="radial" class-css="" width="WIDTH" height="300" current="EXPRESSION_CURRENT" min="EXPRESSION_MIN" max="EXPRESSION_MAX" target="EXPRESSION_TARGET" format-string="$,d" format-tooltip=",d"][/kpi]`
      let contentPercentage = `<p class="text-center m-0" style="font-size: 15px; color: #23282c; font-weight: 500; width: WIDTHpx">[format value="EXPRESSION_PERCENTAGE" format='{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}' type="segments" color='{"#7cab2e": "value >=0", "#f45e40": "value < 0"}'][/format]</p>`
      const conditionByDay = { // today 4-25-2024
        MTD_CURRENT: `(@sale_date >= DATE_START_OF(YESTERDAY(),'month')) & (@sale_date <= DATE_END_OF(YESTERDAY(), 'day'))`, // 4-1-2024 to 4-24-2024
        MTD_TARGET: `(@sale_date >= DATE_START_OF(DATE_LAST(1,'year'), 'month')) & (@sale_date < DATE_START_OF(DATE_LAST(1,'year'), 'day'))`, // 4-1-2023 to 4-24-2023
        MTD_MAX: `(@sale_date >= DATE_START_OF(DATE_LAST(1,'year'),'month')) & (@sale_date <= DATE_END_OF(DATE_LAST(1,'year'), 'month'))`, // 4-1-2023 to 4-30-2023
        YTD_CURRENT: `(@sale_date >= DATE_START_OF(YESTERDAY(),'years')) & (@sale_date <= DATE_END_OF(YESTERDAY(), 'day'))`, // 1-1-2024 to 4-24-2024
        YTD_TARGET: `(@sale_date >= DATE_START_OF(DATE_LAST(1,'year'), 'year')) & (@sale_date < DATE_START_OF(DATE_LAST(1,'year'), 'day'))`, // 4-1-2023 to 4-24-2023
        YTD_MAX: `(@sale_date >= DATE_START_OF(DATE_LAST(1,'year'),'years')) & (@sale_date <= DATE_END_OF(DATE_LAST(1,'year'), 'years'))` // 1-1-2023 to 12-31-2023
      }
      const divisionData = this.listOfDivisions.find(item => item.key === division)
      const baseConditions = [
        "(@item_sale_status $eq 'Shipped')",
        '@item_sale_charged not_null',
        "(@channel_name $eq 'amazon.com')",
        `(@segment $eq '${divisionData.name}')`
      ].join(' & ')

      contentPercentage = contentPercentage.replace('WIDTH', this.width)
      contentKpiChartYTD = contentKpiChartYTD
        .replace('WIDTH', this.width)
        .replace('EXPRESSION_MIN', 0)
        .replace('EXPRESSION_MAX', this.saveAndConfigManualExpressionShortCode(dsId, `radial__${conditionDay}__${upperCase(division)}__MAX`, `{SUMIF(@item_sale_charged, ${baseConditions} & ${conditionByDay[`${conditionDay}_MAX`]}, '${dsId}')}`, division, `${conditionDay}_MAX`))
        .replace('EXPRESSION_CURRENT', this.saveAndConfigManualExpressionShortCode(dsId, `radial__${conditionDay}__${upperCase(division)}__CURRENT`, `{SUMIF(@item_sale_charged, ${baseConditions} & ${conditionByDay[`${conditionDay}_CURRENT`]}, '${dsId}')}`))
        .replace('EXPRESSION_TARGET', this.saveAndConfigManualExpressionShortCode(dsId, `radial__${conditionDay}__${upperCase(division)}__TARGET`, `{SUMIF(@item_sale_charged, ${baseConditions} & ${conditionByDay[`${conditionDay}_TARGET`]}, '${dsId}')}`, division, `${conditionDay}_TARGET`))

      let expressionPercentage = '(((EXPRESSION_CURRENT - EXPRESSION_TARGET) / EXPRESSION_TARGET) as c4 * 100)'
      expressionPercentage = expressionPercentage
        .replace('EXPRESSION_CURRENT', `SUMIF(@item_sale_charged, ${baseConditions} & ${conditionByDay[`${conditionDay}_CURRENT`]}, '${dsId}')`)
        .replace(/EXPRESSION_TARGET/g, this.getConfigManualExpressionShortCode(`SUMIF(@item_sale_charged, ${baseConditions} & ${conditionByDay[`${conditionDay}_TARGET`]}, '${dsId}')`, division, `${conditionDay}_TARGET`))
      return contentKpiChartYTD.concat(contentPercentage.replace('EXPRESSION_PERCENTAGE', this.saveAndConfigManualExpressionShortCode(dsId, `format__PERCENTAGE__${conditionDay}__${upperCase(division)}`, expressionPercentage)))
    },
    buildTableExportConfig(columns) {
      return {
        cols: columns,
        rows: [...this.buildRowsLocal(columns)]
      }
    },
    buildColumnsExport() {
      const listCol = []
      this.listOfDivisionsByUser.map(division => {
        for (let timeFilter in timePeriodFilters) {
          for (let valueChart of ['CURRENT', 'TARGET', 'MAX']) {
            listCol.push({
              'name': `${division}__${timeFilter}__${valueChart}__KPI_CHART`,
              'type': 'string',
              'alias': `${division} ${valueChart} (${upperCase(timeFilter)})`,
              'displayName': `${division} ${valueChart} (${upperCase(timeFilter)})`
            })
          }
          listCol.push({
            'name': `${division}__${timeFilter}__PERCENTAGE`,
            'type': 'string',
            'alias': `${division} Percentage (${upperCase(timeFilter)})`,
            'displayName': `${division} Percentage (${upperCase(timeFilter)})`
          })
        }
        listCol.push({
          'name': `${division}__UNITS_SOLD`,
          'type': 'string',
          'alias': `${division} Units Sold`,
          'displayName': `${division} Units Sold`
        })
      })
      return listCol
    },
    splitKeyByUnderscores(key) {
      return key.split('__')
    },
    buildRowsLocal(columns) {
      const items = this.expressionShortCode || {}
      const listKey = Object.keys(items) || []
      const rows = []
      for (const col of columns) {
        const colData = this.splitKeyByUnderscores(col.name)
        let data = null
        for (const key of listKey) {
          const keyNames = this.splitKeyByUnderscores(key)
          if (keyNames[0] === 'format' && keyNames.length === 3 && keyNames[1] === colData[1] && keyNames[2] === upperCase(colData[0])) {
            data = items[key]
          }
          if (keyNames[0] === 'format' && keyNames[1] === colData[2] && keyNames[2] === colData[1] && keyNames[3] === upperCase(colData[0])) {
            data = items[key]
          }
          if (keyNames[0] === 'radial' && keyNames[1] === colData[1] && keyNames[2] === upperCase(colData[0]) && keyNames[3] === colData[2]) {
            data = items[key]
          }
        }
        if (!data) {
          data = 0
        }
        rows.push(data)
      }
      return [rows]
    },
    saveDataWidgetToDsLocal() {
      const columnsExport = this.buildColumnsExport()
      this.configExport.columns = cloneDeep(columnsExport)
      this.config.elements[0].config.columns = cloneDeep(columnsExport)
      window.salesByDivisionsDSLocal = this.buildTableExportConfig(columnsExport)
      this.config.elements[0].config.dataSource = 'salesByDivisionsDSLocal'
    },
    exportData() {
      this.$nextTick(() => {
        this.$refs.widgetSaleByDivision.widgetExport(this.configExport.dataSource, this.configExport.type, this.configExport.fileName)
      })
    },
    buildExpression() {
      const expressionUnitSold = this.listOfDivisionsByUser.map(division => `<div style="flex-grow: 1;">
        <p class="text-center m-0" style="font-size: 10pt; color: #23282c; font-weight: 500; width: WIDTH_KPI_CHARTpx">${upperCase(division)}_UNITS_SOLD</p>
        </div>`).join('')
      let mainExpressionChart = ''
      for (let timeFilter in timePeriodFilters) {
        if (timePeriodFilters.hasOwnProperty(timeFilter)) {
          const expressionKIPChart = this.listOfDivisionsByUser.map(division => `<div style="width: WIDTH_KPI_CHARTpx; flex-grow: 1;"><p class="text-center m-0">${upperCase(timeFilter)}_${upperCase(division)}_KPI_CHART</p></div>`).join('')
          mainExpressionChart += `<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; ${upperCase(timeFilter) === timePeriodFilters.YTD ? 'padding-top: 20px' : 'padding-bottom: 10px;'};"> <div style="flex: 1 0 auto;"><p class="text-center m-0" style="font-size: 15pt;color: #23282c;"><strong>${upperCase(timeFilter)}</strong></p></div>${expressionKIPChart}</div>`
        }
      }
      return `<div style="margin-left: 0px; margin-right: 0px; display: flex; flex-wrap: wrap; justify-content: center; align-items: center;"><div style="flex: 1 0 auto;"><p class="text-center m-0 invisible" style="font-size: 15pt;color: #23282c;"><strong>DIV</strong></p></div>${expressionUnitSold}</div>${mainExpressionChart}`
    },
    replaceExpressionAndReRender(dsId) {
      this.updateWidth()
      let contentWidget = this.buildExpression()
      // list of division
      this.listOfDivisionsByUser.forEach(division => {
        const expressionUnitsSold = `SUMIF(@quantity, (@segment $eq '${division}') & (@channel_name $eq 'amazon.com') & (@sale_date >=DATE_START_OF(YESTERDAY(),'years')) & (@sale_date <= DATE_END_OF(YESTERDAY(), 'day')), '${dsId}') as 'current'`
        contentWidget = contentWidget
          .replace(/WIDTH_KPI_CHART/g, parseInt(this.width))
          .replace(`YTD_${upperCase(division)}_KPI_CHART`, this.replaceExpressionKPIChart(dsId, timePeriodFilters.YTD, division))
          .replace(`MTD_${upperCase(division)}_KPI_CHART`, this.replaceExpressionKPIChart(dsId, timePeriodFilters.MTD, division))
          .replace(`${upperCase(division)}_UNITS_SOLD`, `[format value="${this.saveAndConfigManualExpressionShortCode(dsId, `format__UNITS_SOLD__${upperCase(division)}`, expressionUnitsSold, division)}" type="numeric" format=','][/format]`)
      })
      this.config.elements[0].config.content = contentWidget
      this.isHideMenu = false
      this.saveDataWidgetToDsLocal()
      this.count++
    },
    buildAndRefreshWidget(dataSource) {
      this.dataCalculated = dataSource
      this.lastUpdated = this.dataCalculated ? this.dataCalculated.lastUpdated : null
      this.replaceExpressionAndReRender(this.dsId.data_source_id)
    }
  },
  async created() {
    this.isHideMenu = true
    await this.fetchListOfDivisionsByUser({
      dashboard: this.dashboard,
      clientId: this.$route.params.client_id,
      widgetName: this.widgetName,
      widgetSlug: this.widgetSlug
    })
    await this.fetchDivisionsConfig({
      clientId: this.$route.params.client_id,
      dashboard: this.dashboard,
      widgetName: this.widgetSlug
    })
    this.mixinsWidgetMenuConfig.selection = {
      options: [
        {
          label: 'Edit Divisions',
          icon: 'fa fa-pencil',
          value: 'edit-divisions',
          type: 'item'
        },
        {
          label: 'Configure Sync Data',
          icon: 'fa fa-cog',
          value: 'configure-divisions',
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
  watch: {
    widgetData: {
      immediate: true,
      async handler(data, previousData) {
        if (!data.id || isEqual(data, previousData) || !this.dataCalculated) return
        this.replaceExpressionAndReRender(this.dsId.data_source_id)
      }
    },
    divisionsConfig: {
      immediate: true,
      async handler(data, previousData) {
        if (!this.dataCalculated) return
        this.replaceExpressionAndReRender(this.dsId.data_source_id)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.sales-by-division {
  &.list-empty {
    min-height: 300px;
    padding-bottom: 40px;
  }
  &.list-non-empty {
    min-height: 700px;
  }
  display: flex;
  flex-direction: column;
  border: solid 1px #d9d9d9;
  height: 100%;
  background-color: #fff;

  .sales-by-division-body {
    height: 100%;

    &::v-deep {
      .cbpo-widget {
        border: none;
      }

      .cbpo-container-html-editor,
      .cbpo-control-features {
        padding: 0 !important;
        overflow: unset;
      }

      .cbpo-container-html-editor {
        g.group-bar {
          circle {
            display: none;
          }

          &.Current_Value rect {
            fill: #52c0e1;
          }

          &.Target_Value rect {
            fill: #91e4ab;
          }

          &.Max_Value rect {
            fill: #d0dde7;
          }
        }

        g.group-points text {
          font-family: "Inter";
          font-style: normal;
          font-weight: 400;
          line-height: 20px;
          fill: #080e2c;
          font-size: 14px;
        }
      }
    }
  }
}

::v-deep .cbpo-container-html-editor {
  .ql-editor {
    svg {
      overflow: visible;
    }
  }
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

::v-deep .needle-value {
  font-size: 15px;
}

.header-division {
  margin-left: 0px;
  margin-right: 0px;
  padding-top: 10px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
}

::v-deep .cbpo-container {
  .ql-container {
    height: 100%;
  }
}

::v-deep .sales-by-division {
  .dropdown-menu {
    li {
      &:hover {
        background-color: #5897fb !important;
      }
    }
  }
}

::v-deep .cbpo-feature-container {
  height: 80% !important;
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
