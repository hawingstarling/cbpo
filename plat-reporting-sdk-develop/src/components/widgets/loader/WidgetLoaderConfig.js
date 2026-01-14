import _ from 'lodash'
import {defaultMenuConfig} from '@/components/widgets/loader/MenuConfig'

export const defaultGridItemConfig = {
  x: 0,
  y: 0,
  w: 12,
  h: 4,
  i: 0
}

export const DEFAULT_WIDGET_LOADER_CONFIG = {
  grid: _.cloneDeep(defaultGridItemConfig),
  widgetId: null,
  dataSource: null,
  menu: {
    enabled: true,
    config: _.cloneDeep(defaultMenuConfig)
  },
  widget: {
    style: {}
  },
  save: function() {},
  load: function() {},
  beforeSave: function() {}
}

export const makeWidgetLoaderDefaultConfig = (configObj) => {
  let defaultConfig = _.defaultsDeep(configObj, DEFAULT_WIDGET_LOADER_CONFIG)
  return Object.assign({}, defaultConfig)
}
