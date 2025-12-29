import axios from 'axios'
import LS from './_localStorage'
import get from 'lodash/get'

const ROOT_API = process.env.VUE_APP_PF_API_BASE_URL

const pfAxios = axios.create({
  baseURL: ROOT_API,
  timeout: 600000
})

pfAxios.interceptors.request.use(function (config) {
  let apiToken = localStorage.getItem('auth') ? get(JSON.parse(localStorage.getItem('auth')), 'ps.userModule.userToken', '') : LS.getCurrentAccessToken()
  if (apiToken) {
    config.headers.Authorization = 'Bearer ' + apiToken
  }
  const clientID = localStorage.getItem('auth') ? get(JSON.parse(localStorage.getItem('auth')), 'ps.userModule.current_client.id', '') : LS.getCurrentClientId()
  config.headers['x-ps-client-id'] = clientID
  return config
}, function (error) {
  return Promise.reject(error)
})

pfAxios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  return Promise.reject(error)
})

export default pfAxios
