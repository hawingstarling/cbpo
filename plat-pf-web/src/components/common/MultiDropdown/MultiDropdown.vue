<template>
  <div class="select-input">
    <div class="label">{{ label }}</div>
    <b-dropdown
      id="dropdown-main"
      class="select-dropdown"
      ref="dropdownMain"
      :class="{'disabled-non-hover': ignoreState && ignoreState.base && ignoreState.base.value}"
      toggle-class="not-button"
      @show="opened = true; isChangeValue = false"
      @hide="opened = false"
      no-caret
    >
      <template #button-content>
        {{ selectedText }} <i class="fa fa-2x" :class="opened ? 'fa-angle-up' : 'fa-angle-down'"></i>
      </template>
      <div v-for="(option, index) in options" :key="index">
        <DropdownItem
          v-if="option.hasChildren"
          v-model="dataSelected"
          :text="option.text"
          :index="option.index"
          :options="option.children"
          :default="option.defaultOption"
          class="dropdown-submenu"
        ></DropdownItem>
        <b-dropdown-item
          v-else
          :active="isSelected(option)"
          @click="selected = option.value; $emit('change', option)"
        >
        </b-dropdown-item>
      </div>
    </b-dropdown>
  </div>
</template>

<script>
import isArray from 'lodash/isArray'
import isEqual from 'lodash/isEqual'

import DropdownItem from '@/components/common/MultiDropdown/DropdownItem'

export default {
  name: 'MultiDropdown',
  props: {
    value: {
      type: [String, Array],
      required: true
    },
    default: [String, Array],
    label: {
      type: String,
      required: true
    },
    text: String,
    options: Array,
    ignoreState: Object
  },
  components: {
    DropdownItem
  },
  data() {
    return {
      opened: false,
      isChangeValue: false,
      isDropdownVisible: false,
      isDropdownChildVisible: false
    }
  },
  methods: {
  },
  computed: {
    dataSelected: {
      get() {
        return this.value || null
      },
      set(val) {
        this.isChangeValue = true
        this.$emit('input', val)
      }
    },
    selectedText() {
      if (this.text) {
        return this.text
      }
      if (this.options) {
        const option = this.options.find(op => {
          return this.isSelected(op)
        })
        return (option && option.text) || ''
      }
      return ''
    },
    isSelected() {
      return option => {
        return isArray(option.value) ? isEqual(option.value, this.selected) : option.value === this.$props.default
      }
    }
  },
  mounted() {
    this.$root.$on('bv::dropdown::show', bvEvent => {
      if (bvEvent.componentId === 'dropdown-child-0') {
        this.isDropdownVisible = true
        this.isDropdownChildVisible = false // Reset child state when parent opens
      }
      if (bvEvent.componentId === 'dropdown-child-1') {
        this.isDropdownChildVisible = true
      }
    })

    this.$root.$on('bv::dropdown::hide', bvEvent => {
      // Handle dropdown-child-0 (first level child)
      if (bvEvent.componentId === 'dropdown-child-0') {
        if (this.isDropdownChildVisible) {
          // If child-1 is open, prevent child-0 from closing
          bvEvent.preventDefault()
        } else {
          this.isDropdownVisible = false
        }
      }

      // Handle dropdown-child-1 (second level child)
      if (bvEvent.componentId === 'dropdown-child-1') {
        this.isDropdownChildVisible = false
      }

      // Prevent main dropdown from closing when child is open and no value change occurred
      if (bvEvent.componentId === 'dropdown-main') {
        // Prevent closing if a child dropdown is open and no value has changed
        if ((this.isDropdownVisible || this.isDropdownChildVisible) && !this.isChangeValue) {
          bvEvent.preventDefault()
        }
      }
    })
  },
  watch: {
    dataSelected() {
      const dropdown = this.$refs.dropdownMain
      if (!dropdown) {
        return
      }
      dropdown.hide()
    }
  }
}
</script>

<style lang="scss" scoped>
@import "./Dropdown.scss";
</style>
