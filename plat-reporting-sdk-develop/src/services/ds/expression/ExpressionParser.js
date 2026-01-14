import { parseShortcode, SHORT_CODES } from '@/utils/exprUtils'
import { FormatShortcodeHandler } from '@/services/ds/expression/types/FormatShortcodeHandler'
import { KPIShortCodeHandler } from '@/services/ds/expression/types/KPIShortCodeHandler'
import { ListShortCodeHandler } from '@/services/ds/expression/types/ListShortCodeHandler'
import cloneDeep from 'bootstrap-vue/esm/utils/clone-deep'

class ExpressionParser {
  replacer = /\[(\w+).*?\][^\][]*\[\/(\w+)\]/gm
  constructor(replacer) {
    if (replacer) {
      this.replacer = replacer
    }
    this.instance = {
      [SHORT_CODES.FORMAT]: new FormatShortcodeHandler(),
      [SHORT_CODES.KPI]: new KPIShortCodeHandler(),
      [SHORT_CODES.LIST]: new ListShortCodeHandler()
    }
  }

  getExpressions(template = '') {
    const matchedShortcode = template.match(this.replacer)
    let matchedExprs = []
    if (matchedShortcode && matchedShortcode.length) {
      matchedExprs = matchedShortcode.map(shortCode => {
        try {
          let parsedShortcode = parseShortcode(shortCode)
          parsedShortcode.shortCode = shortCode
          return parsedShortcode
        } catch (error) {
          console.error(error)
          return {}
        }
      })
      // filter valid shortCodes
      const validShortcodes = Object.values(SHORT_CODES) || []
      matchedExprs = matchedExprs.filter(shortCode => validShortcodes.includes(shortCode.name))
    }
    return matchedExprs
  }

  async eval(shortCodes, config) {
    let resultShortCode = shortCodes.map(shortCode => this.instance[shortCode.name].evalFormat(shortCode, config))
    let result = await Promise.all(resultShortCode.map((promise, i) =>
      promise
        .then(value => ({ status: 'fulfilled', value }))
        .catch(reason => ({ status: 'rejected', value: reason }))
    ))
    return result
      .map((r, i) => { if (r.value) r.value.type = shortCodes[i].name; return r })
      .filter(r => r.status === 'fulfilled')
      .map(r => r.value)
  }

  replaceShortcodeContent(evalData, decodedContent) {
    if (!(evalData && evalData.length && decodedContent)) return ''
    let parsingContent = decodedContent
    let replacedEvalData = cloneDeep(evalData).map((item, i) => {
      let {data, content} = this.instance[item.type].replaceShortcode(item, parsingContent)
      parsingContent = content
      return data
    })
    return {
      newEvalData: replacedEvalData,
      parsingContent
    }
  }

  applyCallback(dataCallback = []) {
    dataCallback.forEach(data => {
      this.instance[data.type].callback(data)
    })
  }

  // get datasource ids
  getDataSourceIDs(shortCodes) {
    let dataSources = shortCodes.reduce((dsArr, shortCode) => {
      const ds = this.instance[shortCode.name].getDataSourceIDs(shortCode)
      return ds ? [...dsArr, ...ds] : dsArr
    }, [])
    return [...new Set(dataSources)]
  }
}

export default new ExpressionParser()
