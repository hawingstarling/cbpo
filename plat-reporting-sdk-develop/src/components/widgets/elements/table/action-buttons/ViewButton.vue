<template>
  <div class="action-buttons view-btn">
    <b-button
      v-bind="config.props"
      :style="config.style"
      @click="viewDetail"
    >
      <i class="fa" :class="dataRow.showDetail ? config.icons.opened : config.icons.closed"></i>
      {{ config.label }}
    </b-button>
  </div>
</template>

<script>
export default {
  name: 'ViewButton',
  props: {
    config: {
      type: Object
    },
    dataRow: {
      type: Object
    },
    indexRow: Number
  },
  methods: {
    viewDetail () {
      this.$emit('showDetailView', {
        item: this.dataRow,
        index: this.indexRow
      })
    }
  }
}
</script>

<style lang="scss">
@import './ActionButtons.scss';
</style>
