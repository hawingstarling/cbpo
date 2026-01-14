import progressFormatConfig from './progressFormatConfig'
import defaults from 'lodash/defaults'
import ceil from 'lodash/ceil'
import orderBy from 'lodash/orderBy'

const numeral = (string, fallback) => {
  const parseValue = Number.parseInt(string) || Number.parseFloat(string)
  return (!Number.isNaN(parseValue) ? parseValue : fallback).toLocaleString('en-US')
}

/**
 * @param {Object} formatConfig object format config
 * @param {boolean} isHtml return function is Html
 */
export default (formatConfig, isHtml) => {
  defaults(formatConfig, progressFormatConfig)
  formatConfig.conditions = orderBy(formatConfig.conditions || [], 'max')

  return (value) => {
    const percent = `${ceil(Math.min((value / formatConfig.base) * 100, 100), 2)}`
    if (!isHtml) return percent

    const template = (percent, color, label) => `
        <div class="cbpo-progress-container" title="${numeral(label, value)}">
          <div class="cbpo-progress" style="width: ${percent}%; background-color: ${color}"></div>
        </div>`
    switch (formatConfig.visualization) {
      case 'bar':
        return template(percent, formatConfig.color, formatConfig.label)
      case 'bar_with_conditions':
        const condition = formatConfig.conditions.find(c => percent <= c.max)
        return template(percent, condition ? condition.color : formatConfig.color, formatConfig.label)
      case 'percentage':
        return percent
      default:
        console.error(formatConfig.visualization + ' is not supported')
        break
    }
  }
}
