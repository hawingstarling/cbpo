<template>
  <div class="cbpo-aggregation-format-container">
    <!--Aggregation format type-->
    <b-form-group class="--bold" label="Aggregation Format Type">
      <b-form-select
        text-field="label"
        value-field="value"
        size="sm"
        v-model="aggregationType"
        :options="listAggregationTypes">
      </b-form-select>
    </b-form-group>
    <!--Format type-->
    <format-config-builder v-if="aggregationType" :format-config.sync="formatConfig"/>
  </div>
</template>
<script>
import { BOOL_TYPE, INT_TYPE, NUM_TYPE, TEMPORAL_TYPE, TEXT_TYPE } from '@/services/ds/data/DataTypes'
import FormatConfigBuilder from '@/components/formatBuilder/FormatConfigBuilder'
import cloneDeep from 'lodash/cloneDeep'
import { defaultFormatConfig } from '@/components/widgets/elements/table/TableConfig'

export default {
  name: 'AggregationFormatBuilder',
  props: {
    aggregationFormatConfig: Object
  },
  components: {
    'format-config-builder': FormatConfigBuilder
  },
  data() {
    return {
      aggregation: {},
      aggregationType: null,
      formatConfig: cloneDeep(defaultFormatConfig),
      listAggregationTypes: [
        { label: 'Selected a type', value: null },
        { label: 'Text', value: TEXT_TYPE.type },
        { label: 'Int', value: INT_TYPE.type },
        { label: 'Num', value: NUM_TYPE.type },
        { label: 'Temporal', value: TEMPORAL_TYPE.type },
        { label: 'Boolean', value: BOOL_TYPE.type }
      ]
    }
  },
  methods: {
    convertToAggregationFormat() {
      if (this.aggregationType) {
        this.aggregation[this.aggregationType] = this.formatConfig
        this.$emit('update:aggregationFormatConfig', this.aggregation)
      }
    }
  },
  created() {
    if (this.aggregationFormatConfig) {
      this.aggregation = cloneDeep(this.aggregationFormatConfig)
    }
    this.aggregationType = Object.keys(this.aggregation)[0] || null
    if (this.aggregationType) {
      this.formatConfig = cloneDeep(this.aggregation[this.aggregationType])
    }
  },
  watch: {
    aggregationType() {
      this.convertToAggregationFormat()
    },
    formatConfig() {
      this.convertToAggregationFormat()
    }
  }
}
</script>
