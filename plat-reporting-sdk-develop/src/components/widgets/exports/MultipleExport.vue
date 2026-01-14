<template>
  <div class="cbpo-multiple-export">
    <slot :openModal="openModal" name="button">
      <button class="multi-export-open-btn" @click="openModal()">
        <div class="multi-export-icon"></div>
      </button>
    </slot>

    <b-modal :id="multiExportModalId" modal-class="multiple-export-modal" size="md" centered hide-header-close>
      <template v-slot:modal-title>
        <span class="title-modal">Select widgets to export multiple CSV</span>
      </template>
      <div class="py-2">
        <div class="d-flex justify-content-center">
          <div class="position-relative">
            <input v-model.trim="searchInput" class="search-input d-flex align-items-center"
              placeholder="Search Widget">
            <div class="search-icon"></div>
          </div>
        </div>
        <div class="w-100 mt-2 parent">
          <div v-show="widgetsBySearch.length > 0" class="select-all">
            <div @click="toggleCheckAll()" class="check-box" :class="{ 'checked': isCheckedAll }">
              <div class="check-box-img"></div>
            </div>
            <span class="pl-2">Select All</span>
          </div>
          <div class="d-flex align-items-center flex-wrap">
            <div v-for="(widget, index) of widgetsBySearch" :key="index" @click="toggleCheckedWidget(widget)"
              :class="widgetClass">
              <div class="check-box" :class="{ 'checked': widget.checked }">
                <div class="check-box-img"></div>
              </div>
              <span :id="`widget-${widget.id}`" class="pl-2 text-truncate">{{ widget.displayName }}</span>
              <b-popover :target="`widget-${widget.id}`" triggers="hover" placement="top">
                <span>{{ widget.displayName }}</span>
              </b-popover>
            </div>
            <div v-if="shouldShowPlaceholder" class="select-widget"></div>
          </div>
        </div>
      </div>
      <span v-if="!widgetsBySearch.length" class="no-widgets-msg">There is no widget to export</span>
      <template v-slot:modal-footer>
        <b-button :disabled="!selectedWidgets.length" @click="handleExport()" class="multi-export-btn">
          <div class="export-img"></div>
          <span>Export</span>
        </b-button>
      </template>
    </b-modal>
    <b-modal :id="exportWidgetCompleteModalId" modal-class="export-widget-complete-modal" size="md" centered
      :hide-footer="true" :hide-header="true" hide-header-close>
      <div class="export-complete">
        <span class="export-complete-msg">The following widgets CVS were successfully exported!</span>
        <ul class="export-complete-list">
          <li v-for="(widget, index) of widgetsExported" :key="index">
            <span class="export-complete-widget-name">{{ widget.displayName }}</span>
          </li>
        </ul>
      </div>
    </b-modal>
  </div>
</template>
<script>
import cloneDeep from 'lodash/cloneDeep'
import CBPO from '@/services/CBPO'
import { BUS_EVENT } from '@/services/eventBusType'
import { v4 as uuid } from 'uuid'

export default {
  name: 'MultipleExport',
  components: {
  },
  props: {
    widgets: Array
  },
  data() {
    return {
      searchInput: '',
      widgetsWaitingExport: [],
      widgetsExported: [],
      downloadToasted: null,
      processingWidgetId: null,
      expectedCallbacks: 0,
      receivedCallbacks: 0
    }
  },
  computed: {
    widgetClass() {
      return this.widgetsBySearch.length === 1 ? 'select-all first-widget' : 'select-widget'
    },
    shouldShowPlaceholder() {
      return this.widgetsBySearch.length % 2 !== 0 && this.widgetsBySearch.length > 1
    },
    selectedWidgets() {
      const results = this.widgets.filter(widget => widget.checked)
      return results
    },
    multiExportModalId() {
      return `multiple-export-modal-${uuid()}`
    },
    exportWidgetCompleteModalId() {
      return `export-widget-complete-modal-${uuid()}`
    },
    widgetsBySearch() {
      return this.searchInput ? this.widgets.filter(widget => widget.displayName.toLowerCase().includes(this.searchInput.toLowerCase())) : cloneDeep(this.widgets)
    },
    isCheckedAll() {
      return this.widgetsBySearch.every(widget => widget.checked)
    }
  },
  methods: {
    openModal() {
      this.$bvModal.show(this.multiExportModalId)
    },
    getListenerCount(widgetId) {
      const eventName = BUS_EVENT.EXPORT_WIDGET(widgetId)
      const listeners = CBPO.$bus._events && CBPO.$bus._events[eventName]
      return listeners ? listeners.length : 0
    },
    handleResponse(res, widgetId) {
      // Ignore callbacks from previous widgets
      if (this.processingWidgetId !== widgetId) {
        return
      }

      this.receivedCallbacks++

      // Wait for all listeners to respond
      if (this.receivedCallbacks < this.expectedCallbacks) {
        return
      }

      if (res) {
        this.widgetsExported.push(this.widgetsWaitingExport.shift())
      } else {
        this.widgetsWaitingExport.shift()
      }

      if (this.widgetsWaitingExport.length) {
        const nextWidget = this.widgetsWaitingExport[0]
        if (!nextWidget) {
          console.error('Next widget is undefined!')
          this.finishExport()
          return
        }

        // Skip all widgets with no listeners using iteration
        let currentWidget = nextWidget
        while (currentWidget) {
          this.expectedCallbacks = this.getListenerCount(currentWidget.id)
          this.receivedCallbacks = 0

          if (this.expectedCallbacks > 0) {
            // Found widget with listeners, emit event
            this.processingWidgetId = currentWidget.id
            CBPO.$bus.$emit(BUS_EVENT.EXPORT_WIDGET(currentWidget.id), currentWidget, (isSuccess) => {
              this.handleResponse(isSuccess, currentWidget.id)
            })
            return
          }

          // No listeners, skip this widget
          this.widgetsWaitingExport.shift()
          currentWidget = this.widgetsWaitingExport[0]
        }

        // All remaining widgets had no listeners
        this.finishExport()
      } else {
        this.finishExport()
      }
    },
    finishExport() {
      this.processingWidgetId = null
      this.expectedCallbacks = 0
      this.receivedCallbacks = 0
      if (this.downloadToasted) {
        this.downloadToasted.goAway(1500)
      }
      this.$bvModal.show(this.exportWidgetCompleteModalId)
      this.widgets.forEach(widget => {
        widget.checked = false
      })
      setTimeout(() => {
        this.$bvModal.hide(this.exportWidgetCompleteModalId)
      }, 3000)
    },
    handleExport() {
      this.downloadToasted = this.$toasted.show('Downloading...', {
        theme: 'outline',
        position: 'top-center',
        iconPack: 'custom-class',
        className: 'cpbo-toast-export',
        icon: {
          name: 'fa fa-spinner fa-spin fa-fw',
          after: false
        },
        duration: null
      })
      this.widgetsExported = []
      this.widgetsWaitingExport = cloneDeep(this.selectedWidgets)
      this.$bvModal.hide(this.multiExportModalId)

      const firstWidget = this.widgetsWaitingExport[0]
      if (!firstWidget) {
        console.error('No widget to export!')
        if (this.downloadToasted) {
          this.downloadToasted.goAway(1500)
        }
        return
      }

      // Count listeners for first widget
      this.expectedCallbacks = this.getListenerCount(firstWidget.id)
      this.receivedCallbacks = 0

      if (this.expectedCallbacks === 0) {
        this.finishExport()
        return
      }

      this.processingWidgetId = firstWidget.id

      CBPO.$bus.$emit(BUS_EVENT.EXPORT_WIDGET(firstWidget.id), firstWidget, (isSuccess) => {
        this.handleResponse(isSuccess, firstWidget.id)
      })
    },
    toggleCheckAll() {
      const isChecked = !this.isCheckedAll
      const widgetIds = this.widgetsBySearch.map(w => w.id)
      this.widgets.filter(w => widgetIds.includes(w.id)).forEach(w => {
        w.checked = isChecked
      })
    },
    toggleCheckedWidget(widget) {
      const index = this.widgets.findIndex(p => p.id === widget.id)
      if (index !== -1) {
        this.widgets[index].checked = !this.widgets[index].checked
      }
    }
  },
  destroyed() {
    this.selectedWidgets.forEach(widget => {
      CBPO.$bus.$off(BUS_EVENT.EXPORT_WIDGET(widget.id))
    })
  }
}
</script>
<style lang="scss" scoped>
@import "./MultipleExport.scss";
</style>
