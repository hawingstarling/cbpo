import defaultsDeep from 'lodash/defaultsDeep'
import cloneDeep from 'lodash/cloneDeep'
import {defaultMenuConfig} from '@/components/dashboard/MenuConfig'
export const DEFAULT_DASHBOARD_CONFIG = {
  style: {
    background_color: null,
    foreground_color: null,
    header_background_color: null,
    header_foreground_color: null,
    border_width: null,
    border_radius: null
  },
  widget: {
    title: {
      enabled: true,
      text: 'Dashboard Builder'
    }
  },
  widgetLayout: {},
  menu: {
    enabled: true,
    config: cloneDeep(defaultMenuConfig)
  }
}

export const makeWidgetDefaultConfig = (configObj) => {
  defaultsDeep(configObj, DEFAULT_DASHBOARD_CONFIG)
  return configObj
}
