<template>
  <div
    class="action-buttons action-btn"
    v-if="config.controls && config.controls.length > 0"
  >
    <b-button-group>
      <template v-if="multi || config.inline > 0">
        <template v-for="(actionInline, actionInlineIndex) in inlineActions">
          <b-button
            v-if="checkCondition(actionInline, actionInlineIndex, dataRow)"
            :key="`action-inline-${actionInlineIndex}`"
            :style="actionInline.style"
            v-bind="actionInline.props"
            @click.stop="
              actionInline.event(handledData),
                $emit('changeIcon', $event.target)
            "
          >
            <i class="fa" :class="actionInline.icon"></i>
            {{ actionInline.label }}
          </b-button>
        </template>
      </template>
      <!-- split -->
      <b-dropdown
        right
        v-bind="inlineActions[0].props"
        v-if="isDropdownActionsShown && !multi"
      >
        <b-dropdown-item
          v-for="(action, actionIndex) in dropdownActions"
          :key="actionIndex"
          v-bind="action.props"
          :style="action.style"
          @click.stop="action.event(handledData)"
        >
          <i class="fa" :class="action.icon"></i>
          {{ action.label }}
        </b-dropdown-item>
      </b-dropdown>
    </b-button-group>
  </div>
</template>

<script>
import isFunction from 'lodash/isFunction'

export default {
  name: 'ActionButtons',
  props: {
    config: {
      type: Object
    },
    dataRow: {
      type: [Object, Array]
    },
    items: {
      type: Array
    },
    multi: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    checkCondition() {
      return (item, index, dataRow) => {
        return isFunction(item.condition)
          ? item.condition(item, index, dataRow, this.handledData)
          : true
      }
    },
    maxInlineItem() {
      return this.config.inline <= 2 ? this.config.inline : 2
    },
    inlineActions() {
      return this.multi
        ? this.config.controls
        : this.config.controls.slice(0, this.maxInlineItem)
    },
    isDropdownActionsShown() {
      return this.config.controls.length - this.maxInlineItem > 0
    },
    dropdownActions() {
      return this.config.controls.slice(this.maxInlineItem)
    },
    handledData() {
      if (Array.isArray(this.dataRow)) {
        if (this.dataRow.length === 1) {
          // Multi Select but 1 Item
          return this.items.find((item) =>
            this.dataRow.includes(item.pk_id_sdk)
          )
        } else {
          // Multi Select and Multi Items
          let result = {}
          result.item_ids = this.items.filter((item) =>
            this.dataRow.includes(item.pk_id_sdk)
          )
          return result
        }
      } else {
        return this.dataRow
      }
    }
  }
}
</script>

<style lang="scss">
@import './ActionButtons.scss';
</style>
