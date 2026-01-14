<template>
  <div class="cbpo-list position-relative" :id="`connector-${config.id}`">
    <div class="cbpo-list__twin px-3">
      <div class="cbpo-list__search-wrapper">
          <b-form class="cbpo-list__search-wrapper__form">
            <b-input-group class="my-1">
              <template v-slot:prepend>
                <b-input-group-text class="cursor-pointer">
                  <i class="fa fa-search"></i>
                </b-input-group-text>
              </template>
              <i
                class="fa fa-times-circle clear-keyword"
                v-if="keyword"
                @click="clearKeyword()"
              ></i>
              <b-form-input
                id="input-valid"
                placeholder="Search Column"
                type="text"
                v-model="keyword"
                @keyup.native="handleKeywordChange($event)"
              >
              </b-form-input>
            </b-input-group>
          </b-form>
      </div>
    </div>
    <div
      v-for="(element, elementIndex) in columnsInElements"
      :key="`element-${elementIndex}`"
      class="p-3 cbpo-list-element position-relative"
    >
      <template
        v-if="isAnyColumnEnabled(element.columns)"
        class="cbpo-list-element__wrapper position-relative"
      >
        <div :id="`element-${element.id}`" class="cbpo__element row no-gutters position-relative">

          <!-- Visible Columns -->
          <div class="col-6 cbpo__element--border-right position-relative">
            <div v-if="filteredColumns(element.columns, true).length" class="position-relative">
              <div class="wrapper-row">
                <div
                  class="col-reorder-dropzone first shadow-sm"
                  v-cbpo-droppable="{ index: 0, scope: element.id }"
                >
                  <i class="fa fa-arrow-circle-right" aria-hidden="true" />
                  <div class="x-line"></div>
                </div>
              </div>
              <!-- Dont use Computed for element.columns -->
              <div
                class="wrapper-row"
                :class="{ 'wrapper-row--disabled': col && col.disabled, '--hidden': !col.visible && !isHiddenColumn(col) }"
                v-for="(col, colIndex) in element.columns"
                :key="`element-column-${colIndex}`"
              >
                <div class="cbpo__row" :id="col.name" v-show="col.visible && !isHiddenColumn(col)">
                  <div class="cbpo__drag-arrow">
                    <i
                      v-cbpo-draggable="{
                        index: colIndex,
                        scope: element.id,
                        containment: `#element-${element.id}`,
                        [EVENT.START_EVENT]: startEvent,
                        [EVENT.STOP_EVENT]: stopEvent
                      }"
                      v-cbpo-connector="{
                        position: {
                          start: 'center', //top-left, bottom-left, top-right, bottom-right, center, default: mouse position
                          end: 'center'
                        },
                        scopeId: `connector-${config.id}`
                      }"
                      :class="element.id"
                      class="fa fa-circle"
                      aria-hidden="true"
                    />
                  </div>
                  <div :title="col.displayName || col.name" class="cbpo__name">
                    {{ col.displayName || col.name }}
                  </div>
                  <div class="cbpo__switch">
                    <b-form-checkbox
                     :id="`element-checkbox-twin-${col.alias ? col.alias : col.name}`"
                      ref="columnsList"
                      @change="switchColumn(col)"
                      v-model="col.visible"
                      switch
                    />
                  </div>
                </div>
                <div
                  class="col-reorder-dropzone shadow-sm"
                  v-cbpo-droppable="{ scope: element.id, index: colIndex + 1 }"
                  v-show="col.visible"
                >
                  <i class="fa fa-arrow-circle-right" aria-hidden="true" />
                  <div class="x-line"></div>
                </div>
              </div>
            </div>
            <div class="cbpo__empty" v-else>No visible column.</div>
          </div>

          <!-- Hidden Columns -->
          <div class="col-6">
            <div v-if="filteredColumns(element.columns, false).length">
              <div
                class="wrapper-row"
                :class="{ 'wrapper-row--disabled': col && col.disabled, '--hidden': !col.visible && !isHiddenColumn(col) }"
                :key="`element-column-${col.alias ? col.alias : col.name}`"
                v-for="col in element.columns"
              >
                <div class="cbpo__row" :id="col.name" v-show="!col.visible && !isHiddenColumn(col)">
                  <div class="cbpo__drag-arrow">
                    <i class="fa fa-circle" aria-hidden="true" />
                  </div>
                  <div :title="col.displayName || col.name" class="cbpo__name">
                    {{ col.displayName || col.name }}
                  </div>
                  <div class="cbpo__switch">
                    <b-form-checkbox
                      :id="`element-checkbox-twin-${col.alias ? col.alias : col.name}`"
                      v-model="col.visible"
                      switch
                    />
                  </div>
                </div>
              </div>
            </div>
            <div class="cbpo__empty" v-else>No invisible column.</div>
          </div>
        </div>
      </template>
      <div v-else class="cbpo__element--not-found">
        No column found.
      </div>
    </div>
  </div>
</template>
<script>
import dragDirective from '@/directives/dragDirective'
import dropDirective from '@/directives/dropDirective'
import $ from 'jquery'
import { EVENT } from '@/utils/dragAndDropUtil'
import connectorDirective from '@/directives/connectorDirective'
import { generateIdIfNotExist } from '@/utils/configUtil'

export default {
  name: 'ListColumnsTwinMode',
  data() {
    return {
      EVENT: EVENT,
      config: {
        id: null
      },
      twinMode: false,
      keyword: ''
    }
  },
  props: {
    columnsInElements: Array,
    hiddenColumns: Array
  },
  directives: {
    'cbpo-draggable': dragDirective,
    'cbpo-droppable': dropDirective,
    'cbpo-connector': connectorDirective
  },
  computed: {
    isAnyColumnEnabled() {
      return columns => columns.some((column) => !column.disabled)
    },
    filteredColumns() {
      return (columns, visible) => {
        const filterColumns = columns.filter(col => !this.hiddenColumns.find(hiddenCol => hiddenCol.name === col.name))
        return visible
          ? filterColumns.filter((col) => col.visible)
          : filterColumns.filter((col) => !col.visible)
      }
    },
    isHiddenColumn() {
      const hiddenColumns = this.hiddenColumns.map(column => column.name)
      return column => hiddenColumns.includes(column.name)
    }
  },
  methods: {
    startEvent({ scope, index }, el, ui) {
      let $selectors = $(`#element-${scope} .col-reorder-dropzone`)
      // Should remove 1 more time to make sure it won't cause bug when drag and drop too fast
      $selectors.removeClass('disabled-dropzone')
      // Add some css to current element which is dragging
      $(el.target)
        .closest('div')
        .addClass('cbpo__dragging')

      // Hide some dropzone
      if (!index) {
        $($selectors.get(0)).addClass('disabled-dropzone')
        $($selectors.get(1)).addClass('disabled-dropzone')
      } else {
        $($selectors.get(index)).addClass('disabled-dropzone')
        $($selectors.get(index + 1)).addClass('disabled-dropzone')
      }
    },
    stopEvent({ scope, index }, el, ui) {
      $(`#element-${scope} .col-reorder-dropzone`).removeClass(
        'disabled-dropzone'
      )
    },
    async switchColumn(col) {
      await this.$nextTick()
      const enabledColumns = this.$refs.columnsList.filter((col) => col.checked)
      if (enabledColumns.length === 0) {
        col.visible = true
      }
    },
    handleKeywordChange() {
      const columnData = this.columnsInElements[0].columns
      const filterSearchString = (str) =>
        str
          .replace(/[^a-zA-Z0-9]/g, ' ')
          .trim()
          .toLowerCase()
      const resultData = columnData.map((item) => {
        if (
          filterSearchString(item.displayName || item.name).includes(
            filterSearchString(this.keyword)
          )
        ) {
          item.disabled = false
        } else {
          item.disabled = true
        }
        return item
      })
      this.$set(this.columnsInElements[0], 'columns', resultData)
    },
    clearKeyword() {
      const columnData = this.columnsInElements[0].columns
      const resultData = columnData.map((item) => {
        if (item.hasOwnProperty('disabled')) {
          delete item.disabled
        }
        return item
      })
      this.keyword = ''
      this.$set(this.columnsInElements[0], 'columns', resultData)
    }
  },
  watch: {
    columnsInElements: {
      deep: true,
      immediate: true,
      handler: function(newVal, oldVal) {
        if (newVal !== oldVal) {
          this.$emit('update:columnsInElements', newVal)
        }
      }
    }
  },
  created() {
    generateIdIfNotExist(this.config)
    this.clearKeyword()
  }
}
</script>

<style scoped lang="scss">
@import '@/components/widgets/columns/ListColumnsTwinMode.scss';
</style>
