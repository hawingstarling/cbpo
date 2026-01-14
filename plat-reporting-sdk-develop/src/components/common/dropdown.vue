<template>
  <b-dropdown ref="refConfig" size="sm" class="dropdown-exp" toggle-class="text-decoration-none" no-caret>
    <b-dropdown-item @click="sendValueNodeData(EXPRESSION_SYNTAX.TODAY)">Today</b-dropdown-item>
    <b-dropdown-item @click="sendValueNodeData(EXPRESSION_SYNTAX.YESTERDAY)">Yesterday</b-dropdown-item>
    <b-dropdown-item @click="sendValueNodeData(EXPRESSION_SYNTAX.DATE_THIS)">Start date of month</b-dropdown-item>
    <b-dropdown-item @click="sendValueNodeData(EXPRESSION_SYNTAX.DATE_LAST)">Date from last 30 days</b-dropdown-item>
  </b-dropdown>
</template>

<script>
import { EXPRESSION_SYNTAX } from '@/services/ds/filter/FilterDefinitions'

export default {
  name: 'dropdownExpression',
  props: {
    index: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      EXPRESSION_SYNTAX
    }
  },
  methods: {
    sendValueNodeData(value) {
      this.$emit('setValueNodeData', {'index': this.index, 'value': value})
    },
    showDropdown: function () {
      this.$refs.refConfig.show()
    }
  }
}
</script>
