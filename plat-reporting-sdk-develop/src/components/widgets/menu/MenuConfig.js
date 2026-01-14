import _ from 'lodash'

export const defaultMenuOptions = [{
  label: 'Widget Settings',
  icon: 'fa fa-cog',
  value: 'widget-settings',
  type: 'item'
},
{
  label: 'Element Settings',
  icon: 'fa fa-cog',
  value: 'element-settings',
  type: 'item'
},
{
  label: 'Remove',
  icon: 'fa fa-times',
  value: 'remove',
  type: 'item'
},
{
  type: 'divider'
},
{
  label: 'Export CSV',
  icon: 'fa fa-download',
  value: 'csv',
  type: 'item'
},
{
  label: 'Data Source',
  icon: 'fa fa-database',
  value: '',
  link: true,
  type: 'item'
}]

export const defaultMenuConfig = {
  label: {
    text: ''
  },
  icons: {
    css: 'fa fa-ellipsis-h'
  },
  dataSource: null,
  selection: {
    dsUrl: '',
    // option ({label, value})
    options: []
  }
}

export const makeMenuDefaultConfig = (configObj) => {
  let defaultOptions = _.cloneDeep(defaultMenuOptions)
  const optionsConfig = _.get(configObj, 'selection.options', [])
  defaultOptions = defaultOptions.filter(option => {
    let optionValue = ''
    optionsConfig.forEach(p => {
      if (option.value === p.value) optionValue = p.value
    })
    return option.value !== optionValue
  })
  const linkOption = optionsConfig.find(item => item.link)
  if (linkOption) {
    defaultOptions = defaultOptions.filter(item => !item.link)
  }
  defaultMenuConfig.selection.options = _.cloneDeep(defaultOptions)
  _.defaultsDeep(configObj, defaultMenuConfig)
}
