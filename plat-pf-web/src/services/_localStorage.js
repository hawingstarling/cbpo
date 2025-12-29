import get from 'lodash/get'
const DUMMY_CLIENT_ID = process.env.VUE_APP_PF_CLIENT_ID
const DUMMY_TOKEN = process.env.VUE_APP_PF_API_DEV_ACCESS_TOKEN
export default {
  getCurrentClientId () {
    return localStorage.getItem('ps_current_client_id') || DUMMY_CLIENT_ID
  },
  getCurrentAccessToken() {
    let auth = localStorage.getItem('auth') ? JSON.parse(localStorage.getItem('auth')) : {}
    return get(auth, 'ps.userModule.userToken') || localStorage.getItem('ps_access_token') || DUMMY_TOKEN
  },
  getItem: (name) => {
    return localStorage.getItem(name)
  },
  getCurrentClientName () {
    return get(JSON.parse(localStorage.getItem('auth')), 'ps.userModule.current_client.name', '')
  }
}
