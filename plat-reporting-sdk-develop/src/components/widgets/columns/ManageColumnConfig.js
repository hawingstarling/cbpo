import defaultsDeep from 'lodash/defaultsDeep'
export const defaultColumnConfig = {
  trigger: {
    label: 'Manage Columns' // the button label
  },
  modal: {
    title: 'Manage Columns',
    contentClass: '',
    modalClass: '',
    buttons: {
      reset: {
        visible: true,
        text: 'Reset'
      },
      apply: {
        visible: true,
        text: 'Apply'
      },
      cancel: {
        visible: true,
        text: 'Cancel'
      }
    }
  },
  mode: 'twin', // 'twin', 'single'
  hiddenColumns: [],
  managedColumns: [
    /**
     * Column Format
     *
     * column{Object} with name{string} and type{string}
     * displayName{string}
     * visible{boolean}
     * **/
  ]
}

export const makeColumnManagerDefaultConfig = (config) => {
  defaultsDeep(config, defaultColumnConfig)
}
