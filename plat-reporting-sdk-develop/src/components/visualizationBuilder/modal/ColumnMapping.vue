<template>
  <div class="preset-column-mapping" v-if="presetConfig">
    <p>
      Your data source has different columns from the selected preset.<br/>
      Please manually map the columns to populate your expectation.
    </p>
    <div class="table-responsive-sm">
      <table class="b-table table table-bordered table-striped bv-docs-table">
        <thead>
          <tr>
            <th>Zone</th>
            <th>Preset</th>
            <th>Target Data Source</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(zone, axis) in presetConfig.zones">
            <template v-for="(item, index) in zone">
              <tr :key="`${axis}_${index}`">
                <td class="text-nowrap">{{getZoneTitle(axis, index)}}</td>
                <td class="text-nowrap">{{getPresetTitle(item, axis, index)}}</td>
                <td>
                  <select @change="changeColumn($event.target.value, axis, index)" :value="getDefaultValue(item)">
                    <option value="">Select Column</option>
                    <template v-for="(column, key) in targetColumns">
                      <option :key="`field_${key}`" :value="key">{{column.displayName || column.name}}</option>
                    </template>
                  </select>
                  <span :ref="`${axis}_${index}_type`">{{getDefaultType(item)}}</span>
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </div>
  <div v-else>
    <p>Your preset configuration is invalid. </p>
  </div>
</template>
<script>

import {isEmpty, cloneDeep, toUpper, get, find, upperFirst, findIndex, some} from 'lodash'
import { AXIS, ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { createBinColumnAliasInAxis, createBinColumnAlias } from '@/utils/binUtils'

export default {
  name: 'ColumnMapping',
  props: {
    presetConfig: Object,
    targetColumns: Array,
    isApply: Boolean
  },
  data() {
    return {
      presetData: null
    }
  },
  computed: {
    getZoneTitle() {
      return (axis, index) => {
        return axis === AXIS.Y ? `${toUpper(axis)} Axis ${index + 1}` : `${toUpper(axis)} Axis`
      }
    },
    getPresetTitle() {
      return ({name, type, displayName}, axis, index) => {
        let {columns, aggregations} = get(this.presetConfig, 'elementConfig.config.grouping', {columns: [], aggregations: []})
        let aggr = find(aggregations, {column: name})
        let bins = get(this.presetConfig, 'elementConfig.config.bins', [])
        let isGrouped = columns.find(col => col.name === name || col.name === createBinColumnAlias(name))
        let binAlias = ''
        const elementType = get(this.presetConfig, 'elementConfig.type', '')
        switch (elementType) {
          case ELEMENT.CHART:
          case ELEMENT.GAUGE:
            const seriesItem = get(this.presetConfig, `elementConfig.config.charts[0].series[${index}]`, [])
            binAlias = createBinColumnAliasInAxis(seriesItem, { name }, axis)
            break
          default:
            binAlias = createBinColumnAlias(name)
            break
        }
        const isBinned = bins.findIndex(bin => bin.alias === binAlias)
        return `[${displayName}]
                [${upperFirst(type)}]
                ${isGrouped ? `[Grouped]` : ``}
                ${isBinned !== -1 ? `[Binned]` : ``}
                ${aggr ? `[Aggregation: ${upperFirst(aggr.aggregation)}]` : ``}`
      }
    },
    getDefaultValue() {
      return ({name}) => {
        let index = findIndex(this.targetColumns, {name})
        return !(index < 0) ? index : ``
      }
    },
    getDefaultType() {
      return ({type, name}) => {
        let index = findIndex(this.targetColumns, {name})
        return !(index < 0) ? ` [${upperFirst(type)}]` : ``
      }
    }
  },
  methods: {
    getConfig() {
      return cloneDeep(this.presetData)
    },
    changeColumn(columnIndex, axis, index) {
      let idType = `${axis}_${index}_type`
      let column = this.targetColumns[columnIndex] || {}
      this.$refs[idType][0].innerText = column.type ? ` [${upperFirst(column.type)}]` : ``
      this.$set(this.presetData.zones[axis], index, column)
      this.$emit('update:isApply', !some(this.$refs, (e) => e[0].innerText === ``))
    }
  },
  watch: {
    presetConfig: {
      immediate: true,
      deep: true,
      handler: function(val) {
        if (!isEmpty(val)) {
          this.presetData = cloneDeep(val)
        }
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  .table-column-mapping {
    thead th {
      border-bottom-width: 2px;
    }
  }
</style>
