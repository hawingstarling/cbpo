<template>
  <div
    :class="{'--disabled': disabled}"
    class="sdk-dropdown__container"
    v-on-clickaway="{ callback: closeDropdown }">

    <!-- Input trigger builder -->
    <div class="sdk-dropdown__input-container"
         :class="{'--disabled': disabled}">
      <div
        class="sdk-dropdown__input"
        v-html="valueAsHTML"
        @click="toggleDropdown"
      >
        <!-- value html is here -->
      </div>
      <div
        class="sdk-dropdown__filter-icon"
        @click="toggleDropdown">
        <i class="fa fa-filter"></i>
      </div>
    </div>
    <!-- End input trigger builder -->

    <!-- Modal  -->
    <div class="sdk-dropdown__list-container">
      <transition name="sdk-dropdown-fade">
        <div v-if="isMenuOpen" class="sdk-dropdown__dropdown">

          <!-- header dialog -->
          <div class="sdk-dropdown__header">
            <h4>{{ headerText }}</h4>

            <div class="sdk-dropdown__close-icon">
              <i @click="closeDropdown" class="fa fa-times"></i>
            </div>
          </div>

          <!-- search input -->
          <div class="sdk-dropdown__search-container">
            <input
              ref="searchInput"
              placeholder="Search text"
              type="text"
              class="sdk-dropdown__search-input"
              v-model.trim="searchValue">
            <i class="fa fa-search"></i>
          </div>

          <!-- list options -->
          <ul class="sdk-dropdown__list">
            <template v-if="lazyLoading ? currentOptionsList.length : getOptionsList.length">
              <template>
                <li v-for="(option, index) of lazyLoading ? currentOptionsList : getOptionsList" :key="option[keyValue]" class="sdk-dropdown__list-option" @click="toggleValue(option, index)">
                  <div class="sdk-dropdown__checkbox">
                    <input :checked="isChecked(option[keyValue])" type="checkbox">
                  </div>
                  <div :title="option[keyValue]" class="sdk-dropdown__text-option">
                    {{ option[keyLabel] }}
                  </div>
                </li>
                <li v-if="lazyLoading && (count === null || currentOptionsList.length < count)" v-observe-visibility="handleLoadMore"></li>
              </template>
            </template>
            <template v-else>
              <p class="sdk-dropdown__message">No result</p>
            </template>
          </ul>

          <!-- actions handler -->
          <div class="sdk-dropdown__actions">
            <button type="button" class="cbpo-btn mr-auto" @click="deSelectAll">
              Clear
            </button>
            <button type="button" class="cbpo-btn btn-success mr-1" @click="selectAll">
              Select All {{ `(${lazyLoading ? currentOptionsList.length : options.length})` || '' }}
            </button>
            <button v-if="lazy" type="button" class="cbpo-btn btn-primary" @click="apply">
              Apply
            </button>
          </div>
        </div>
      </transition>
    </div>
    <!-- End modal  -->
  </div>
</template>

<script>

import cloneDeep from 'lodash/cloneDeep'
import debounce from 'lodash/debounce'
import VueClickawayCustom from '@/directives/clickAwayDatepicker'
import Vue from 'vue'
import VueObserveVisibility from 'vue-observe-visibility'
Vue.use(VueObserveVisibility)

export default {
  name: 'MultiSelectDropdown',
  props: {
    value: {
      type: Array, // current value of multi select
      default: () => []
    },
    disabled: { // disabled dropdown
      type: Boolean,
      default: false
    },
    options: {
      type: Array, // object array
      default: () => []
    },
    keyLabel: {
      type: String,
      default: 'text' // key label of option value
    },
    keyValue: {
      type: String,
      default: 'value' // key value of option value
    },
    lazy: {
      type: Boolean,
      default: true
    },
    headerText: {
      type: String,
      default: 'Dropdown Selection'
    },
    lazyLoading: {
      type: Boolean,
      default: true
    },
    limit: {
      type: Number,
      default: 20
    },
    colName: {
      type: String
    },
    updateItemsObj: {
      type: Object
    }
  },
  directives: {
    onClickaway: VueClickawayCustom
  },
  data() {
    return {
      isMenuOpen: false,
      searchValue: '',
      selectedValue: [],
      cacheState: [],
      page: 1,
      currentOptionsList: cloneDeep(this.options),
      count: null
    }
  },
  computed: {
    valueAsHTML() {
      const value = this.cacheState
      const htmlTag = value
        .filter((v, i) => i < 3)
        .map(v => `<span title="${v[this.keyLabel]}" class="tag">${v[this.keyLabel]}</span>`)
        .join('')
      const otherValue = value
        .filter((v, i) => i >= 3)
        .map(v => v[this.keyLabel])
      const otherTag = otherValue.length
        ? `<span class="other-tag" title="${otherValue.join(', ')}">and ${otherValue.length} other${otherValue.length > 1 ? 's' : ''}</span>`
        : ''
      return htmlTag + otherTag
    },
    isChecked() {
      return value => !!this.selectedValue.find(v => v[this.keyValue] === value)
    },
    getOptionsList() {
      return this.options.filter(option => option[this.keyLabel].toLowerCase().includes(this.searchValue.toLowerCase()))
    }
  },
  methods: {
    // dropdown handler
    toggleDropdown() {
      if (this.disabled) return
      this.isMenuOpen = !this.isMenuOpen
      this.searchChange()
    },
    closeDropdown() {
      this.isMenuOpen = false
    },
    // value dropdown handler
    selectAll() {
      this.lazyLoading ? this.selectedValue = cloneDeep(this.currentOptionsList) : this.selectedValue = cloneDeep(this.options)
      !this.lazy && this.change()
    },
    deSelectAll() {
      this.selectedValue = []
      !this.lazy && this.change()
    },
    toggleValue(option) {
      const indexOption = this.selectedValue.findIndex(v => v[this.keyValue] === option[this.keyValue])
      if (indexOption !== -1) {
        this.selectedValue.splice(indexOption, 1)
      } else {
        this.selectedValue.push(option)
      }
      !this.lazy && this.change()
      this.focusSearchInput()
    },
    apply() {
      this.change()
      this.closeDropdown()
    },
    change() {
      this.cacheState = cloneDeep(this.selectedValue)
      this.$emit('input', this.selectedValue.map(v => v[this.keyValue]))
    },
    // focus input
    focusSearchInput() {
      this.$refs.searchInput.focus()
    },
    handleLoadMore(isVisible) {
      if (!isVisible) return
      if (this.currentOptionsList.length < this.count || this.count === null) {
        this.page++
        this.$emit('updateItems', {search: this.searchValue, columnName: this.colName, page: this.page, limit: this.limit})
      }
    },
    handleUpdateItems (data) {
      if (this.colName && data[this.colName]) {
        this.page = data[this.colName].page
        this.count = data[this.colName].count
        if (data[this.colName].page !== 1) {
          this.currentOptionsList[data[this.colName]] = this.currentOptionsList.push(...data[this.colName].items)
        } else this.currentOptionsList = cloneDeep(data[this.colName].items)
      }
    },
    searchChange() {
      debounce(() => {
        if (!this.lazyLoading) return
        this.page = 1
        this.$emit('updateItems', {search: this.searchValue, columnName: this.colName, page: this.page, limit: this.limit})
      }, 300)()
    }
  },
  watch: {
    value: {
      immediate: true,
      deep: true,
      handler(arrayValue) {
        if (this.lazyLoading) {
          this.selectedValue = arrayValue.map(val => {
            return {
              text: val,
              value: val
            }
          })
        } else {
          this.selectedValue = arrayValue.reduce((arr, v) => {
            const option = this.options.find(o => o[this.keyValue] === v)
            option && arr.push(option)
            return arr
          }, [])
        }
        this.cacheState = cloneDeep(this.selectedValue)
      }
    },
    isMenuOpen(val) {
      if (val) {
        this.$nextTick(() => this.focusSearchInput())
      } else {
        this.selectedValue = cloneDeep(this.cacheState)
      }
    },
    updateItemsObj: {
      deep: true,
      immediate: true,
      handler(val) {
        if (Object.keys(val).length && this.colName) this.handleUpdateItems(val)
      }
    },
    searchValue: {
      deep: true,
      immediate: true,
      handler(val) {
        this.searchChange()
      }
    }
  }
}
</script>

<style scoped lang="scss">
@import 'src/assets/css/core/color';

.sdk-dropdown {
  &__container {
    position: relative;
    font-size: 12px;
    width: 100%;
  }

  &__header {
    display: flex;
    justify-content: space-between;

    h4 {
      color: $dark;
      font-size: 13px;
      padding-left: 5px;
      line-height: 18px;
      margin-bottom: 0;
    }
  }

  &__close-icon {
    i {
      cursor: pointer;
      color: $danger;
    }
  }

  &__input-container {
    width: 100%;
    height: auto;
    line-height: 24px;
    position: relative;

    &:not(.--disabled):hover {
     .sdk-dropdown__filter-icon {
        cursor: pointer;
      }
    }
  }

  &__input {
    width: 100%;
    height: 100%;
    padding: 3px 20px 0 8px;
    display: flex;
    flex-wrap: wrap;
    min-height: 24px;
    cursor: pointer;
  }
  &__filter-icon {
    position: absolute;
    right: 6px;
    top: 50%;
    transform: translateY(-50%);
  }

  &__dropdown {
    position: absolute;
    width: 250px;
    top: -10px;
    right: 0;
    min-width: 150px;
    padding: .5rem;
    background-color: $light;
    border-radius: 3px;
    z-index: 9999;
  }

  &__search-container {
    position: relative;
    margin: 0.5rem .25rem;

    input {
      padding: 0 23px 0 5px;
      height: 24px;
      line-height: 24px;
      width: 100%;
      background-color: $light !important;
      border: 1px solid $default;
      border-radius: 3px;
      color: $dark !important;
    }

    i {
      position: absolute;
      right: 8px;
      top: 5px;
      color: $dark !important;
    }
  }

  &__list {
    padding: 0;
    margin-bottom: 0;
    max-height: 300px;
    overflow: auto;
  }

  &__list-option {
    display: flex;
    padding: 5px 0;
    transition: all 0.2s;
    cursor: pointer;

    .sdk-dropdown__checkbox {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      width: 40px;
      height: 100%;
      padding-left: 5px;

      input[type="checkbox"] {
        position: relative;
        width: 1.5em;
        height: 1.5em;
        color: $light;
        border: 1px solid $default;
        border-radius: 4px;
        appearance: none;
        outline: 0;
        cursor: pointer;
        transition: background 175ms cubic-bezier(0.1, 0.1, 0.25, 1);

        &::before {
          position: absolute;
          content: '';
          display: block;
          top: 1px;
          left: 5px;
          width: 6px;
          height: 11px;
          border-style: solid;
          border-color: $light;
          border-width: 0 2px 2px 0;
          transform: rotate(45deg);
          opacity: 0;
        }

        &:checked {
          color: $light;
          border-color: $primary;
          background: $primary;

          &::before {
            opacity: 1;
          }

          ~ label::before {
            clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
          }
        }
      }
    }

    .sdk-dropdown__text-option {
      width: 100%;
      overflow: hidden;
      color: $dark;
      text-overflow: ellipsis;
      white-space: nowrap;
      padding-right: 5px;
    }

    &:hover {
      background-color: darken($light, 10);
    }
  }

  &__actions {
    margin-top: 0.5rem;
    display: flex;
  }

  &__message {
    padding: 5px 0;
    color: $dark;
    text-align: center;
  }
}

::v-deep span.tag {
  display: inline-block;
  padding: 0 5px;
  background-color: $default;
  color: $light;
  border-radius: 20px;
  min-width: 40px;
  text-align: center;
  font-size: 9px;
  height: 18px;
  line-height: 18px;
  max-width: 120px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
  margin-bottom: 3px;

  &:not(:last-child) {
    margin-right: 0.25rem;
  }
}

::v-deep .other-tag {
  font-size: 9px;
  line-height: 18px;
}

.sdk-dropdown-fade-enter-active, .sdk-dropdown-fade-leave-active {
  transition: opacity .3s;
}

.sdk-dropdown-fade-enter, .sdk-dropdown-fade-leave-to {
  opacity: 0;
}
</style>
