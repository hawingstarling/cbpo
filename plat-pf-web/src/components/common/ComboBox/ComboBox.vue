<template>
  <div class="combobox">
    <ValidationProvider
      :name="filteredName(name)"
      immediate
      :rules="validateRules"
      v-slot="{ errors }"
      :vid="name"
    >
      <b-input-group
        class="pf-input"
        :size="size"
        :class="{ 'is-invalid': errors.length }"
      >
        <b-form-input
          class="combobox__input"
          autocomplete="off"
          v-model="dataValue"
          :placeholder="placeholder"
          :disabled="disabled"
          @click="toggleAutocompleteDropdown"
          @keyup.enter.prevent="select(selectedIndex)"
          @keydown.down.prevent="selectNext()"
          @keydown.up.prevent="selectPrev()"
          @keyup.8="handleBackspace()"
          @blur="showAutocompleteDropdown = false"
          :readonly="isSelectType"
          :state="isHasError(errors)"
        ></b-form-input>
        <ul
          class="combobox-list"
          v-show="showAutocompleteDropdown"
          @mousedown.prevent
        >
          <li
            class="combobox-list__item"
            v-for="(item, index) in filteredList"
            :key="index"
            @click="select(index)"
            v-bind:class="{
              'combobox-list__item--selected': index == selectedIndex
            }"
            v-html="$options.filters.highlight(item, dataValue)"
          >
            {{ item }}
          </li>
        </ul>
      </b-input-group>
      <b-form-checkbox
        v-for="(param, key, index) in params"
        :key="`${key}-${index}`"
        v-model="param.value"
        :name="`${key}-checkbox`"
        class="combobox__param-checkbox"
        :size="size"
        @input="changeParam($event)"
        :value="param.checkedValue"
        :unchecked-value="param.uncheckedValue"
      >
        {{ param.label }}
      </b-form-checkbox>
      <b-form-invalid-feedback v-if="errors.length">
        {{ errors[0] }}
      </b-form-invalid-feedback>
    </ValidationProvider>
  </div>
</template>

<script>
import _ from 'lodash'
import '@/plugins/vee-validate'
import { checkFieldFormatMixins, validateMixins } from '@/shared/utils'

export default {
  name: 'ComboBox',
  props: {
    type: String,
    name: String,
    options: Array,
    params: Object,
    value: [String, Boolean],
    optionType: String,
    placeholder: String,
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
  data() {
    return {
      showAutocompleteDropdown: false,
      selectedIndex: 0,
      isSearching: true
    }
  },
  mixins: [checkFieldFormatMixins, validateMixins],
  filters: {
    highlight(word, query) {
      var check = new RegExp(query, 'ig')
      return word.toString().replace(check, function(matchedText) {
        return '<strong>' + matchedText + '</strong>'
      })
    }
  },
  computed: {
    dataValue: {
      get() {
        return this.$props.value || ''
      },
      set(val) {
        this.$emit('input', val)
      }
    },
    validateRules() {
      return this.validateIf ? this.stringRules(this.rules) : null
    },
    isSelectType() {
      return this.type === 'select'
    },
    filteredList() {
      if (this.dataValue && !this.isSelectType) {
        const matched = this.options.filter(
          item =>
            item.toLowerCase().indexOf(this.dataValue.toLowerCase()) !== -1
        )
        const unmatched = this.options.filter(
          item =>
            item.toLowerCase().indexOf(this.dataValue.toLowerCase()) === -1
        )
        return matched.concat(unmatched)
      }
      return this.options
    }
  },
  methods: {
    toggleAutocompleteDropdown() {
      this.showAutocompleteDropdown = !this.showAutocompleteDropdown
    },
    handleBackspace() {
      this.showAutocompleteDropdown = true
    },
    select(index) {
      this.isSearching = false
      const cloneFilteredList = JSON.parse(JSON.stringify(this.filteredList))
      this.showAutocompleteDropdown = false
      this.dataValue = cloneFilteredList[index]
      this.$emit('keyup', { type: this.optionType, value: '' })
    },
    selectNext() {
      if (this.showAutocompleteDropdown) {
        if (this.selectedIndex < this.filteredList.length - 1) {
          this.selectedIndex++
        } else {
          this.selectedIndex = 0
        }
      } else {
        this.showAutocompleteDropdown = true
      }
    },
    selectPrev() {
      if (this.selectedIndex > 0) {
        this.selectedIndex--
      } else {
        this.selectedIndex = this.filteredList.length - 1
      }
    },
    changeParam: _.debounce(function() {
      this.$emit('changeParam', {
        type: this.optionType,
        value: this.dataValue,
        params: this.params
      })
    }, 500)
  },
  watch: {
    dataValue: _.debounce(function(newValue) {
      if (!this.isSelectType && this.isSearching) {
        this.$emit('keyup', { type: this.optionType, value: newValue })
      }
      this.isSearching = true
    }, 500)
  }
}
</script>

<style lang="scss" scoped>
@import "./ComboBox.scss";
</style>
