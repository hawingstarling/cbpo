class ConfigService {
  version = '1.0.0'

  getConfig = async (baseURL, token, clientId, payload) => {
    let {id} = payload
    try {
      let response = await getAxiosInstance(baseURL, token, clientId).get(`configs/${id}`)
      return response.data
    } catch (e) {
      throw new Error(e)
    }
  }

  createConfig = async (baseURL, token, clientId, payload) => {
    let {data} = payload
    try {
      let response = await getAxiosInstance(baseURL, token, clientId).post(`configs`, data)
      return response.data
    } catch (e) {
      throw new Error(e)
    }
  }

  updateConfig = async (baseURL, token, clientId, payload) => {
    let {id, data} = payload
    try {
      let response = await getAxiosInstance(baseURL, token, clientId).put(`configs/${id}`, data)
      return response.data
    } catch (e) {
      throw new Error(e)
    }
  }

  setConfigToStorage = (configs) => {
    localStorage.setItem('SDK-LiveDocs', JSON.stringify({
      version: this.version,
      configs: configs
    }))
  }

  getConfigFromStorage = () => {
    let storage = localStorage.getItem('SDK-LiveDocs')
    let v = this.version
    if (storage) {
      storage = JSON.parse(storage)
      let {version, configs} = storage
      if (version !== v) {
        this.setConfigToStorage([])
        return []
      }
      return configs
    } else {
      this.setConfigToStorage([])
      return []
    }
  }

  findConfig = (baseURL, dataSource) => {
    return this.getConfigFromStorage().find(item => item.baseURL === baseURL && item.dataSource === dataSource)
  }

  addNewLocalConfig = (baseURL, dataSource, configId) => {
    let configs = this.getConfigFromStorage()
    let index = _.findIndex(configs, item => item.baseURL === baseURL && item.dataSource === dataSource)
    if (index === -1) {
      configs = [...configs, {baseURL, dataSource, configId}]
      this.setConfigToStorage(configs)
    }
  }
}

const configService = new ConfigService()
