import precond from 'precond'

export const checkDsColumn = (column) => {
  precond.checkIsObject(column, `Column needs to be object {name: 'columnname', type: 'column data type'}`)
  precond.checkState(column.name, `column.name is required`)
  precond.checkState(column.type, `column.type is required`)
}

export const checkFeColumn = (column) => {
  precond.checkIsString(column, `Column needs to be a string`)
}
