const renderMixins = Vue.component('renderMixins', {
  methods: {
    render(selector, template, url, token, clientId) {
      this.reset(selector)
      if (url) this.setBaseURL(url)
      $(selector).html(template)
      window.CBPO.wgManager().init(selector)
      window.CBPO.dsManager().setRemoteAPIToken(token)
      window.CBPO.dsManager().setRemoteAPIClientId(clientId)
      window.CBPO.dsManager().setRemoteAPICallbackErrorHandler(() => {})
    },
    reset(selector) {
      $(selector).html('')
    },
    setBaseURL(baseURL) {
      window.CBPO.dsManager().setRemoteAPIBaseUrl(baseURL)
    }
  }
})
