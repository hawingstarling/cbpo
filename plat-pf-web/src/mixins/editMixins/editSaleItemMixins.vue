<script>
import moment from 'moment-timezone'
import _ from 'lodash'
import { UNIQUE_KEY_DS } from '@/shared/constants/column.constant'
import { EDITABLE_DATA_FIELD } from '@/shared/constants'
import { BULK_PROGRESS } from '@/shared/messages'
import { filterColumnName } from '@/shared/filters'
import { checkFieldFormatMixins, numberFormat } from '@/shared/utils'
import { mapGetters } from 'vuex'

export default {
  props: {
    sdkID: {
      type: String
    },
    dataRenderUI: {
      type: Array,
      default: function() {
        return EDITABLE_DATA_FIELD
      }
    },
    currentChannel: {
      type: String
    }
  },
  mixins: [checkFieldFormatMixins],
  data() {
    return {
      clientID: '',
      originalInternalData: [],
      internalData: {},
      internalBulkData: [],

      BULK_PROGRESS: BULK_PROGRESS
    }
  },
  filters: {
    filterColumnName
  },
  computed: {
    ...mapGetters({
      sdkConfig: 'pf/analysis/sdkConfig'
    }),
    dataForApi() {
      return this.internalData.data
        ? this.prepareDataApi(this.internalData)
        : null
    },
    getIdsBulkSelection() {
      const bulkIDs = this.internalBulkData.reduce((acc, current) => {
        acc.push(current.data[UNIQUE_KEY_DS].base)
        return acc
      }, [])
      return bulkIDs
    },
    getArrayItemIDs() {
      return this.getIdsBulkSelection.reduce((acc, current, index) => {
        index === 0
          ? (acc = `sale_item_ids[]=${current}`)
          : (acc = acc + `&sale_item_ids[]=${current}`)
        return acc
      }, '')
    },
    isObject() {
      return data => _.isObject(data)
    },
    flattenedData() {
      return this.$props.dataRenderUI.reduce((acc, current, index) => {
        if (current.subGroup) {
          const subGroups = current.subGroup.map(item => item.data).flat()
          return [...acc, ...current.data, ...subGroups]
        } else {
          return [...acc, ...current.data]
        }
      }, [])
    },
    totalItems() {
      const bulkActions = this.sdkConfig.elements[0].config.bulkActions
      return bulkActions.filterMode
        ? bulkActions.total
        : this.internalBulkData.length
    },
    hasColumnData() {
      // This compute is just suitable for sdk data
      return (columnData, column) =>
        _.has(columnData, ['data', column, 'base'], false)
    }
  },
  methods: {
    handleCloseModal() {
      this.bulkDataState = {}
      this.$bvModal.hide(`${this.id}`)
    },
    getIndexProperty(property) {
      return this.columns.reduce((acc, currentValue, index) => {
        if (property === currentValue) acc = index
        return acc
      }, 0)
    },
    getColumnName(columnValue) {
      const column = this.columns.find(column => column === columnValue)
      return column || null
    },
    numberFormat(value, locale = 'en-US') {
      return numberFormat(value, locale)
    },
    prepareDataApi(data) {
      return this.flattenedData.reduce((acc, currentValue, index) => {
        const baseValueData = this.hasColumnData(data, currentValue.name) ? data.data[currentValue.name].base : null
        if (
          !this.isReadonly(currentValue.format) &&
          baseValueData !== null &&
          baseValueData !== undefined
        ) {
          (this.isCurrency(currentValue.format) ||
            this.isPercent(currentValue.format)) &&
          baseValueData === ''
            ? (acc[currentValue.id] = null)
            : (acc[currentValue.id] = baseValueData)
        }
        return acc
      }, {})
    },
    isBulkData(data) {
      const bulkKey = ['item_ids']
      return bulkKey.every(key => Object.keys(data).includes(key))
    },
    latestBulkDataForApi(type = 'delete') {
      // ['edit', 'delete', 'sync']
      let result = {}
      const isfilterMode = this.sdkConfig.elements[0].config.bulkActions
        .filterMode

      if (isfilterMode) {
        let query = {}
        const configSDK = this.sdkConfig.elements[0].config
        query.timezone = configSDK.timezone.utc || moment.tz.guess()
        query.filter = configSDK.filter
        result.query = query
      } else {
        if (type === 'sync' && this.internalData.data) {
          result.ids = [this.internalData.data[UNIQUE_KEY_DS].base]
        } else {
          result.ids = this.getIdsBulkSelection
        }
      }
      if (type === 'edit') {
        result.updates = Object.keys(this.bulkDataState).reduce(
          (acc, curKey) => {
            if (this.bulkDataState[curKey]) {
              acc.push({
                column: curKey,
                action: this.bulkActionsForApi[curKey],
                value: this.bulkDataForApi[curKey]
              })
            }
            return acc
          },
          []
        )
      }
      return result
    },
    buildPayloadCustomExport() {
      const bulkOperations = Object.keys(this.bulkDataState).reduce(
        (acc, curKey) => {
          if (this.bulkDataState[curKey]) {
            acc.push({
              column: curKey,
              action: this.bulkActionsForApi[curKey],
              value: this.bulkDataForApi[curKey]
            })
          }
          return acc
        },
        []
      )
      let columns = []
      this.sdkConfig.elements[0].config.columns.forEach(col => {
        if (col.visible) {
          columns.push({
            name: col.name,
            alias: col.displayName
          })
        }
      })
      const result = {
        name: this.exportName,
        ds_query: {
          timezone: this.sdkConfig.elements[0].config.timezone.utc,
          filter: _.get(this.sdkConfig, 'elements[0].config.filter')
        },
        columns: columns,
        bulk_operations: bulkOperations
      }
      return result
    },
    isAmazonMarketplace(marketplace) {
      return _.includes(marketplace, 'amazon')
    }
  },
  created() {
    this.clientID = this.$route.params.client_id
  },
  watch: {
    dataRow(newValue) {
      this.isUpdating = false
      if (this.isBulkData(newValue)) {
        this.internalData = {}
        this.internalBulkData = newValue.item_ids.slice()
      } else {
        this.internalBulkData = []
        this.internalData = _.cloneDeep(newValue)
        this.originalInternalData = _.cloneDeep(newValue)
      }
      if (!this.isAmazonMarketplace(this.currentChannel)) {
        this.dataRenderUI = this.dataRenderUI.map((item) => {
          if (item.group === 'sale') {
            item.data = _.filter(item.data, dataItem => dataItem.name !== 'is_prime')
            return item
          }
          return item
        })
      }
    }
  }
}
</script>
