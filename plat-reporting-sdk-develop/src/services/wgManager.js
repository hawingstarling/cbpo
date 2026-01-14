import Vue from 'vue'
import components from '@/services/components'
import formatDirective from '@/directives/formatDirective'
import $ from 'jquery'
import CBPO from '@/services/CBPO'
const directives = {
  'cbpo-format': formatDirective
}

class WgManager {
  init (selector) {
    $(selector).attr('data-cbpo', '')
    let url = $(selector).data('ds-api-url')
    if (url) CBPO.dsManager().setRemoteAPIBaseUrl(url || process.env.VUE_APP_BASE_URL)
    return new Vue({
      components: components,
      directives: directives
    }).$mount(selector)
  }
}

export default new WgManager()
