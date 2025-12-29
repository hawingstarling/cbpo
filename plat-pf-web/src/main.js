// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import VueRouter from 'vue-router'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Vuelidate from 'vuelidate'
import store from '@/store/store'
import Toasted from 'vue-toasted'
import '@coreui/coreui/scss/coreui.scss'
import VueMoment from 'vue-moment'
import _nav from '@/_nav'
import importModule from 'plat-import-lib'
import pfAxios from './services/pfAxios'
import sdkModule from 'plat-rs-sdk'
import 'plat-rs-sdk/dist/reporting-sdk.css'
import 'plat-import-lib/dist/import-lib-web.css'
import '@/assets/scss/style.scss'
import 'plat-coreui-themes/src/assets/scss/themes/precise-theme.scss'
import 'plat-rs-sdk/dist/precise-theme.css'
import moment from 'moment-timezone'

Vue.use(VueMoment, {
  moment
})
Vue.use(Toasted)
Vue.use(Vuelidate)
Vue.use(BootstrapVue)
Vue.use(VueRouter)
Vue.config.productionTip = false

const EventBus = new Vue()

Object.defineProperties(Vue.prototype, {
  $bus: {
    get: function () {
      return EventBus
    }
  }
})

const getClientId = () => {
  return process.env.VUE_APP_PF_CLIENT_ID
}

const getToken = () => {
  return localStorage.getItem('auth') ? JSON.parse(localStorage.getItem('auth')).ps.userModule.userToken : process.env.VUE_APP_PF_API_DEV_ACCESS_TOKEN
}

const DS_API_CONFIG = {
  baseUrl: process.env.VUE_APP_DS_API_BASE_URL
}

const endPointAPI = {
  process: `/v1/clients/${_nav.clientId}`
}

Vue.use(importModule, { store, router, _nav, endPointAPI })

importModule.setAxios(pfAxios)

router.beforeEach((to, from, next) => {
  to.path === '/pf' ? next({name: 'PFAnalysis', params: {client_id: _nav.clientId}}) : next()
})

Vue.use(sdkModule, {getToken, getClientId, themeClass: 'cbpo-sdk-precise-theme', DS_API_CONFIG})

/* eslint-disable no-new */
new Vue({
  router,
  store,
  render: (h) => h(App)
}).$mount('#app')
