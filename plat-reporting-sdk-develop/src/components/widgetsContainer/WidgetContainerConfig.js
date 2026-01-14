import defaultsDeep from 'lodash/defaultsDeep'

const DEFAULT_WIDGET_CONTAINER_CONFIG = {
  scope: '',
  class: '',
  style: '',
  dragWidgets: {
    enabled: false
  },
  widgets: []
}

export const makeDefaultWidgetContainerConfig = (config) => {
  defaultsDeep(config, DEFAULT_WIDGET_CONTAINER_CONFIG)
}
