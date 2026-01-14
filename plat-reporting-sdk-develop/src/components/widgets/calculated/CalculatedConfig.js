import defaultsDeep from 'lodash/defaultsDeep'

export const defaultCalculatedColumnConfig = {
  trigger: {
    label: 'Calculated Column'
  },
  modal: {
    title: 'Add a New Calculated Column'
  },
  columns: [
    /**
     * Column Format
     *
     * column{Object} with name{string} and type{string}
     * displayName{string}
     * expr{string}
     * visible{boolean}
     * **/
  ],
  enabled: true
}

export const makeCalculatedColumnDefaultConfig = (config) => {
  defaultsDeep(config, defaultCalculatedColumnConfig)
}
