import defaultsDeep from 'lodash/defaultsDeep'
export const defaultMenuConfig = {
  label: {
    text: ''
  },
  icons: {
    css: 'fa fa-ellipsis-h'
  },
  dataSource: null,
  selection: {
    // option ({label, value})
    options: [{
      label: 'Dashboard Settings',
      icon: 'fa fa-cog',
      value: 'widget-settings',
      type: 'item'
    }]
  }
}

export const makeMenuDefaultConfig = (configObj) => {
  defaultsDeep(configObj, defaultMenuConfig)
}
