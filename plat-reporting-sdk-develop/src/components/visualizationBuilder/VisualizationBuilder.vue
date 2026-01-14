<template>
  <div class="visualization-builder" v-if="configReady">
    <grid-layout
      ref="gridLayout"
      class="w-100"
      :layout.sync="layout"
      :col-num="12"
      :row-height="10"
      :margin="[10, 10]"
      :is-draggable="true"
      :is-resizable="true"
      :vertical-compact="true"
      :use-css-transforms="true">
      <grid-item
        dragIgnoreFrom=".cell-box"
        :key="0"
        :x="layout[0].x"
        :y="layout[0].y"
        :w="layout[0].w"
        :h="layout[0].h"
        :i="layout[0].i">
        <div class="cbpo-card">
          <VisualizationAxis
            ref="visualizationAxis"
            :wrapperId="config.id"
            :element.sync="elementData"
            :dataSource="config.dataSource"
            :selectedElement="selected"
            :fields="fields"
            @forceGroupColumn="forceGroupColumn($event)"
            @createAggregationOnly="createAggregationOnly($event)"
            @forceUngroupColumn="forceUngroupColumn($event)"
            @modalTrigger="modalTrigger($event)"
            @mappingDefaultGauge="forceMappingDefaultGauge($event)">
          </VisualizationAxis>
        </div>
      </grid-item>
      <grid-item
        dragIgnoreFrom=".cbpo-visualization-content"
        :key="1"
        :x="layout[1].x"
        :y="layout[1].y"
        :w="layout[1].w"
        :h="layout[1].h"
        :i="layout[1].i"
        @resized="resizeEvent"
        @resize="resizeEvent">
        <div class="cbpo-card">
          <Visualization
            ref="visualizationWidget"
            :widgetConfig.sync="widgetData"
            :selected="selected"
            @modalTrigger="modalTrigger($event)"
            @widgetConfigChange="widgetConfigChange($event)"
            @elementConfigChange="elementConfigChange($event)"
            @resetAllConfig="resetAllConfig"
          >
          </Visualization>
        </div>
      </grid-item>
      <grid-item
        :key="2"
        :x="layout[2].x"
        :y="layout[2].y"
        :w="layout[2].w"
        :h="layout[2].h"
        :i="layout[2].i">
        <div class="cbpo-card">
          <b-card no-body>
            <b-tabs pills card vertical end>
              <b-tab active>
                <template v-slot:title>
                  <i class="fa fa-file-o" aria-hidden="true"></i>
                </template>
                <VisualizationElement
                  ref="elementVisualize"
                  :dataSource="config.dataSource"
                  :selectedElement.sync="selected"
                  :element.sync="elementData"
                  @modalTrigger="modalTrigger($event)"
                  @createGroupingFromConfig="createGroupingFromConfig()"
                  @createFirstSeries="buildSelectedType()"
                  @update:element="updateSelection($event)">
                </VisualizationElement>
              </b-tab>
              <b-tab>
                <template v-slot:title>
                  <i class="fa fa-folder-o" aria-hidden="true"></i>
                </template>
                <div class="p-1 cbpo-preset">
                  <slot name="preset-header"></slot>
                  <PresetElement
                    :templates="config.templates"
                    :templateData="presetData.template"
                    @input="selectedTemplate($event)">
                  </PresetElement>
                  <slot name="preset-footer"></slot>
                </div>
              </b-tab>
            </b-tabs>
          </b-card>
        </div>
      </grid-item>
      <grid-item
        dragIgnoreFrom=".cell-box, .cbpo-column-content, .grid-item-ignore-drag-handler"
        dragAllowFrom=".cbpo-column-header"
        :key="3"
        :x="layout[3].x"
        :y="layout[3].y"
        :w="layout[3].w"
        :h="layout[3].h"
        :i="layout[3].i"
      >
        <div class="cbpo-card">
          <ColumnManager
            ref="visualizeColumn"
            :element="elementData"
            :dataSource="config.dataSource"
            :wrapperId="config.id"
            :fields.sync="fields"
            @modalTrigger="modalTrigger($event)"
            @dragColumnChange="changeDragData($event)"
            @exportQuery="applyQuery($event)"
            :builderObj="config.widgetConfig.filter.base.config">
          </ColumnManager>
        </div>
      </grid-item>
    </grid-layout>

    <!--X AXIS COLUMN MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="md" :ref="modalId('xAxisColumnSetting')" :id="modalId('xAxisColumnSetting')" title="Column Axis Settings">
      <XAxisColumnSettings :ref="modalContent('xAxisColumnSetting')"
                           @updateBins="updateBinConfig($event)"
                           :selectedType="selected"
                           :element="elementData"
                           :axis="AXIS.X"
                           :column="selectedColumn ? selectedColumn.column: null" :fields="fields"
                           :series="selectedColumn ? selectedColumn.series: null"/>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button @click="exportConfig('xAxisColumnSetting')" class="cbpo-btn btn-primary mr-2">
            Save
          </button>
          <button @click="modalTrigger({type: 'xAxisColumnSetting', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--Y AXIS COLUMN MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="md" :ref="modalId('yAxisColumnSetting')" :id="modalId('yAxisColumnSetting')" title="Column Axis Settings">
      <YAxisColumnSettings :ref="modalContent('yAxisColumnSetting')"
                           @updateBins="updateBinConfig($event)"
                           :selectedType="selected"
                           :element="elementData"
                           :axis="AXIS.Y"
                           :column="selectedColumn ? selectedColumn.column: null"
                           :series="selectedColumn ? selectedColumn.series: null"/>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button @click="exportConfig('yAxisColumnSetting')" class="cbpo-btn btn-primary mr-2">
            Save
          </button>
          <button @click="modalTrigger({type: 'yAxisColumnSetting', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--Z AXIS COLUMN MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="md" :ref="modalId('zAxisColumnSetting')" :id="modalId('zAxisColumnSetting')" title="Column Axis Settings">
      <ZAxisColumnSettings :ref="modalContent('zAxisColumnSetting')"
                           @updateBins="updateBinConfig($event)"
                           :selectedType="selected"
                           :element="elementData"
                           :axis="AXIS.Z"
                           :column="selectedColumn ? selectedColumn.column: null"
                           :series="selectedColumn ? selectedColumn.series: null"/>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button @click="exportConfig('zAxisColumnSetting')" class="cbpo-btn btn-primary mr-2">
            Save
          </button>
          <button @click="modalTrigger({type: 'zAxisColumnSetting', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--X AXIS MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="md" :ref="modalId('xAxisSetting')" :id="modalId('xAxisSetting')" :title="`X Axis Settings`">
      <XAxisSettings :ref="modalContent('xAxisSetting')" :element="elementData" :selectedElement="selected" :config="selectedColumn"/>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button @click="exportConfig('xAxisSetting')" class="cbpo-btn btn-primary mr-2">
            Save
          </button>
          <button @click="modalTrigger({type: 'xAxisSetting', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--Y AXIS MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="md" :ref="modalId('yAxisSetting')" :id="modalId('yAxisSetting')" :title="`Y Axis ${getAxisName} Settings`">
      <YAxisSettings :ref="modalContent('yAxisSetting')" :element="elementData" :selectedElement="selected" :config="selectedColumn"/>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button @click="exportConfig('yAxisSetting')" class="cbpo-btn btn-primary mr-2">
            Save
          </button>
          <button @click="modalTrigger({type: 'yAxisSetting', isShow: false})"  class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--COLUMN MAPPING MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="lg" :ref="modalId('columnMapping')" :id="modalId('columnMapping')" :title="`Preset Column Mapping`">
      <ColumnMapping
      :ref="modalContent('columnMapping')"
      :presetConfig="presetData.config"
      :targetColumns="fields"
      :isApply.sync="presetData.isApply"/>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button :disabled="!presetData.isApply" @click="exportConfig('columnMapping')" class="cbpo-btn btn-primary mr-2">
            Apply
          </button>
          <button @click="modalTrigger({type: 'columnMapping', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--COLUMN MODAL-->
    <ColumnManagerModal
      ref="columnManagerModal"
      v-if="fields"
      :wrapperId="config.id"
      :modalName="modalName"
      :columns="fields"
      @dragColumnChange="changeDragData($event)"
    >
    </ColumnManagerModal>
  </div>
</template>
<script>
import Visualization from '@/components/visualizationBuilder/visualization/Visualization'
import VisualizationAxis from '@/components/visualizationBuilder/axis/AxisContainer'
import ColumnManager from '@/components/column/ColumnManager'
import VisualizationElement from '@/components/visualizationBuilder/element/ElementTypeSelectionContainer'
import PresetElement from '@/components/visualizationBuilder/preset/PresetElement'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import XAxisColumnSettings from '@/components/visualizationBuilder/modal/xAxisColumnSettings'
import YAxisColumnSettings from '@/components/visualizationBuilder/modal/yAxisColumnSettings'
import ZAxisColumnSettings from '@/components/visualizationBuilder/modal/zAxisColumnSettings'
import XAxisSettings from '@/components/visualizationBuilder/modal/xAxisSettings'
import YAxisSettings from '@/components/visualizationBuilder/modal/yAxisSettings'
import ColumnMapping from '@/components/visualizationBuilder/modal/ColumnMapping'
import VueGridLayout from 'vue-grid-layout'
import { makeDefaultVisualizationWrapperConfig } from '@/components/visualizationBuilder/VisualizationBuilderConfig'
import { ELEMENT, AXIS } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { debounce, get, findIndex, forEach, cloneDeep, isEmpty } from 'lodash'
import { BUS_EVENT } from '@/services/eventBusType'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import CBPO from '@/services/CBPO'
import {
  handleGrouping,
  handleGroupingBubble,
  handleUngrouping,
  buildAxisChart,
  buildAxisTable,
  buildAxisGause,
  buildAxisHeatMap,
  removeChartColumn,
  createNewColumnChart,
  updateTableColumn, GROUPING_TYPE, buildAxisCrosstabTable,
  updateGroupingTable,
  mappingFilter,
  mappingControlFilter
} from '@/utils/visualizationUtil'
import ColumnManagerModal from '@/components/column/ColumnManagerModal'
import { makeDefaultBulletGaugeConfig, makeDefaultSolidGaugeConfig } from '@/components/widgets/elements/gauge/GaugeConfig'
import { getDefaultAggregationsOfDataType, DataTypeUtil, getAggregationObjFromAggregationName } from '@/services/ds/data/DataTypes'
import { DEFAULT_WIDGET_CONFIG } from '@/components/widgets/WidgetConfig'
import { buildBinFromConfig, createBinColumnAlias, createBinColumnAliasInAxis } from '@/utils/binUtils'
import { DEFAULT_STATE_BIN } from '@/components/widgets/elements/table/grouping/ColumnSettingsConfig'

export default {
  name: 'VisualizationWrapper',
  components: {
    Visualization,
    VisualizationAxis,
    VisualizationElement,
    ColumnManager,
    XAxisColumnSettings,
    YAxisColumnSettings,
    ZAxisColumnSettings,
    XAxisSettings,
    YAxisSettings,
    ColumnMapping,
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem,
    PresetElement,
    ColumnManagerModal
  },
  computed: {
    modalId() {
      return type => `${this.config.id}_modal_visualization_${type}`
    },
    modalContent() {
      return type => `${this.config.id}_modal_content_${type}`
    },
    getAxisName() {
      return get(this.selectedColumn, 'index', 0) + 1
    },
    updatedColumnsState () {
      return CBPO.channelManager().getChannel().getColumnSvc().getColumns()
    },
    editedTitle() {
      return get(this.elementData, 'config.widget.title.edited', false) ||
        get(this.config, 'widgetConfig.widget.title.edited', false)
    }
  },
  mixins: [WidgetBaseMixins],
  props: {
    outsideConfig: {
      type: Object,
      default: () => {
        return {}
      }
    }
  },
  data() {
    return {
      ELEMENT,
      AXIS,
      // This will be updated by Column Manager component
      fields: [],
      selectedColumn: null,
      widgetData: null,
      elementData: null,
      presetData: {
        template: null,
        isApply: false,
        config: null
      },
      selected: {
        elementType: null,
        chartType: null
      },
      filterAlignment: null,
      // TODO Make a config for layout later
      layout: [
        {'x': 0, 'y': 0, 'w': 2, 'h': 24, i: 0},
        {'x': 2, 'y': 0, 'w': 8, 'h': 24, i: 1},
        {'x': 10, 'y': 0, 'w': 2, 'h': 24, i: 2},
        {'x': 2, 'y': 1, 'w': 16, 'h': 16, i: 3}
      ],
      modalName: 'column-modal'
    }
  },
  methods: {
    resizeEvent(i, h, w, hpx, wpx) {
      const { id } = this.elementData.config
      debounce(() => {
        CBPO.$bus.$emit(BUS_EVENT.ELEMENT_RESIZE_EVENT(id), {i, h, w, hpx, wpx, colSize: this.$refs.gridLayout.width / 12})
      }, 500)()
    },
    widgetConfig (config) {
      this.config = makeDefaultVisualizationWrapperConfig(config)
      this.buildSelectedType(this.config)
    },
    resetAllConfig() {
      this.$refs.elementVisualize.createNewElementConfig(ELEMENT.CHART, TYPES.PIE, false)
    },
    /**
     * Build this.selected base on current config
     * Will be call inside widgetConfig method, after extended default config or after $event create series emit from ElementTypeSelectionContainer
     * **/
    buildSelectedType() {
      if (this.config.widgetConfig.elements[0]) {
        let { type } = this.config.widgetConfig.elements[0]
        if (type === ELEMENT.CHART) {
          let chartType = this.config.widgetConfig.elements[0].config.charts[0].series[0].type
          let hasSameType = this.config.widgetConfig.elements[0].config.charts[0].series
            .every(item => item.type === chartType)
          this.selected.chartType = hasSameType ? chartType : TYPES.PARETO
        }
        this.selected.elementType = type
      }
    },
    selectedTemplate(config) {
      // reset base filter
      if (get(config, 'filter.base.config.query.conditions')) {
        config.filter.base.config.query.conditions = []
      }
      if (get(config, 'elements[0].config.filter.conditions')) {
        config.elements[0].config.filter.conditions = []
      }

      let type = get(config, 'elements[0].type')
      let isMatchedColumns = false
      this.presetData.template = config
      config.elements[0].config.dataSource = this.config.dataSource
      switch (type) {
        case ELEMENT.TABLE:
        case ELEMENT.CHART:
        case ELEMENT.GAUGE: {
          isMatchedColumns = get(config, 'elements[0].config.columns', []).every(e => {
            return findIndex(this.fields, { name: e.name }) >= 0
          })
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          let isMatchXColumns = get(config, 'elements[0].config.xColumns', []).every(e => {
            return findIndex(this.fields, { name: e.name }) >= 0
          })
          let isMatchYColumns = get(config, 'elements[0].config.yColumns', []).every(e => {
            return findIndex(this.fields, { name: e.name }) >= 0
          })
          let isMatchTColumns = get(config, 'elements[0].config.tColumns', []).every(e => {
            return findIndex(this.fields, { name: e.name }) >= 0
          })
          isMatchedColumns = isMatchXColumns && isMatchTColumns && isMatchYColumns
          break
        }
      }
      this.presetData.config = this.buildPresetConfig(config)
      if (isMatchedColumns) {
        this.presetData.isApply = false
        this.selected.elementType = type
        if (type === ELEMENT.CHART || type === ELEMENT.GAUGE) {
          const series = get(config, 'elements[0].config.charts[0].series', [])
          const isLine = series.some(e => e.type === TYPES.LINE)
          const isBar = series.some(e => e.type === TYPES.BAR)
          if (isLine && isBar) {
            this.selected.chartType = TYPES.PARETO
          } else if (series.length && series[0].type) {
            this.selected.chartType = series[0].type
          }
        }
        // update selection menu
        this.updateSelectionMenu(config)
        this.widgetConfigChange(config)
      } else {
        this.modalTrigger({type: 'columnMapping', isShow: true})
      }
    },
    buildPresetConfig(config) {
      const elementConfig = config.elements[0]
      let presetConfig = { elementConfig, filter: config.filter }
      switch (elementConfig.type) {
        case ELEMENT.TABLE:
          presetConfig.zones = buildAxisTable(elementConfig)
          break
        case ELEMENT.CHART:
          presetConfig.zones = buildAxisChart(elementConfig)
          break
        case ELEMENT.CROSSTAB_TABLE:
          presetConfig.zones = buildAxisCrosstabTable(elementConfig)
          break
        case ELEMENT.GAUGE:
          presetConfig.zones = buildAxisGause(elementConfig)
          break
        case ELEMENT.HEAT_MAP:
          presetConfig.zones = buildAxisHeatMap(elementConfig)
          break
        default:
          break
      }
      return presetConfig
    },
    mappingPresetToElement(presetConfig) {
      let { elementConfig, filter, zones } = presetConfig
      switch (elementConfig.type) {
        case ELEMENT.TABLE:
          this.mappingColumnTable(elementConfig, filter, zones)
          break
        case ELEMENT.CHART:
        case ELEMENT.HEAT_MAP:
        case ELEMENT.GAUGE:
          this.mappingColumnChart(elementConfig, filter, zones)
          break
        case ELEMENT.CROSSTAB_TABLE:
          this.mappingColumnCrosstabTable(elementConfig, filter, zones)
          break
      }
      return { elementConfig, filter }
    },
    binningAccept(column) {
      const type = get(column, 'type')
      return DataTypeUtil.isNumeric(type) || DataTypeUtil.isTemporal(type)
    },
    mappingColumnChart(elementConfig, filter, zones) {
      let getColumn = (axis, index) => {
        let column = elementConfig.config.columns
          .find(column => column.name === elementConfig.config.charts[0].series[index].data[axis])
        return column || {}
      }
      let checkBinnedColumn = (newColumn, axis, index) => {
        let { sorting = [], bins = [] } = elementConfig.config
        const sortingIndex = sorting.findIndex(st => st.column.includes(elementConfig.config.columns[index].name))
        const seriesItem = get(elementConfig, `config.charts[0].series[${index}]`, {})
        const binIndex = bins
          .findIndex(bin => bin.alias === createBinColumnAliasInAxis(seriesItem, { name: seriesItem.data[axis] }, axis))
        if (binIndex !== -1) {
          if (this.binningAccept(newColumn)) {
            const binnedCol = bins[binIndex]
            const newBinnedCol = {
              alias: createBinColumnAliasInAxis(seriesItem, { name: newColumn.name }, axis),
              options: {...binnedCol.options},
              column: { name: newColumn.name, type: newColumn.type }
            }
            bins.push(newBinnedCol)
            if (sortingIndex !== -1) sorting[sortingIndex].column = createBinColumnAlias(newColumn.name)
          } else {
            if (sortingIndex !== -1) sorting[sortingIndex].column = newColumn.name
          }
          bins.splice(binIndex, 1)
        } else {
          if (sortingIndex !== -1) sorting[sortingIndex].column = newColumn.name
          // auto bin if new column is Temporal and do not exist on bins and current axis is x axis
          if (DataTypeUtil.isTemporal(newColumn.type) && axis === AXIS.X) {
            const binConfig = cloneDeep(DEFAULT_STATE_BIN.auto_temporal)
            const newAutoBin = buildBinFromConfig(binConfig, newColumn)
            bins.push(newAutoBin)
          }
        }
      }
      forEach(zones, (item, axis) => {
        if (item.length > 0) {
          forEach(item, (column, index) => {
            let oldColumn = getColumn(axis, index)
            if (column.name !== oldColumn.name) {
              // mapping filter config
              this.mappingFilterConfig(filter, oldColumn, column)
              // update column in elementConfig
              checkBinnedColumn(column, axis, index)
              removeChartColumn(elementConfig, axis, index)
              createNewColumnChart(elementConfig, column, axis, index)
            }
          })
        }
      })
      elementConfig.config.charts && forEach(elementConfig.config.charts[0].series, (item) => {
        let aggregation = (elementConfig.config.grouping.aggregations || []).find(aggr => aggr.column === item.data.y)
        if (aggregation) {
          let aggregaionObj = getAggregationObjFromAggregationName(aggregation.aggregation)
          let column = elementConfig.config.columns.find(column => column.name === item.data.y)
          item.name = `${column.label || column.displayName || column.name} (${aggregaionObj.label})`
        }
      })
    },
    mappingColumnTable(elementConfig, filter, zones) {
      let groupingColumns = []
      let checkBinnedColumn = (newColumn, oldColumn) => {
        let { sorting = [], bins = [] } = elementConfig.config
        const sortingIndex = sorting
          .findIndex(st => st.column.includes(oldColumn.name))
        const binIndex = bins
          .findIndex(bin => bin.alias === createBinColumnAlias(oldColumn.name))
        if (binIndex !== -1) {
          if (this.binningAccept(newColumn)) {
            const binnedCol = bins[binIndex]
            const newBinnedCol = {
              alias: createBinColumnAlias(newColumn.name),
              options: {...binnedCol.options},
              column: { name: newColumn.name, type: newColumn.type }
            }
            bins.push(newBinnedCol)
            if (sortingIndex !== -1) sorting[sortingIndex].column = createBinColumnAlias(newColumn.name)
          } else {
            if (sortingIndex !== -1) sorting[sortingIndex].column = newColumn.name
          }
          bins.splice(binIndex, 1)
        } else {
          if (sortingIndex !== -1) sorting[sortingIndex].column = newColumn.name
        }
      }
      let checkGroupedColumn = (newColumn, oldColumn) => {
        const groupedIndex = elementConfig.config.grouping.columns.findIndex(col => col.name.includes(oldColumn.name))
        if (groupedIndex !== -1) groupingColumns.push(newColumn)
      }
      forEach(zones.x, (column, index) => {
        let { columns = [] } = elementConfig.config
        if (column.name !== columns[index].name) {
          // mapping filter config
          this.mappingFilterConfig(filter, columns[index], column)
          // update columns in elementConfig
          checkBinnedColumn(column, columns[index])
          checkGroupedColumn(column, columns[index])
          updateTableColumn(elementConfig, column, index)
        }
      })
      // check group and bin
      updateGroupingTable(elementConfig, [...groupingColumns])
    },
    mappingColumnCrosstabTable(elementConfig, filter, zones) {
      let handleCallback = (name) => (column, index) => {
        // mapping filter config
        this.mappingFilterConfig(filter, elementConfig.config[name][index], column)
        let { sorting = [], bins = [] } = elementConfig.config
        const sortingIndex = sorting.findIndex(st => st.column.includes(elementConfig.config[name][index].name))
        let binIndex = findIndex(
          bins,
          bin => bin.column.name === elementConfig.config[name][index].name
        )
        if (binIndex !== -1) {
          if (elementConfig.config[name][index].type === column.type) {
            bins[binIndex].column.name = column.name
            bins[binIndex].alias = createBinColumnAlias(column.name)
            if (sortingIndex !== -1) sorting[sortingIndex].column = createBinColumnAlias(column.name)
          } else {
            bins.splice(binIndex, 1)
            if (sortingIndex !== -1) sorting[sortingIndex].column = column.name
          }
        } else {
          if (sortingIndex !== -1) sorting[sortingIndex].column = column.name
        }
        if (elementConfig.config[name][index].type !== column.type) {
          elementConfig.config[name][index].format = null
        }
        elementConfig.config[name][index].name = column.name
        elementConfig.config[name][index].displayName = column.displayName
        elementConfig.config[name][index].type = column.type
      }
      forEach(zones.x, handleCallback('xColumns'))
      forEach(zones.y, handleCallback('yColumns'))
      forEach(zones.z, handleCallback('tColumns'))
    },
    mappingFilterConfig (filter, oldColumn, newColumn) {
      filter.builder.config.query = mappingFilter(filter.builder.config.query, oldColumn, newColumn)
      // filter.form.config.query = mappingFilter(filter.form.config.query, oldColumn, newColumn)
      filter.form.config.controls = mappingControlFilter(filter.form.config.controls, oldColumn, newColumn, this.config.dataSource)
    },
    updateSelectionMenu (config) {
      if (isEmpty(config)) return
      const selectionConfig = get(config, 'menu.config.selection', {})
      const currentSelectionConfig = get(this.config, 'widgetConfig.menu.config.selection', {})
      selectionConfig.dsUrl = currentSelectionConfig.dsUrl || ''
    },
    updateSelection(element) {
      this.$set(this.config.widgetConfig.elements, 0, element)
      this.$set(this.config.widgetConfig, 'filter', DEFAULT_WIDGET_CONFIG.filter)
      this.widgetData = {...this.config.widgetConfig}
    },
    applyQuery(filter) {
      this.$refs.visualizationWidget.changeGlobalFilter(filter)
    },
    changeDragData(dragData) {
      this.$refs.visualizationAxis.dragDataChange(dragData)
    },
    modalTrigger({type, isShow, data}) {
      if (isShow) {
        // handle some special case
        this.selectedColumn = data
        // show modal
        this.$bvModal.show(this.modalId(type))
      } else {
        // remove flag data
        this.selectedColumn = null
        // hide modal
        this.$bvModal.hide(this.modalId(type))
      }
    },
    /**
     * Change widget config
     * Will be called when widget setting apply
     * @param {Object} config - widget config
     * **/
    widgetConfigChange(config) {
      this.config.widgetConfig = cloneDeep(config)
      this.$emit('update:outsideConfig', this.config)
    },
    elementConfigChange(config) {
      this.$set(this.config.widgetConfig.elements[0], 'config', config.config)
      this.widgetData = {...this.config.widgetConfig}
    },
    exportConfig(type) {
      switch (type) {
        case 'xAxisColumnSetting': {
          let config = this.$refs[this.modalContent(type)].getConfig()
          if (this.selected.elementType !== ELEMENT.CROSSTAB_TABLE) {
            this.$set(this.config.widgetConfig.elements[0].config, 'grouping', config.config.grouping)
          }
          this.$set(this.config.widgetConfig.elements, 0, config)
          this.$refs[this.modalContent(type)].apply()
          this.modalTrigger({type: type, isShow: false})
          // Change series name if aggregation, displayName change
          // setTimeout wait for this.$set done setting new value
          this.$nextTick(() => {
            if (this.selected.elementType === ELEMENT.CHART) {
              this.$refs.visualizationAxis.mappingChartName()
            }
          })
          break
        }
        case 'zAxisColumnSetting': {
          let config = this.$refs[this.modalContent(type)].getConfig()
          this.$set(this.config.widgetConfig.elements, 0, config)
          this.$refs[this.modalContent(type)].apply()
          this.modalTrigger({type: type, isShow: false})
          // Change series name if aggregation, displayName change
          // setTimeout wait for this.$set done setting new value
          this.$nextTick(() => {
            if (this.selected.elementType === ELEMENT.CHART) {
              this.$refs.visualizationAxis.mappingChartName()
            }
          })
          break
        }
        case 'yAxisColumnSetting': {
          const selectedColumn = cloneDeep(this.selectedColumn)
          let config = this.$refs[this.modalContent(type)].getConfig()
          this.$set(this.config.widgetConfig.elements, 0, config)
          if (this.selected.elementType === ELEMENT.GAUGE) {
            this.mappingDefaultGauge(config, this.selectedColumn)
          }
          this.$refs[this.modalContent(type)].apply()
          this.modalTrigger({type: type, isShow: false})
          // Change series name if aggregation, displayName change
          // setTimeout wait for this.$set done setting new value
          this.$nextTick(() => {
            if (this.selected.elementType === ELEMENT.CHART || this.selected.elementType === ELEMENT.GAUGE) {
              this.$refs.visualizationAxis.mappingChartName()
            }
            // update aggregations on the column pill in AxisContainer
            if (selectedColumn && (this.selected.elementType === ELEMENT.CHART || this.selected.elementType === ELEMENT.GAUGE)) {
              this.$refs.visualizationAxis.getAggregationFromGrouping(selectedColumn.series.id, selectedColumn.column.name)
            }
          })
          break
        }
        case 'xAxisSetting': {
          let {index, item, element} = this.$refs[this.modalContent(type)].getConfig()
          this.$set(this.config.widgetConfig.elements[0].config.charts[0].series, index, item)
          this.$set(this.config.widgetConfig.elements, 0, element)
          this.modalTrigger({type: type, isShow: false})
          break
        }
        case 'yAxisSetting': {
          let {index, item, element, axisIndex} = this.$refs[this.modalContent(type)].getConfig()
          this.$set(this.config.widgetConfig.elements[0].config.charts[0].series, index, item)
          this.$set(this.config.widgetConfig.elements[0].config.charts[0].axis.y, axisIndex, element.config.charts[0].axis.y[axisIndex])
          this.$set(this.config.widgetConfig.elements, 0, element)
          this.modalTrigger({type: type, isShow: false})
          break
        }
        case 'columnMapping': {
          this.modalTrigger({type: type, isShow: false})
          let config = this.$refs[this.modalContent(type)].getConfig()
          let { elementConfig, filter } = this.mappingPresetToElement(config)
          this.$set(this.presetData.template.elements, '0', elementConfig)
          this.$set(this.presetData.template, 'filter', filter)
          this.selected = this.getSelected(elementConfig)
          // update selection menu
          this.updateSelectionMenu(this.presetData.template)
          this.widgetConfigChange(this.presetData.template)
          break
        }
      }
    },
    getSelected(element) {
      if (!element) return null
      let chartType = null
      let config = element.config
      let type = element.type
      if (type === ELEMENT.CHART) {
        let series = config.charts[0].series
        if (series.every(e => e.type === TYPES.PIE)) {
          chartType = TYPES.PIE
        } else if (series.every(e => e.type === TYPES.BAR)) {
          chartType = TYPES.BAR
        } else if (series.every(e => e.type === TYPES.LINE)) {
          chartType = TYPES.LINE
        } else if (series.every(e => e.type === TYPES.BUBBLE)) {
          chartType = TYPES.BUBBLE
        } else if (series.every(e => e.type === TYPES.SCATTER)) {
          chartType = TYPES.SCATTER
        } else if (series.every(e => e.type === TYPES.AREA)) {
          chartType = TYPES.AREA
        } else if (series.some(e => e.type === TYPES.BAR) && series.some(e => e.type === TYPES.LINE)) {
          chartType = TYPES.PARETO
        }
      }
      if (type === ELEMENT.GAUGE) {
        let series = config.charts[0].series
        if (series.every(e => e.type === TYPES.BULLETGAUGE)) {
          chartType = TYPES.BULLETGAUGE
        } else if (series.every(e => e.type === TYPES.SOLIDGAUGE)) {
          chartType = TYPES.SOLIDGAUGE
        }
      }
      if (type === ELEMENT.HEAT_MAP) {
        chartType = TYPES.HEAT_MAP
      }
      return {
        elementType: type,
        chartType
      }
    },
    createAggregationOnly(data) {
      let {column, id, seriesItem = null} = data
      let aggregation = getDefaultAggregationsOfDataType(column.type).aggregation
      let newAggregation = {
        column: column.name,
        alias: `${column.name}_${aggregation}_${id}`,
        aggregation: aggregation
      }
      this.elementData.config.grouping.aggregations.push(newAggregation)
      if (this.selected.elementType === ELEMENT.GAUGE) {
        return this.mappingDefaultGauge(this.elementData, {series: seriesItem})
      }
    },
    forceGroupColumn(data) {
      let { column: {name, type}, groupType, seriesItem = null } = data
      if (this.selected && this.selected.chartType === TYPES.BUBBLE) {
        handleGroupingBubble(this.elementData, seriesItem, { name, type }, groupType)
      } else {
        handleGrouping(this.elementData, seriesItem, { name, type }, groupType)
      }
      this.$set(this.config.widgetConfig.elements[0].config, 'grouping', this.elementData.config.grouping)
    },
    forceUngroupColumn(data) {
      let { column: {name, type}, groupType, seriesItem = null } = data
      handleUngrouping(this.elementData, seriesItem, { name, type }, groupType)
      this.$set(this.config.widgetConfig.elements[0].config, 'grouping', this.elementData.config.grouping)
    },
    forceMappingDefaultGauge (data) {
      this.mappingDefaultGauge(data.element, data.series)
      // Change series name if aggregation, displayName change
      // setTimeout wait for this.$set done setting new value
      this.$nextTick(() => {
        this.$refs.visualizationAxis.mappingChartName()
      })
    },
    mappingDefaultGauge(element, data) {
      let {series} = data
      CBPO.dsManager().getDataSource(this.config.dataSource).query({
        paging: {limit: 1},
        group: element.config.grouping
      }).then(({rows, cols}) => {
        let colIndex = findIndex(cols, e => e.alias ? e.alias.includes(series.id) : e.name.includes(series.id))
        switch (this.selected.chartType) {
          case TYPES.BULLETGAUGE:
            makeDefaultBulletGaugeConfig(this.elementData, rows[0][colIndex], series)
            break
          case TYPES.SOLIDGAUGE:
            makeDefaultSolidGaugeConfig(this.elementData, rows[0][colIndex], series)
            break
          default:
            break
        }
        this.$set(this.config.widgetConfig.elements, 0, this.elementData)
      })
    },
    /**
     * Binning
     */
    updateBinConfig (data) {
      if (data.bins) this.$set(this.config.widgetConfig.elements[0].config, 'bins', data.bins)
      if (data.grouping && this.selected.elementType !== ELEMENT.CROSSTAB_TABLE) this.$set(this.config.widgetConfig.elements[0].config, 'grouping', data.grouping)
    },
    /**
     * Create grouping config after change from scatter chart to another chart
     * Will be called when VisualizeElement fire 'createGroupingFromConfig' event
     */
    createGroupingFromConfig() {
      let hasGroupX = false
      let hasGroupY = false
      this.elementData.config.charts[0].series.forEach(item => {
        let {x, y, z} = item.data
        if (x && !hasGroupX) {
          hasGroupX = true
          let {name, type} = cloneDeep(this.fields.find(col => col.name === x))
          handleGrouping(this.elementData, item, {name, type}, GROUPING_TYPE.COLUMNS)
        }
        if (y && !hasGroupY) {
          hasGroupY = true
          let {name, type} = cloneDeep(this.fields.find(col => col.name === y))
          if (item.type === TYPES.BUBBLE) {
            handleGrouping(this.elementData, item, {name, type}, GROUPING_TYPE.COLUMNS)
          } else {
            handleGrouping(this.elementData, item, {name, type}, GROUPING_TYPE.AGGREGATIONS)
            this.$nextTick(() => {
              // update aggregations on the column pill in AxisContainer
              this.$refs.visualizationAxis.getAggregationFromGrouping(item.id, y)
            })
          }
        }
        if (z) {
          let {name, type} = cloneDeep(this.fields.find(col => col.name === z))
          handleGrouping(this.elementData, item, {name, type}, GROUPING_TYPE.AGGREGATIONS)
          this.$nextTick(() => {
            // update aggregations on the column pill in AxisContainer
            this.$refs.visualizationAxis.getAggregationFromGrouping(item.id, z)
          })
        }
      })
      this.$set(this.config.widgetConfig.elements[0].config, 'grouping', this.elementData.config.grouping)
    },
    createDefaultWidgetTitle (config) {
      const elementData = get(config, 'elements[0]', {})
      let newTitle = ''
      if (!isEmpty(elementData)) {
        const type = elementData.type || ''
        let series = get(config, 'elements[0].config.charts[0].series', [])
        let bins = get(config, 'elements[0].config.bins', [])
        let xColumns = []
        let yColumns = []
        switch (type) {
          case ELEMENT.CHART:
            series.forEach(ser => {
              if (ser && ser.data.x) xColumns = [{name: ser.data.x}]
              if (ser && ser.data.y) yColumns.push({name: ser.data.y})
            })
            newTitle = this.createDefaultTitleWithAxis(xColumns, yColumns, [], bins)
            break
          case ELEMENT.TABLE:
            const columns = get(config, 'elements[0].config.columns', [])
            newTitle = this.createDefaultTitleWithColumns(columns)
            break
          case ELEMENT.CROSSTAB_TABLE:
            xColumns = get(config, 'elements[0].config.xColumns', [])
            yColumns = get(config, 'elements[0].config.yColumns', [])
            const tColumns = get(config, 'elements[0].config.tColumns', [])
            newTitle = this.createDefaultTitleWithAxis(xColumns, yColumns, tColumns, bins)
            break
          case ELEMENT.GLOBAL_FILTER:
            newTitle = 'Global filter'
            break
          case ELEMENT.GAUGE:
            yColumns = []
            series.forEach(ser => {
              if (ser && ser.data.y) yColumns.push({name: ser.data.y})
            })
            newTitle = this.createDefaultTitleWithAxis([], yColumns, [], [])
            break
          case ELEMENT.HTML_EDITOR:
            newTitle = 'Rich text content'
            break
          case ELEMENT.HEAT_MAP:
            series.forEach(ser => {
              if (ser && ser.data.x) xColumns = [{name: ser.data.x}]
              if (ser && ser.data.y) yColumns = [{name: ser.data.y}]
            })
            newTitle = this.createDefaultTitleWithAxis(xColumns, yColumns, [], bins)
            break
        }
      }
      if (newTitle) {
        config.widget.title.text = newTitle
        if (!isEmpty(get(config, 'elements[0].config.widget', {}))) {
          config.elements[0].config.widget.title.text = newTitle
        }
      }
    },
    createDefaultTitleWithColumns (columns) {
      if (isEmpty(columns)) return 'Table of []'
      let title = 'Table of'
      let columnsName = columns.map(col => col.name)
      return `${title} [${columnsName.join(', ')}]`
    },
    createDefaultTitleWithAxis (xColumns = [], yColumns = [], tColumns = [], bins = []) {
      let yData = []
      let xTData = []
      if (!isEmpty(yColumns)) {
        yData = yColumns.map(col => col.name)
      }
      if (!isEmpty(xColumns)) {
        xTData = xColumns.map(col => col.name)
      }
      if (!isEmpty(tColumns)) {
        xTData = yData.concat(tColumns.map(col => col.name))
      }
      let title = `Quantitation of [${yData.length ? yData.join(', ') : ''}] ${xTData.length ? 'over [' + xTData.join(', ') + ']' : ''}`
      if (isEmpty(bins)) return title
      const binData = bins.reduce((binText, bin) => {
        const binType = get(bin, 'options.alg', '')
        const binWidth = binType === 'auto' ? get(bin, 'options.numOfBins', '') : `${get(bin, 'options.uniform.width', '')} ${get(bin, 'options.uniform.unit', '')}`
        binText += `${binWidth} ${get(bin, 'options.alg', '')}`
        return binText
      }, '')
      return `${title} per ${binData} interval`
    },
    isDisplayNameChanged(columns, widgetColumns) {
      let isChanged = false
      columns.forEach(column => {
        const widgetColumn = widgetColumns.find(col => col.name === column.name && col.displayName !== column.displayName)
        if (widgetColumn) {
          widgetColumn.displayName = column.displayName
          isChanged = true
        }
      })
      return isChanged
    },
    updateWidgetColumns(columns) {
      this.$set(this.config.widgetConfig.elements[0].config, 'columns', [...columns])
      this.$nextTick(() => {
        if (this.selected.elementType === ELEMENT.CHART || this.selected.elementType === ELEMENT.GAUGE) {
          this.$refs.visualizationAxis.mappingChartName()
        }
      })
    },
    updateFields (columns) {
      if (columns && columns.length) {
        const clonedFields = cloneDeep(this.fields)
        columns.forEach((column, index) => {
          const field = clonedFields.find(field => field.name === column.name)
          if (field) {
            field.displayName = column.displayName || field.displayName
          }
        })
        this.fields = [...clonedFields]

        // Update display name of column in axis and chart
        const widgetColumns = cloneDeep(this.config.widgetConfig.elements[0].config.columns)
        const isChanged = this.isDisplayNameChanged(columns, widgetColumns)
        if (isChanged) this.updateWidgetColumns(widgetColumns)
      }
    }
  },
  watch: {
    'config.widgetConfig': {
      deep: true,
      handler: function(val) {
        this.widgetData = val
      }
    },
    widgetData: {
      deep: true,
      handler: function(val) {
        const editMode = get(val, 'editMode', false)
        if (!this.editedTitle && !editMode) this.createDefaultWidgetTitle(val)
        let [firstElement] = val.elements
        this.elementData = firstElement
      }
    },
    elementData: {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal !== oldVal) {
          this.config.widgetConfig.elements = [newVal]
          this.config.widgetConfig.filter.globalFilter.enabled = !!(newVal && newVal.type === ELEMENT.GLOBAL_FILTER)
          this.widgetData = {...this.config.widgetConfig}
        }
      }
    },
    'outsideConfig.templates' (val) {
      this.$set(this.config, 'templates', val)
    },
    updatedColumnsState: {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal && newVal.length) {
          // check from channels
          this.updateFields(newVal)
        }
      }
    }
  }
}
</script>
<style scoped lang="scss">
  @import "VisualizationBuilder";
</style>
