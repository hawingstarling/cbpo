import _ from 'lodash'
import { defaultFilterConfig } from '@/components/widgets/builder/DynamicFilterConfig'
import { defaultColumnConfig } from '@/components/widgets/columns/ManageColumnConfig'
import { makeMenuDefaultConfig } from '@/components/widgets/menu/MenuConfig'
import { DEFAULT_WIDGET_TITLE_CONFIG } from '@/components/widgets/title/WidgetTitleConfig'

export const defaultGridItemConfig = {
  x: 0,
  y: 0,
  w: 12,
  h: 4,
  i: 0
}

export const DEFAULT_WIDGET_CONFIG = {
  grid: _.cloneDeep(defaultGridItemConfig),
  autoHeight: false,
  widget: _.cloneDeep(DEFAULT_WIDGET_TITLE_CONFIG),
  action: {
    elements: []
  },
  elements: [],
  filter: {
    form: {
      config: {
        controls: [],
        query: {}
      }
    },
    base: {
      config: {
        query: {}
      }
    },
    builder: {
      enabled: false,
      readable: {
        enabled: false
      },
      config: _.cloneDeep(defaultFilterConfig)
    },
    globalFilter: {
      enabled: false
    },
    alignment: ''
  },
  columnManager: {
    enabled: false,
    config: _.cloneDeep(defaultColumnConfig)
  },
  calculatedColumn: {
    enabled: false
  },
  menu: {
    enabled: true,
    config: {}
  },
  waitingForGlobalFilter: false
}

export const makeWidgetDefaultConfig = (configObj) => {
  let defaultConfig = _.defaultsDeep(configObj, DEFAULT_WIDGET_CONFIG)
  makeMenuDefaultConfig(defaultConfig.menu.config)
  return Object.assign({}, defaultConfig)
}
