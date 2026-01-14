import _, {cloneDeep} from 'lodash'
import { DEFAULT_WIDGET_CONFIG } from '@/components/widgets/WidgetConfig'

const defaultVisualizationConfig = {
  dataSource: null,
  widgetConfig: cloneDeep(DEFAULT_WIDGET_CONFIG),
  templates: []
}

export const makeDefaultVisualizationWrapperConfig = (config) => {
  let defaultConfig = _.defaultsDeep(config, defaultVisualizationConfig)
  return Object.assign({}, defaultConfig)
}
