const notImplementedText = 'not implemented'

class AbstractDataSource {
  /**
   * Construct the datasource with an id.
   *
   * @param {string} id The data source id.
   */
  constructor (id) {
    this._id = id
  }

  async columns (params) {
    throw notImplementedText
  }

  /**
   *
   * @param {object} params The query parameters.
   * @param {object} cancelToken token was create by CancelAxios
   */
  async query (params, cancelToken) {
    throw notImplementedText
  }

  /**
   * @param {Object} params: query params
   * @param {string} fileName: name of file will be downloaded
   * @param {string} fileType: type The file type export
   * @param {Array} columns: columns of SDK
   **/
  async export (params, fileName, fileType, columns) {
    throw notImplementedText
  }

  /**
   *
   * @param {object} params The query parameters.
   * @param {object} cancelToken token was create by CancelAxios
   */
  async total (params, cancelToken) {
    throw notImplementedText
  }
}

export default AbstractDataSource
