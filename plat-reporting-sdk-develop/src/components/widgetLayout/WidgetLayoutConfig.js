import defaultsDeep from 'lodash/defaultsDeep'

export const DEFAULT_WIDGET_LAYOUT_CONFIG = {
  gridConfig: {
    colNum: 12,
    rowHeight: 1,
    margin: [8, 8],
    defaultHeight: 50,
    minHeight: 10,
    responsive: {
      enabled: false,
      breakpoints: { lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 },
      cols: { lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }
    }
  },
  widgets: [],
  layout: []
}

export const makeDefaultLayoutConfig = (layoutConfig) => {
  defaultsDeep(layoutConfig, DEFAULT_WIDGET_LAYOUT_CONFIG)
  return layoutConfig
}
