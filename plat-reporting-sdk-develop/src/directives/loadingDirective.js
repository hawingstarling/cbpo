import Vue from 'vue'
import Loading from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/vue-loading.css'
import $ from 'jquery'
import _ from 'lodash'
Vue.use(Loading)

const DEFAULT_LOADING = {
  canCancel: false,
  fullPage: false,
  color: '#000000',
  loader: 'spinner',
  width: 64,
  height: 64,
  backgroundColor: '#ffffff',
  opacity: 0.5,
  zIndex: 999,
  labelLeftIcon: '',
  labelRightIcon: '',
  iconLoading: ''
}

const buildLoading = (el, data, vnode) => {
  _.defaults(data.value, DEFAULT_LOADING)
  const { fullPage, labelRightIcon, labelLeftIcon, iconLoading, loading } = data.value

  // Show loading indicator if loading is true and elementLoading is not already an object
  if (loading && (!vnode.context.elementLoading || !_.isObject(vnode.context.elementLoading))) {
    $(el).css('position', 'relative')
    vnode.context.elementLoading = Vue.$loading.show({
      ...data.value,
      container: fullPage ? null : el
    }, {
      default: iconLoading,
      before: labelRightIcon,
      after: labelLeftIcon
    })
  }
  // Hide loading indicator if loading is false and elementLoading is an object
  if (!loading && vnode.context.elementLoading && _.isObject(vnode.context.elementLoading)) {
    setTimeout(() => {
      if (vnode.context && vnode.context.elementLoading && _.isObject(vnode.context.elementLoading)) {
        vnode.context.elementLoading.hide()
        delete vnode.context.elementLoading
      }
    }, 500)
  }
}

export default {
  bind(el, data, vnode) {
    buildLoading(el, data, vnode)
  },
  update(el, data, vnode) {
    buildLoading(el, data, vnode)
  },
  unbind(el, data) {

  }
}
