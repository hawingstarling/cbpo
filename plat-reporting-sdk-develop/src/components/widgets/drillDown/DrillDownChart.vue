<template>
  <!-- Config ready will be enabled after widgetConfig function -->
  <div v-if="configReady" class="cbpo-drill-down-container">

    <!-- breadcrumbs -->
    <div class="cbpo-breadcrumbs-container">
      <slot name="breadcrumbs" :items="breadcrumbs" :resetDrillDown="resetDrillDownToIndex">
        <b-breadcrumb class="mb-2" v-if="breadcrumbs.length">
            <template v-for="(item, index) of breadcrumbs">
              <b-breadcrumb-item :id="'tooltip_target_' + index" @click="resetDrillDownToIndex(index)" :key="index">
                <p class="mb-0 label text-left">
                  <b class="cbpo-drilldown-main-column">{{ index === 0 && rootLabel ? rootLabel : item.displayName }}</b>
                </p>
                <p v-if="breadcrumbs[index - 1] && breadcrumbs[index - 1].value !== null" class="mb-0 sub-label text-left" v-html="`<small>${getTemplateMessage(breadcrumbs[index - 1].columnName, breadcrumbs[index - 1].value)}</small>`">
                </p>
              </b-breadcrumb-item>
              <b-tooltip :key="'tooltip_' + index" :target="'tooltip_target_' + index" triggers="hover">
                <p class="mb-0 label text-left">
                  <b class="cbpo-drilldown-main-column">{{ item.displayName }}</b>
                </p>
                <p v-if="breadcrumbs[index - 1] && breadcrumbs[index - 1].value !== null" class="mb-0 sub-label text-left" v-html="`<small>${getTemplateMessage(breadcrumbs[index - 1].columnName, breadcrumbs[index - 1].value)}</small>`">
                </p>
              </b-tooltip>
            </template>
          </b-breadcrumb>
      </slot>
    </div>
    <!-- end breadcrumbs -->

    <!-- modal -->
    <b-modal
      dialog-class="cbpo-custom-modal"
      :id="'drill-down-modal-' + config.modal.id"
      size="lg"
      no-close-on-backdrop
    >
      <template v-slot:modal-title>
        {{ config.modal.header.text }}
      </template>
      <!-- list columns -->
      <div v-if="drillDownData" class="cbpo-drill-down-detail">
        <p>
          You are going to drill down on <span v-html="getTemplateMessage(breadcrumbs.length ? breadcrumbs[breadcrumbs.length -1].columnName : drillDownData.columnName, drillDownData.value)"></span>
        </p>
      </div>
      <div class="cbpo-columns-label">
        <p>Next level column: </p>
      </div>

      <!-- drill down option -->
      <div
        v-if="columns.length > 0"
        class="row"
        v-cbpo-loading="{ loading: loading }"
      >
        <div
          class="col-4 d-flex cbpo-column-selection"
        >
          <v-select
            class="cbpo-custom-select w-100"
            v-model="selectedColumn"
            label="displayName"
            :reduce="option => option.name"
            :options="mappingColumns"
            :clearable="false"
            :placeholder="'Please select a column...'"
          >
            <template #open-indicator="{ attributes }">
              <i class="fa fa-angle-down" v-bind="attributes"></i>
            </template>
          </v-select>
        </div>
      </div>
      <!-- end drill down option -->

      <!-- config binning -->
      <div class="cbpo-binning">
        <cbpo-binning-options v-if="isBinningApplicable" :config.sync="binConfig" :columnType="columnType"></cbpo-binning-options>
      </div>
      <!-- end config binning -->

      <!-- end list columns -->
      <template v-slot:modal-footer="{ ok, cancel }">
        <!-- Emulate built in modal footer ok and cancel button actions -->
        <button :disabled="!selectedColumn" @click="apply()" class="cbpo-btn btn-primary mr-2">
          <span>{{ config.modal.actions.applyButton.text }}</span>
        </button>
        <button class="cbpo-btn" @click="cancel()">
          <span>{{ config.modal.actions.cancelButton.text }}</span>
        </button>
      </template>
    </b-modal>
    <!-- end modal -->
  </div>
</template>

<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import loadingDirective from '@/directives/loadingDirective'
import BinningConfig from '@/components/widgets/elements/table/grouping/BinningConfig'
import cloneDeep from 'lodash/cloneDeep'
import defaultsDeep from 'lodash/defaultsDeep'
import isEmpty from 'lodash/isEmpty'
import isObject from 'lodash/isObject'
import findIndex from 'lodash/findIndex'
import CBPO from '@/services/CBPO'
import { makeDefaultDrillDownConfig } from '@/components/widgets/drillDown/DrillDownConfig'
import { SUPPORT_LOGIC } from '@/utils/filterUtils'
import { SUPPORT_OPERATORS } from '@/services/ds/filter/FilterDefinitions'
import { DataTypeUtil, getDefaultAggregationsOfDataType } from '@/services/ds/data/DataTypes'
import { DEFAULT_STATE_BIN } from '@/components/widgets/elements/table/grouping/ColumnSettingsConfig'
import { buildBinFromConfig, createBinColumnAlias } from '@/utils/binUtils'
import DataFormatManager, { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import defaultTemporal from '@/services/dataFormats/temporalFormatConfig.js'

export default {
  name: 'DrillDown',
  props: {
    channelId: String,
    autoOrder: {
      type: Boolean,
      default: true
    },
    rootLabel: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // context data
      breadcrumbs: [],
      aggregations: [],
      selectedColumn: null,
      drillDownData: null,
      // bin component
      binConfig: null,
      columnType: null,
      // flag
      isModalOpen: false,
      isBinningApplicable: null
    }
  },
  directives: {
    'cbpo-loading': loadingDirective
  },
  components: {
    'cbpo-binning-options': BinningConfig
  },
  mixins: [WidgetBaseMixins, WidgetLoaderMixins],
  methods: {
    getDisplayName (name) {
      const column = this.columns.find(col => col.name === name)
      return column ? column.displayName || column.name : name
    },
    // modal state handler
    openModal({column, value, query}) {
      this.selectedColumn = null // reset value
      this.drillDownData = cloneDeep({ columnName: column.name, value })
      this.query = query
      this.$bvModal.show('drill-down-modal-' + this.config.modal.id)
    },
    // apply path to drilldown
    applyPath({column, value, query}) {
      this.query = query
      let level = this.breadcrumbs.length
      // push to breadcrumbs if current is empty
      if (!level) { // = 0
        this.breadcrumbs.push({
          columnName: column.name,
          displayName: this.getDisplayName(column.name),
          value: value,
          binConfig: this.binConfig
        })
      } else {
        // assign value to last one
        level--
        this.breadcrumbs[level].value = value
      }
      let path = this.config.path.settings[level]
      if (!path) return
      // push new breadcrumb
      this.selectedColumn = path.column
      this.breadcrumbs.push({
        columnName: path.column,
        displayName: this.getDisplayName(path.column),
        value: null,
        binConfig: path.binConfig
      })
      // apply query
      let cloneBreadcrumbs = cloneDeep(this.breadcrumbs)
      let cloneQuery = cloneDeep(this.query)
      let newQuery = this._buildMainQuery(cloneBreadcrumbs, cloneQuery)
      // emit query to outside
      this.$emit('input', { query: newQuery, columns: this.columns })
    },
    hideModal() {
      this.$bvModal.hide('drill-down-modal-' + this.config.modal.id)
    },
    // modal actions handler
    apply() {
      console.log(this.selectedColumn, 'selected column')
      if (!this.selectedColumn) throw new Error('Please select a column to apply drill down')
      // if breadcrumbs is empty, add default breadcrumb
      if (!this.breadcrumbs.length) {
        this.breadcrumbs.push({
          columnName: this.drillDownData.columnName,
          displayName: this.getDisplayName(this.drillDownData.columnName),
          value: null,
          binConfig: this.binConfig
        })
      }
      // add selected value into last breadcrumbs to build query
      this.breadcrumbs[this.breadcrumbs.length - 1].value = this.drillDownData.value
      // add current selected column into breadcrumbs with null value
      this.breadcrumbs.push({
        columnName: this.selectedColumn,
        displayName: this.getDisplayName(this.selectedColumn),
        value: null,
        binConfig: this.binConfig
      })

      // build query includes filter, bins and grouping and add emit to parent
      let cloneBreadcrumbs = cloneDeep(this.breadcrumbs)
      let cloneQuery = cloneDeep(this.query)
      let newQuery = this._buildMainQuery(cloneBreadcrumbs, cloneQuery)
      // emit query to outside
      this.$emit('input', { query: newQuery, columns: this.columns })
      this.hideModal()
    },
    cancel() {
      this.hideModal()
    },
    // create bin config base on current column, be called every time open modal or after columns is fetched
    createBinConfig() {
      this.isBinningApplicable = false
      if (this.selectedColumn) {
        let { type } = this.columns.find(column => column.name === this.selectedColumn)
        if (DataTypeUtil.isTemporal(type)) {
          this.isBinningApplicable = true
          this.columnType = FORMAT_DATA_TYPES.TEMPORAL
          this.binConfig = cloneDeep(DEFAULT_STATE_BIN.auto_temporal)
          return
        } else if (DataTypeUtil.isNumeric(type)) {
          this.isBinningApplicable = true
          this.columnType = FORMAT_DATA_TYPES.NUMERIC
          this.binConfig = cloneDeep(DEFAULT_STATE_BIN.auto_numeric)
          return
        }
      }
      this.columnType = null
      this.binConfig = cloneDeep(DEFAULT_STATE_BIN.null)
    },
    // onClick drilldown handler
    resetDrillDownToIndex(spliceIndex) {
      if (spliceIndex === this.breadcrumbs.length - 1) return
      this.breadcrumbs = this.breadcrumbs.filter((breadcrumb, index) => index <= spliceIndex)
      this.breadcrumbs[this.breadcrumbs.length - 1].value = null
      this.selectedColumn = this.breadcrumbs[this.breadcrumbs.length - 1].columnName
      if (this.breadcrumbs.length === 1) {
        this.breadcrumbs = []
      }
      let cloneBreadcrumbs = cloneDeep(this.breadcrumbs)
      let query = cloneDeep(this.query)
      let newQuery = this._buildMainQuery(cloneBreadcrumbs, query)
      this.$emit('input', { query: newQuery, columns: this.columns })
    },
    // default config
    widgetConfig(config) {
      // re-init config object with reactive system
      this.config = Object.assign(
        {},
        cloneDeep(makeDefaultDrillDownConfig(config))
      )
    },
    // build query on selected columns
    _buildMainQuery(breadcrumbs, query) {
      let bins = this._buildBinQuery(breadcrumbs, query.bins)
      let filter = this._buildFilterQuery(breadcrumbs, query.filter)
      let grouping = this._buildGroupingQuery(breadcrumbs, bins, query.grouping)
      let orders = this.autoOrder ? this._buildOrdersQuery(breadcrumbs, query.orders) : query.orders
      return { filter, grouping, orders, bins }
    },
    // build filter query
    _buildFilterQuery(breadcrumbs, baseFilter) {
      let filter = {
        type: SUPPORT_LOGIC.AND,
        conditions: []
      }
      // build filter
      filter.conditions = breadcrumbs
        .filter(breadcrumb => breadcrumb.value)
        .map(breadcrumb => {
          return isObject(breadcrumb.value)
            // filter for bin
            ? {
              type: SUPPORT_LOGIC.AND,
              conditions: [
                {
                  column: breadcrumb.columnName,
                  operator: breadcrumb.value.minOp,
                  value: breadcrumb.value.min
                },
                {
                  column: breadcrumb.columnName,
                  operator: breadcrumb.value.maxOp,
                  value: breadcrumb.value.max
                }
              ]
            }
            // filter for normal column
            : {
              column: breadcrumb.columnName,
              operator: SUPPORT_OPERATORS.$eq.value,
              value: breadcrumb.value
            }
        })
      if (isEmpty(baseFilter)) {
        return filter.conditions.length ? filter : {}
      } else {
        baseFilter.conditions.push(filter)
        return baseFilter.conditions.length ? baseFilter : {}
      }
    },
    // build grouping query
    _buildGroupingQuery(breadcrumbs, bins, baseGrouping) {
      let {columns: baseColumns, aggregations: baseAggregations} = baseGrouping
      if (isEmpty(baseColumns)) return { columns: [], aggregations: [] }
      if (isEmpty(breadcrumbs)) return { columns: baseColumns, aggregations: baseAggregations }

      // create bin value
      // build as normal
      let columns = breadcrumbs
        .map(breadcrumb => {
          let bin = bins.find(bin => bin.column.name === breadcrumb.columnName)
          if (!isEmpty(bin)) {
            baseAggregations
              .push({
                column: bin.column.name,
                alias: bin.alias,
                aggregation: 'count'
              })
          }
          // keep last breadcrumbs which value is null
          return breadcrumb.value ? null : {name: bin ? bin.alias : breadcrumb.columnName}
        })
        .filter(column => column)

      // remove new column in exited aggregations
      // find column to default aggregation
      let column = this.columns.find(column => column.name === baseColumns[0].name || createBinColumnAlias(column.name) === baseColumns[0].name)

      // remove old aggregation
      let index = findIndex(baseAggregations, aggr => aggr.column === column.name)
      if (index === -1) {
        let aggregationObj = getDefaultAggregationsOfDataType(column.type)
        baseAggregations.push({
          column: column.name,
          alias: column.name,
          aggregation: aggregationObj.aggregation
        })
      }

      // if current parent of drill down is chart, remove old columns from aggregations
      baseAggregations = baseAggregations.filter(aggr => aggr.column !== baseColumns[0].name)

      return {columns, aggregations: baseAggregations}
    },
    // build bin config
    _buildBinQuery(breadcrumbs, baseBins) {
      let { binConfig } = (breadcrumbs[breadcrumbs.length - 1] || {})
      if (!binConfig || binConfig.type === 'null') return baseBins
      let column = this.columns.find(column => column.name === this.selectedColumn)
      let binData = buildBinFromConfig(binConfig, column)
      return binData ? [...baseBins, binData] : baseBins
    },
    // build sort
    _buildOrdersQuery(breadcrumbs, orders) {
      let lastBreadCrumb = breadcrumbs[breadcrumbs.length - 1]
      if (lastBreadCrumb) {
        orders = []
        orders.push({ column: lastBreadCrumb.columnName, direction: 'asc' })
      }
      return orders
    }
  },
  computed: {
    getTemplateMessage() {
      return (columnName, value) => {
        let isBin = isObject(value)
        let { name, displayName, type } = this.columns.find(column => column.name === columnName || createBinColumnAlias(column.name) === columnName)
        return `<span class="cbpo-drilldown-column">@${displayName || name}</span> ${this.getDrillDownOperator(isBin, type, value)}`
      }
    },
    getDrillDownOperator() {
      return (isBin, type, value) => {
        if (value === null) return ``
        let formatObj = null
        // check data type and build format obj
        if (DataTypeUtil.isTemporal(type)) formatObj = { type: 'temporal', config: defaultsDeep({}, defaultTemporal) }
        if (DataTypeUtil.isNumeric(type)) formatObj = { type: 'numeric', config: { } }
        // format value
        let formatValue = isBin
          ? DataFormatManager.formatBin(value, formatObj, true)
          : DataFormatManager.format(value, formatObj, true)
        // return value
        return isBin
          ? `<span class="cbpo-drilldown-operator"> = </span> <span class="cbpo-drilldown-value">${formatValue}</span>`
          : `<span class="cbpo-drilldown-operator"> = <span> <span class="cbpo-drilldown-value">${formatValue}</span>`
      }
    },
    updatedColumnsState () {
      return CBPO.channelManager().getChannel().getColumnSvc().getColumns()
    },
    columns() {
      return CBPO.channelManager().getChannel(this.channelId).getColumnSvc().getColumns()
    },
    mappingColumns() {
      return cloneDeep(this.columns).filter(column => !cloneDeep(this.breadcrumbs).map(crumb => crumb.columnName).includes(column.name))
    }
  },
  watch: {
    selectedColumn(column) {
      this.createBinConfig()
    },
    updatedColumnsState: {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal && newVal.length) {
          newVal.forEach(col => this.updateColumn(col))
        }
      }
    }
  }
}
</script>

<style lang="scss">
@import "src/assets/css/core/color";
.cbpo-breadcrumbs-container {
  /deep/ .breadcrumb {
    border: none!important;
  }
  /deep/ .breadcrumb-item {
    a {
      display: inline-block;
      vertical-align: top;
    }
    &:last-child a {
    cursor: default!important;
    text-decoration: none;
    }
  }

  .label, .sub-label {
    display: block;
    max-width: 150px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    font-size: 13px;
  }
  .label {
    color: $primary;
  }
  .sub-label {
    color: $info;
  }
}

.cbpo-column-selection {
  /deep/ {
    .vs__search, .vs__selected, .vs__dropdown-menu {
      font-size: 13px;
    }
  }
}
</style>
