<template>
  <div class="cbpo-detail-layout">
    <div class="cbpo-row">
      <div class="cbpo-col" v-for="colIndex in colsLayout" :key="colIndex" :style="{width: `${colWidth}%`}">
        <b-row v-for="(column, cellIndex) of columns" :key="cellIndex" class="cbpo-1-row">
          <div class="cbpo-1-col" :style="{'width': `${columnStyles.col1}px`}">
            <strong class="text custom-text">{{ column.displayName || column.name }}</strong>
          </div>
          <div class="cbpo-2-col" :style="{'width': columnStyles.col1 ? `calc(100% - ${columnStyles.col1}px)` : ''}">
            <span class="text custom-text"
              v-html="item.data[column.name].format">
            </span>
          </div>
        </b-row>
      </div>
    </div>
  </div>
</template>

<script>
import formatDirective from '@/directives/formatDirective'

export default {
  props: {
    item: Object,
    configObj: Object,
    columns: Array,
    tableWidth: Number
  },
  directives: {
    'cbpo-format': formatDirective
  },
  data () {
    return {
      columnsGroup: {},
      colsLayout: 1,
      columnStyles: {}
    }
  },
  computed: {
    colWidth () {
      return 100 / this.colsLayout
    }
  },
  methods: {
    buildGridItem () {
      // const columnsGroup = {}
      // const colsNum = this.metaCols.length
      // const limit = Math.ceil(colsNum / this.colsLayout)
      // for (let x = 0; x < this.colsLayout; x++) {
      //   columnsGroup[x] = []
      //   for (let y = 0; y < colsNum; y++) {
      //     if (parseInt(y / limit) === x) columnsGroup[x].push(this.visibleColumns[y])
      //   }
      // for (let y = 0; y < colsNum; y++) {
      //   const column = cloneDeep(this.columns[y])
      //   if (column.detailColIndex === x) {
      //     columnsGroup[x].push(this.visibleColumns[y])
      //   } else if (column.detailColIndex >= this.colsLayout) {
      //     columnsGroup[this.colsLayout - 1].push(this.visibleColumns[y])
      //   }
      // }
      // }
      // this.columnsGroup = {...columnsGroup}
    },
    onResize () {
      const breakpoints = this.configObj.detailView.breakpoints || {}
      for (let threshold in breakpoints) {
        const parsedThreshold = parseInt(threshold)
        if (window.innerWidth >= parsedThreshold) {
          this.colsLayout = parseInt(breakpoints[threshold])
        }
      }
      this.buildGridItem()
      // col width
      if (this.colsLayout === 1) {
        const col1 = this.tableWidth * 40 / 100
        this.columnStyles.col1 = col1
      }
    }
  },
  mounted() {
    this.onResize()
  },
  watch: {
    tableWidth (newVal, oldVal) {
      if (newVal && newVal !== oldVal) {
        this.onResize()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  @import './InlineDetail.scss';
</style>
