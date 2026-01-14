import LocalDataSource from '@/services/ds/data-sources/LocalDataSource.js'
import RemoteDataSource from '@/services/ds/data-sources/RemoteDataSource.js'
import HybridDataSource from '@/services/ds/data-sources/HybridDataSource.js'

var cached = {}

class DsManager {
  url = undefined
  apiToken = undefined
  clientId = undefined
  callbackErrorHandler = undefined

  getDataSource (id) {
    // TODO make better caching that based on the data but the id
    // if (cached[id]) {
    //   return cached[id]
    // }
    if (window[id]) {
      cached[id] = id.startsWith('hybrid___') ? new HybridDataSource(id) : new LocalDataSource(id)
    } else {
      cached[id] = new RemoteDataSource(id)
    }
    return cached[id]
  }

  setRemoteAPIBaseUrl(url) {
    this.url = url
  }

  getRemoteAPIBaseUrl() {
    return this.url
  }

  setRemoteAPIToken(apiToken) {
    this.apiToken = apiToken
  }

  getRemoteAPIToken() {
    return this.apiToken
  }

  setRemoteAPIClientId(clientId) {
    this.clientId = clientId
  }

  getRemoteAPIClientId() {
    return this.clientId
  }

  getRemoteAPICallbackErrorHandler() {
    return this.callbackErrorHandler
  }

  setRemoteAPICallbackErrorHandler(callback) {
    this.callbackErrorHandler = callback
  }
}

export default new DsManager()
