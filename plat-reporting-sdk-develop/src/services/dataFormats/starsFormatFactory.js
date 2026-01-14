import starFormatConfig from './starsFormatConfig'
import dataFormatManager from '@/services/dataFormatManager'
import _ from 'lodash'
/**
 * @param {Object} formatConfig object format config
 */
export default (formatConfig, isHtml) => {
  _.defaultsDeep(formatConfig, starFormatConfig)
  const { maximum, value: {display, format}, style: {color, half} } = formatConfig
  let templateHTML = ` <i style="color: ${color}" class="fa fa-star"></i>`

  const formatLabelStars = (value) => {
    value = `${dataFormatManager.format(value, format, true)}`
    let max = parseInt(value) < maximum ? parseInt(value) : maximum
    let dataStars = ``
    for (let index = 0; index < max; index++) {
      dataStars = dataStars.concat(templateHTML)
    }
    if (value < maximum && half) {
      const decimalNumber = value - parseInt(value)
      if (decimalNumber >= 0.25 && decimalNumber < 0.75) {
        let halfStyleHtml = ` <i style="color: ${color}" class="fa fa-star-half-o"></i>`
        dataStars = dataStars.concat(halfStyleHtml)
      } else if (decimalNumber >= 0.75) {
        dataStars = dataStars.concat(templateHTML)
      }
    }
    const labelStars = {
      left: `${isNaN(value) ? '' : value} ${dataStars}`,
      right: `${dataStars} ${isNaN(value) ? '' : value}`,
      none: `${dataStars}`
    }
    return labelStars[display] || labelStars[`none`]
  }

  return (value) => {
    return isHtml ? formatLabelStars(value) : value
  }
}
