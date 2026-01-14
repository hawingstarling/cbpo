import $ from 'jquery'
import {forEach} from 'lodash'

const blueLine = {
  scaleHeight: 50,
  disabled: false,
  addPath: function (data) {
    let heightCanvas = getHeightCanvas(data)
    blueLine.canvas = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    blueLine.canvas.setAttribute('id', 'connector-blue-canvas')
    blueLine.canvas.setAttribute('height', heightCanvas)
    $(`${data.value && data.value.scopeId ? `#${data.value.scopeId}` : 'body'}`).css('position', 'relative').append(blueLine.canvas)

    blueLine.path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    blueLine.path.setAttribute('class', 'connector-blue-path')
    blueLine.canvas.appendChild(blueLine.path)

    blueLine.circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    blueLine.circle.setAttribute('r', 7)
    blueLine.circle.setAttribute('fill', '#5bb7e8')
    blueLine.circle.setAttribute('class', 'connector-blue-circle')
    blueLine.canvas.appendChild(blueLine.circle)
  },
  drawPath: function (start, end) {
    var d = Math.sqrt(Math.pow(start[0] - end[0], 2) + Math.pow(start[1] - end[1], 2))
    var alpha = Math.atan2(end[1] - start[1], end[0] - start[0])
    var a = Math.min(blueLine.scaleHeight, Math.max(d - 50, 0) / 2)
    if (Math.abs(alpha) > Math.PI / 2) a = -a
    var offsetX = Math.round(d / 2 * Math.cos(alpha) + a * Math.sin(alpha))
    var offsetY = Math.round(d / 2 * Math.sin(alpha) - a * Math.cos(alpha))
    var mid = [start[0] + offsetX, start[1] + offsetY]
    blueLine.path.setAttribute('d', `M${start[0]},${start[1]} Q${mid[0]}, ${mid[1]} ${end[0]}, ${end[1]}`)
    blueLine.circle.setAttribute('cx', end[0])
    blueLine.circle.setAttribute('cy', end[1])
  },
  removePath: function () {
    if (blueLine.canvas) {
      blueLine.canvas.remove()
    }
  }
}

const getHeightCanvas = (data) => {
  if (data.value && data.value.scopeId) {
    return Math.max(
      $(`#${data.value.scopeId}`)[0].scrollHeight,
      $(`#${data.value.scopeId}`)[0].offsetHeight,
      $(`#${data.value.scopeId}`)[0].clientHeight
    )
  }
  return Math.max(
    document.body.scrollHeight, document.documentElement.scrollHeight,
    document.body.offsetHeight, document.documentElement.offsetHeight,
    document.body.clientHeight, document.documentElement.clientHeight
  )
}

const dragEL = (ui, data, position) => {
  if (blueLine.disabled) return null
  const el = $(`${data.value && data.value.scopeId ? `#${data.value.scopeId}` : 'body'}`)
  let offset = el.offset()
  blueLine.end = [ui.offset.left - offset.left + position.end.left, ui.offset.top - offset.top + position.end.top + el[0].scrollTop]
  blueLine.drawPath(blueLine.start, blueLine.end)
}

const dragStartEL = (ui, data, position) => {
  if (blueLine.disabled) return null
  const el = $(`${data.value && data.value.scopeId ? `#${data.value.scopeId}` : 'body'}`)
  let offset = el.offset()
  blueLine.start = [ui.offset.left - offset.left + position.start.left, ui.offset.top - offset.top + position.start.top + el[0].scrollTop]
  blueLine.addPath(data)
}

const dragStopEL = () => {
  if (blueLine.disabled) return null
  blueLine.removePath()
}

const updateDisabled = (data) => {
  blueLine.disabled = data.value && data.value.disabled === true
}

// top-left, bottom-left, top-right, bottom-right, center
const getPositionConnector = (el, data, ui, e) => {
  const offset = $(`${data.value && data.value.scopeId ? `#${data.value.scopeId}` : 'body'}`).offset()
  const top = e.pageY - ui.offset.top - offset.top
  const left = e.pageX - ui.offset.left - offset.left
  const position = {start: {left, top}, end: {left, top}}
  if (data.value && data.value.position) {
    forEach(data.value.position, (item, name) => {
      switch (item) {
        case 'center':
          position[name].top = Math.ceil($(el).height() / 2)
          position[name].left = Math.ceil($(el).width() / 2)
          break
        case 'bottom-left':
          position[name].top = $(el).height()
          position[name].left = 0
          break
        case 'top-left':
          position[name].top = 0
          position[name].left = 0
          break
        case 'top-right':
          position[name].left = $(el).width()
          position[name].top = 0
          break
        case 'bottom-right':
          position[name].top = $(el).height()
          position[name].left = $(el).width()
          break
        default:
          break
      }
    })
  }
  return position
}

export default {
  bind (el, data, vnode) {
    let {value: {enabled = true}} = data
    if (enabled) {
      updateDisabled(data)
      $(document).ready(function() {
        let position = {}
        // add draggable event if it doesnt exist
        if (!$(el).data('uiDraggable')) {
          $(el).draggable({
            containment: 'document',
            revert: 'invalid',
            helper: 'clone',
            appendTo: 'body',
            zIndex: 10000
          })
        }
        // bind draggable
        $(el).bind({
          dragstart: function(e, ui) {
            position = getPositionConnector(el, data, ui, e)
            dragStartEL(ui, data, position)
            $(document).one('mouseup.connectorDirective', function () {
              dragStopEL()
            })
          },
          drag: function(e, ui) {
            dragEL(ui, data, position)
          },
          dragstop: function() {
            dragStopEL()
          }
        })
      })
    }
  },
  update (el, data, vnode) {
    updateDisabled(data)
  },
  unbind (el, data, vnode) {
    // no need doing any thing for now
  }
}
