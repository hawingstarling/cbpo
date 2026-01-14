import $ from 'jquery'
import 'jquery-ui/ui/widgets/droppable'
import { EVENT } from '@/utils/dragAndDropUtil'
import { BUS_EVENT } from '@/services/eventBusType'
import cloneDeep from 'lodash/cloneDeep'

export default {
  bind: function(el, data, vnode) {
    let {value: {tolerance = 'fit'}} = data
    $(document).ready(function () {
      $(el).droppable({
        activeClass: 'active-dropzone',
        hoverClass: 'hover-dropzone',
        tolerance: tolerance,
        scope: data.value.scope,
        accept: function(el, ui) {
          if (data.value[EVENT.ACCEPT_EVENT]) {
            return data.value[EVENT.ACCEPT_EVENT](data.value, el, ui)
          }
          return true
        },
        drop: function(el, ui) {
          let event = cloneDeep(vnode.context[BUS_EVENT.DRAG_DATA_DIRECTIVE])
          if (!event) return
          event.data.target = data.value
          vnode.context.$emit('dropChange', event)

          // Callback drop event
          if (data.value[EVENT.DROP_EVENT]) {
            data.value[EVENT.DROP_EVENT](event, el, ui)
          }

          // Set default for drag event if drag and drop from 2 different components
          vnode.context[BUS_EVENT.DRAG_DATA_DIRECTIVE] = null
        },
        over: function(el, ui) {
          if (data.value[EVENT.OVER_EVENT]) {
            data.value[EVENT.OVER_EVENT](data.value, el, ui)
          }
        },
        out: function(el, ui) {
          if (data.value[EVENT.OUT_EVENT]) {
            data.value[EVENT.OUT_EVENT](data.value, el, ui)
          }
        },
        activate: function(el, ui) {
          if (data.value[EVENT.ACTIVATE_EVENT]) {
            data.value[EVENT.ACTIVATE_EVENT](data.value, el, ui)
          }
        },
        deactivate: function(el, ui) {
          if (data.value[EVENT.DEACTIVATE_EVENT]) {
            data.value[EVENT.DEACTIVATE_EVENT](data.value, el, ui)
          }
        },
        create: function(el, ui) {
          if (data.value[EVENT.CREATE_EVENT]) {
            data.value[EVENT.CREATE_EVENT](data.value, el, ui)
          }
        }
      })
    })
  }
}
