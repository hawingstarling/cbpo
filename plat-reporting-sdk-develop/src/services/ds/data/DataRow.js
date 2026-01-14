export default class DataRow {
  constructor (row, parentRow, parentMetaRow, level) {
    this.row = row
    this.parent = parentRow
    this.parentMeta = parentMetaRow
    this.level = level || 0
    this.expanded = false
    this.showDetail = false
  }
}
