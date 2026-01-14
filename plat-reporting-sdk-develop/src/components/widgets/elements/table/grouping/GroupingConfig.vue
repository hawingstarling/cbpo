<template>
  <div class="cbpo-grouping-container">
    <div class="grouping-row">
      <div class="label">
        <span>Grouping</span>
      </div>
      <div class="action">
        <b-form-checkbox v-model="model.isGrouped" switch :disabled="globalGrouping">
        </b-form-checkbox>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'GroupingConfig',
  props: {
    grouping: Object,
    selected: Object,
    globalGrouping: Boolean
  },
  data() {
    return {
      model: this.selected
    }
  },
  watch: {
    model: {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal !== oldVal) {
          this.$emit('input:selected', newVal)
        }
      }
    }
  }
}
</script>
<style scoped lang="scss">
  .grouping-row {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    .label {
      width: 100%;
      padding: 0.5rem 0;
    }
    .action {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      width: 120px;
    }
  }
</style>
