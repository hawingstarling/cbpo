<template>
  <div class="cbpo-axis-zone">
    <div class="cbpo-axis-header">
      <h4>Axis</h4>
    </div>
    <div class="cbpo-axis-content">
      <!--DROP ZONE X-->
      <div v-if="element && element.type">
        <div v-if="element.type !== ELEMENT.GAUGE && element.type !== ELEMENT.GLOBAL_FILTER">
          <span class="title">
            <span>X axis</span>
            <i v-if="element.type === ELEMENT.CHART" @click="xAxisSettingsModalTrigger()" class="fa fa-gear"/>
          </span>
          <div v-cbpo-droppable="{
                  scope: wrapperId,
                  dropZone: AXIS.X,
                  tolerance: 'intersect',
                  [EVENT.DROP_EVENT]: dropEvent,
                  [EVENT.OVER_EVENT]: overEvent,
                  [EVENT.OUT_EVENT]: outEvent,
                  [EVENT.ACCEPT_EVENT]: acceptEvent
                }" class="cbpo-dropzone cbpo-x-zone">
            <!--FOR CHART || HEAT MAP-->
            <div v-if="element.type === ELEMENT.CHART || element.type === ELEMENT.HEAT_MAP">
              <div class="cbpo-column-content" v-if="element.config.charts[0].series[0].data.x">
                <div class="cell-box">
                  <span class="text text-truncate text-center d-block w-100">
                    {{getDisplayName(AXIS.X, 0)}}
                  </span>
                  <i @click="xAxisColumnModalTrigger(0)" class="fa fa-gear"/>
                  <i class="fa fa-times-circle" @click="removeChartColumn(AXIS.X, 0)"/>
                </div>
              </div>
            </div>
            <!--FOR TABLE-->
            <div v-else-if="element.type === ELEMENT.TABLE || element.type === ELEMENT.HTML_EDITOR">
              <div class="cbpo-column-content">
                <div :key="`column_${colIndex}`" v-for="(column, colIndex) in element.config.columns" class="cell-box">
                  <span class="text text-truncate text-center d-block w-100">
                    {{column.displayName || column.name}}
                  </span>
                  <i @click="xAxisColumnModalTrigger(colIndex)" class="fa fa-gear"/>
                  <i class="fa fa-times-circle" @click="removeTableColumn(colIndex)"/>
                </div>
              </div>
            </div>
            <!--FOR CROSSTAB TABLE-->
            <div v-else-if="element.type === ELEMENT.CROSSTAB_TABLE">
              <div class="cbpo-column-content">
                <div :key="`column_${colIndex}`" v-for="(column, colIndex) in element.config.xColumns" class="cell-box">
                  <span class="text text-truncate text-center d-block w-100">
                    {{column.displayName || column.name}}
                  </span>
                  <i @click="xAxisColumnModalTrigger(colIndex)" class="fa fa-gear"/>
                  <i class="fa fa-times-circle" @click="removeCrosstabTableColumn(AXIS.X, column)"/>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!--DROP ZONE Y-->
      <div v-if="element && element.type">
        <!--FOR CHART-->
        <div v-if="element.type === ELEMENT.CHART">
          <div v-if="selectedElement.chartType === TYPES.PARETO">
            <template v-for="(item, index) of element.config.charts[0].series">
              <span :key="`yAxis_title_${index}`" class="title">
                <span>Y axis {{ index + 1 }}</span>
                <span class="flex-spacer"></span>
                <i v-if="element.config.charts[0].series.length > 1" @click="removeYAxis(index)" class="feature__buttons fa fa-minus text-danger"/>
                <i v-if="element.config.charts[0].series.length > 0 && element.config.charts[0].series.length < 2" @click="addYAxis(index + 1)" class="feature__buttons fa fa-plus text-success"/>
                <i v-if="element.type === ELEMENT.CHART" @click="yAxisSettingsModalTrigger(item, index)" class="feature__buttons fa fa-gear"/>
              </span>
              <div :key="`yAxis_column_${index}`" v-cbpo-droppable="{
                scope: wrapperId,
                dropZone: AXIS.Y,
                dropIndex: index,
                tolerance: 'intersect',
                [EVENT.DROP_EVENT]: dropEvent,
                [EVENT.OVER_EVENT]: overEvent,
                [EVENT.OUT_EVENT]: outEvent,
                [EVENT.ACCEPT_EVENT]: acceptEvent
              }" class="cbpo-dropzone cbpo-y-zone">
                <div class="cbpo-column-content" v-if="item.data.y">
                  <div class="cell-box">
                    <span class="text text-truncate text-center d-block w-100">
                      {{getDisplayName(AXIS.Y, index)}}
                    </span>
                    <div>
                      <b-form-select
                        v-if="columnAggregations[item.id]"
                        :value="columnAggregations[item.id].currentAggregation"
                        @change="aggregationChange($event, item, item.data.y)"
                        :options="columnAggregations[item.id].aggregations"
                        text-field="label"
                        value-field="aggregation"
                        size="sm">
                      </b-form-select>
                      <i @click="yAxisColumnModalTrigger(index)" class="fa fa-gear"/>
                    </div>
                    <i class="fa fa-times-circle" @click="removeChartColumn(AXIS.Y, index)"/>
                  </div>
                </div>
              </div>
            </template>
          </div>
          <div v-else>
            <span class="title">
              <span>Y axis</span>
              <span class="flex-spacer"></span>
              <i v-if="element.type === ELEMENT.CHART && element.config.charts[0].series.length" @click="yAxisSettingsModalTrigger(element.config.charts[0].series[0], 0)" class="feature__buttons fa fa-gear"/>
            </span>
            <div v-cbpo-droppable="{
              scope: wrapperId,
              dropZone: AXIS.Y,
              tolerance: 'intersect',
              [EVENT.DROP_EVENT]: dropEvent,
              [EVENT.OVER_EVENT]: overEvent,
              [EVENT.OUT_EVENT]: outEvent,
              [EVENT.ACCEPT_EVENT]: acceptEvent
            }" class="cbpo-dropzone cbpo-y-zone">
              <div class="cbpo-column-content">
                <template v-for="(item, index) of element.config.charts[0].series">
                  <div class="cell-box" v-if="item.data.y" :key="index">
                    <span class="text text-truncate text-center d-block w-100">
                      {{getDisplayName(AXIS.Y, index)}}
                    </span>
                    <div>
                      <b-form-select
                        v-if="selectedElement.chartType !== TYPES.BUBBLE && selectedElement.chartType !== TYPES.SCATTER && columnAggregations[item.id]"
                        :value="columnAggregations[item.id].currentAggregation"
                        @change="aggregationChange($event, item, item.data.y)"
                        :options="columnAggregations[item.id].aggregations"
                        text-field="label"
                        value-field="aggregation"
                        size="sm">
                      </b-form-select>
                      <i v-if="selectedElement.chartType === TYPES.BUBBLE" @click="yAxisColumnModalTrigger(index, AXIS.Y, GROUPING_TYPE.COLUMNS)" class="fa fa-gear mt-1"/>
                      <i v-else @click="yAxisColumnModalTrigger(index)" class="fa fa-gear mt-1"/>
                    </div>
                    <i class="fa fa-times-circle" @click="removeChartColumn(AXIS.Y, index)"/>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
        <!--FOR GAUGE-->
        <div v-else-if="element.type === ELEMENT.GAUGE">
          <span class="title">
              <span>Y axis</span>
              <span class="flex-spacer"></span>
              <i v-if="element.config.charts[0].series.length" @click="yAxisSettingsModalTrigger(element.config.charts[0].series[0], 0)" class="feature__buttons fa fa-gear"/>
            </span>
            <div v-cbpo-droppable="{
              scope: wrapperId,
              dropZone: AXIS.Y,
              tolerance: 'intersect',
              [EVENT.DROP_EVENT]: dropEvent,
              [EVENT.OVER_EVENT]: overEvent,
              [EVENT.OUT_EVENT]: outEvent,
              [EVENT.ACCEPT_EVENT]: acceptEvent
            }" class="cbpo-dropzone cbpo-y-zone">
              <div class="cbpo-column-content">
                <template v-for="(item, index) of element.config.charts[0].series">
                  <div class="cell-box" v-if="item.data.y" :key="index">
                    <span class="text text-truncate text-center d-block w-100">
                      {{getDisplayName(AXIS.Y, index)}}
                    </span>
                    <div>
                      <b-form-select
                        v-if="columnAggregations[item.id]"
                        :value="columnAggregations[item.id].currentAggregation"
                        @change="aggregationChange($event, item, item.data.y)"
                        :options="columnAggregations[item.id].aggregations"
                        text-field="label"
                        value-field="aggregation"
                        size="sm">
                      </b-form-select>
                      <i @click="yAxisColumnModalTrigger(index)" class="fa fa-gear"/>
                    </div>
                    <i class="fa fa-times-circle" @click="removeChartColumn(AXIS.Y, index)"/>
                  </div>
                </template>
              </div>
            </div>
        </div>
        <!-- FOR HEAT MAP -->
        <div v-else-if="element.type === ELEMENT.HEAT_MAP">
          <span class="title">
              <span>Y axis</span>
              <span class="flex-spacer"></span>
              <i v-if="element.config.charts[0].series.length" @click="yAxisSettingsModalTrigger(element.config.charts[0].series[0], 0)" class="feature__buttons fa fa-gear"/>
            </span>
          <div v-cbpo-droppable="{
              scope: wrapperId,
              dropZone: AXIS.Y,
              tolerance: 'intersect',
              [EVENT.DROP_EVENT]: dropEvent,
              [EVENT.OVER_EVENT]: overEvent,
              [EVENT.OUT_EVENT]: outEvent,
              [EVENT.ACCEPT_EVENT]: acceptEvent
            }" class="cbpo-dropzone cbpo-y-zone">
            <div class="cbpo-column-content">
              <template v-for="(item, index) of element.config.charts[0].series">
                <div class="cell-box" v-if="item.data.y" :key="index">
                    <span class="text text-truncate text-center d-block w-100">
                      {{getDisplayName(AXIS.Y, index)}}
                    </span>
                  <div>
                    <b-form-select
                      v-if="columnAggregations[item.id]"
                      :value="columnAggregations[item.id].currentAggregation"
                      @change="aggregationChange($event, item, item.data.y)"
                      :options="columnAggregations[item.id].aggregations"
                      text-field="label"
                      value-field="aggregation"
                      size="sm">
                    </b-form-select>
                    <i @click="yAxisColumnModalTrigger(index)" class="fa fa-gear"/>
                  </div>
                  <i class="fa fa-times-circle" @click="removeChartColumn(AXIS.Y, index)"/>
                </div>
              </template>
            </div>
          </div>
        </div>
        <!--FOR CROSSTAB-->
        <div v-else-if="element.type === ELEMENT.CROSSTAB_TABLE">
          <span :key="`yAxis_title_table`" class="title">
            <span>Y axis</span>
          </span>
          <div v-cbpo-droppable="{
              scope: wrapperId,
              dropZone: AXIS.Y,
              tolerance: 'intersect',
              [EVENT.DROP_EVENT]: dropEvent,
              [EVENT.OVER_EVENT]: overEvent,
              [EVENT.OUT_EVENT]: outEvent,
              [EVENT.ACCEPT_EVENT]: acceptEvent
            }" class="cbpo-dropzone cbpo-y-zone">
            <div class="cbpo-column-content">
              <template v-for="(column, index) of element.config.yColumns">
                <div class="cell-box" :key="index">
                  <span class="text text-truncate text-center d-block w-100">
                    {{column.displayName || column.name}}
                  </span>
                  <div>
                    <b-form-select
                      v-if="columnAggregations[column.name]"
                      :value="columnAggregations[column.name].currentAggregation"
                      @change="aggregationChange($event, null, column.name)"
                      :options="columnAggregations[column.name].aggregations"
                      text-field="label"
                      value-field="aggregation"
                      size="sm">
                    </b-form-select>
                    <i @click="yAxisColumnModalTrigger(index)" class="fa fa-gear"/>
                  </div>
                  <i class="fa fa-times-circle" @click="removeCrosstabTableColumn(AXIS.Y, column)"/>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
      <!--DROP ZONE Z-->
      <div v-if="shouldShowAxisZ">
        <span class="title">
          <span>{{element.type === ELEMENT.CROSSTAB_TABLE ? 'T' : 'Z'}} axis</span>
        </span>
        <div v-cbpo-droppable="{
              scope: wrapperId,
              dropZone: AXIS.Z,
              tolerance: 'intersect',
              [EVENT.DROP_EVENT]: dropEvent,
              [EVENT.OVER_EVENT]: overEvent,
              [EVENT.OUT_EVENT]: outEvent,
              [EVENT.ACCEPT_EVENT]: acceptEvent
            }" class="cbpo-dropzone cbpo-z-zone">
          <!--FOR CHART-->
          <div v-if="element.type === ELEMENT.CHART">
            <div class="cbpo-column-content" v-if="element.config.charts[0].series[0].data.z">
              <div class="cell-box">
                <span class="text text-truncate text-center d-block w-100">
                  {{getDisplayName(AXIS.Z, 0)}}
                </span>
                <div>
                  <b-form-select
                    v-if="columnAggregations[element.config.charts[0].series[0].id]"
                    :value="columnAggregations[element.config.charts[0].series[0].id].currentAggregation"
                    @change="aggregationChange($event, element.config.charts[0].series[0], element.config.charts[0].series[0].data.z)"
                    :options="columnAggregations[element.config.charts[0].series[0].id].aggregations"
                    text-field="label"
                    value-field="aggregation"
                    size="sm">
                  </b-form-select>
                  <i @click="yAxisColumnModalTrigger(0, AXIS.Z, GROUPING_TYPE.AGGREGATIONS)" class="fa fa-gear"/>
                </div>
                <i class="fa fa-times-circle" @click="removeChartColumn(AXIS.Z, 0)"/>
              </div>
            </div>
          </div>
          <!--FOR CROSSTAB TABLE-->
          <div v-else-if="element.type === ELEMENT.CROSSTAB_TABLE">
            <div class="cbpo-column-content" :key="`crosstab-column-${index}`" v-for="(column, index) of element.config.tColumns">
              <div class="cell-box">
                <span class="text text-truncate text-center d-block w-100">
                  {{column.displayName || column.name}}
                </span>
                <i @click="zAxisColumnModalTrigger(index)" class="fa fa-gear"/>
                <i class="fa fa-times-circle" @click="removeCrosstabTableColumn(AXIS.Z, column)"/>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- DATA COUNTRY FOR HEAT MAP -->
      <div class="mt-2" v-if="element && element.type === ELEMENT.HEAT_MAP">
        <div class="form-group">
          <label for="geo">Geo Location</label>
          <select id="geo" class="form-control custom-select" @change="setDefaultGeo" v-model="element.config.charts[0].series[0].data.country.geo">
            <option :key="geo.value" v-for="geo of getGeoLocation" :value="geo.value"> {{ geo.label }} </option>
          </select>
        </div>
        <div class="form-group">
          <label for="geo-detail">Geo Detail</label>
          <select id="geo-detail" class="form-control custom-select" v-model="element.config.charts[0].series[0].data.country.geoDetail">
            <option :key="geo.value" v-for="geo of getGeoDetailLocation" :value="geo.value"> {{ geo.label }} </option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  GEO_DETAIL_LOCATION_SUPPORTS,
  GEO_LOCATION_SUPPORTS
} from '@/components/widgets/elements/chart/builder/highcharts/HeatMapBuilder'
import dropDirective from '@/directives/dropDirective'
import { EVENT } from '@/utils/dragAndDropUtil'
import { AXIS, ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { isEmpty, cloneDeep, get, defaultsDeep, forEachRight, findIndex } from 'lodash'
import $ from 'jquery'
import { BUS_EVENT } from '@/services/eventBusType'
import { getAggregationObjFromAggregationName, getDataTypeFromType, findNumericAggregations } from '@/services/ds/data/DataTypes'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import {
  DEFAULT_CONFIG_X_AXIS,
  DEFAULT_CONFIG_Y_AXIS,
  DEFAULT_SERIES_CONFIG,
  getDefaultOptionsConfigFromChartTypeChartJs
} from '@/components/widgets/elements/chart/types/ChartTypes'
import { GROUPING_TYPE } from '@/utils/visualizationUtil'
import { createBinColumnAlias, buildBinObj, hasBinningAccept } from '@/utils/binUtils'
import { DEFAULT_CROSSTAB_COLUMN_CONFIG } from '@/components/widgets/elements/crosstab-table/CrosstableTableConfig'

export default {
  name: 'VisualizationAxis',
  props: {
    wrapperId: String,
    element: Object,
    selectedElement: Object,
    rows: Array,
    fields: Array
  },
  directives: {
    'cbpo-droppable': dropDirective
  },
  data() {
    return {
      EVENT,
      AXIS,
      TYPES,
      ELEMENT,
      DRAG_EVENT: null,
      GROUPING_TYPE,
      columnAggregations: {}
    }
  },
  beforeMount() {
    let series = get(this.element, 'config.charts[0].series')
    if (!isEmpty(series)) {
      switch (this.element.type) {
        case ELEMENT.CHART:
        case ELEMENT.GAUGE: {
          this.buildChartAggregations(this.selectedElement.chartType === TYPES.BUBBLE ? AXIS.Z : AXIS.Y)
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          this.buildTableAggregations()
          break
        }
      }
    }
  },
  computed: {
    getGeoLocation() {
      return GEO_LOCATION_SUPPORTS
    },
    getGeoDetailLocation() {
      if (!this.element || this.element.type !== ELEMENT.HEAT_MAP) return []
      return GEO_DETAIL_LOCATION_SUPPORTS[this.element.config.charts[0].series[0].data.country.geo] || []
    },
    getDisplayName() {
      return (axis, index) => {
        let column = this.element.config.columns
          .find(column => column.name === this.element.config.charts[0].series[index].data[axis])
        return column ? column.displayName : ''
      }
    },
    shouldShowAxisZ() {
      if (!this.selectedElement) return false
      return this.selectedElement.chartType === TYPES.BUBBLE || this.selectedElement.elementType === ELEMENT.CROSSTAB_TABLE
    }
  },
  methods: {
    setDefaultGeo() {
      const { geo } = this.element.config.charts[0].series[0].data.country
      const [ defaultGeo ] = GEO_DETAIL_LOCATION_SUPPORTS[geo]
      this.element.config.charts[0].series[0].data.country.geoDetail = defaultGeo.value
    },
    // Show aggregations dropdown
    buildChartAggregations(axisType = AXIS.Y) {
      const series = get(this.element, 'config.charts[0].series', [])
      const columns = get(this.element, 'config.columns', [])
      if (series.length) {
        series.forEach(ser => {
          if (ser.data[axisType] && ser.id) {
            this.columnAggregations[ser.id] = {
              aggregations: [],
              currentAggregation: null
            }
            const column = columns.find(column => column.name === ser.data[axisType])
            let aggregations = findNumericAggregations(column.type)
            if (!aggregations || !aggregations.length) {
              this.columnAggregations[ser.id].aggregations = [{label: 'No aggregation', aggregation: null}]
            }
            this.columnAggregations[ser.id].aggregations = [...aggregations]
            this.getAggregationFromGrouping(ser.id, column.name)
          }
        })
      }
    },
    buildTableAggregations () {
      const yColumns = get(this.element, 'config.yColumns', [])
      if (yColumns && yColumns.length) {
        yColumns.forEach(col => {
          this.columnAggregations[col.name] = {
            aggregations: [],
            currentAggregation: null
          }
          // let aggregations = findNumericAggregations(col.type)
          let aggregations = getDataTypeFromType(col.type).aggregations
          if (!aggregations || !aggregations.length) {
            this.columnAggregations[col.name].aggregations = [{label: 'No aggregation', aggregation: null}]
          }
          this.columnAggregations[col.name].aggregations = [...aggregations]
          this.getAggregationFromGrouping('', col.name)
        })
      }
    },
    getAggregationFromGrouping(serId, columnName) {
      switch (this.element.type) {
        case ELEMENT.GAUGE:
        case ELEMENT.HEAT_MAP:
        case ELEMENT.CHART: {
          const aggregations = this.element.config.grouping.aggregations
            .find(agg => agg.alias.includes(serId))
          const columnAggregations = {...this.columnAggregations}
          columnAggregations[serId].currentAggregation = aggregations && aggregations.aggregation ? aggregations.aggregation : ''
          this.columnAggregations = cloneDeep(columnAggregations)
          break
        }
        case ELEMENT.TABLE: {
          const aggregations = this.element.config.grouping.aggregations
            .find(agg => agg.column === columnName)
          this.columnAggregations[serId].currentAggregation = aggregations ? aggregations.aggregation : ''
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          const aggregations = this.element.config.yColumns
            .find(column => column.name === columnName).aggregation
          this.columnAggregations[columnName].currentAggregation = aggregations ? aggregations.aggregation : ''
          break
        }
      }
    },
    aggregationChange(aggregation, series, columnName) {
      let data
      switch (this.element.type) {
        case ELEMENT.GAUGE:
        case ELEMENT.HEAT_MAP:
        case ELEMENT.CHART: {
          data = this.element.config.grouping.aggregations.find(agg => agg.alias.includes(series.id))
          break
        }
        case ELEMENT.TABLE: {
          data = this.element.config.grouping.aggregations.find(agg => agg.column === columnName)
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          data = this.element.config.yColumns.find(column => column.name === columnName).aggregation
        }
      }
      if (data) data.aggregation = aggregation
      // apply to update config
      this.$nextTick(() => {
        if (this.element.type && this.element.type === ELEMENT.CHART) {
          this.mappingChartName()
        } else if (this.element.type && this.element.type === ELEMENT.GAUGE) {
          this.$emit('mappingDefaultGauge', {element: this.element, series})
        }
      })
    },
    removeYAxis(index) {
      let { id } = this.element.config.charts[0].series[index]
      this.element.config.charts[0].axis.x = this.element.config.charts[0].axis.x.filter(axis => !axis.id.includes(id))
      this.element.config.charts[0].axis.y = this.element.config.charts[0].axis.y.filter(axis => !axis.id.includes(id))
      this.element.config.charts[0].series.splice(index, 1)
      if (this.selectedElement.chartType === TYPES.PARETO) {
        this.element.config.charts[0].series[0].type = TYPES.BAR
        this.element.config.charts[0].axis.y[0].position = 'left'
      }
      this.$emit('update:element', this.element)
    },
    addYAxis(index) {
      let itemInSeries = this.element.config.charts[0].series[0]
      let axisColumns = this.element.config.charts[0].axis.y.find(axis => axis.id.includes(itemInSeries.id))
      let item = defaultsDeep({ type: this.selectedElement.chartType === TYPES.PARETO ? (itemInSeries.type === TYPES.BAR ? TYPES.LINE : TYPES.BAR) : this.selectedElement.chartType }, DEFAULT_SERIES_CONFIG)
      item.options = defaultsDeep(item.options, getDefaultOptionsConfigFromChartTypeChartJs(TYPES.BAR))
      item.id = Date.now()
      item.axis = {
        x: `x_${item.id}`,
        y: `y_${item.id}`
      }
      if (this.element.type === ELEMENT.GAUGE) delete item.axis.x
      if (this.selectedElement.chartType === TYPES.BUBBLE) item.data.z = itemInSeries.data.z
      this.element.config.charts[0].axis.y = [...this.element.config.charts[0].axis.y, {...{id: `y_${item.id}`}, ...cloneDeep(DEFAULT_CONFIG_Y_AXIS), ...{position: axisColumns && axisColumns.position === 'left' ? 'right' : 'left'}}]
      this.element.config.charts[0].series.splice(index, 0, item)
      this.$emit('update:element', this.element)
    },
    /**
     * Trigger modal via submit an event to Visualization builder
     * Will be called when drop a object
     * **/
    xAxisColumnModalTrigger(index) {
      switch (this.element.type) {
        case ELEMENT.HEAT_MAP:
        case ELEMENT.CHART: {
          let column = this.element.config.columns.find(column => column.name === this.element.config.charts[0].series[index].data.x)
          this.$emit('modalTrigger', {type: 'xAxisColumnSetting', isShow: true, data: {column: cloneDeep(column), series: this.element.config.charts[0].series[index]}})
          break
        }
        case ELEMENT.HTML_EDITOR:
        case ELEMENT.TABLE: {
          if (this.element.config.grouping.columns.length === 0 || this.element.config.grouping.columns.find(col => col.name === this.element.config.columns[index].name)) {
            this.$emit('modalTrigger', {type: 'xAxisColumnSetting', isShow: true, data: {column: cloneDeep(this.element.config.columns[index]), series: null}})
          } else {
            this.$emit('modalTrigger', {type: 'yAxisColumnSetting', isShow: true, data: {column: cloneDeep(this.element.config.columns[index]), series: null}})
          }
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          let column = this.element.config.xColumns[index]
          this.$emit('modalTrigger', {type: 'xAxisColumnSetting', isShow: true, data: {column: cloneDeep(column), series: null}})
        }
      }
    },
    /**
     * Trigger modal via submit an event to Visualization builder
     * Will be called when drop a object
     * **/
    yAxisColumnModalTrigger(index, axisType = AXIS.Y, groupType = GROUPING_TYPE.AGGREGATIONS) {
      if (this.element.type === ELEMENT.CROSSTAB_TABLE) {
        let column = this.element.config.yColumns[index]
        this.$emit('modalTrigger', {type: 'yAxisColumnSetting', isShow: true, data: {column: cloneDeep(column), series: null}})
      } else {
        let column = this.element.config.columns.find(column => column.name === this.element.config.charts[0].series[index].data[axisType])
        if (groupType === GROUPING_TYPE.COLUMNS) {
          this.$emit('modalTrigger', {type: 'xAxisColumnSetting', isShow: true, data: { column: cloneDeep(column), series: this.element.config.charts[0].series[index] }})
        } else {
          this.$emit('modalTrigger', {type: 'yAxisColumnSetting', isShow: true, data: { column: cloneDeep(column), series: this.element.config.charts[0].series[index] }})
        }
      }
    },
    /**
     * Trigger modal via submit an event to Visualization builder
     * Will be called when drop a object
     * **/
    zAxisColumnModalTrigger(index) {
      switch (this.element.type) {
        case ELEMENT.CHART: {
          let column = this.element.config.columns.find(column => column.name === this.element.config.charts[0].series[index].data.z)
          this.$emit('modalTrigger', {type: 'zAxisColumnSetting', isShow: true, data: {column: cloneDeep(column), series: this.element.config.charts[0].series[index]}})
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          let column = this.element.config.tColumns[index]
          this.$emit('modalTrigger', {type: 'zAxisColumnSetting', isShow: true, data: {column: cloneDeep(column), series: null}})
          break
        }
      }
    },
    /**
    * Trigger modal via submit an event to Visualization builder
    * Will be call when user click on gear icon on the top right of axis name
    * */
    xAxisSettingsModalTrigger() {
      this.$emit('modalTrigger', {type: 'xAxisSetting', isShow: true, data: {item: this.element.config.charts[0].series[0], index: 0, axisType: AXIS.X}})
    },
    /**
     * Trigger modal via submit an event to Visualization builder
    * Will be call when user click on gear icon on the top right of axis name
     * */
    yAxisSettingsModalTrigger(item, index) {
      this.$emit('modalTrigger', {type: 'yAxisSetting', isShow: true, data: {item, index, axisType: AXIS.Y}})
    },
    /**
     * Method callback of drag directive
     * Will be called when drop a object
     * **/
    dropEvent(data, el) {
      $(el.target).removeClass('active')
      const chartType = get(this.element.config, 'charts[0].series[0].type', '')
      switch (this.element.type) {
        case ELEMENT.CHART:
        case ELEMENT.HEAT_MAP:
        case ELEMENT.GAUGE: {
          if (chartType === TYPES.BUBBLE) {
            this.createNewColumnBubble(data)
            this.buildChartAggregations(AXIS.Z)
          } else {
            this.createNewColumnChart(data)
            this.buildChartAggregations()
          }
          break
        }
        case ELEMENT.HTML_EDITOR:
        case ELEMENT.TABLE: {
          this.createNewColumnTable(data)
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          this.createNewColumnCrosstabTable(data)
          this.buildTableAggregations()
          break
        }
      }
    },
    /**
     * Method callback of drag directive
     * Will be called when mouse over a drop zone
     * **/
    overEvent(_, el) {
      $(el.target).addClass('active')
    },
    /**
     * Method callback of drag directive
     * Will be called when mouse out a drop zone
     * **/
    outEvent(_, el) {
      $(el.target).removeClass('active')
    },
    /**
     * Method callback of drag directive
     * Will be called when a dragging object drag to a drop zone with same scope
     * **/
    acceptEvent(data) {
      if (isEmpty(this.element)) {
        return false
      }
      let {dropZone} = data
      switch (this.element.type) {
        case ELEMENT.CHART: {
          if (dropZone) {
            switch (dropZone) {
              case AXIS.X:
                if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE]) {
                  // let name = get(this[BUS_EVENT.DRAG_DATA_DIRECTIVE], 'data.source.column.name', null)
                  // return isEmpty(get(this.element, `config.charts[0].series[0].data.x`, null)) &&
                  //   get(this.element, 'config.charts[0].series', []).every(item => item.data.y !== name) &&
                  //   get(this.element, 'config.charts[0].series[0].data.z', null) !== name
                  return isEmpty(get(this.element, `config.charts[0].series[0].data.x`, null))
                }
                return false
              case AXIS.Y:
                if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE]) {
                  // let name = get(this[BUS_EVENT.DRAG_DATA_DIRECTIVE], 'data.source.column.name', null)
                  // return isEmpty(get(this.element, `config.charts[0].series[${dropIndex}].data.y`, null)) &&
                  //   get(this.element, 'config.charts[0].series[0].data.x', null) !== name &&
                  //   get(this.element, 'config.charts[0].series[0].data.z', null) !== name
                  return true
                }
                return false
              case AXIS.Z:
                if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE]) {
                  // let name = get(this[BUS_EVENT.DRAG_DATA_DIRECTIVE], 'data.source.column.name', null)
                  // return isEmpty(get(this.element, `config.charts[0].series[0].data.z`, null)) &&
                  //   get(this.element, 'config.charts[0].series', []).every(item => item.data.y !== name) &&
                  //   get(this.element, 'config.charts[0].series[0].data.z', null) !== name
                  return isEmpty(get(this.element, `config.charts[0].series[0].data.z`, null))
                }
                return false
            }
          }
          return false
        }
        case ELEMENT.GAUGE: {
          if (dropZone === AXIS.Y) {
            if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE]) {
              // let name = get(this[BUS_EVENT.DRAG_DATA_DIRECTIVE], 'data.source.column.name', null)
              // return isEmpty(get(this.element, `config.charts[0].series[${dropIndex}].data.y`, null)) &&
              //   get(this.element, 'config.charts[0].series[0].data.x', null) !== name &&
              //   get(this.element, 'config.charts[0].series[0].data.z', null) !== name
              return true
            }
            return false
          }
          return false
        }
        case ELEMENT.HEAT_MAP:
          if (dropZone === AXIS.Y) {
            if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE] && !get(this.element, 'config.charts[0].series[0].data.y')) {
              return true
            }
            return false
          } else if (dropZone === AXIS.X) {
            if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE] && !get(this.element, 'config.charts[0].series[0].data.x')) {
              return true
            }
            return false
          }
          return false
        case ELEMENT.HTML_EDITOR:
        case ELEMENT.TABLE: {
          // if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE]) {
          //   let {data: {source}} = this[BUS_EVENT.DRAG_DATA_DIRECTIVE]
          //   if (source && source.column) {
          //     return !this.element.config.columns.find(col => col.name === source.column.name)
          //   }
          // }
          return dropZone === AXIS.X
        }
        case ELEMENT.CROSSTAB_TABLE: {
          if (dropZone === AXIS.Y && this.element.config.yColumns.length > 0) {
            return false
          }
          if (this[BUS_EVENT.DRAG_DATA_DIRECTIVE]) {
            let {data: {source}} = this[BUS_EVENT.DRAG_DATA_DIRECTIVE]
            let xColumn = this.element.config.xColumns.find(column => column.name === source.column.name)
            let yColumn = this.element.config.yColumns.find(column => column.name === source.column.name)
            let tColumn = this.element.config.tColumns.find(column => column.name === source.column.name)
            return isEmpty(xColumn) && isEmpty(yColumn) && isEmpty(tColumn)
          }
          return false
        }
      }
      return false
    },
    createNewColumnBubble({data: {target, source}}) {
      if (!target || !source) throw Error('Invalid target or source')
      let { name, displayName, type } = source.column
      let {dropZone} = target
      // default value for columns in chart
      source.column = {...{ name, displayName, type }, ...{ format: null, aggrFormats: null }}

      // remove some property doesn't exist in column in chart
      if (source.cell) delete source.cell
      if (source.header) delete source.header

      // remove old column
      if (dropZone === AXIS.Y && this.element.config.charts[0].series[0].data[dropZone]) {
        this.$emit('forceUngroupColumn', {
          column: {name: this.element.config.charts[0].series[0].data[dropZone]} || {},
          seriesItem: this.element.config.charts[0].series[0],
          groupType: GROUPING_TYPE.COLUMNS,
          dropIndex: 0
        })
      }

      // Mapping column name into each item in series
      this.element.config.charts[0].series[0].data[dropZone] = source.column.name

      // Mapping axis into series
      if (!this.element.config.charts[0].axis.x.length && dropZone === AXIS.X) {
        let axis = {id: `x_${this.element.config.charts[0].series[0].id}`, ...cloneDeep(DEFAULT_CONFIG_X_AXIS)}
        this.element.config.charts[0].axis.x.push(axis)
        this.element.config.charts[0].series.forEach(item => { item.axis.x = axis.id })
      }

      // Add new column if it doesn't exist
      if (!this.element.config.columns.find(col => col.name === source.column.name)) this.element.config.columns.push(source.column)

      // Update element and force grouping column by emit event to outside
      this.$emit('update:element', this.element)
      this.$emit('forceGroupColumn', {
        column: source.column || {},
        seriesItem: (target.dropZone === AXIS.X || target.dropZone === AXIS.Y) ? null : this.element.config.charts[0].series[0],
        groupType: (target.dropZone === AXIS.X || target.dropZone === AXIS.Y) ? GROUPING_TYPE.COLUMNS : GROUPING_TYPE.AGGREGATIONS,
        dropIndex: 0
      })
      // Mapping series name by column name and aggregation name
      setTimeout(() => {
        this.mappingChartName()
      }, 0)
    },
    createNewColumnChart({data: {target, source}}) {
      if (!target || !source) throw Error('Invalid target or source')
      let { name, displayName, type } = source.column
      let {dropZone, dropIndex} = target
      let seriesLength = 0
      // default value for columns in chart
      source.column = {...{ name, displayName, type }, ...{ format: null, aggrFormats: null }}

      // remove some property doesn't exist in column in chart
      if (source.cell) delete source.cell
      if (source.header) delete source.header
      // add to series
      if (dropZone === AXIS.Y && this.element.config.charts[0].series.length >= 1 &&
        this.element.config.charts[0].series[0].data.y &&
        this.selectedElement.chartType !== TYPES.PARETO
      ) {
        seriesLength = this.element.config.charts[0].series.length
        this.addYAxis(seriesLength)
      }
      // Mapping column name into each item in series
      this.element.config.charts[0].series[((dropZone === AXIS.X || dropZone === AXIS.Z) ? 0 : dropIndex !== undefined ? dropIndex : seriesLength)].data[dropZone] = source.column.name
      let dataX = this.element.config.charts[0].series[0].data.x
      let dataZ = this.element.config.charts[0].series[0].data.z
      if (!isEmpty(dataX)) {
        this.element.config.charts[0].series.forEach(item => { item.data.x = dataX })
      }
      if (!isEmpty(dataZ)) {
        this.element.config.charts[0].series.forEach(item => { item.data.z = dataZ })
      }

      // Mapping axis into series
      if (!this.element.config.charts[0].axis.x.length && dropZone === AXIS.X) {
        let axis = {id: `x_${this.element.config.charts[0].series[0].id}`, ...cloneDeep(DEFAULT_CONFIG_X_AXIS)}
        this.element.config.charts[0].axis.x.push(axis)
        this.element.config.charts[0].series.forEach(item => { item.axis.x = axis.id })
      }

      // Add new column if it doesn't exist
      if (!this.element.config.columns.find(col => col.name === source.column.name)) this.element.config.columns.push(source.column)

      // auto binning for temporal or numberic
      const validBinningCharts = [TYPES.PARETO, TYPES.BAR, TYPES.PIE]
      if (dropZone === AXIS.X && hasBinningAccept(source.column) && validBinningCharts.includes(this.selectedElement.chartType)) {
        const binObj = buildBinObj(source.column)
        if (!isEmpty(binObj)) {
          this.element.config.bins.push(binObj)
        }
      }

      // Update element and force grouping column by emit event to outside
      this.$emit('update:element', this.element)
      if (this.selectedElement.chartType !== TYPES.SCATTER) {
        let {data, id} = this.element.config.charts[0].series[dropIndex !== undefined ? dropIndex : seriesLength]
        if (data.y && !data.x) {
          this.$emit('createAggregationOnly', {
            column: source.column,
            id,
            seriesItem: (target.dropZone === AXIS.X || target.dropZone === AXIS.Z) ? null : this.element.config.charts[0].series[dropIndex !== undefined ? dropIndex : seriesLength]
          })
        } else {
          this.$emit('forceGroupColumn', {
            column: source.column || {},
            seriesItem: (target.dropZone === AXIS.X || target.dropZone === AXIS.Z) ? null : this.element.config.charts[0].series[dropIndex !== undefined ? dropIndex : seriesLength],
            groupType: (target.dropZone === AXIS.X || target.dropZone === AXIS.Z) ? GROUPING_TYPE.COLUMNS : GROUPING_TYPE.AGGREGATIONS,
            dropIndex: dropIndex !== undefined ? dropIndex : seriesLength
          })
        }
      }
      // Mapping series name by column name and aggregation name
      setTimeout(() => {
        this.mappingChartName()
      }, 0)
    },
    mappingChartName() {
      this.element.config.charts[0].series = this.element.config.charts[0].series.map((item, index) => {
        let column = this.element.config.columns.find(column => column.name === item.data.y)
        let aggregation = this.element.config.grouping.aggregations.find(column => column.alias.includes(item.id))
        if (column) {
          if (aggregation) {
            let aggr = getAggregationObjFromAggregationName(aggregation.aggregation)
            item.name = `${column.displayName || column.name} (${aggr ? aggr.label : aggregation.aggregation})`
          } else {
            item.name = `${column.displayName || column.name}`
          }
        }
        return item
      })
    },
    createNewColumnTable({data: {target, source}}) {
      if (!target || !source) {
        throw Error('Invalid target or source')
      }
      this.element.config.columns.push(source.column)
      this.$emit('update:element', this.element)
    },
    createNewColumnCrosstabTable({data: {target, source}}) {
      let {dropZone} = target
      let {column: {name, displayName, type}} = source
      let newColumn = defaultsDeep({name, displayName, type}, DEFAULT_CROSSTAB_COLUMN_CONFIG)
      switch (dropZone) {
        case AXIS.X:
          this.element.config.xColumns.push(newColumn)
          break
        case AXIS.Y:
          let aggregation = getDataTypeFromType(type).defaultAggregation.aggregation
          newColumn = defaultsDeep(newColumn, {
            aggregation: {
              aggregation,
              alias: `${name}_${Date.now()}`
            }
          })
          this.element.config.yColumns.push(newColumn)
          break
        case AXIS.Z:
          this.element.config.tColumns.push(newColumn)
          this.element.config.sorting.push({column: name, direction: 'asc'})
          break
      }
      this.$emit('update:element', this.element)
    },
    removeBins (axis, index) {
      let { bins } = this.element.config
      // remove column in bins
      const ser = this.element.config.charts[0].series[index]
      let binnedColAlias = ''
      if (bins && bins.length) {
        if (axis === AXIS.X) {
          binnedColAlias = createBinColumnAlias(ser.data[axis])
        } else if (axis === AXIS.Y) {
          if (ser.type === TYPES.BUBBLE) {
            binnedColAlias = createBinColumnAlias(ser.data[axis])
          } else {
            binnedColAlias = createBinColumnAlias(ser.data[axis], `${ser.id}_bin`)
          }
        }
        const binnedColIndex = bins.findIndex(bin => bin.alias === binnedColAlias)
        if (binnedColIndex !== -1) bins.splice(binnedColIndex, 1)
      }
    },
    removeChartColumn(axis, index) {
      let currentSeries = cloneDeep(this.element.config.charts[0].series[index])
      // remove bins
      this.removeBins(axis, index)
      // if column is still in other axis, can't remove
      const name = this.element.config.charts[0].series[index].data[axis]
      // check series
      let columnInSeries = 0
      this.element.config.charts[0].series.forEach(ser => {
        columnInSeries += Object.values(ser.data).reduce((total, val) => { return val === name ? ++total : total }, 0)
      })
      // Update widget config
      let flagColumn = cloneDeep(this.element.config.columns.find(col => col.name === this.element.config.charts[0].series[index].data[axis]))
      if (columnInSeries <= 1) {
        this.element.config.columns = this.element.config.columns.filter(col => col.name !== this.element.config.charts[0].series[index].data[axis])
      }
      if (axis === AXIS.X) {
        this.element.config.charts[0].series = this.element.config.charts[0].series.map(ser => {
          ser.data[axis] = ''
          ser.axis.x = null
          return ser
        })
        this.element.config.charts[0].axis.x = []
      } else if (axis === AXIS.Y) {
        this.$nextTick(() => {
          if (this.element.config.charts[0].series.length > 1) {
            this.removeYAxis(index)
          } else {
            this.element.config.charts[0].series[index].data[axis] = ''
          }
        })
      } else if (axis === AXIS.Z) {
        this.element.config.charts[0].series = this.element.config.charts[0].series.map(ser => {
          ser.data[axis] = ''
          ser.axis.z = null
          return ser
        })
      }
      // remove axis
      const chartType = get(this.element.config, 'charts[0].series[0].type', '')
      if (this.selectedElement.chartType !== TYPES.BAR && this.selectedElement.chartType !== TYPES.PIE) {
        this.$emit('forceUngroupColumn', {
          seriesItem: this.element.config.charts[0].series[index],
          column: cloneDeep(flagColumn),
          groupType: (axis === AXIS.X || (chartType === TYPES.BUBBLE && axis === AXIS.Y)) ? GROUPING_TYPE.COLUMNS : GROUPING_TYPE.AGGREGATIONS
        })
      } else {
        if (axis === AXIS.X) {
          this.element.config.grouping.columns = []
        } else {
          this.element.config.grouping.aggregations = this.element.config.grouping.aggregations.filter(aggr => !aggr.alias.includes(currentSeries.id))
        }
      }

      this.$emit('update:element', this.element)
    },
    removeTableColumn(colIndex) {
      let flagColumn = cloneDeep(this.element.config.columns[colIndex])
      this.element.config.columns.splice(colIndex, 1)
      this.$emit('forceUngroupColumn', {
        seriesItem: null,
        column: cloneDeep(flagColumn),
        groupType: GROUPING_TYPE.COLUMNS
      })
      this.$emit('update:element', this.element)
    },
    removeCrosstabTableColumn(axis, column) {
      // reove column in sort
      if (this.element.config.sorting && this.element.config.sorting.length) {
        this.element.config.sorting = this.element.config.sorting.filter(sorting => sorting.column !== column.name)
      }
      this.element.config.bins = this.element.config.bins.filter(bin => bin.column.name !== column.name)
      switch (axis) {
        case AXIS.X: {
          let index = findIndex(this.element.config.xColumns, _col => _col.name === column.name)
          if (index !== -1) this.element.config.xColumns.splice(index, 1)
          break
        }
        case AXIS.Y: {
          let index = findIndex(this.element.config.yColumns, _col => _col.name === column.name)
          if (index !== -1) this.element.config.yColumns.splice(index, 1)
          break
        }
        case AXIS.Z: {
          let index = findIndex(this.element.config.tColumns, _col => _col.name === column.name)
          if (index !== -1) this.element.config.tColumns.splice(index, 1)
          break
        }
      }
    },
    dragDataChange(data) {
      this[BUS_EVENT.DRAG_DATA_DIRECTIVE] = data
    }
  },
  watch: {
    selectedElement: {
      deep: true,
      handler: function(val) {
        if (val && val.chartType === TYPES.PARETO) {
          if (get(this.element, 'config.charts[0].axis.y')) {
            if (this.element.config.charts[0].axis.y.length > 2) {
              forEachRight(this.element.config.charts[0].axis.y, (item, index) => {
                if (index < 2) return
                this.removeYAxis(index)
              })
            }
          }
        }
      }
    },
    'element.config' (val) {
      if (!isEmpty(val)) {
        switch (this.element.type) {
          case ELEMENT.CHART:
          case ELEMENT.GAUGE: {
            this.buildChartAggregations(this.selectedElement.chartType === TYPES.BUBBLE ? AXIS.Z : AXIS.Y)
            break
          }
          case ELEMENT.CROSSTAB_TABLE: {
            this.buildTableAggregations()
            break
          }
        }
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "AxisContainer";
</style>
