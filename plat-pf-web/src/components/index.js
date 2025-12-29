import modulesStore from '@/store/modules'
import { routerRender } from '@/router/routes.js'
import routes from '@/router/_routerConfig'
import nav from '@/_nav'
import '@/assets/scss/style.scss'
import pfAxios from '@/services/pfAxios'
import dsAxios from '@/services/dsAxios'
import get from 'lodash/get'
// import isFunction from 'lodash/isFunction'
import LS from '@/services/_localStorage'
import PFSidebarNav from '@/containers/PFSidebarNav'
import isObject from 'lodash/isObject'
import { GET_GLOBAL_TOAST_INFO, SAVE_GLOBAL_TOAST_INFO, SAVE_ERROR_NETWORK_TOAST_INFO, RESET_ERROR_NETWORK_TOAST_INFO, HIDE_NETWORK_ERROR_IF_SHOWING } from '@/services/_constant'

const Components = {}

const plugins = {
  install: function(Vue, options = {}) {
    if (!options.store || !options.layout || !options.router || !options.nav || !options.PF_API_CONFIG) {
      console.log('Please check params again!')
    }

    // baseUrl PF
    if (options.PF_API_CONFIG) {
      if (options.PF_API_CONFIG.baseUrl) {
        pfAxios.defaults.baseURL = options.PF_API_CONFIG.baseUrl
      }
    }

    if (options.DS_API_CONFIG) {
      if (options.DS_API_CONFIG.baseUrl) {
        dsAxios.defaults.baseURL = options.DS_API_CONFIG.baseUrl
        window.URL.VUE_APP_DS_API_BASE_URL = options.DS_API_CONFIG.baseUrl
      }
    }

    if (options.PF_WEB_CONFIG) {
      if (options.PF_WEB_CONFIG.VUE_APP_PF_USER_ID) {
        window.URL.VUE_APP_PF_USER_ID = options.PF_WEB_CONFIG.VUE_APP_PF_USER_ID
      }

      if (options.PF_WEB_CONFIG.VUE_APP_PF_API_DEV_ACCESS_TOKEN) {
        window.URL.VUE_APP_PF_API_DEV_ACCESS_TOKEN = options.PF_WEB_CONFIG.VUE_APP_PF_API_DEV_ACCESS_TOKEN
      }

      if (options.PF_WEB_CONFIG.VUE_APP_PF_CLIENT_ID) {
        window.URL.VUE_APP_PF_CLIENT_ID = options.PF_WEB_CONFIG.VUE_APP_PF_CLIENT_ID
      }

      if (options.PF_WEB_CONFIG.VUE_APP_PF_IS_BETA) {
        window.URL.VUE_APP_PF_IS_BETA = options.PF_WEB_CONFIG.VUE_APP_PF_IS_BETA
      }
    }

    // request PF
    const setCount = (type, loadingType) => {
      const loading = loadingType || 'progress'
      options.store.dispatch(`ps/loadingModule/SET_COUNT`, {type, loading})
    }
    const defaultMsg = options.store.getters[`ps/loadingModule/GET_DEFAULT_MESSAGE`]
    const setMessage = (type, msg = '', url = '') => {
      if (msg && url) {
        options.store.dispatch(`ps/loadingModule/SET_MESSAGE`, { type, msg, url })
      }
    }

    pfAxios.interceptors.request.use(function (config) {
      const apiToken = LS.getCurrentAccessToken()
      const clientID = options.store.getters['ps/userModule/GET_CURRENT_CLIENT'].id || LS.getCurrentClientId()
      config.headers.Authorization = `Bearer ${apiToken}`
      config.headers['x-ps-client-id'] = clientID
      // loading
      if (options.store && !get(config, 'ignoreLoading')) {
        setCount('increment', get(config, 'loading'))
        // set message
        config.message = config.message || defaultMsg
        setMessage('increment', config.message, config.url)
      }
      return config
    }, function (error) {
      return Promise.reject(error)
    })

    // retry
    // const retryFn = (error, axios) => {
    //   if (get(error, 'response.status') === 401) {
    //     if (options.retryOn401 && isFunction(options.retryOn401)) {
    //       return options.retryOn401().then((token) => {
    //         error.config.headers['Authorization'] = `Bearer ${token}`
    //         error.config._retry = true
    //         return axios(error.config)
    //       })
    //     }
    //   }
    // }

    // Response PF
    pfAxios.interceptors.response.use(function (response) {
      // loading
      if (options.store && !get(response, 'config.ignoreLoading')) {
        setCount('decrease', get(response, 'config.loading'))
        // set message
        setMessage('decrease', get(response, 'config.message'), get(response, 'config.url'))
      }
      // hide network error if showing
      options.store.dispatch(`ps/globalToast/${HIDE_NETWORK_ERROR_IF_SHOWING}`)
      return response
    }, function (error) {
      // loading
      if (options.store && !get(error, 'config.ignoreLoading')) {
        setCount('decrease', get(error, 'config.loading'))
        // set message
        setMessage('decrease', get(error, 'config.message'), get(error, 'config.url'))
      }
      // redirect to login page when can not refresh token and 401
      if (get(error, 'response.status') === 401) {
        Vue.prototype.$bus.$emit('relogin', get(options, 'router.currentRoute.path', ''))
        return Promise.reject(error)
      }
      // 401 status
      // retryFn(error, pfAxios)
      // 500 status
      if (get(error, 'response.status') >= 500) {
        const globalToastFor500Error = 'error500'
        let globalToastInfo = options.store.getters[`ps/globalToast/${GET_GLOBAL_TOAST_INFO}`] || []
        if (!globalToastInfo.includes(globalToastFor500Error)) {
          Vue.toasted.global.error500()
          options.store.dispatch(`ps/globalToast/${SAVE_GLOBAL_TOAST_INFO}`, globalToastFor500Error)
          options.store.dispatch(`ps/globalToast/${RESET_ERROR_NETWORK_TOAST_INFO}`)
        }
        return
      }
      // Network error
      if (get(error, 'message') === 'Network Error') {
        const globalToastForNetworkError = 'errorNetwork'
        let globalToastInfo = options.store.getters[`ps/globalToast/${GET_GLOBAL_TOAST_INFO}`] || []
        if (!globalToastInfo.includes(globalToastForNetworkError)) {
          options.store.dispatch(`ps/globalToast/${SAVE_GLOBAL_TOAST_INFO}`, globalToastForNetworkError)
          options.store.dispatch(`ps/globalToast/${SAVE_ERROR_NETWORK_TOAST_INFO}`, Vue.toasted.global.errorNetwork())
        }
        return
      }
      // return Error object with Promise
      return Promise.reject(error)
    })

    // DS request
    dsAxios.interceptors.request.use(function (config) {
      const apiToken = LS.getCurrentAccessToken()
      const clientID = options.store.getters['ps/userModule/GET_CURRENT_CLIENT'].id || LS.getCurrentClientId()
      if (apiToken) {
        config.headers = {
          Authorization: `Bearer ${apiToken}`,
          'x-ps-client-id': clientID
        }
      }
      // loading
      if (options.store && !get(config, 'ignoreLoading')) {
        setCount('increment', get(config, 'loading'))
        // set message
        config.message = config.message || defaultMsg
        setMessage('increment', config.message, config.url)
      }
      return config
    }, function (error) {
      return Promise.reject(error)
    })

    // DS response
    dsAxios.interceptors.response.use(function (response) {
      // loading
      if (options.store && !get(response, 'config.ignoreLoading')) {
        setCount('decrease', get(response, 'config.loading'))
        // set message
        setMessage('decrease', get(response, 'config.message'), get(response, 'config.url'))
      }
      // hide network error if showing
      options.store.dispatch(`ps/globalToast/${HIDE_NETWORK_ERROR_IF_SHOWING}`)
      return response
    }, function (error) {
      // loading
      if (options.store && !get(error, 'config.ignoreLoading')) {
        setCount('decrease', get(error, 'config.loading'))
        // set message
        setMessage('decrease', get(error, 'config.message'), get(error, 'config.url'))
      }
      // redirect to login page when can not refresh token and 401
      if (get(error, 'response.status') === 401) {
        Vue.prototype.$bus.$emit('relogin', get(options, 'router.currentRoute.path', ''))
        return Promise.reject(error)
      }
      // 401 status
      // retryFn(error, dsAxios)
      // 500 status
      if (get(error, 'response.status') >= 500) {
        const globalToastFor500Error = 'error500'
        let globalToastInfo = options.store.getters[`ps/globalToast/${GET_GLOBAL_TOAST_INFO}`] || []
        if (!globalToastInfo.includes(globalToastFor500Error)) {
          Vue.toasted.global.error500()
          options.store.dispatch(`ps/globalToast/${SAVE_GLOBAL_TOAST_INFO}`, globalToastFor500Error)
          options.store.dispatch(`ps/globalToast/${RESET_ERROR_NETWORK_TOAST_INFO}`)
        }
        return
      }
      // Network error
      if (get(error, 'message') === 'Network Error') {
        const globalToastForNetworkError = 'errorNetwork'
        let globalToastInfo = options.store.getters[`ps/globalToast/${GET_GLOBAL_TOAST_INFO}`] || []
        if (!globalToastInfo.includes(globalToastForNetworkError)) {
          options.store.dispatch(`ps/globalToast/${SAVE_GLOBAL_TOAST_INFO}`, globalToastForNetworkError)
          options.store.dispatch(`ps/globalToast/${SAVE_ERROR_NETWORK_TOAST_INFO}`, Vue.toasted.global.errorNetwork())
        }
        return
      }
      return Promise.reject(error)
    })

    routerRender.forEach((route) => {
      Components[route.name] = route.component
    })
    Object.keys(Components).forEach((name) => {
      Vue.component(name, Components[name])
    })
    Object.keys(modulesStore).map((name) => {
      options.store.registerModule(name, modulesStore[name])
    })
    // use DefaultContainer in Portal
    routes.component = options.layout
    if (routes.children && routes.children.length) {
      routes.children.forEach((route) => {
        if (route.meta && route.meta.title) {
          route.meta.title = route.meta.title + ' - PF - Channel Precision'
        }
      })
    }
    options.router.addRoutes([routes])
    // update _nav
    const currentClient = options.store.getters['ps/userModule/GET_CURRENT_CLIENT'] || ''
    if (currentClient && currentClient.id) {
      nav.setItem = currentClient.id
    }
    options.nav.pf = nav
    // push psNav to pfNav
    // nav.addItems = options.nav.ps.items || []
    if (isObject(options.customSidebar)) {
      options.customSidebar.pf = PFSidebarNav
    }
    // update client_id to store
    Vue.prototype.$bus.$on('ps_set_current_client_id', (clientID) => {
      nav.setItem = clientID
    })
  }
}

export default plugins
