<template>
  <div v-if="columnData" class="w-100">
    <b-form-group label="Display Name">
      <b-form-input v-model="columnData.displayName">
      </b-form-input>
    </b-form-group>
    <b-form-group v-if="selectedType.chartType !== TYPES.SCATTER" label="Aggregation">
      <b-form-select
        :value="currentAggregation"
        @change="aggregationChange($event)"
        :options="aggregations"
        text-field="label"
        value-field="aggregation"
        size="sm">
      </b-form-select>
    </b-form-group>
    <!--Binning-->
    <b-form-group>
      <BinningConfig v-if="selectedType.chartType === TYPES.SCATTER && binningAccept"
                     :config.sync="binObj"
                     :columnType="columnType"
      />
    </b-form-group>
    <b-form-group label="Format">
      <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.formatTypeCollapse>Options</span>
        </b-card-header>
        <!--Format Type Config-->
        <b-collapse id="formatTypeCollapse">
          <b-card-body class="cbpo-form-control">
            <format-config-builder
              v-if="columnData"
              :format-config.sync="getFormatConfig"/>
          </b-card-body>
        </b-collapse>
      </b-card>
    </b-form-group>
    <b-form-group  v-if="selectedType.elementType === ELEMENT.TABLE" label="Aggregation Format">
      <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.aggregationFormatTypeCollapse>Options</span>
        </b-card-header>
        <!--Format Type Config-->
        <b-collapse id="aggregationFormatTypeCollapse">
          <b-card-body class="cbpo-form-control">
            <aggregation-format-config-builder
              v-if="columnData"
              :aggregationFormatConfig.sync="getAggregationFormatConfig"
            />
          </b-card-body>
        </b-collapse>
      </b-card>
    </b-form-group>
  </div>
</template>
<script>
import { findNumericAggregations, getDataTypeFromType } from '@/services/ds/data/DataTypes'
import AxisMixins from '@/components/visualizationBuilder/AxisColumnMixins'
import FormatConfigBuilder from '@/components/formatBuilder/FormatConfigBuilder'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import BinningConfig from '@/components/widgets/elements/table/grouping/BinningConfig'
import ColumnSettingsMixins from '@/components/widgets/elements/table/grouping/ColumnSettingsMixins'
import { findIndex } from 'lodash'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import AggregationFormatBuilder from '@/components/formatBuilder/AggregationFormatBuilder'

export default {
  name: 'YAxisColumnSettings',
  mixins: [AxisMixins, ColumnSettingsMixins, WidgetBaseMixins],
  components: {
    'format-config-builder': FormatConfigBuilder,
    'aggregation-format-config-builder': AggregationFormatBuilder,
    BinningConfig
  },
  props: {
    column: Object,
    element: Object,
    selectedType: Object
  },
  data() {
    return {
      TYPES,
      ELEMENT: ELEMENT,
      aggregations: [],
      currentAggregation: null
    }
  },
  methods: {
    widgetConfig (config) {
      this.$set(this.config, 'id', config.id)
    },
    buildAggregations() {
      if ([ELEMENT.TABLE, ELEMENT.CROSSTAB_TABLE].includes(this.selectedType.elementType)) {
        this.aggregations = getDataTypeFromType(this.columnData.type).aggregations || []
      } else {
        this.aggregations = findNumericAggregations(this.columnData.type)
      }
    },
    getAggregationFromGrouping() {
      switch (this.selectedType.elementType) {
        case ELEMENT.GAUGE:
        case ELEMENT.HEAT_MAP:
        case ELEMENT.CHART: {
          const aggregations = this.elementData.config.grouping.aggregations
            .find(agg => agg.alias.includes(this.series.id))
          this.currentAggregation = aggregations ? aggregations.aggregation : ''
          break
        }
        case ELEMENT.HTML_EDITOR:
        case ELEMENT.TABLE: {
          const aggregations = this.elementData.config.grouping.aggregations
            .find(agg => agg.column === this.column.name)
          this.currentAggregation = aggregations ? aggregations.aggregation : ''
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          const aggregations = this.elementData.config.yColumns
            .find(column => column.name === this.column.name).aggregation
          this.currentAggregation = aggregations ? aggregations.aggregation : ''
          break
        }
      }
    },
    aggregationChange(aggregation) {
      let data
      switch (this.selectedType.elementType) {
        case ELEMENT.GAUGE:
        case ELEMENT.HEAT_MAP:
        case ELEMENT.CHART: {
          data = this.elementData.config.grouping.aggregations.find(agg => agg.alias.includes(this.series.id))
          break
        }
        case ELEMENT.HTML_EDITOR:
        case ELEMENT.TABLE: {
          data = this.elementData.config.grouping.aggregations.find(agg => agg.column === this.column.name)
          break
        }
        case ELEMENT.CROSSTAB_TABLE: {
          data = this.elementData.config.yColumns.find(column => column.name === this.column.name).aggregation
        }
      }
      if (data) data.aggregation = aggregation
    },
    isGroupedColumn (name) {
      return findIndex(this.element.config.grouping.columns, col => col.name.includes(name))
    },
    // override apply function from axis mixins
    apply () {
      const bins = this.buildNewBinningForColumns()
      this.$emit('updateBins', {bins})
    }
  },
  created() {
    this.buildAggregations()
    this.getAggregationFromGrouping()
  }
}
</script>
<style scoped lang="scss">
  .text-transform {
    text-transform: capitalize;
    display: inline!important;
  }
</style>
