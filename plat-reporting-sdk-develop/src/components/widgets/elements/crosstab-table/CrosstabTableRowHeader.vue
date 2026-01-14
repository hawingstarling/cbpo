<template>
  <table class="cbpo-crosstab-table-last-left-column">
    <tbody>
      <tr :key="`last-left-tr-${ih}`" v-for="(header, ih) of headers">
        <td :class="{'rowspan-td': getRowSpan(ih, iv) > 1, 'no-border-bottom-td': isLastValue(), 'no-border-left-td': header.length === 1}"
            :rowspan="getRowSpan(ih, iv)"
            :key="`last-left-td-${iv}`"
            v-for="(value , iv) of header">
          <span :style="colorStyle" class="cbpo-text-value" v-cbpo-format="getFormatConfig(value, iv)"/>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import range from 'lodash/range'
import reverse from 'lodash/reverse'
import isEqual from 'lodash/isEqual'
import isEmpty from 'lodash/isEmpty'
import forEachRight from 'lodash/forEachRight'
import formatDirective from '@/directives/formatDirective'

export default {
  name: 'CrosstabTableRowHeader',
  props: {
    xValues: Array,
    xColumns: Array,
    xHeaders: Array,
    xBinColumns: Array,
    dm: Object,
    colorStyle: {
      type: Object,
      default() {
        return {}
      }
    }
  },
  data() {
    return {
      lastValues: [],
      range: range,
      headers: []
    }
  },
  directives: {
    'cbpo-format': formatDirective
  },
  computed: {
    getFormatConfig() {
      return (value, indexHeader) => {
        let column = this.xColumns[indexHeader]
        return {
          data: value,
          dataType: this.dm.columnNameToColumn[column.name].type,
          aggr: null, // tab table does not have aggregation
          aggrFormat: null,
          bin: !!this.xBinColumns.find(_col => _col.column.name === column.name),
          format: column.format
        }
      }
    },
    getRowSpan() {
      return (indexRow, indexTd) => {
        if (this.headers[indexRow].length === 1) return 1
        let array = [...this.xValues]
        array.splice(0, indexTd + 1)
        return array.reduce((total, value) => { total *= value.length; return total }, 1)
      }
    },
    isLastValue() {
      return value => this.lastValues.includes(value)
    }
  },
  methods: {
    clearDuplicateValueOnRow(headers) {
      let newHeaders = []
      forEachRight(headers, (header, i) => {
        if (isEmpty(headers[i - 1])) {
          newHeaders.push(headers[i]); return newHeaders
        }
        newHeaders.push(this.getDifferentDataBetweenTwoHeaders(header, headers[i - 1]))
      })
      return reverse(newHeaders)
    },
    getDifferentDataBetweenTwoHeaders(head1, head2) {
      if (head1.length !== head2.length) throw new Error('Invalid Header!!! header 1 and header 2 have different length')
      let indexMatch = 0
      let startIndex = 0
      while (startIndex !== head1.length) {
        if (isEqual(head1[startIndex], head2[startIndex])) {
          indexMatch = (startIndex + 1)
          break
        }
        startIndex++
      }
      let newHead = [...head1]
      newHead.splice(0, indexMatch)
      return newHead
    }
  },
  watch: {
    xValues: {
      deep: true,
      immediate: true,
      handler(xValues) {
        this.headers = this.clearDuplicateValueOnRow(this.xHeaders)
        this.lastValues = xValues.map(values => values[values.length - 1])
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  .cbpo-crosstab-table-last-left-column {
    /*border-right-style: hidden;*/
    width: 100%;
    border-collapse: collapse;
    td {
      border-width: 1px;
      border-style: solid;
      .rowspan-td {
        border-right: none;
      }
      .no-border-left-td  {
        border-left: none;
      }
      ::v-deep span.d-sdk-na,::v-deep span.d-sdk-empty,::v-deep span.d-sdk-nil {
        line-height: normal;
        border-radius: 3px;
        padding: 0 $spacing;
        display: inline-block;
        font-size: 90%;
      }
    }
    tr {
      > td:first-child {
        border-left: none;
      }
    }
  }
</style>
