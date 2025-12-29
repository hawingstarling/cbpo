<script>
import moment from 'moment-timezone'
import {
  DATASOURCES_MAPPING,
  DATASOURCES_OPTIONS,
  DATASOURCES_OPTIONS_MAPPING
} from '@/shared/constants/sync.constant'
import { filterColumnName } from '@/shared/filters'
import { numberFormat } from '@/shared/utils'
import placeholderURL from '@/assets/img/profile-placeholder.png'

export default {
  data() {
    return {
      placeholderURL: placeholderURL,
      DATASOURCES_MAPPING: DATASOURCES_MAPPING,
      DATASOURCES_OPTIONS: DATASOURCES_OPTIONS,
      DATASOURCES_OPTIONS_MAPPING: DATASOURCES_OPTIONS_MAPPING
    }
  },
  filters: {
    filterColumnName
  },
  methods: {
    getFullName(userInfo) {
      return `${userInfo.first_name} ${userInfo.last_name}`
    },
    getDateTime(time) {
      return this.$moment.duration(this.$moment().diff(time)).asHours() > 24
        ? this.$moment(time).format('MM/DD/YYYY hh:mm A')
        : this.$moment(time).from()
    },
    getAssetsByCommand(command, asset) {
      // { command: ['edit', 'delete', 'sync'], asset: ['icon', 'variant'] }
      if (command === 'edit') {
        switch (asset) {
          case 'icon':
            return 'pencil'
          case 'variant':
            return 'primary'
        }
      } else if (command === 'delete') {
        switch (asset) {
          case 'icon':
            return 'trash'
          case 'variant':
            return 'danger'
        }
      } else if (command === 'sync') {
        switch (asset) {
          case 'icon':
            return 'magic'
          case 'variant':
            return 'success'
        }
      } else if (command === 'shipping_cost_calculation') {
        switch (asset) {
          case 'icon':
            return 'cogs'
          case 'variant':
            return 'primary'
        }
      }
    },
    buildExpression(expression) {
      const isValidDate = date =>
        date.toString().match(
          // eslint-disable-next-line
          /(\d{4})-(\d{2})-(\d{2})T(\d{2})\:(\d{2})\:(\d{2})\.(\d{3,6})Z/g
        )
      const column = `<span class="expression__column">@${this.$options.filters.filterColumnName(
        expression.column
      )}</span>`
      const action = `<span class="expression__action"> ${
        expression.action
      } </span>`
      const expValue = isValidDate(expression.value)
        ? this.$moment(expression.value).format('MM/DD/YYYY hh:mm A')
        : expression.value
      const value = `<span class="expression__value">${expValue}</span>`
      return `<span class="expression">${column + action + value}</span>`
    },
    isPropertyExisted(query, property) {
      return query && query.hasOwnProperty(property)
    },
    getTimezoneTitle(timezone) {
      if (timezone) {
        const timezoneOffset =
          moment.tz.zone(timezone).utcOffset(moment.utc()) / -60
        return 'UTC' + this.convertNumberToTime(timezoneOffset)
      } else {
        return 'UTC'
      }
    },
    convertNumberToTime(number) {
      const convertTime = num =>
        moment.utc(moment.duration(num, 'h').asMilliseconds()).format('HH:mm')
      if (number > 0) {
        return '+' + convertTime(number)
      } else if (number < 0) {
        return '-' + convertTime(-number)
      }
      return ''
    },
    isProgressCompleted(progress) {
      return progress === 100
    },
    numberFormat(value, locale = 'en-US') {
      return numberFormat(value, locale)
    }
  }
}
</script>
