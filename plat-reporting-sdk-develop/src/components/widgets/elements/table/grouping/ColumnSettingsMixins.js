import {OPTIONS} from './ColumnSettingsConfig'
export default {
  data () {
    return {
      OPTIONS: OPTIONS
    }
  },
  computed: {
    getGlobalControlOptions () {
      return (config, controlOptions) => {
        switch (controlOptions) {
          case OPTIONS.GROUPING:
            return config.grouping.enabled
          case OPTIONS.GLOBAL_GROUPING:
            return config.globalGrouping.enabled
          case OPTIONS.GLOBAL_GROUPING_VALUE:
            return config.globalGrouping.config.value
          case OPTIONS.AGGREGATION:
            return config.aggregation.enabled
          case OPTIONS.EDIT_COLUMN:
            return config.editColumn.enabled
          case OPTIONS.EDIT_COLUMN_LABEL:
            return config.editColumnLabel.enabled
          case OPTIONS.EDIT_COLUMN_FORMAT:
            return config.editColumnFormat.enabled
          case OPTIONS.EDIT_BIN:
            return config.editBin.enabled
          default:
            return false
        }
      }
    }
  }
}
