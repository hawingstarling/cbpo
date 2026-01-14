import $ from 'jquery'
export default {
  bind(el, binding, vnode) {
    if (binding.value.enabled) {
      // add event keydown for windown
      $(window)
        .on(`keydown.table-${vnode.context._uid}`, (event) => {
          let _scrollLeft = $(el).scrollLeft()
          // ArrowLeft
          if (event.keyCode === 37) {
            $(el).scrollLeft(_scrollLeft - 100)
          }
          // ArrowRight
          if (event.keyCode === 39) {
            $(el).scrollLeft(_scrollLeft + 100)
          }
        })
    }
  },
  unbind(el, binding, vnode) {
    if (binding.value.enabled) {
      $(window).off(`keydown.table-${vnode.context._uid}`)
    }
  }
}
