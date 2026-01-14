import defaultsDeep from 'lodash/defaultsDeep'
import { generateIdIfNotExist } from '@/utils/configUtil'

export const DEFAULT_DRILL_DOWN_CONFIG = {
  modal: {
    id: null,
    header: {
      text: 'Drill Down'
    },
    actions: {
      applyButton: {
        text: 'Apply'
      },
      cancelButton: {
        text: 'Cancel'
      }
    }
  },
  path: {
    enabled: false,
    settings: []
  }
}

export const makeDefaultDrillDownConfig = (config) => {
  config = defaultsDeep(config, DEFAULT_DRILL_DOWN_CONFIG)
  generateIdIfNotExist(config.modal)
  return config
}
