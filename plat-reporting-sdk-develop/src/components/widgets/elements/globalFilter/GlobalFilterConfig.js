import defaultsDeep from 'lodash/defaultsDeep'
import cloneDeep from 'lodash/cloneDeep'
import { DEFAULT_WIDGET_TITLE_CONFIG } from '@/components/widgets/title/WidgetTitleConfig'

export const defaultConfig = {
  widget: cloneDeep(DEFAULT_WIDGET_TITLE_CONFIG)
}

export const makeDefaultGlobalConfig = (config) => {
  defaultsDeep(config, defaultConfig)
  delete config.widget.title
}
