const getRAAxiosInstance = () => {
  const raAxiosInstance = axios.create({
    baseURL: 'http://ra-api.qa.channelprecision.com/v1'
  })

  raAxiosInstance.interceptors.request.use(
    config => {
      config.headers.authorization = 'Bearer '
      return config
    },
    err => Promise.reject(err)
  )
  raAxiosInstance.interceptors.response.use((response) => {
    return response
  }, (error) => {
    if (error.response && error.response.data) {
      return Promise.reject(error.response.data)
    }
    return Promise.reject(error.message)
  })

  return raAxiosInstance
}
