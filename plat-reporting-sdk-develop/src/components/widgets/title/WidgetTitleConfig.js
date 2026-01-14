import _ from 'lodash'
export const DEFAULT_WIDGET_TITLE_CONFIG = {
  title: {
    text: 'Widget Title',
    enabled: true,
    edited: false
  },
  style: {
    background_color: null,
    foreground_color: null,
    header_background_color: null,
    header_foreground_color: null,
    border_width: null,
    border_radius: null
  }
}

export const makeWidgetDefaultConfig = (configObj) => {
  _.defaultsDeep(configObj, DEFAULT_WIDGET_TITLE_CONFIG)
}
