import flattenDeep from 'lodash/flattenDeep'
import { DsCalculatedColumnGrammar } from 'plat-expr-sdk'

export const uniqueRules = {
  validate(value, args) {
    const columns = flattenDeep(args.map(arg => arg.columns))
    const columnIndex = columns.findIndex(col => col.name === value)
    return columnIndex === -1
  },
  message: 'Name is unique.'
}

export const validExpr = {
  validate(value, args) {
    const matched = DsCalculatedColumnGrammar.match(value)
    return !matched.failed()
  },
  message: 'Expression is invalid.'
}
