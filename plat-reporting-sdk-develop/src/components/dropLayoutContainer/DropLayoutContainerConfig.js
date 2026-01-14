import defaultsDeep from 'lodash/defaultsDeep'

export const DEFAULT_LAYOUT_CONTAINER_CONFIG = {
  scope: '',
  buildDashboard: {
    enabled: false
  },
  dashboardConfig: {}
}

export const makeDefaultDropLayoutContainerConfig = (config) => {
  config = defaultsDeep(config, DEFAULT_LAYOUT_CONTAINER_CONFIG)
  return config
}
