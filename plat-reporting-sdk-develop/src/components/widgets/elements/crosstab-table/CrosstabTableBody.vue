<template>
  <table class="cbpo-crosstab-table-cell">
    <tr :key="`${rowIndex}-index-row`" :class="{'row-even': (rowIndex % 2) === 0 }" v-for="(yValue, rowIndex) of yValues">
      <template v-for="(value, colIndex) of yValue">
        <template v-for="(cellValue, cellIndex) of getYValueOnly(value)">
          <td class="body-td" :key="`${rowIndex}-${colIndex}-${cellIndex}-index-row`">
            <span :style="colorStyle" class="cbpo-text-value" v-cbpo-format="getFormatConfig(cellIndex, cellValue)"/>
          </td>
        </template>
      </template>
    </tr>
  </table>
</template>

<script>

import range from 'lodash/range'
import isEmpty from 'lodash/isEmpty'
import isNull from 'lodash/isNull'
import formatDirective from '@/directives/formatDirective'
export default {
  name: 'CrosstabTableBody',
  props: {
    yValues: Array,
    yColumns: Array,
    yBinColumns: Array,
    dm: Object,
    colorStyle: {
      type: Object,
      default() {
        return {}
      }
    }
  },
  directives: {
    'cbpo-format': formatDirective
  },
  data() {
    return {
      range: range
    }
  },
  computed: {
    getYValueOnly() {
      return values => {
        if (isNull(values[0])) return values
        let indexes = this.yColumns.map(column => {
          if (isEmpty(this.yBinColumns)) return this.dm.columnNameToIndex[column.aggregation.alias]
          let binColumn = this.yBinColumns.find(col => col.column.name === column.name)
          return this.dm.columnNameToIndex[binColumn ? binColumn.alias : column.aggregation.alias]
        })
        return values.filter((value, i) => indexes.includes(i))
      }
    },
    getFormatConfig() {
      return (cellIndex, cellValue, test) => {
        let column = this.yColumns[cellIndex]
        return {
          data: cellValue,
          dataType: this.dm.columnNameToColumn[column.aggregation.alias].type,
          aggr: null,
          aggrFormat: null,
          bin: !!this.yBinColumns.find(binColumn => binColumn.name === column.name),
          format: column.format
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  .cbpo-crosstab-table-cell {
    td {
      border-width: 1px;
      border-style: solid;
      ::v-deep span.d-sdk-na,::v-deep span.d-sdk-empty,::v-deep span.d-sdk-nil {
        line-height: normal;
        border-radius: 3px;
        padding: 0 $spacing;
        display: inline-block;
        font-size: 90%;
      }
    }

    tr {
      background-color: #ffffff;
      td:first-child {
        border-left: none;
      }
      td:last-child {
        border-right: none;
      }
    }
  }
</style>
