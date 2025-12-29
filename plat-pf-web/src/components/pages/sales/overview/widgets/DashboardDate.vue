<template>
    <b-card class="dashboard-date">
        <div class="w-full text-left underline">
          <span class="before-today">
            {{ todayFormat }} {{ utcFormat }}
          </span>
        </div>
    </b-card>
</template>

<script>
import moment from 'moment-timezone'
const timeZoneData = require('@/shared/timeZoneData.json')

export default {
  name: 'DashboardDate',
  data() {
    return {
      timezone: 'America/Los_Angeles'
    }
  },
  computed: {
    todayFormat() {
      return moment.tz(this.timezone).format('dddd | MMM D, YYYY')
    },
    utcFormat() {
      const result = timeZoneData.find(item => item.utc.includes(this.timezone))
      return result ? `- ${result.text_utc || result.text}` : null
    }
  }
}
</script>

<style scoped>
    .before-today {
        font-style: normal;
        font-weight: bold;
        font-size: 14px;
        line-height: 16px;
        letter-spacing: 0.005em;
        color: #999999;
    }
    .underline {
      border-bottom: 2px solid #1E3450;
      padding-bottom: 16px;
    }
</style>
