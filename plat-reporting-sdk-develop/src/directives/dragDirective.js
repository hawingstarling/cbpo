import $ from 'jquery'
import 'jquery-ui/ui/widgets/draggable'
import { EVENT } from '@/utils/dragAndDropUtil'
import { BUS_EVENT } from '@/services/eventBusType'
import cloneDeep from 'lodash/cloneDeep'

const jqueryDraggable = (el, data, vnode) => {
  $(document).ready(function () {
    $(el).draggable({
      scope: data.value.scope,
      // Add the container that wraps up all draggable items and connector
      // Add position: relative to all html tags from the connector
      containment: data.value.containment || 'document',
      revert: 'invalid',
      helper: 'clone',
      appendTo: data.value.containment || 'body',
      zIndex: 10000,
      drag: function (el, ui) {
        // Change selector
        if (vnode.context[BUS_EVENT.DRAG_DATA_DIRECTIVE]) {
          vnode.context[BUS_EVENT.DRAG_DATA_DIRECTIVE].selector = el
        }

        // Drag event
        if (data.value[EVENT.DRAG_EVENT]) {
          data.value[EVENT.DRAG_EVENT](cloneDeep(vnode.context[BUS_EVENT.DRAG_DATA_DIRECTIVE]), el, ui)
        }
      },
      start: function (el, ui) {
        // Create drag event
        vnode.context[BUS_EVENT.DRAG_DATA_DIRECTIVE] = {
          data: {
            source: data.value,
            target: null
          },
          selector: el,
          scope: data.value.scope
        }

        // Start event
        if (data.value[EVENT.START_EVENT]) {
          data.value[EVENT.START_EVENT](data.value, el, ui)
        }
      },
      stop: function (el, ui) {
        // Set default drag event for current component which contain drag directive
        vnode.context[BUS_EVENT.DRAG_DATA_DIRECTIVE] = null

        // Stop Event
        if (data.value[EVENT.STOP_EVENT]) {
          data.value[EVENT.STOP_EVENT](data.value, el, ui)
        }
        // $(ui.item).removeClass('ui-draggable-helper')
      },
      create: function (el, ui) {
        if (data.value[EVENT.CREATE_EVENT]) {
          data.value[EVENT.CREATE_EVENT](data.value, el, ui)
        }
      }
    })
    $(el).mousedown(function (e) {
      e.stopImmediatePropagation()
    })
  })
}

export default {
  bind: function (el, data, vnode) {
    let { value: { enabled = true } } = data
    if (enabled) {
      jqueryDraggable(el, data, vnode)
    }
  },
  update(el, data, vnode) {
    let { value: { enabled = true } } = data
    if (enabled && data.oldValue.column !== data.value.column) {
      jqueryDraggable(el, data, vnode)
    }
  }
}
