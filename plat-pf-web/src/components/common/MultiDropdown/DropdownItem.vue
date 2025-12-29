<template>
  <b-dropdown
    class="select-dropdown dropdown-submenu"
    :id="`dropdown-child-${index}`"
    text
    :class="{'disabled-non-hover': ignoreState && ignoreState.base && ignoreState.base.value}"
    toggle-class="not-button"
    @show="opened = true"
    @hide="opened = false"
    no-caret
  >
    <template #button-content>
      {{ text }} <i class="fa fa-2x" v-if="options.length > 0" :class="opened ? 'fa-angle-right' : 'fa-angle-down'"></i>
    </template>
    <div v-for="(option, index) in options" :key="index">
      <MultiDropdown
        v-if="option.hasChildren"
        v-model="dataSelected"
        :text="option.text"
        :index="option.index"
        :options="option.children"
        :default="option.defaultOption"
        class="dropdown-submenu"
      ></MultiDropdown>
      <b-dropdown-item
        v-else
        :active="isSelected(option)"
        :title="option.text"
        @click="handlerSelectItem(option)"
      >
        {{ option.text }}<i v-if="isSelected(option)"></i>
      </b-dropdown-item>
    </div>
  </b-dropdown>
</template>

<script>
import isArray from 'lodash/isArray'

export default {
  name: 'MultiDropdown',
  props: {
    value: {
      type: [String, Array],
      required: true
    },
    text: String,
    index: Number,
    default: [String, Array],
    options: Array,
    ignoreState: Object
  },
  data() {
    return {
      opened: false,
      isDropdownVisible: false,
      isDropdownChildVisible: false,
      hideHandler: null
    }
  },
  methods: {
    handlerSelectItem(option) {
      // Check if the option is already selected
      const isCurrentlySelected = this.isSelected(option)
      if (isCurrentlySelected) {
        // Deselect: set to null and prevent dropdown from hiding
        this.$emit('input', null)
        this.$emit('change', null)
      } else {
        // Select the option - allow dropdown to close
        this.$emit('input', option)
        this.$emit('change', option)
      }
    }
  },
  computed: {
    selected: {
      get() {
        return this.$props.value || this.$props.default || (isArray(this.$props.value) ? [] : '')
      },
      set(val) {
        this.$emit('input', val)
      }
    },
    selectedText() {
      if (this.options) {
        const option = this.options.find(op => {
          return this.isSelected(op)
        })
        return (option && option.text) || ''
      }
      return this.text
    },
    dataSelected: {
      get() {
        return this.value || null
      },
      set(val) {
        this.$emit('input', val)
      }
    },
    isSelected() {
      return option => this.value ? option.text === this.value.text : false
    }
  }
}
</script>

<style lang="scss" scoped>
@import "./Dropdown.scss";
</style>
