import {getWidthOfScrollBar} from '@/utils/DOMUtil'
import $ from 'jquery'
import debounce from 'lodash/debounce'

let lastScrollLeft = 0

// cache scroll top
const debounceFn = debounce(function (data) {
  // scroll
  let scrollTop = $(this).scrollTop()
  let height = $(this).height()
  let scrollBar = $(this).hasScrollBar('horizontal') ? getWidthOfScrollBar() : 0

  let currentScrollLeft = $(this).get(0).scrollLeft

  if (currentScrollLeft !== lastScrollLeft) {
    lastScrollLeft = currentScrollLeft
    return
  }

  if (Math.abs($(this).get(0).scrollHeight - (scrollTop + height - scrollBar)) <= 32) {
    data.callback()
  }
}, 100)

export default {
  bind(el, data) {
    if (!data.value.enabled || !data.value.isReady) return ''

    lastScrollLeft = 0

    $(el).off('scroll.lazy-load').on('scroll.lazy-load', function () {
      debounceFn.bind(this)(data.value)
    })
  },
  update(el, data) {
    if (!data.value.enabled || !data.value.isReady) return ''

    lastScrollLeft = 0

    $(el).off('scroll.lazy-load').on('scroll.lazy-load', function () {
      debounceFn.bind(this)(data.value)
    })
  },
  unbind(el) {
    $(el).off('scroll.lazy-load')
  }
}
