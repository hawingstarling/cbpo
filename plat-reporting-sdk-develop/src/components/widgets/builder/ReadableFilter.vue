<template>
  <div :class="classCss" v-if="filter">
    <div class="filter-popover-left" role="tooltip">
      <div class="arrow"></div>
      <div class="readable-filter" v-html="filter"></div>
    </div>
  </div>
</template>
<script>
import { ReadableFilterExpression } from '@/services/ds/filter/FilterExpessionBuilders'
import isEmpty from 'lodash/isEmpty'
import CBPO from '@/services/CBPO'

export default {
  name: 'ReadableFilter',
  props: {
    dataFilter: Object,
    classCss: {
      type: Object,
      default: () => ({})
    },
    dataColumns: Array
  },
  computed: {
    updatedColumnsState () {
      return CBPO.channelManager().getChannel().getColumnSvc().getColumns()
    }
  },
  data() {
    return {
      filterBuilder: new ReadableFilterExpression(),
      filter: undefined
    }
  },
  watch: {
    dataFilter: {
      deep: true,
      handler(val) {
        if (!isEmpty(val)) {
          this.filter = window.CBPO.dataQueryManager().getFilterReadableFromFilter(val, this.dataColumns)
        } else {
          this.filter = undefined
        }
      }
    },
    updatedColumnsState: {
      deep: true,
      handler(val) {
        if (!isEmpty(val) && !isEmpty(this.dataFilter)) {
          this.filter = window.CBPO.dataQueryManager().getFilterReadableFromFilter(this.dataFilter, this.dataColumns)
        } else {
          this.filter = undefined
        }
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  /deep/ .filter-popover-left{
    border-radius: .3rem;
    position: relative;
    margin-right: .5rem;
    border: 1px solid rgba(0,0,0,.25);
    cursor: default;
    .arrow{
      right: calc((.5rem + 1px) * -1);
      width: .5rem;
      height: 1rem;
      margin: .3rem 0;
      position: absolute;
      top: 2px;
      display: block;
      &::before{
        position: absolute;
        display: block;
        content: "";
        border-color: transparent;
        border-style: solid;
        border-width: .5rem 0 .5rem .5rem;
        right: 0;
        border-left-color: rgba(0,0,0,.25);
      }
      &::after{
        position: absolute;
        display: block;
        content: "";
        border-color: transparent;
        border-style: solid;
        border-width: .5rem 0 .5rem .5rem;
        right: 1px;
        border-left-color: #fff;
      }
    }
  }
  /deep/ .readable-filter{
    height: 100%;
    font-weight: 500;
    display: inline-block;
    width: 100%;
    // white-space: nowrap;
    overflow: hidden !important;
    text-overflow: ellipsis;
    text-align: left;
    padding: 0 10px;
    span{
      vertical-align: middle;
    }
  }
</style>
