import DataManager from '@/services/ds/data/DataManager'
import $ from 'jquery'
import * as render from 'jsrender'
import dsFormatManager from '@/services/dataFormatManager'
import cloneDeep from 'lodash/cloneDeep'

const jsRender = render($)

export class HtmlReplacer {
  replacer = /(?:{{:)(.*?)(?:}})/g // default will use regex of jsRender
  templateReplacer = (value) => `{{:${value}}}` // default template string of jsRender
  dm = null

  constructor(replacer, templateReplacer) {
    if (replacer && templateReplacer) {
      this.replacer = replacer
      this.templateReplacer = templateReplacer
    }
    this.dm = new DataManager()
  }

  setDataSource({rows = [], cols = []}) {
    this.dm.setData(cols, rows)
    return this
  }

  // convert template from editor into template string of jsRender
  parse(columns, bins, template = '') {
    let mapper = template.split(this.replacer)
    let data = cloneDeep(this.dm.rows[0]) || []
    let strTemplate = mapper.map((str, i) => {
      // this will be column, map string to data_path which can be access by jsRender
      // format will be {{:data_path}}
      if ((i % 2)) {
        let columnName = str
        let binColumn = bins.find(bin => bin.column.name === columnName)
        let indexColumn = this.dm.columnNameToIndex[binColumn ? binColumn.alias : columnName]
        // if there is no column match with dataSource, return str
        if (indexColumn === undefined) return '#Error'
        // find column and it's format
        let column = columns.find(column => column.name === columnName)
        if (column && column.format) {
          let formatFactory = dsFormatManager.create(column.format, true)
          data[indexColumn] = formatFactory(data[indexColumn])
        }
        // build string with default template string of jsRender and let it handle other parts
        let strTemplate = binColumn ? `(data[${[indexColumn]}] === null ? data[${[indexColumn]}] : data[${[indexColumn]}].label)` : `(data[${[indexColumn]}] || 0)`
        return this.templateReplacer(strTemplate)
      }
      return str
    }).join('')
    return this.jsRenderParsing(strTemplate, data)
  }

  // jsRender handle replace data from template
  jsRenderParsing(template, data) {
    let dataTemplate = {data: data || []}
    let jTemplate = jsRender.templates(template)
    return jTemplate.render(dataTemplate)
  }
}
