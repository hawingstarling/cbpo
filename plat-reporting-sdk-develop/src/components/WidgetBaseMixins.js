/**
 * Implement if your callbacks is BEFORE child components callback.
 * @see https://alligator.io/vuejs/composing-components/
 */
import _ from 'lodash'
import { generateIdIfNotExist } from '@/utils/configUtil'
import { makeWidgetBaseDefaultConfig } from './WidgetBaseConfig'
import configManager from '@/services/configManager'
import axios from 'axios'

export default {
  props: {
    configObj: {
      type: Object,
      default: () => {
        return {}
      }
    },
    outsideConfig: {
      type: Object,
      default: () => {
        return {}
      }
    }
  },
  data () {
    return {
      cancelToken: null,
      configReady: false,
      config: this.configObj
    }
  },
  watch: {
    configObj (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.config = this.configObj
        // Make an id.
        generateIdIfNotExist(this.config)
      }
    },
    config(val) {
      this.$emit('update:configObj', val)
    }
  },
  methods: {
    createCancelToken() {
      this.cancelToken = axios.CancelToken.source()
    },
    widgetInit () {
      console.log('WidgetBaseMixins::widgetInit')
    },
    widgetConfig (config) {
      makeWidgetBaseDefaultConfig(config)
    },
    widgetBaseFilter (filterObj) {
      console.error('WidgetBaseMixins::widgetBaseFilter', filterObj)
    },
    widgetResetCurrentPage() {
      console.error('WidgetBaseMixins::widgetResetCurrentPage')
    },
    widgetExport () {
      console.error('WidgetBaseMixins::widgetExport')
    },
    /**
     * Get config data to save to backend.
     */
    getAndCleanRuntimeConfig () {
      console.error('WidgetBaseMixins::getAndCleanRuntimeConfig')
      return this.config
    },
    /**
     * Calculate height of element by DOM
     * */
    calculateElementHeight() {
      console.error('WidgetBaseMixins::calculatedElementHeight')
    },
    widgetMappingColumns(columns) {
      let columnConfigs = _.get(this.config, 'columns', [])
      return columns.map(column => {
        let columnConfig = columnConfigs.find(col => col.name === column.name)
        if (columnConfig) {
          column.displayName = columnConfig.label || columnConfig.displayName || _.startCase(column.name)
        } else {
          column.displayName = _.startCase(column.name)
        }
        return column
      })
    },
    async fetchColumnsAndSaveToService(channelId) {
      try {
        let columns = await window.CBPO.dsManager()
          .getDataSource(this.config.dataSource)
          .columns()
        columns = this.widgetMappingColumns(columns)
        window.CBPO.channelManager().getChannel(channelId).getColumnSvc().setColumns(columns)
      } catch (e) {
        console.error(e)
      }
    }
  },
  created () {
    console.log('WidgetBaseMixins::created')
    // this.widgetConfig(this.config)
    this.createCancelToken()
  },
  beforeMount () {
    console.log('WidgetBaseMixins::mounted')

    const resolveConfig = () => {
      // TODO more way of configuration management

      // Make an id.
      generateIdIfNotExist(this.config)

      // widget init default
      this.widgetConfig(this.config)
      this.widgetInit()
      this.configReady = true
    }

    // try to load config from config-ref that the name of a variable at window context
    let configRef = this.$attrs['config-ref']
    if (!_.isEmpty(configRef)) {
      configManager.get(configRef).then(d => {
        this.config = d
        if (_.get(this.config, 'widgetConfig.id', '')) {
          this.config.widgetConfig.editMode = true
        }
        resolveConfig()
      })
    } else if (_.isEmpty(this.outsideConfig)) {
      resolveConfig()
    }
  },
  mounted() {
    if (!_.isEmpty(this.outsideConfig)) {
      this.config = this.outsideConfig
      if (_.get(this.config, 'widgetConfig.id', '')) {
        this.config.widgetConfig.editMode = true
      }
      // resolve config
      // TODO more way of configuration management

      // Make an id.
      generateIdIfNotExist(this.config)

      // widget init default
      this.widgetConfig(this.config)
      this.widgetInit()
      this.configReady = true
    }
  }
}
