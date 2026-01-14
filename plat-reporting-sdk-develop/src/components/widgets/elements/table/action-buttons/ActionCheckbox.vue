<template>
  <div class="checkbox" v-show="!multi || (multi && dataLength > 0)">
    <div
      class="action-checkbox"
      :class="{
      'action-checkbox--checked': checked,
      'action-checkbox--partial-checked': checkedState === 'partial-checked'
      }"
      role="checkbox"
      @click="onClick()"
    ></div>
    <template v-if="multi">
      <span v-if="checkedState === 'unchecked'" class="select-none" @click="onClick()">Select All</span>
      <span v-if="dataRow && this.dataRow.length > 0 && !isSelectedAll" class="pr-2">{{ countItemSelected }} selected</span>
      <template v-if="dataRow && this.dataRow.length > 0 && !isCountFetching">
        <span @click="selectAllData" v-if="canShowLabel" class="cbpo-message" :class="{ '--no-action': isSelectedAll }">
          {{ isSelectedAll ? getAllSelectedLabel : getSelectAllLabel }}
        </span>
      </template>
      <template v-if="dataRow && this.dataRow.length > 0 && !isSelectedAll && isCountFetching">
        <div class="spinner-container">
          <i class="fa fa-circle-o-notch fa-spin"></i>
        </div>
      </template>
    </template>
  </div>
</template>

<script>
import isArray from 'lodash/isArray'
import dataFormatManager, { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'

export default {
  name: 'ActionCheckbox',
  props: {
    isCountFetching: {
      type: Boolean,
      default: false
    },
    bulkEventMode: {
      type: Boolean,
      default: false
    },
    isChecked: {
      type: Boolean,
      default: false
    },
    isSelectedAll: {
      type: Boolean,
      default: false
    },
    multi: {
      type: Boolean,
      default: false
    },
    checkedState: {
      type: String, // 'checked', 'unchecked', 'partial-check'
      default: 'unchecked'
    },
    dataRow: {
      type: [Object, Array],
      default: () => {
      }
    },
    dataLength: {
      type: Number,
      default: 0
    },
    count: {
      type: [Number, String],
      default: 0
    },
    labels: Object
  },
  data() {
    const formatFn = dataFormatManager.create({
      type: FORMAT_DATA_TYPES.NUMERIC,
      config: {
        precision: 0
      }
    }, false)
    return {
      formatFn
    }
  },
  computed: {
    canShowLabel() {
      return isArray(this.dataRow)
        ? this.checked && this.dataRow.length < this.count && this.dataRow.length === this.dataLength
        : false
    },
    getSelectAllLabel() {
      return this.labels.selectAll.replace(/\$total/, this.formatFn(this.count))
    },
    getAllSelectedLabel() {
      return this.labels.allSelected.replace(/\$total/, this.formatFn(this.count))
    },
    checked() {
      if (this.multi) {
        return this.checkedState === 'checked'
      }
      return this.isChecked
    },
    countItemSelected() {
      return this.formatFn(this.dataRow.length)
    }
  },
  methods: {
    onClick(e) {
      if (this.multi) this.$emit('onClick')
    },
    selectAllData() {
      this.$emit('allItemSelected')
    }
  }
}
</script>

<style lang="scss" scoped>
.checkbox {
  display: flex;
  justify-content: center;
  align-items: center;

  span {
    font-size: 12px;
    padding-bottom: 1px;
  }

  .select-none {
    user-select: none;
  }
}

.action-checkbox {
  vertical-align: text-bottom;
  font-size: 1px;
  border-radius: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  outline: none;
  position: relative;
  z-index: 0;
  background-color: transparent;
  border: none;
  box-shadow: none;
  height: 26px;
  width: 30px;
  margin: 0;
  opacity: 0.16;
  cursor: pointer;
  background-image: url('~@/assets/images/icons/checkbox_outline_black.png');
  background-position: center;
  background-repeat: no-repeat;
  background-size: 18px;

  &--checked {
    background-image: url('~@/assets/images/icons/checkbox_black.png');
    background-position: center;
    background-repeat: no-repeat;
    background-size: 18px;
    opacity: 0.54;
  }

  &--partial-checked {
    background-image: url('~@/assets/images/icons/indeterminate_checkbox_black.png');
    background-position: center;
    background-repeat: no-repeat;
    background-size: 18px;
    opacity: 0.54;
  }

  &:hover {
    opacity: 1;
  }
}

.cbpo-message {
  padding-right: 5px;
  &:not(.--no-action) {
    cursor: pointer;
  }
}

.spinner-container {
  padding-right: 8px;
}
</style>

<style lang="scss">
// Dark-theme
.cbpo-sdk-dark-theme {
  .action-checkbox {
    background-image: url('~@/assets/images/icons/checkbox_outline_white.png');

    &--checked {
      background-image: url('~@/assets/images/icons/checkbox_white.png');
    }

    &--partial-checked {
      background-image: url('~@/assets/images/icons/indeterminate_checkbox_white.png');
    }
  }
}
</style>
