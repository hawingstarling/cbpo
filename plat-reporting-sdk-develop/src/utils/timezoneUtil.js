import moment from 'moment-timezone'
import get from 'lodash/get'

const timezoneData = require('../components/widgets/elements/timezone-selector/timezoneData')

const findUTCIndex = (datetime) => {
  return timezoneData.findIndex(item =>
    item.utc.find((utcItem) => utcItem === datetime)
  )
}

export const defaultTimezone = (config) => {
  const indexUTC = config.timezone.utc
    ? findUTCIndex(config.timezone.utc)
    : findUTCIndex(moment.tz.guess())

  if (get(config, 'timezone.enabled') && !get(config, 'timezone.utc')) {
    config.timezone.utc = timezoneData[indexUTC].utc[0]
  }
}
