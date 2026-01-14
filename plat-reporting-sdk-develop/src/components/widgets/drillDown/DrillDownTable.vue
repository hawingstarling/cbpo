<template>
  <!-- Config ready will be enabled after widgetConfig function -->
  <div v-if="configReady" class="cbpo-drill-down-container">

    <!-- breadcrumbs -->
    <div class="cbpo-breadcrumbs-container">
      <slot name="breadcrumbs" :items="breadcrumbs" :resetDrillDown="resetDrillDownToIndex">
        <b-breadcrumb class="mb-2" v-if="breadcrumbs.length">
            <b-breadcrumb-item @click="resetDrillDownToIndex(-1)">
              <p class="mb-0 label text-left">
                <b class="cbpo-drilldown-main-column">{{ rootLabel }}</b>
              </p>
            </b-breadcrumb-item>
            <template v-for="(item, index) of breadcrumbs">
              <b-breadcrumb-item :id="'tooltip_target_' + index" @click="resetDrillDownToIndex(index)" :key="index">
                <p class="mb-0 label text-left">
                  <b class="cbpo-drilldown-main-column">{{ item.displayName }}</b>
                </p>
                <p class="mb-0 sub-label text-left" v-html="`<small>${getTemplateMessage(item.columnName, item.value)}</small>`">
                </p>
              </b-breadcrumb-item>
              <b-tooltip :key="'tooltip_' + index" :target="'tooltip_target_' + index" triggers="hover">
                <p class="mb-0 label text-left">
                  <b class="cbpo-drilldown-main-column">{{ item.displayName }}</b>
                </p>
                <p class="mb-0 sub-label text-left" v-html="`<small>${getTemplateMessage(item.columnName, item.value)}</small>`">
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
          You are going to drill down on <span v-html="getTemplateMessage(drillDownData.columnName, drillDownData.value)"></span>
        </p>
      </div>

      <!-- drill down option -->
      <div
        v-if="columns.length > 0"
        v-cbpo-loading="{ loading: loading }"
      >
        <b-form-group class="custom-checkbox-group" label="Next level column:">
          <b-form-checkbox-group
            v-model="selectedColumns"
            value-field="name"
            text-field="displayName"
            name="column"
            :options="columns"
          ></b-form-checkbox-group>
        </b-form-group>
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
        <button :disabled="!selectedColumns.length" @click="apply()" class="cbpo-btn btn-primary mr-2">
          <span>{{ config.modal.actions.applyButton.text }}</span>
        </button>
        <button class="cbpo-btn" @click="cancel()">
          <span>{{ config.modal.actions.cancelButton.text }}</span>
        </button>
      </template>
    </b-modal>
    <!-- end modal -->

    <!-- err modal -->
    <b-modal dialog-class="cbpo-custom-modal" id="drill-down-error-modal" size="md" title="Error" header-text-variant="danger">
      <div v-if="drillDownErr" class="cbpo-drill-down-detail">
        <p>You are already drill down on <span v-html="getTemplateMessage(drillDownErr.columnName, drillDownErr.value)"></span></p>
      </div>

      <template v-slot:modal-footer="{ ok, cancel }">
        <!-- Emulate built in modal footer ok and cancel button actions -->
        <button class="cbpo-btn" @click="cancel()">
          <span>{{ config.modal.actions.cancelButton.text }}</span>
        </button>
      </template>
    </b-modal>

  </div>
</template>

<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import loadingDirective from '@/directives/loadingDirective'
import BinningConfig from '@/components/widgets/elements/table/grouping/BinningConfig'
import cloneDeep from 'lodash/cloneDeep'
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
import { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'

export default {
  name: 'DrillDownTable',
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
      selectedColumns: [],
      aggregations: [],
      drillDownData: null,
      // bin component
      binConfig: null,
      columnType: null,
      // flag
      isModalOpen: false,
      isBinningApplicable: null,
      drillDownErr: null
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
      return this.columns.find(column => column.name === name).displayName
    },
    // modal state handler
    openModal({column, value, query}) {
      // check if drilldown already exist
      if (this.breadcrumbs.findIndex(crumb => crumb.columnName === column.name) !== -1) {
        this.$bvModal.show('drill-down-error-modal')
        this.drillDownErr = cloneDeep({columnName: column.name, value})
        return
      }
      this.selectedColumns = this.columns.map(column => column.name) // reset value
      this.drillDownData = cloneDeep({ columnName: column.name, value })
      this.query = query
      this.$bvModal.show('drill-down-modal-' + this.config.modal.id)
    },
    // apply path to drilldown
    applyPath({column, value, query}) {
      // check if drilldown alreadt exist
      if (this.breadcrumbs.findIndex(crumb => crumb.columnName === column.name) !== -1) {
        this.$bvModal.show('drill-down-error-modal')
        this.drillDownErr = cloneDeep({columnName: column.name, value})
        return
      }
      this.query = query
      this.selectedColumns = this.columns.map(column => column.name)
      // push to breadcrumbs if current is empty
      this.breadcrumbs.push({
        columnName: column.name,
        displayName: this.getDisplayName(column.name),
        value: value,
        columns: this.selectedColumns,
        binConfig: this.binConfig
      })
      // apply query
      let cloneBreadcrumbs = cloneDeep(this.breadcrumbs)
      let cloneQuery = cloneDeep(this.query)
      let newQuery = this._buildMainQuery(cloneBreadcrumbs, cloneQuery)
      // emit query to outside
      this.$emit('input', { query: newQuery, columns: this.selectedColumns })
    },
    hideModal() {
      this.$bvModal.hide('drill-down-modal-' + this.config.modal.id)
    },
    // modal actions handler
    apply() {
      if (!this.selectedColumns.length) throw new Error('Please select a column to apply drill down')

      this.breadcrumbs.push({
        columnName: this.drillDownData.columnName,
        displayName: this.getDisplayName(this.drillDownData.columnName),
        columns: this.selectedColumns,
        value: this.drillDownData.value,
        binConfig: this.binConfig
      })

      // build query includes filter, bins and grouping and add emit to parent
      let cloneBreadcrumbs = cloneDeep(this.breadcrumbs)
      let cloneQuery = cloneDeep(this.query)
      let newQuery = this._buildMainQuery(cloneBreadcrumbs, cloneQuery)

      // emit query to outside
      this.$emit('input', { query: newQuery, columns: this.selectedColumns })
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
      if (spliceIndex === -1) {
        this.breadcrumbs = []
      } else {
        this.breadcrumbs = this.breadcrumbs.filter((_br, i) => i <= spliceIndex)
      }

      let cloneBreadcrumbs = cloneDeep(this.breadcrumbs)
      let query = cloneDeep(this.query)
      let newQuery = this._buildMainQuery(cloneBreadcrumbs, query)
      this.$emit('input', {
        query: newQuery,
        columns: this.breadcrumbs.length
          ? this.breadcrumbs[this.breadcrumbs.length - 1].columns
          : this.columns.map(column => column.name)
      })
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
        .filter(breadcrumb => breadcrumb.value.base)
        .map(breadcrumb => {
          return isObject(breadcrumb.value.base)
            // filter for bin
            ? {
              type: SUPPORT_LOGIC.AND,
              conditions: [
                {
                  column: breadcrumb.columnName,
                  operator: breadcrumb.value.base.minOp,
                  value: breadcrumb.value.base.min
                },
                {
                  column: breadcrumb.columnName,
                  operator: breadcrumb.value.base.maxOp,
                  value: breadcrumb.value.base.max
                }
              ]
            }
            // filter for normal column
            : {
              column: breadcrumb.columnName,
              operator: SUPPORT_OPERATORS.$eq.value,
              value: breadcrumb.value.base
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
        orders.push({ column: lastBreadCrumb.columnName, direction: 'asc' })
      }
      return orders
    }
  },
  computed: {
    getTemplateMessage() {
      return (columnName, value) => {
        let { name, displayName } = this.columns.find(column => column.name === columnName || createBinColumnAlias(column.name) === columnName)
        return `<span class="cbpo-drilldown-column">@${displayName || name}</span> ${this.getDrillDownOperator(value)}`
      }
    },
    getDrillDownOperator() {
      return (value) => `<span class="cbpo-drilldown-operator"> = </span> <span class="cbpo-drilldown-value">${value.format}</span>`
    },
    columns () {
      return CBPO.channelManager().getChannel(this.channelId).getColumnSvc().getColumns()
    }
  },
  watch: {
    selectedColumn(column) {
      this.createBinConfig()
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

.custom-checkbox-group {
  & > div >div {
    display: flex;
    flex-wrap: wrap;
    .custom-control {
      width: calc(25% - 1rem);
    }
  }
}
</style>
