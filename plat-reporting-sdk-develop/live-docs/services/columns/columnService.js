class ColumnService {
  getColumns = async (baseURL, token, clientId, payload) => {
    let {dataSource} = payload
    try {
      let response = await getAxiosInstance(baseURL, token, clientId).get(`ds/${dataSource}/columns`)
      return response.data
    } catch (e) {
      throw new Error(e)
    }
  }
}

const columnService = new ColumnService()
