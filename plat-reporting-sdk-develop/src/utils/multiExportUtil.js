import get from 'lodash/get'

export const getFileName = (config) => {
  return get(config, 'exportConfig.fileName') || get(config, 'widget.title.text') || 'export'
}

export const getPollingSetting = (config) => {
  return get(config, 'exportConfig.polling')
}

export const getPollingIntervalSetting = (config) => {
  return get(config, 'exportConfig.pollingInterval')
}
