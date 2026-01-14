<template>
    <input :value="value"
    onkeydown="console.log('-')"
    class="form-control"
    @input='updateInput($event.target)'/>
</template>
<script>
import { regexNumber } from './regexFormat'
export default {
  name: 'CustomNumericInput',
  props: [
    'value',
    'type',
    'min',
    'max'
  ],
  data () {
    return {
      oldValue: ''
    }
  },
  methods: {
    validateFormat(value) {
      // If no type provided, treat as normal input
      if (!regexNumber[this.type]) {
        return true
      } else {
        return !value || regexNumber[this.type].test(value)
      }
    },
    validateMinMax(value, selectionStart) {
      // Wont check min max if: value empty, type '-' as the first character
      if (value === '' || !value || (selectionStart === 1 && value === '-' && this.min < 0)) {
        return true
      } else {
        let validMax = this.max ? Number(value) <= Number(this.max) : true
        let validMin = this.min ? Number(value) >= Number(this.min) : true
        return validMin && validMax
      }
    },
    // handel input and pointer potition
    updateInput(input) {
      let oldValue = this.value
      if (this.validateFormat(input.value) && this.validateMinMax(input.value, input.selectionStart)) {
        oldValue = input.value
        input.oldSelectionStart = input.selectionStart
        input.oldSelectionEnd = input.selectionEnd
      } else {
        input.value = oldValue
        input.setSelectionRange(input.oldSelectionStart || input.selectionStart, input.oldSelectionEnd || input.selectionEnd)
      }
      this.$emit('input', input.value)
    }
  }
}
</script>
