import _ from 'lodash'
export const defaultExportConfig = {
  label: {
    text: 'Download'
  },
  icons: {
    css: 'fa fa-ellipsis-h'
  },
  dataSource: null,
  selection: {
    // option ({label, value})
    options: [{
      label: 'Download CSV',
      value: 'csv'
    }]
  }
}

export const makeExportDefaultConfig = (configObj) => {
  _.defaultsDeep(configObj, defaultExportConfig)
}
