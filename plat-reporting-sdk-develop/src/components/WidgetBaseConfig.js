import _ from 'lodash'
export const makeWidgetBaseDefaultConfig = (configObj) => {
  _.defaultsDeep(configObj, {widget: {
    title: {
      enabled: true,
      text: ''
    },
    class: '',
    style: {}
  }})
}
