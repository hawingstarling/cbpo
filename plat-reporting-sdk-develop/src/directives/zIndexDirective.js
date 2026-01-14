import $ from 'jquery'

export default {
  bind (el, data, vnode) {
    $(el).bind('mouseenter', function (e) {
      $(el).addClass('z-index-directive')
    })
    $(el).bind('mouseleave', function (e) {
      $(el).removeClass('z-index-directive')
    })
  },
  update (el, data, vnode) {
  },
  unbind (el, data, vnode) {
  }
}
