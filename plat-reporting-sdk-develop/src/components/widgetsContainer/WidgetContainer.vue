<template>
  <div class="widget-">
    <div class="widget-header">
      <slot name="widget-header">
        <h6>Widget List</h6>
      </slot>
    </div>
    <div class="widget-list-container">
      <div :style="config.style" :class="config.class" class="widget-list">
        <div class="widget-slot"
             :key="index"
             v-cbpo-draggable="{
               scope: config.scope,
               enabled: config.dragWidgets.enabled,
               widget: widget,
               [EVENT.START_EVENT]: startEvent,
               [EVENT.STOP_EVENT]: stopEvent,
               [EVENT.DRAG_EVENT]: dragEvent
              }"
             v-for="(widget, index) of config.widgets">
          <slot name="widget-item" :item="widget">
            <div class="widget-content">
              <div class="img-content">
                <img :src="widget.screenshot" :alt="widget.name">
              </div>
              <p class="text-center text-truncate mb-0">
                {{widget.name}}
              </p>
            </div>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import {makeDefaultWidgetContainerConfig} from '@/components/widgetsContainer/WidgetContainerConfig'
import dragDirective from '@/directives/dragDirective'
import { EVENT } from '@/utils/dragAndDropUtil'
import CBPO from '@/services/CBPO'
import { BUS_EVENT } from '@/services/eventBusType'
export default {
  name: 'WidgetContainer',
  mixins: [WidgetBaseMixins],
  directives: {
    'cbpo-draggable': dragDirective
  },
  props: {
    widgetType: {
      type: String,
      default: 'cbpo-widget'
    }
  },
  data() {
    return {
      EVENT,
      [BUS_EVENT.DRAG_DATA_DIRECTIVE]: null
    }
  },
  methods: {
    widgetConfig(config) {
      makeDefaultWidgetContainerConfig(config)
    },
    startEvent({source, target}, el) {
      this[BUS_EVENT.DRAG_DATA_DIRECTIVE].data.source.widgetType = this.widgetType
      this.emitData(this[BUS_EVENT.DRAG_DATA_DIRECTIVE])
    },
    stopEvent({source, target}, el) {
      this.emitData(null)
    },
    emitData(data) {
      CBPO.$bus.$emit(`${BUS_EVENT.DRAG_EVENT_DASHBOARD_BUILDER_INTERNAL}_${this.config.scope}`, data)
    },
    dragEvent({source, target}, el, ui) {
      this[BUS_EVENT.DRAG_DATA_DIRECTIVE].data.ui = ui
      this[BUS_EVENT.DRAG_DATA_DIRECTIVE].data.source.widgetType = this.widgetType
      this.emitData(this[BUS_EVENT.DRAG_DATA_DIRECTIVE])
    }
  }
}
</script>
<style scoped lang="scss">
  @import "WidgetContainer";
</style>
