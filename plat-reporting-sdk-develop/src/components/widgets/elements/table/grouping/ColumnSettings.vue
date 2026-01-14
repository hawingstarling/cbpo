<template>
  <div v-if="config.id" class="cbpo-grouping-container">
    <b-modal dialog-class="cbpo-custom-modal" no-enforce-focus :id="modalId" size="md" no-close-on-backdrop @close="cancel()">
      <template v-slot:modal-title>
        Column Settings {{selected && selected.col ? selected.col.displayName : ''}}
      </template>
      <GroupingConfig v-if="selected && getGlobalControlOptions(config, OPTIONS.GROUPING)"
                      :globalGrouping="globalGrouping"
                      :selected.sync="selected"
                      :grouping.sync="grouping">
      </GroupingConfig>
      <ColumnFormatConfig
        v-if="selected && getGlobalControlOptions(config, OPTIONS.EDIT_COLUMN_FORMAT)"
        :selected.sync="selected"
      />
      <ColumnLabelConfig
        v-if="selected && getGlobalControlOptions(config, OPTIONS.EDIT_COLUMN_LABEL)"
        :selected.sync="selected"
        :columnsData="columns"
      />
      <BinningConfig v-if="getGlobalControlOptions(config, OPTIONS.EDIT_BIN) && binningAccept"
                     :config.sync="binObj"
                     :columnType="columnType"
      />
      <template v-slot:modal-footer>
        <button @click="apply()" class="cbpo-btn btn-primary mr-2" :disabled="!isDisableBtnApply">
          <span>Apply</span>
        </button>
        <button @click="cancel()" class="cbpo-btn">
          <span>Cancel</span>
        </button>
      </template>
    </b-modal>
  </div>
</template>

<script>
import GroupingConfig from './GroupingConfig'
import ColumnFormatConfig from './ColumnFormatConfig'
import { DEFAULT_STATE_BIN, makeColumnSettingsDefaultConfig } from './ColumnSettingsConfig'
import { DataTypeUtil, getDataTypeFromType } from '@/services/ds/data/DataTypes'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import ColumnSettingsMixins from './ColumnSettingsMixins'
import ColumnLabelConfig from './ColumnLabelConfig'
import BinningConfig from './BinningConfig'
import { cloneDeep, findIndex, assignIn, get } from 'lodash'
import { buildBinFromConfig, createBinColumnAlias, createBinType } from '@/utils/binUtils'
import { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
export default {
  name: 'ColumnSettings',
  components: {
    GroupingConfig,
    ColumnFormatConfig,
    ColumnLabelConfig,
    BinningConfig
  },
  mixins: [WidgetBaseMixins, ColumnSettingsMixins],
  computed: {
    isInvalid() {
      return !!this.columns.find((col, index) => (col.displayName === get(this, 'selected.col.displayName', '') && this.selected.colIndex !== index) || get(this, 'selected.col.displayName', '') === '')
    },
    modalId() {
      return `grouping-modal-${this.config.id}`
    },
    binningAccept() {
      const name = get(this.selected, 'col.name')
      if (!name) return false
      let column = this.columns.find(col => col.name === name)
      if (!column || !column.type) return false
      return DataTypeUtil.isNumeric(column.type) || DataTypeUtil.isTemporal(column.type)
    },
    isDisableBtnApply() {
      if (this.isInvalid) return false
      if (!this.getGlobalControlOptions(this.config, this.OPTIONS.EDIT_BIN)) return true
      if (this.binObj && this.binObj.binningType === 'uniform' && this.binObj.width <= 0) return false
      return !(this.binObj && this.binObj.binningType === 'auto' && this.binObj.expected <= 0)
    },
    globalGrouping () {
      return get(this.config, 'globalGrouping.config.value', false)
    }
  },
  data() {
    return {
      groupingObj: this.grouping,
      columnType: null,
      binObj: null,
      selected: null,
      defaultState: null,
      findIndex: findIndex,
      get: get
    }
  },
  props: {
    bins: Array,
    rows: Array,
    columns: Array,
    grouping: Object
  },
  methods: {
    widgetConfig (config) {
      this.$set(this.config, 'id', config.id)
      makeColumnSettingsDefaultConfig(config)
    },
    toggleModal (isOpen = false) {
      isOpen
        ? this.$bvModal.show(this.modalId)
        : this.$bvModal.hide(this.modalId)
    },
    show(selected) {
      this.selected = selected
      this.defaultState = cloneDeep(selected)
      if (this.binningAccept) {
        let column = this.columns.find(col => col.name === this.selected.col.name)
        this.columnType = DataTypeUtil.isTemporal(column.type) ? FORMAT_DATA_TYPES.TEMPORAL : FORMAT_DATA_TYPES.NUMERIC
        this.buildBinObj()
      } else {
        this.binObj = {}
        this.columnType = get(this.selected, 'col.cell.format.type')
      }
      this.toggleModal(true)
    },
    apply() {
      if (this.isDisableBtnApply) {
        let bins = this.buildNewBinningForColumns()
        let grouping = this.buildNewGroupForColumns(cloneDeep(this.groupingObj), cloneDeep(this.columns), cloneDeep(bins), cloneDeep(this.selected), this.binObj)
        this.$emit('input', {group: grouping, bins: bins, column: cloneDeep(this.selected)})
        this.selected = null
        this.toggleModal()
      }
    },
    cancel() {
      this.selected = null
      this.toggleModal()
    },
    buildBinObj() {
      let binObj = this.bins.find(bin => bin.column.name === this.selected.col.name)
      if (!binObj) {
        this.binObj = cloneDeep(DEFAULT_STATE_BIN['null'])
      } else {
        let binningType = binObj.binningType || 'null'
        this.binObj = cloneDeep(DEFAULT_STATE_BIN[`${binningType}_${this.columnType}`])
        this.binObj = {
          binningType: binObj.options.alg,
          nice: binObj.options.nice,
          expected: binObj.options.numOfBins
        }
        if (binObj.options.uniform) {
          this.binObj.unit = binObj.options.uniform.unit
          this.binObj.width = binObj.options.uniform.width
        }
      }
    },
    buildNewBinningForColumns() {
      let bins = cloneDeep(this.bins)
      if (!this.binningAccept) {
        return bins
      }
      let binIndex = findIndex(bins, bin => {
        return this.selected.col.name === bin.column.name
      })
      if (!this.binObj.binningType) {
        binIndex !== -1 && (bins.splice(binIndex, 1))
        return bins
      }
      let column = this.columns.find(column => column.name === this.selected.col.name)
      let bin = buildBinFromConfig(this.binObj, column)
      if (bin) {
        binIndex === -1 ? bins.push(bin) : bins[binIndex] = bin
      }
      return bins
    },
    buildNewGroupForColumns(newGrouping, columns, bins, current, currentBin) {
      columns = this.resetColumnsFromBins(columns, bins, current, currentBin)
      if (current.isGrouped) {
        let grouped = { name: current.col.name }
        if (this.binningAccept && currentBin.binningType) {
          grouped = {name: createBinColumnAlias(current.col.name)}
        }
        newGrouping.columns = [grouped]
      } else {
        newGrouping.columns = [...newGrouping.columns.filter(col => col.name !== current.col.name && col.name !== `${current.col.name}_bin`)]
      }
      if (newGrouping.columns.length) {
        newGrouping.aggregations = columns
          .reduce((aggres, col) => {
            // TODO Hot fix for bug in DD
            let {name, type = 'text'} = col
            if (!col.type) {
              console.error('type of column is undefined!!!')
            }
            let groupedColIndex = findIndex(newGrouping.columns, groupedCol => groupedCol.name === name)
            if (groupedColIndex === -1) {
              let defaultAggregation = getDataTypeFromType(type).defaultAggregation
              aggres = [...aggres, {
                column: name,
                aggregation: defaultAggregation.aggregation,
                alias: name
              }]
            }
            return aggres
          }, [])
        newGrouping.aggregations = bins
          .reduce((aggres, bin) => {
            if (!newGrouping.columns.find(col => col.name === bin.alias)) {
              let { column: {type}, alias } = bin
              let defaultAggregation = getDataTypeFromType(createBinType(type)).defaultAggregation
              aggres = [...aggres, {
                column: alias,
                aggregation: defaultAggregation.aggregation,
                alias: alias
              }]
            }
            return aggres
          }, newGrouping.aggregations)
      } else {
        newGrouping.aggregations = []
      }
      return newGrouping
    },
    resetColumnsFromBins(columns, bins, currentColumn, currentBin) {
      columns = columns.filter(column => !bins.find(bin => bin.alias === column.name))
      if (this.binningAccept && !currentBin.binningType) {
        columns = columns.filter(column => column.name !== `${currentColumn.col.name}_bin`)
      }
      return columns
    }
  },
  created() {
    this.groupingObj = assignIn({
      columns: [],
      aggregations: []
    }, this.grouping)
  },
  watch: {
    grouping: {
      deep: true,
      handler(val) {
        this.groupingObj = assignIn({
          columns: [],
          aggregations: []
        }, val)
      }
    }
  }
}
</script>
