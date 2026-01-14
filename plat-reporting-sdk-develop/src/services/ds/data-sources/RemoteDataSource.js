import AbstractDataSource from './AbstractDataSource'
import axios from 'axios'
import _ from 'lodash'
import CBPO from '@/services/CBPO'
import { handleExportFileFromObject } from '@/utils/fileUtil'

const DS_EXPORT_JOB_STATUS = { success: 'success', error: 'error' }
const EXPORT_POLLING_MIN_INTERVAL = 2000
const EXPORT_MAX_TIMEOUT = 300000 // 5 minutes

async function getTableData (query, cancelToken) {
  try {
    const options = cancelToken ? { cancelToken: cancelToken.token } : {}
    let response = await this.axiosInstance.post(
      `ds/${this._id}/exec`,
      {query},
      options
    )
    return response.data
  } catch (e) {
    throw new Error(e)
  }
}

async function getCount (query, cancelToken) {
  try {
    const options = cancelToken ? { cancelToken: cancelToken.token } : {}
    let response = await this.axiosInstance.post(`ds/${this._id}/count`, {query}, options)
    return response.data.count
  } catch (e) {
    throw new Error(e)
  }
}

async function getColumns () {
  let response = await this.axiosInstance.get(`ds/${this._id}/columns`)
  return response.data.columns
}

async function exportData(query, polling, pollingInterval) {
  try {
    if (polling) {
      let response = await this.axiosInstance.post(`ds/${this._id}/export-request`, {query})

      const {export_request_id: exportId} = response.data
      if (!exportId) {
        throw new Error('Export failed: no export ID returned')
      }

      const startTime = Date.now()
      if (typeof pollingInterval !== 'number' || pollingInterval <= 0) {
        console.warn(`Invalid pollingInterval: ${pollingInterval}. Using default value: ${EXPORT_POLLING_MIN_INTERVAL}`)
        pollingInterval = EXPORT_POLLING_MIN_INTERVAL
      }
      while (Date.now() - startTime < EXPORT_MAX_TIMEOUT) {
        await new Promise(resolve => setTimeout(resolve, pollingInterval))
        let exportData = await this.axiosInstance.get(`ds/${this._id}/export-request/${exportId}`)
        const { status, file_uri: fileUri } = exportData.data

        if (status === DS_EXPORT_JOB_STATUS.success && fileUri) {
          return exportData.data
        }
        if (status === DS_EXPORT_JOB_STATUS.error) {
          throw new Error('Export failed: get status error')
        }
      }
      throw new Error('Export request timed out: Job did not complete within the expected time')
    } else {
      let response = await this.axiosInstance.post(`ds/${this._id}/export`, {query})
      return response.data
    }
  } catch (error) {
    throw error instanceof Error ? error : new Error(String(error))
  }
}

class RemoteDataSource extends AbstractDataSource {
  constructor (dsId) {
    super(dsId)
    this.axiosInstance = axios.create({
      baseURL: CBPO.dsManager().getRemoteAPIBaseUrl() || '',
      timeout: 60000
    })
    this.axiosInstance.interceptors.request.use(
      config => {
        let clientId = CBPO.dsManager().getRemoteAPIClientId()
        let token = CBPO.dsManager().getRemoteAPIToken()
        if (clientId) {
          // If user not setting client or token, DS will check and throw error 401.
          // SDK should not add empty headers and token (need for demo, at least for now)
          config.headers['x-ps-client-id'] = clientId || ''
          config.headers.Authorization = 'Bearer ' + token || ''
        } else {
          config.headers.Authorization = token || ''
        }
        return config
      },
      err => Promise.reject(err)
    )
    this.axiosInstance.interceptors.response.use((response) => {
      return response
    }, (error) => {
      if (error.response && error.response.data) {
        let handler = CBPO.dsManager().getRemoteAPICallbackErrorHandler()
        if (!handler) {
          console.log('No remove API error handler.')
        } else {
          handler(error.response.data.statusCode)
        }
        return Promise.reject(error.response.data)
      }
      return Promise.reject(error.message)
    })
  }

  async columns () {
    // eslint-disable-next-line no-return-await
    return await getColumns.bind(this)()
  }

  async query (params, cancelToken) {
    if (!params.paging) params.paging = {current: 1, limit: 1000}
    if (!params.paging.current) {
      params.paging.current = 1
    }
    let query = _.cloneDeep(params)
    // Get Table Data
    // eslint-disable-next-line no-return-await
    return await getTableData.bind(this)(query, cancelToken)
  }

  async export(params, fileName = '', fileType = 'csv', columns = [], polling = true, pollingInterval = EXPORT_POLLING_MIN_INTERVAL) {
    // polling = false: export is triggered and response is returned immediately in a single request
    // This may cause an Axios timeout if the file is large
    // pollingInterval only works when polling is true
    let query = _.cloneDeep(params)
    // Export Data
    // eslint-disable-next-line no-return-await

    let data = await exportData.bind(this)(query, polling, pollingInterval)
    // handle download file
    handleExportFileFromObject(data, fileName)
    return data.file_uri || ''
  }

  async total (params, cancelToken) {
    let query = _.cloneDeep(params)
    // eslint-disable-next-line no-return-await
    return await getCount.bind(this)(query, cancelToken)
  }
}

export default RemoteDataSource
