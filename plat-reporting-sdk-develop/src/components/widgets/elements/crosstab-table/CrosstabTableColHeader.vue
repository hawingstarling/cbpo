<template>
  <table ref="table" class="cbpo-crosstab-table-header">
    <tr :key="`tr-${rowIndex}`" v-for="rowIndex of range(maxRows)">
      <th :colspan="getRowSpan(rowIndex)" :key="`td-${hI}`" v-for="(header, hI) of headers[rowIndex]">
        <span
          v-cbpo-format="getFormatConfig(rowIndex, header)"
          :style="colorStyle"
          :title="header && header.bin ? header.label : (header || 'empty')"
          class="cbpo-text-value"
          v-b-tooltip.hover.left
          />
      </th>
    </tr>
  </table>
</template>

<script>
import range from 'lodash/range'
import formatDirective from '@/directives/formatDirective'

export default {
  name: 'CrosstabTableColHeader',
  props: {
    tValues: Array,
    tColumns: Array,
    tBinColumns: Array,
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
      range: range,
      headers: [],
      maxRows: 0
    }
  },
  computed: {
    getFormatConfig() {
      return (rowIndex, value) => {
        // TODO: Refactor by format data before it render
        let column = this.tColumns[rowIndex]
        return {
          data: value,
          dataType: this.dm.columnNameToColumn[column.name].type,
          aggr: null,
          aggrFormat: null,
          bin: !!this.tBinColumns.find(_col => _col.column.name === column.name),
          format: column.format
        }
      }
    },
    getRowSpan() {
      return (indexRow) => {
        let array = [...this.tValues]
        array.splice(0, indexRow + 1)
        return array.reduce((total, value) => { total *= value.length; return total }, 1)
      }
    }
  },
  methods: {
    heightChange() {
      this.$nextTick(() => this.$emit('heightChange', this.$refs.table.clientHeight))
    },
    duplicateSubHeader(tValues) {
      this.headers = tValues.reduce((array, value, i) => {
        if (i === 0) {
          array = [...array, value]
        } else {
          let duplicates = []
          for (let i = 0; i < array[array.length - 1].length; i++) {
            duplicates = [...duplicates, ...value]
          }
          array = [...array, duplicates]
        }
        return array
      }, [])
    }
  },
  watch: {
    tValues: {
      deep: true,
      immediate: true,
      handler(tValues) {
        this.maxRows = tValues.length
        this.duplicateSubHeader(tValues)
        this.heightChange()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  .cbpo-crosstab-table-header {
    border-collapse: collapse;
    th {
      border-width: 1px;
      border-style: solid;
      font-weight: bold;
      text-align: center;
      &:first-child {
        border-left: none;
      }
    }
    tr {
      &:first-child {
        th {
          border-top: none;
        }
      }
      &:last-child {
        th {
          border-bottom: none;
        }
      }
      th:last-child {
        border-right: none;
      }
    }
  }
</style>
