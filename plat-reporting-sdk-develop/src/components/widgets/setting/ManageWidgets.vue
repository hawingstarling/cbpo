<template>
  <div class="cbpo-manage-column">
    <slot :openModal="openModal" name="button" />
    <!--Modal widget manager-->
    <b-modal dialog-class="cbpo-custom-modal" modal-class="custom-columns-modal" :id="modalId" size="md" @close="cancel()" @hide="cancel()">
      <template v-slot:modal-title>
        <span>{{ configObj.modal.title }}</span>
      </template>
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
                    placeholder="Search Widget"
                    type="text"
                    v-model="keyword"
                  >
                  </b-form-input>
                </b-input-group>
              </b-form>
          </div>
        </div>
        <div
          class="p-3 cbpo-list-element position-relative"
        >
          <template
            class="cbpo-list-element__wrapper position-relative"
          >
            <div id="widget-manage" class="cbpo__element row no-gutters position-relative">

              <!-- Visible Columns -->
              <div class="col-6 cbpo__element--border-right position-relative">
                <div v-if="filteredWidget(true).length" class="position-relative">
                  <div class="wrapper-row">
                    <div
                      class="col-reorder-dropzone first shadow-sm"
                      v-cbpo-droppable="{ index: 0, [EVENT.DROP_EVENT]: dropEvent }"
                    >
                      <i class="fa fa-arrow-circle-right" aria-hidden="true" />
                      <div class="x-line"></div>
                    </div>
                  </div>
                  <!-- Dont use Computed for element.columns -->
                  <div
                    class="wrapper-row"
                    v-for="(widget, index) in widgetSearch"
                    :class="{ '--hidden': !widget.enabled }"
                    :key="`element-widget-${index}`"
                  >
                    <div class="cbpo__row" :id="widget.widget.key" v-show="widget.enabled">
                      <div class="cbpo__drag-arrow">
                        <i
                          v-cbpo-draggable="{
                            index: index,
                            containment: `#widget-manage`,
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
                          class="fa fa-circle"
                          aria-hidden="true"
                          :id="`draggable-${index}`"
                        />
                        <b-popover custom-class="custom-tooltip" triggers="hover" placement="right" :key="`draggable-${index}`" :target="`draggable-${index}`">
                          You can drag and drop the widget to change its position.
                        </b-popover>
                      </div>
                      <div class="cbpo__name">
                        <template v-if="widget.proportion === 'Half'">
                          <span :id="`proportion-${widget.id}-${index}`" v-if="widget.proportion === 'Half'" class="widget-proportion">(1/2)</span>
                          <b-popover custom-class="custom-tooltip" triggers="hover" placement="right" :key="`proportion-${widget.id}-${index}`" :target="`proportion-${widget.id}-${index}`">
                            The width of this widget is half of the Dashboard's width.
                          </b-popover>
                        </template>
                        <span :title="widget.widget.value">{{ widget.widget.value }}</span>
                      </div>
                      <div class="cbpo__switch">
                        <b-form-checkbox
                          :id="`element-checkbox-${widget.widget.key}`"
                          v-model="widget.enabled"
                          @change="toggleCheckedWidget(widget)"
                          switch
                        />
                      </div>
                    </div>
                    <div
                      class="col-reorder-dropzone shadow-sm"
                      v-cbpo-droppable="{ index: index + 1, [EVENT.DROP_EVENT]: dropEvent  }"
                      v-show="widget.enabled"
                    >
                      <i class="fa fa-arrow-circle-right" aria-hidden="true" />
                      <div class="x-line"></div>
                    </div>
                  </div>
                </div>
                <div class="cbpo__empty" v-else>No visible widget.</div>
              </div>

              <!-- Hidden Columns -->
              <div class="col-6">
                <div v-if="filteredWidget(false).length">
                  <div
                    class="wrapper-row"
                    v-for="widget in widgetSearch"
                    :key="`element-widget-${widget.id}`"
                    :class="{ '--hidden': widget.enabled }"
                  >
                    <div class="cbpo__row" :id="widget.widget.key" v-show="!widget.enabled">
                      <div class="cbpo__drag-arrow">
                        <i class="fa fa-circle" aria-hidden="true" />
                      </div>
                      <div :title="widget.widget.value" class="cbpo__name">
                        {{ widget.widget.value }}
                      </div>
                      <div class="cbpo__switch">
                        <b-form-checkbox
                          :id="`element-checkbox-${widget.widget.key}`"
                          v-model="widget.enabled"
                          @change="toggleCheckedWidget(widget)"
                          switch
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div class="cbpo__empty" v-else>No invisible widget.</div>
              </div>
            </div>
          </template>
        </div>
      </div>
      <template v-slot:modal-footer>
        <button
          v-if="modalButtonsConfig.reset.visible"
          @click="resetToDefault()" class="cbpo-btn btn-reset"
          :disabled="isDefault"
        >
          <span>{{ modalButtonsConfig.reset.text }}</span>
        </button>
        <!-- Emulate built in modal footer ok and cancel button actions -->
        <button v-if="modalButtonsConfig.apply.visible" @click="apply()" class="cbpo-btn btn-primary btn-apply">
          <span>{{ modalButtonsConfig.apply.text }}</span>
        </button>
        <button v-if="modalButtonsConfig.cancel.visible" @click="cancel()" class="cbpo-btn btn-cancel">
          <span>{{ modalButtonsConfig.cancel.text }}</span>
        </button>
      </template>
    </b-modal>
  </div>
</template>
<script>
import dragDirective from '@/directives/dragDirective'
import dropDirective from '@/directives/dropDirective'
import $ from 'jquery'
import { EVENT } from '@/utils/dragAndDropUtil'
import connectorDirective from '@/directives/connectorDirective'
import { generateIdIfNotExist } from '@/utils/configUtil'
import { moveElement } from '@/utils/arrayUtil'
import { cloneDeep, sortBy } from 'lodash'

export default {
  name: 'ManageWidgets',
  data() {
    return {
      EVENT: EVENT,
      config: {
        id: null
      },
      keyword: '',
      widgetsDashboardSettings: []
    }
  },
  props: {
    widgetList: Array,
    configObj: Object
  },
  directives: {
    'cbpo-draggable': dragDirective,
    'cbpo-droppable': dropDirective,
    'cbpo-connector': connectorDirective
  },
  computed: {
    filteredWidget() {
      return (enabledStatus) => {
        return this.widgetSearch.filter(element => element.enabled === enabledStatus)
      }
    },
    modalId() {
      return 'widget-manager-modal-' + this.config.id
    },
    modalButtonsConfig() {
      return this.configObj.modal.buttons
    },
    widgetSearch() {
      return this.keyword ? this.widgetsDashboardSettings.filter(p => p.widget.value.toLowerCase().includes(this.keyword.toLowerCase())) : cloneDeep(this.widgetsDashboardSettings)
    },
    isDefault() {
      return this.widgetSearch.filter((element, index) => index + 1 === element.position_default && element.enabled).length === this.widgetsDashboardSettings.length
    }
  },
  methods: {
    startEvent({ index }, el) {
      let $selectors = $(`#widget-manage .col-reorder-dropzone`)
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
    stopEvent() {
      $(`#widget-manage .col-reorder-dropzone`).removeClass(
        'disabled-dropzone'
      )
    },
    clearKeyword() {
      this.keyword = ''
    },
    openModal() {
      this.toggleModal(true)
    },
    cancel() {
      this.toggleModal()
      this.widgetsDashboardSettings = cloneDeep(this.widgetList)
    },
    apply() {
      this.$emit('updated', this.widgetsDashboardSettings)
      this.toggleModal()
    },
    toggleModal (isOpen = false) {
      this.clearKeyword()
      isOpen
        ? this.$bvModal.show(this.modalId)
        : this.$bvModal.hide(this.modalId)
    },
    dropEvent(e) {
      let result = cloneDeep(this.widgetsDashboardSettings)
      let {data: {source, target}} = {...e}
      this.widgetsDashboardSettings = moveElement(result, source.index, target.index)
    },
    toggleCheckedWidget(widget) {
      const index = this.widgetsDashboardSettings.findIndex(p => p.id === widget.id)
      if (index !== -1) {
        this.widgetsDashboardSettings[index].enabled = !this.widgetsDashboardSettings[index].enabled
      }
    },
    resetToDefault() {
      this.widgetsDashboardSettings = sortBy(this.widgetsDashboardSettings, ['position_default']).map(w => ({ ...w, enabled: true }))
    }
  },
  watch: {
    widgetList: {
      deep: true,
      immediate: true,
      handler: function(newVal, oldVal) {
        if (newVal !== oldVal) {
          this.$emit('update:widgetList', newVal)
          this.widgetsDashboardSettings = cloneDeep(newVal)
        }
      }
    },
    configObj: {
      deep: true,
      immediate: true,
      handler: function(newVal, oldVal) {
        if (newVal !== oldVal) {
          this.$emit('update:configObj', newVal)
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
::v-deep .tooltip-inner {
  max-width: max-content;
}
::v-deep .modal-dialog {
  @media (min-width: 576px) {
    min-width: 500px;
    max-width: 750px;
    width: 50%;
  }
}
.widget-proportion {
  padding-right: 4px;
  cursor: default;
}
</style>
