import { AbtractShortcodeHandler } from '@/services/ds/expression/types/AbtractShortcodeHandler'
import get from 'lodash/get'
import cloneDeep from 'lodash/cloneDeep'
import findIndex from 'lodash/findIndex'
import isEmpty from 'lodash/isEmpty'
import CBPO from '@/services/CBPO'
import QueryBuilder from '../../query/QueryBuilder'

const ERROR_MES = {
  INVALID_COLUMN_OPTION: 'Missing column option or column name is blank',
  NOT_MATCH: `Column name does not match any column in data source`
}
export class ListShortCodeHandler extends AbtractShortcodeHandler {
  /**
   * Declare callback function
   *  @param {Object} parsedShortcode: shortCode result
   *  @param {Object} config: config of element HTML
   * **/
  async evalFormat(parsedShortcode, config) {
    const attributes = get(parsedShortcode, 'attributes', {})
    const {
      datasource = '',
      column = '',
      groupTag = 'ul',
      itemTag = 'li',
      sort = null,
      'empty-message': emptyMessage = 'None at this time'
    } = attributes

    try {
      let query = new QueryBuilder()
      column && !isEmpty(column) && sort && query.setOrder(column, sort)
      var result = await CBPO.dsManager().getDataSource(datasource).query(query.getParams())
    } catch {
      throw new Error(`Can not get DS data with ds ID ${datasource}`)
    }
    const shortCode = get(parsedShortcode, 'shortCode', '')
    const configShortCode = {
      result,
      shortCode,
      formatObject: {},
      options: { groupTag, itemTag, column, sort, empty_message: emptyMessage }
    }
    return configShortCode
  }

  /**
   * Format value in expression
   * **/
  format(value) {
    if (!value && value !== 0) return ''
  }

  /**
   *  get data query from expression
   *  @param {Object} itemOfEvalData: item of data of evalFormat function
   *  @param {string} parsingContent: template short code
   **/
  replaceShortcode(itemOfEvalData, parsingContent) {
    let {options} = itemOfEvalData
    let index
    if (options.column && !isEmpty(options.column)) {
      index = findIndex(itemOfEvalData.result.cols, {name: options.column})
    } else {
      throw new Error(ERROR_MES.INVALID_COLUMN_OPTION)
    }
    let arrayContent = cloneDeep(itemOfEvalData.result.rows)
    var newContent = ``
    if (index > -1) {
      let listContent = arrayContent.reduce((str, item) => {
        if (item[index] !== null) {
          str += `<${options.itemTag}>${item[index]}</${options.itemTag}>`
        }
        return str
      }, '')
      if (!isEmpty(listContent)) {
        newContent = `<${options.groupTag}>${listContent}</${options.groupTag}>`
      } else {
        newContent = `<${options.groupTag}><${options.itemTag}>${options.empty_message}</${options.itemTag}></${options.groupTag}>`
      }
    } else {
      throw new Error(ERROR_MES.NOT_MATCH)
    }
    parsingContent = parsingContent.replace(itemOfEvalData.shortCode, newContent)
    return {
      data: itemOfEvalData,
      content: parsingContent
    }
  }

  /**
   * this callback is building solid chart
   * @param {Object} data: must contain id which was generate by uuidv4
   * **/
  callback(data) {
  }

  getChartId(id) {
    return `cbpo_shortcode_handler_html_editor_${id}`
  }

  // get datasource IDs
  getDataSourceIDs(shortCode) {
    const ds = get(shortCode, 'attributes.datasource', '')
    return ds ? [ds] : ''
  }
}
