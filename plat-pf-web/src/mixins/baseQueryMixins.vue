<script>
import _ from 'lodash'
import { mapGetters } from 'vuex'
import { DEFAULT_CHANNEL } from '@/shared/constants'

export default {
  data() {
    return {
      currentChannel: DEFAULT_CHANNEL,
      currentDateQuery: [
        "DATE_START_OF(DATE_LAST(30,'day'), 'day')",
        "DATE_END_OF(TODAY(), 'day')"
      ],
      currentCommonFilter: ''
    }
  },
  computed: {
    ...mapGetters({
      channelList: 'pf/analysis/channelList'
    }),
    defaultChannel() {
      return this.channelOptions.length && this.hasChannel(this.channelOptions)
        ? DEFAULT_CHANNEL
        : this.channelOptions[0].value
    },
    channelOptions() {
      let channelList = []
      if (this.channelList && this.channelList.results) {
        channelList = this.channelList.results.reduce((acc, item) => {
          if (item.use_in_global_filter) {
            acc.push({ text: item.label, value: item.name })
          }
          return acc
        }, [])
      }
      return channelList
    }
  },
  methods: {
    setBaseQueryFilter() {
      let baseQuery = {
        config: {
          query: {
            type: 'AND',
            conditions: []
          }
        }
      }
      if (
        Array.isArray(this.currentDateQuery) &&
        this.currentDateQuery.length &&
        !this.currentDateQuery.every(_.isNull) // case: null absolute date
      ) {
        baseQuery.config.query.conditions.push(
          {
            column: 'sale_date',
            operator: '$gte',
            value: this.currentDateQuery[0]
          },
          {
            column: 'sale_date',
            operator: '$lte',
            value: this.currentDateQuery[1]
          }
        )
      }
      if (this.currentChannel) {
        baseQuery.config.query.conditions.push({
          column: 'channel_name',
          operator: '$eq',
          value: this.currentChannel
        })
      }
      if (this.currentCommonFilter) {
        baseQuery.config.query.conditions.push({
          type: 'OR',
          conditions: [
            {
              column: 'channel_id',
              operator: 'contains',
              value: this.currentCommonFilter
            },
            {
              column: 'asin',
              operator: 'contains',
              value: this.currentCommonFilter
            },
            {
              column: 'sku',
              operator: 'contains',
              value: this.currentCommonFilter
            },
            {
              column: 'brand',
              operator: 'contains',
              value: this.currentCommonFilter
            },
            {
              column: 'brand_sku',
              operator: 'contains',
              value: this.currentCommonFilter
            }
          ]
        })
      }
      if (!baseQuery.config.query.conditions.length) {
        baseQuery.config.query = {}
      }
      return baseQuery
    },
    resetCurrentDate() {
      this.currentDateQuery = [
        "DATE_START_OF(DATE_LAST(30,'day'), 'day')",
        "DATE_END_OF(TODAY(), 'day')"
      ]
    },
    resetChannel() {
      this.currentChannel = this.defaultChannel
    },
    resetCommonFilter() {
      this.currentCommonFilter = ''
    },
    resetBaseQuery() {
      this.resetCurrentDate()
      this.resetChannel()
      this.resetCommonFilter()
    },
    selectBaseQueryFilter(filter) {
      const baseCondtion = _.get(filter, 'base.config.query.conditions', [])
      const dateValueArray = baseCondtion.length
        ? baseCondtion.reduce((result, item) => {
          if (item.column === 'sale_date') {
            result.push(item.value)
          }
          return result
        }, [])
        : []
      const isAbsoluteDate = this.checkAbsoluteDate(dateValueArray)
      if (isAbsoluteDate) {
        this.currentDateQuery = [dateValueArray[0], dateValueArray[1]]
      } else {
        this.currentDateQuery = dateValueArray
      }
      // Channel
      let channelValue = ''
      if (baseCondtion.length) {
        const channelIndex = baseCondtion.findIndex(
          item => item.column === 'channel_name'
        )
        channelValue =
          channelIndex !== -1 ? baseCondtion[channelIndex].value : ''
      }
      this.currentChannel =
        channelValue && this.hasChannel(this.channelOptions, channelValue)
          ? channelValue
          : this.defaultChannel
      // Common Filter
      if (baseCondtion.length) {
        const commonFilterIndex = baseCondtion.findIndex(item =>
          item.hasOwnProperty('conditions')
        )
        this.currentCommonFilter =
          commonFilterIndex !== -1 &&
          baseCondtion[commonFilterIndex].conditions.length
            ? baseCondtion[commonFilterIndex].conditions[0].value
            : ''
      }
    },
    checkAbsoluteDate(data) {
      return (
        Array.isArray(data) &&
        data.length === 2 &&
        (data.every(item => this.$moment(item).isValid()) ||
          data.every(_.isNull))
      )
    },
    hasChannel(options, channel = DEFAULT_CHANNEL) {
      const defaultChannel = options.findIndex(item => item.value === channel)
      return defaultChannel !== -1
    }
  },
  watch: {
    channelOptions(newValue) {
      if (newValue.length && !this.hasChannel(newValue)) {
        this.currentChannel = newValue[0].value
      }
    }
  }
}
</script>
