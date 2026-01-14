<template>
  <div class="summaries">
    <div class="left-side" :class="{'custom-boder': hasGlobalGroupingLeftSeparator}">
      <template v-for="(sumLeft, sumLeftIndex) in summeriesData.left">
        <Summary :summary="sumLeft" :config="configObj" :key="sumLeftIndex" />
      </template>
    </div>
    <div class="right-side">
      <template v-for="(sum, sumIndex) in summeriesData.right">
        <Summary :summary="sum" :config="configObj" :key="sumIndex" />
      </template>
    </div>
  </div>
</template>

<script>
import Summary from './Summary'
import cloneDeep from 'lodash/cloneDeep'
import groupBy from 'lodash/groupBy'
import get from 'lodash/get'

export default {
  name: 'Summaries',
  components: {
    Summary
  },
  props: {
    summaries: {
      type: Array,
      default: () => []
    },
    configObj: {
      type: Object,
      default: () => {}
    }
  },
  computed: {
    hasGlobalGroupingLeftSeparator () {
      return get(this.configObj, 'bulkActions.enabled', false) && get(this.configObj, 'globalControlOptions.globalGrouping.position') === 'table'
    }
  },
  data () {
    return {
      summeriesData: []
    }
  },
  methods: {
    convertSummaries () {
      const clonedSummaries = cloneDeep(this.summaries)
      const groupedList = groupBy(clonedSummaries, 'position')
      this.summeriesData = {...groupedList}
    }
  },
  created () {
    this.convertSummaries()
  }
}
</script>

<style lang="scss" scoped>
  .summaries {
    font-size: 12px;
    display: flex;
    align-items: center;
    flex: auto;
    .left-side {
      margin-right: auto;
      &.custom-boder {
        border-left: 1px solid #d9d9d9;
        margin-left: 0.5rem;
      }
    }
    .right-side {
      margin-left: auto;
    }
  }
</style>
