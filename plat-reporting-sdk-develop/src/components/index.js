import CBPO from '@/services/CBPO'
import components from '@/services/components'
import directives from '@/directives'
import '@/assets/css/main.scss'
import '@/assets/css/base/jquery-ui.scss'
import '@/assets/icons/css/font-awesome.min.css'
import { extend } from 'vee-validate'
import { required } from 'vee-validate/dist/rules'
import { setStyle } from '@/utils/chartUtil'
import VModal from 'vue-js-modal'

extend('required', {
  ...required,
  message: 'This field is required'
})

const plugins = {
  install: (Vue, options) => {
    // use packages in reprting-sdk
    Vue.use(VModal)
    if (!options) options = {}
    // Register component
    for (let prop in components) {
      if (components.hasOwnProperty(prop)) {
        Vue.component(prop, components[prop])
      }
    }
    // register directives
    for (let prop in directives) {
      if (directives.hasOwnProperty(prop)) {
        Vue.directive(prop, directives[prop])
      }
    }
    // window.API_KEY_EDITOR = ''
    // set DS
    if (options.DS_API_CONFIG && options.DS_API_CONFIG.baseUrl) CBPO.dsManager().setRemoteAPIBaseUrl(options.DS_API_CONFIG.baseUrl + '/v1')
    if (options.getToken) CBPO.dsManager().setRemoteAPIToken(options.getToken())
    if (options.getClientId) CBPO.dsManager().setRemoteAPIClientId(options.getClientId())
    if (options.handlerErrorCodeSdk) CBPO.dsManager().setRemoteAPICallbackErrorHandler(options.handlerErrorCodeSdk)
    if (options.SDK_CONFIG && options.SDK_CONFIG.API_KEY_EDITOR) {
      window.API_KEY_EDITOR = options.SDK_CONFIG.API_KEY_EDITOR
    }
    // handle theme
    let {themeClass = 'default-sdk-theme'} = options
    document.querySelector('body').classList.add(themeClass)
    CBPO.channelManager().getChannel().getThemeSvc().setCurrentTheme(themeClass)
    // this color is used by Chart Component
    setStyle(options.chartColor || {
      accentColor: '#000000',
      mainColor: '#ffffff',
      hoverItemColor: '#000000',
      navigationActive: '#17a2b8',
      navigationInactive: '#cecece'
    })
    // CPBO
    Vue.prototype.$CBPO = CBPO
  }
}

export default plugins
