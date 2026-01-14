// custom click away directive from https://github.com/simplesmiler/vue-clickaway
let HANDLER = '_vue_clickaway_handler'

function bind(el, binding, vnode) {
  unbind(el)

  let vm = vnode.context

  let {callback, except = ''} = binding.value
  // @NOTE: Vue binds directives in microtasks, while UI events are dispatched
  //        in macrotasks. This causes the listener to be set up before
  //        the "origin" click event (the event that lead to the binding of
  //        the directive) arrives at the document root. To work around that,
  //        we ignore events until the end of the "initial" macrotask.
  // @REFERENCE: https://jakearchibald.com/2015/tasks-microtasks-queues-and-schedules/
  // @REFERENCE: https://github.com/simplesmiler/vue-clickaway/issues/8
  let initialMacrotaskEnded = false
  setTimeout(function() {
    initialMacrotaskEnded = true
  }, 0)

  el[HANDLER] = function(ev) {
    let exceptNode = except ? document.querySelector(except) : null
    // @NOTE: this test used to be just `el.contains`, but working with path is better,
    //        because it tests whether the element was there at the time of
    //        the click, not whether it is there now, that the event has arrived
    //        to the top.
    // @NOTE: `.path` is non-standard, the standard way is `.composedPath()`
    let path = ev.path || (ev.composedPath ? ev.composedPath() : undefined)
    let isContains = path
      ? (path.indexOf(el) >= 0 || path.indexOf(exceptNode) >= 0)
      : (el.contains(ev.target) || (exceptNode ? exceptNode.contains(ev.target) : false))
    if (initialMacrotaskEnded && !isContains) {
      return callback.call(vm, ev)
    }
  }

  document.documentElement.addEventListener('click', el[HANDLER], false)
}

function unbind(el) {
  document.documentElement.removeEventListener('click', el[HANDLER], false)
  delete el[HANDLER]
}

export default {
  bind: bind,
  update: function(el, binding, vnode) {
    if (binding.value === binding.oldValue) return
    bind(el, binding, vnode)
  },
  unbind: unbind
}
