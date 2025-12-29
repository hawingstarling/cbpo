<template>
  <div class="select-input">
    <div class="label">{{ label }}</div>
    <b-dropdown class="select-dropdown"
      :class="{ 'disabled-non-hover': ignoreState && ignoreState.base && ignoreState.base.value }"
      toggle-class="not-button" @show="opened = true" @hide="opened = false" no-caret>
      <template #button-content>
        {{ selectedText }}<i class="fa fa-2x" :class="opened ? 'fa-angle-up' : 'fa-angle-down'"></i>
      </template>
      <b-dropdown-item v-for="(option, index) in options" v-bind:key="index" :active="isSelected(option)"
        @click="selected = option.value; $emit('change', option)">
        {{ option.text }}<i v-if="isSelected(option)"></i>
      </b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
import isArray from 'lodash/isArray'
import isEqual from 'lodash/isEqual'

export default {
  name: 'SelectInput',
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
    isDataRange: {
      type: Boolean,
      default: false
    },
    options: Array,
    ignoreState: Object
  },
  data() {
    return {
      opened: false
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
      const option = this.options.find(op => this.isSelected(op))
      if (this.isDataRange) {
        return (option && option.text) || 'Select Date Range'
      }
      return (option && option.text) || ''
    },
    isSelected() {
      return option => {
        return isArray(option.value)
          ? isEqual(option.value, this.selected)
          : option.value === this.selected
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.select-input {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  min-width: 120px !important;
}

.label {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.33;
  letter-spacing: 0.12px;
  color: #667085;
}

::v-deep .select-dropdown {
  width: 100%;
  height: 36px;

  &.show .dropdown-toggle {
    background-color: unset;
    border: 1px solid #E6E8F0;
    &:focus,
    &:active {
      box-shadow: none ; // Remove the box-shadow on click and focus
    }
  }

  &.disabled-non-hover:not(:hover) .dropdown-toggle {
    background-color: #E9ECEf;
    color: #6C757D;
  }

  .dropdown-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 10px;
    font-weight: normal;
    font-size: 12px;
    color: #232F3E;

    &:hover {
      color: #232F3E !important;
      background-color: #FFFFFF !important;
    }

    &:focus {
      box-shadow: none;
    }

    i {
      font-size: 20px;
      color: #667085;
    }
  }

  .dropdown-menu {
    width: 100%;
    padding: 0;
    border-radius: 0 0 5px 5px;
    margin-top: 1px;
    font-size: 12px;
    text-align: left;
    box-shadow: 0 4px 5px 0 rgba(16, 24, 40, 0.25);

    .dropdown-item {
      display: inline-flex;
      justify-content: space-between;
      padding: 8px 6px 8px 10px;

      &.active {
        color: #232F3E;
        background-color: #F2F4F7;
      }

      i {
        width: 18px;
        height: 14px;
        margin: 0 2px;
        background-size: 100%;
      }
    }
  }
}
</style>
