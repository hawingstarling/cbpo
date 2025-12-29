<template>
  <b-form-checkbox v-model="dataValue" name="check-button" switch>
  </b-form-checkbox>
</template>

<script>
export default {
  name: 'ComboBox',
  props: {
    type: String,
    name: String,
    options: Array,
    value: [String, Boolean],
    disabled: Boolean,
    size: {
      type: String,
      default: 'md'
    },
    rules: Array,
    validateIf: {
      validator: prop => typeof prop === 'boolean' || prop === null,
      default: true
    }
  },
  computed: {
    dataValue: {
      get() {
        return this.$props.value || false
      },
      set(val) {
        this.$emit('input', val)
      }
    }
  }
}
</script>
