const getAxiosInstance = (baseURL, token = this.VUE_DEMO_TOKEN, clientId = '') => {
  const axiosInstance = axios.create({
    baseURL
  })

  axiosInstance.interceptors.request.use(
    config => {
      if (clientId) {
        config.headers['x-ps-client-id'] = clientId
        config.headers.authorization = 'Bearer ' + token
      } else {
        config.headers.authorization = token
      }
      return config
    },
    err => Promise.reject(err)
  )
  axiosInstance.interceptors.response.use((response) => {
    if (response.status !== 200) {
      // let handler = CBPO.dsManager().getRemoteAPICallbackErrorHandler()
      // if (!handler) {
      //   console.log('No remove API error handler.')
      // } else {
      //   handler(response.status)
      // }
    }
    return response
  }, (error) => {
    if (error.response && error.response.data) {
      return Promise.reject(error.response.data)
    }
    return Promise.reject(error.message)
  })

  return axiosInstance
}
