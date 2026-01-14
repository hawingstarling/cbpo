import { cloneDeep, get, isEmpty, findIndex, defaultsDeep, uniqBy } from 'lodash'
import { defaultFormatConfig } from '@/components/widgets/elements/table/TableConfig'
import { AXIS, ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { DEFAULT_STATE_BIN } from '@/components/widgets/elements/table/grouping/ColumnSettingsConfig'
import { buildBinFromConfig, createBinColumnAlias } from '@/utils/binUtils'
import { DataTypeUtil, getDataTypeFromType } from '@/services/ds/data/DataTypes'
import { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import { TYPES } from '../widgets/elements/chart/ChartConfig'

export default {
  data() {
    return {
      columnData: null,
      elementData: null,
      binObj: null,
      columnType: null
    }
  },
  props: {
    column: Object,
    selectedType: Object,
    axis: String,
    series: Object,
    element: Object
  },
  methods: {
    /**
     * This method will be called to get current config
     * Set null to format config if format type is null or empty
     * **/
    getConfig() {
      let column = cloneDeep(this.columnData)
      if (this.elementData.type === ELEMENT.CROSSTAB_TABLE) {
        if (isEmpty(get(column, 'format.type', null))) {
          column.format = null
        }
      } else if (this.elementData.type === ELEMENT.CHART || this.elementData.type === ELEMENT.HTML_EDITOR) {
        if (isEmpty(get(column, 'format.type', null))) {
          column.format = null
        }
      } else if (this.elementData.type === ELEMENT.TABLE) {
        if (isEmpty(column.cell.aggrFormats)) {
          column.cell.aggrFormats = null
        } else {
          let newAggrFormats = Object
            .keys(column.cell.aggrFormats)
            .reduce((newObj, aggr) => {
              if (column.cell.aggrFormats[aggr]) {
                newObj[aggr] = column.cell.aggrFormats[aggr]
              }
              return newObj
            }, {})
          column.cell.aggrFormats = isEmpty(newAggrFormats) ? null : newAggrFormats
        }
        if (isEmpty(get(column, 'cell.format.type', null))) {
          column.cell.format = null
        }
      }
      let index = -1
      if (this.elementData.type === ELEMENT.CROSSTAB_TABLE) {
        switch (this.axis) {
          case AXIS.X: {
            index = findIndex(this.elementData.config.xColumns, (col) => col.name === column.name)
            this.elementData.config.xColumns[index] = column
            break
          }
          case AXIS.Y: {
            index = findIndex(this.elementData.config.yColumns, (col) => col.name === column.name)
            this.elementData.config.yColumns[index] = column
            break
          }
          case AXIS.Z: {
            index = findIndex(this.elementData.config.tColumns, (col) => col.name === column.name)
            this.elementData.config.tColumns[index] = column
            break
          }
        }
      } else {
        index = findIndex(this.elementData.config.columns, (col) => col.name === column.name)
        this.elementData.config.columns[index] = column
      }
      if (this.columnData.sortable) {
        let isEnabled = this.columnData.sortable.enabled
        let isBin = this.binObj && this.binObj.binningType
        let name = isBin ? createBinColumnAlias(this.column.name, this.setAliasBinnedCol) : this.columnData.name
        if (isEnabled) {
          this.elementData.config.sorting.forEach(col => {
            if (col.column === this.columnData.name && isBin) {
              col.column = name
            }
          })
        } else {
          this.elementData.config.sorting = this.elementData.config.sorting.filter(col => col.column !== name)
        }
      }
      return cloneDeep(this.elementData)
    },
    buildBinObj() {
      let binObj
      if (get(this.element, 'config.bins') && this.element.config.bins.length) {
        binObj = this.element.config.bins.find(bin => bin.alias === createBinColumnAlias(this.column.name, this.setAliasBinnedCol))
      }
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
      let bins = cloneDeep(this.element.config.bins)
      if (!this.binningAccept) {
        return bins
      }
      let binIndex = findIndex(bins, bin => bin.alias === createBinColumnAlias(this.column.name, this.setAliasBinnedCol))
      if (!this.binObj.binningType) {
        binIndex !== -1 && (bins.splice(binIndex, 1))
        return bins
      }
      let bin = buildBinFromConfig(this.binObj, this.column, this.setAliasBinnedCol)
      if (bin) {
        binIndex === -1 ? bins.push(bin) : bins[binIndex] = bin
      }
      return bins
    },
    buildNewGroupForColumns(newGrouping, columns, bins, current, currentBin) {
      if (this.isGroupedColumn(current.name) !== -1) {
        if (this.binningAccept && currentBin.binningType) {
          const grouped = { name: createBinColumnAlias(current.name) }
          // check column in group
          const colInGroup = newGrouping.columns.findIndex(col => col.name.includes(current.name))
          colInGroup !== -1 ? newGrouping.columns[colInGroup] = grouped : newGrouping.columns.push(grouped)
          let aggregationData = getDataTypeFromType(current.type).defaultAggregation
          const xAggr = {
            column: current.name,
            aggregation: aggregationData.aggregation,
            alias: current.name
          }
          newGrouping.aggregations = uniqBy([...newGrouping.aggregations, xAggr], 'column')
        } else {
          // remove column bin in group columns
          newGrouping.columns = [...newGrouping.columns.map(col => {
            if (col.name === `${current.name}_bin`) {
              col.name = current.name
            }
            return col
          })]
          newGrouping.aggregations = [...newGrouping.aggregations.filter(aggr => (aggr.column !== current.name && !newGrouping.columns.includes(aggr.column)))]
        }
      } else {
        newGrouping.aggregations = []
        newGrouping.columns = []
      }
      return newGrouping
    },
    apply () {
      let bins = this.buildNewBinningForColumns()
      let grouping = null
      if (this.elementData.type !== ELEMENT.CROSSTAB_TABLE) {
        grouping = this.buildNewGroupForColumns(cloneDeep(this.element.config.grouping), cloneDeep(this.element.config.columns), cloneDeep(bins), this.column, this.binObj)
      }
      this.$emit('updateBins', {bins, grouping})
    }
  },
  computed: {
    /**
     * get format config base on element type
     * **/
    getFormatConfig: {
      get() {
        if (!this.elementData || !this.columnData) {
          return {}
        }
        switch (this.elementData.type) {
          case ELEMENT.TABLE: {
            return this.columnData.cell.format
          }
          case ELEMENT.HTML_EDITOR:
          case ELEMENT.GAUGE:
          case ELEMENT.HEAT_MAP:
          case ELEMENT.CHART: {
            return this.columnData.format
          }
          case ELEMENT.CROSSTAB_TABLE: {
            return this.columnData.format
          }
        }
      },
      set(val) {
        switch (this.elementData.type) {
          case ELEMENT.TABLE: {
            this.columnData.cell.format = val
            break
          }
          case ELEMENT.CROSSTAB_TABLE: {
            this.columnData.format = val
            break
          }
          case ELEMENT.HTML_EDITOR:
          case ELEMENT.GAUGE:
          case ELEMENT.HEAT_MAP:
          case ELEMENT.CHART: {
            this.columnData.format = val
            break
          }
        }
      }
    },
    getAggregationFormatConfig: {
      get() {
        return this.columnData.cell.aggrFormats
      },
      set(val) {
        this.columnData.cell.aggrFormats = val
      }
    },
    binningAccept() {
      const type = get(this.column, 'type')
      return DataTypeUtil.isNumeric(type) || DataTypeUtil.isTemporal(type)
    },
    setAliasBinnedCol() {
      if (![ELEMENT.CHART, ELEMENT.GAUGE].includes(this.elementData.type)) return ''
      const { type } = this.series
      if (this.axis && this.axis === AXIS.Y && type !== TYPES.BUBBLE) {
        return get(this.series, 'id', '') + '_bin'
      } else {
        return ''
      }
    }
  },
  created() {
    if (this.binningAccept) {
      this.columnType = DataTypeUtil.isTemporal(this.column.type) ? FORMAT_DATA_TYPES.TEMPORAL : FORMAT_DATA_TYPES.NUMERIC
      this.buildBinObj()
    } else {
      this.columnType = get(this.column, 'format.type')
    }
  },
  watch: {
    element: {
      deep: true,
      immediate: true,
      handler: function(val) {
        this.elementData = cloneDeep(val)
      }
    },
    column: {
      deep: true,
      immediate: true,
      handler: function(val) {
        if (val) {
          if (this.element && this.element.type) {
            switch (this.element.type) {
              case ELEMENT.HTML_EDITOR:
              case ELEMENT.HEAT_MAP:
              case ELEMENT.CHART: {
                if (!val.format) {
                  val.format = {}
                }
                defaultsDeep(val.format, defaultFormatConfig)
                break
              }
              case ELEMENT.TABLE: {
                if (!val.cell.format) {
                  val.cell.format = {}
                }
                defaultsDeep(val.cell.format, defaultFormatConfig)
                break
              }
              case ELEMENT.CROSSTAB_TABLE: {
                if (!val.format) {
                  val.format = {}
                }
                defaultsDeep(val.format, defaultFormatConfig)
                break
              }
            }
          }
        }
        this.columnData = cloneDeep(val)
      }
    }
  }
}
