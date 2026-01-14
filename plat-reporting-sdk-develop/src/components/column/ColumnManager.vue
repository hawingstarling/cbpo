<template>
  <div class="cbpo-column-manager">
    <div class="cbpo-column-header">
      <h4>Table</h4>
      <ReadableFilter v-if="dataFilter" :dataFilter="dataFilter" class="cbpo-readable-filter"></ReadableFilter>
      <div class="control-box">
        <QueryBuilder
          @filterChange="exportQuery($event)"
          style="width: 30px; display: inline"
          v-if="defaultTableConfig"
          :elements="getDefaultElements"
          :configObj.sync="queryBuilderConfig">
          <template v-slot:button="{ openModal }">
            <button @click="openModal" class="cbpo-btn btn-icon btn-primary mr-1" :disabled="!defaultTableConfig">
              <i class="fa fa-filter" aria-hidden="true"></i>
            </button>
          </template>
        </QueryBuilder>
        <button @click="openColumnModal(modalName)" class="cbpo-btn btn-icon btn-primary">
          <i class="fa fa-bars" aria-hidden="true"></i>
        </button>
        <!--<button v-b-toggle="config.id" class="control-button icon-only btn-minimize-maximize">
          <i :class="column.isMaximize ? 'fa-window-minimize' : 'fa-window-maximize'" class="fa" aria-hidden="true"></i>
        </button>-->
      </div>
    </div>
    <b-collapse :id="config.id" v-model="column.isMaximize" class="mt-2 max-height">
      <div class="cbpo-visualize-column w-100 h-100">
        <template v-if="dataSource">
          <template v-if="defaultTableConfig">
            <Table ref="tableView"
                   :channelId="'column_manager_id'"
                   :configObj="defaultTableConfig"
                   :wrapperId="wrapperId"
                   @dragColumnChange="changeDragData($event)" />
          </template>
        </template>
        <template v-if="isInvalidDataSource">
          <div class="text-center">
            <span>No valid data source defined.</span>
          </div>
        </template>
      </div>
    </b-collapse>
  </div>
</template>
<script>
import CBPO from '@/services/CBPO'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import Table from '@/components/widgets/elements/table/Table'
import QueryBuilder from '@/components/widgets/builder/BuilderFilter'
import ReadableFilter from '@/components/widgets/builder/ReadableFilter'
import { defaultTableConfig, defaultColumnConfig } from '@/components/widgets/elements/table/TableConfig'
import { cloneDeep, defaultsDeep, startCase, isEmpty } from 'lodash'
import { BUS_EVENT } from '@/services/eventBusType'
import temporalFormatConfig from '@/services/dataFormats/temporalFormatConfig'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'

export default {
  name: 'ColumnManager',
  props: {
    wrapperId: String,
    dataSource: String,
    element: Object,
    fields: Array,
    builderObj: Object
  },
  components: {
    Table,
    QueryBuilder,
    ReadableFilter
  },
  data() {
    return {
      ELEMENT,
      defaultTableConfig: null,
      elements: [],
      dm: {
        cols: []
      },
      column: {
        sortedData: {
          types: [],
          columns: []
        },
        isMaximize: true
      },
      modalName: 'column-modal',
      dataFilter: {},
      isGetDataSource: false,
      queryBuilderConfig: cloneDeep(this.builderObj)
    }
  },
  mixins: [WidgetBaseMixins],
  computed: {
    isInvalidDataSource () {
      return this.column.sortedData && isEmpty(this.column.sortedData.columns) && this.isGetDataSource
    },
    updatedColumnsState () {
      return CBPO.channelManager().getChannel().getColumnSvc().getColumns()
    },
    getDefaultElements() {
      return [{ type: ELEMENT.TABLE, config: this.defaultTableConfig }]
    }
  },
  methods: {
    exportQuery(filters) {
      this.dataFilter = filters.builder
      this.defaultTableConfig.filter = cloneDeep(filters.builder)
      window
        .CBPO
        .$bus
        .$emit(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.defaultTableConfig.id), cloneDeep(this.defaultTableConfig))
      this.$emit('exportQuery', filters)
    },
    widgetConfig (config) {
      // No override config
    },
    sortColumnsByTypes(items) {
      items.reduce((data, item) => {
        let index = data.types.indexOf(item.type)
        if (index !== -1) {
          data.columns[index] = [...data.columns[index], item]
        } else {
          let newType = [item]
          data.types = [...data.types, item.type]
          data.columns = [...data.columns, newType]
        }
        return data
      }, this.column.sortedData)
    },
    reset() {
      this.column.sortedData = {
        types: [],
        columns: []
      }
    },
    fetchColumns() {
      CBPO
        .dsManager()
        .getDataSource(this.dataSource)
        .columns()
        .then(columns => {
          let cols = this.mappingColumns(columns)
          this.dm.cols = cloneDeep(cols)
          this.sortColumnsByTypes(cloneDeep(cols))
          this.createDefaultTableConfig(cloneDeep(cols))
          this.$emit('update:fields', columns)
        })
        .catch(() => {
          this.isGetDataSource = true
        })
    },
    mappingColumns(columns) {
      return columns.map(column => {
        if (column.type && (column.type === 'date' || column.type === 'datetime' || column.type === 'time' || column.type === 'temporal')) {
          column.cell = {
            format: {
              type: 'temporal',
              config: defaultsDeep({}, temporalFormatConfig)
            }
          }
        }
        column = defaultsDeep(column, defaultColumnConfig)
        if (!column.displayName) {
          column.displayName = column.label || startCase([column.name])
        }
        return column
      })
    },
    createDefaultTableConfig(columns) {
      let config = cloneDeep(defaultTableConfig)
      config.widget = {title: {enabled: false, text: ''}}
      config.dataSource = this.dataSource
      config.columns = [...config.columns, ...columns]
      config.style = {'height': '100%'}
      config.header.draggable = true
      config.globalControlOptions = {
        globalGrouping: {
          enabled: true,
          config: {
            value: false
          }
        },
        aggregation: {
          enabled: true
        },
        grouping: {
          enabled: true
        },
        editColumn: {
          enabled: true
        },
        editColumnLabel: {
          enabled: true
        },
        editColumnFormat: {
          enabled: true
        },
        editBin: {
          enabled: true
        }
      }
      config.pagination = {
        type: 'lazy',
        limit: 30
      }
      config.detailView.enabled = true
      config.filter = this.queryBuilderConfig.query
      this.defaultTableConfig = config
    },
    openColumnModal (modalName) {
      CBPO.$bus.$emit(`open-${modalName}`)
    },
    changeDragData (data) {
      this.$emit('dragColumnChange', data)
    },
    updateColumn (data) {
      if (data) {
        // update cols for filter
        const findedCol = this.dm.cols.find(col => col.name === data.name)
        if (findedCol) findedCol.displayName = data.displayName || findedCol.displayName
        // update columns in tableConfig
        const findedTableColumn = this.defaultTableConfig.columns.find(col => col.name === data.name)
        if (findedTableColumn) findedTableColumn.displayName = data.displayName || findedTableColumn.displayName
      }
    }
  },
  async created() {
    this.fetchColumns()
  },
  watch: {
    element: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val) {
          let config = cloneDeep(val)
          config.config.columns = cloneDeep(this.dm.cols)
          this.elements = [config]
        }
      }
    },
    'dm.cols': function(val) {
      this.elements[0].config.columns = [...val]
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
<style lang="scss" scoped>
  @import "ColumnManager";
</style>
