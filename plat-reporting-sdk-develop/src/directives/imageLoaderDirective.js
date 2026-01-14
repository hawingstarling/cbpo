import $ from 'jquery'
import isFunction from 'lodash/isFunction'
import debounce from 'lodash/debounce'

const imageChecking = (el, callback) => {
  let $images = $(el).find('img')
  if ($images.length) {
    var emit = debounce(() => { callback() }, 100)
    $images.toArray().forEach(image => {
      image.complete ? emit() : $(image).on('load', () => emit())
    })
  }
}

const offLoadEvent = (el) => {
  let $images = $(el).find('img')
  if ($images.length) {
    $images.off('load')
  }
}

export default {
  bind(el, data, vnode) {
    let {value = {}} = data
    if (value.callback && isFunction(value.callback)) {
      vnode.context.$nextTick(() => {
        imageChecking(el, value.callback)
      })
    }
  },
  update(el, data, vnode) {
    let {value = {}} = data
    if (value.callback && isFunction(value.callback)) {
      vnode.context.$nextTick(() => {
        imageChecking(el, value.callback)
      })
    }
  },
  unbind(el, data, vnode) {
    let {value = {}} = data
    if (value.callback && isFunction(value.callback)) {
      vnode.context.$nextTick(() => {
        offLoadEvent(el)
      })
    }
  }
}
