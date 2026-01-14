import _ from 'lodash'
import * as slugify from 'slugify'

const TYPE = {
  CSV: 'csv'
}

const TYPE_FORMAT = {
  csv: {
    format: 'text/csv;charset=utf-8;',
    colDelim: `,`,
    rowDelim: `\n`
  }
}
/**
 *
 * @param {Array} data List data export
 * @param {string} type The file type export
 * @return {Blob} the data export
 */
export const formatArrayToBlob = (data, type) => {
  let blobData = _.cloneDeep(data)
  switch (type) {
    default:
      blobData = blobData
        .map(row =>
          row.map(data => {
            if ([null, undefined, NaN, ''].includes(data)) {
              return ''
            }
            // Check if data includes special characters such as: '"', ',', or '\n'
            if (typeof data === 'string') {
              return `"${data.replace(/"/g, '""')}"`
            }
            return data
          })
            .join(TYPE_FORMAT[TYPE.CSV].colDelim))
        .join(TYPE_FORMAT[TYPE.CSV].rowDelim)
      type = TYPE_FORMAT[TYPE.CSV].format
      break
  }
  return new Blob([blobData], { type })
}

/**
 * @param {Blob} blobFile
 * @param {string} fileName
 * **/
export const handleExportFileFromBlobType = (blobFile, fileName) => {
  const newFileName = slugify(fileName)
  if (window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveBlob(blobFile, `${newFileName}.csv`)
  } else {
    let a = window.document.createElement('a')
    a.href = window.URL.createObjectURL(blobFile, { type: 'text/plain' })
    a.download = `${newFileName}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
}
/**
 * @typedef {Object} DataExport
 * @property {string} file_uri
 * @property {string} file_name
 * @property {number} limited
 * @property {number} total
 * **/
/**
 * @param {DataExport} dataExport
 * @param {string} fileName
 * **/
export const handleExportFileFromObject = (dataExport, fileName) => {
  if (!dataExport.file_uri) throw new Error('file_uri is undefined')
  const newFileName = slugify(fileName)
  let a = window.document.createElement('a')
  if (newFileName) {
    a.href = `${dataExport.file_uri}?response-content-disposition=attachment;filename=${newFileName}.csv`
  } else {
    a.href = dataExport.file_uri
  }
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
