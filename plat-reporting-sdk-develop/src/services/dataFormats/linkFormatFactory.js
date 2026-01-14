import _ from 'lodash'
import linkFormatConfig from './linkFormatConfig'
const URL_CHECK = new RegExp('^(https?:\\/\\/)')
export default (formatConfig, isHtml) => {
  _.defaultsDeep(formatConfig, linkFormatConfig)
  let target = formatConfig.target || '_blank'
  return (value) => {
    if (!isHtml) return value

    let templateHTML = `<a target="${target}" href="{0}">${formatConfig.text.replace('{value}', value)}</a>`
    let href = value
    // if(formatConfig.baseTemplate) {
    //   href = formatConfig.baseTemplate.replace('{value}', value)
    // }
    formatConfig.baseTemplate && (href = formatConfig.baseTemplate.replace('{value}', value))
    return URL_CHECK.test(href) ? templateHTML.replace('{0}', href) : href
  }
}
