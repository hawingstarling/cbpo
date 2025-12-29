import moment from 'moment-timezone'

const defaultTimeZone = 'America/Los_Angeles'
export const CUSTOM_LABEL = 'Custom'

export const TODAY_OPTION = {
  id: 'today',
  text: 'Today',
  value: ["DATE_START_OF(TODAY(), 'day')", "DATE_END_OF(TODAY(), 'day')"]
}
export const YESTERDAY_OPTION = {
  id: 'yesterday',
  text: 'Yesterday',
  value: ["DATE_START_OF(YESTERDAY(), 'day')", "DATE_END_OF(YESTERDAY(), 'day')"]
}
export const LAST_WEEK_OPTION = {
  id: 'last-week',
  text: 'Last Week',
  value: ["DATE_START_OF(DATE_LAST(1,'week'), 'week')", "DATE_END_OF(DATE_LAST(1,'week'), 'week')"]
}
export const LAST_7_DAYS_OPTION = {
  id: 'last-7-days',
  text: 'Last 7 Days',
  value: ["DATE_START_OF(DATE_LAST(7,'day'), 'day')", "DATE_END_OF(TODAY(), 'day')"]
}
export const THIS_WEEK_OPTION = {
  id: 'this-week',
  text: 'This Week',
  value: ["DATE_START_OF(TODAY(), 'isoWeek')", "DATE_END_OF(TODAY(), 'isoWeek')"]
}
export const LAST_15_DAYS_OPTION = {
  id: 'last-15-days',
  text: 'Last 15 Days',
  value: ["DATE_START_OF(DATE_LAST(15,'day'), 'day')", "DATE_END_OF(TODAY(), 'day')"]
}
export const LAST_30_DAYS_OPTION = {
  id: 'last-30-days',
  text: 'Last 30 Days',
  value: ["DATE_START_OF(DATE_LAST(30,'day'), 'day')", "DATE_END_OF(TODAY(), 'day')"]
}
export const THIS_MONTH_OPTION = {
  id: 'this-month',
  text: 'This Month',
  value: [
    "DATE_START_OF(TODAY(), 'month')",
    "DATE_END_OF(TODAY(), 'month')"
  ]
}
export const LAST_MONTH_OPTION = {
  id: 'last-month',
  text: 'Last Month',
  value: [
    "DATE_START_OF(DATE_LAST(1,'month'), 'month')",
    "DATE_END_OF(DATE_LAST(1,'month'), 'month')"
  ]
}
export const THIS_YEAR_OPTION = {
  id: 'this-year',
  text: 'This Year',
  value: [
    "DATE_START_OF(TODAY(), 'year')",
    "DATE_END_OF(TODAY(), 'year')"
  ]
}
export const LAST_YEAR_OPTION = {
  id: 'last-year',
  text: 'Last Year',
  value: [
    "DATE_START_OF(DATE_LAST(1,'year'), 'year')",
    "DATE_END_OF(DATE_LAST(1,'year'), 'year')"
  ]
}
export const TSTYLE_DAILY = {
  id: 'tstyle_daily',
  text: 'Daily',
  type: 'TSTYLE_DAILY',
  value: [
    moment().tz(defaultTimeZone).startOf('day').format('MM/DD/YYYY'),
    moment().tz(defaultTimeZone).subtract(1, 'day').startOf('day').format('MM/DD/YYYY')
  ]
}
export const TSTYLE_30_DAYS = {
  id: 'tstyle_30_days',
  text: 'Last 30 Days',
  type: 'TSTYLE_30_DAYS',
  value: [
    `30 Days ${moment().tz(defaultTimeZone).year()}`, `30 Days ${moment().tz(defaultTimeZone).subtract(1, 'year').year()}`
  ]
}
export const TSTYLE_MTD = {
  id: 'tstyle_mtd',
  text: 'Month to Date',
  type: 'TSTYLE_MTD',
  value: [ moment().tz(defaultTimeZone).format('MMMM YYYY'), moment().tz(defaultTimeZone).subtract(1, 'month').format('MMMM YYYY') ]
}
export const TSTYLE_YTD = {
  id: 'tstyle_ytd',
  text: 'Year to Date',
  type: 'TSTYLE_YTD',
  value: [ `YTD ${moment().tz(defaultTimeZone).year()}`, `YTD ${moment().tz(defaultTimeZone).subtract(1, 'year').year()}` ]
}
export const ALL_OPTION = {
  id: 'all',
  text: 'All',
  value: []
}
export const CUSTOM_OPTION = {
  id: 'custom',
  text: CUSTOM_LABEL,
  value: [
    moment()
      .add(-30, 'day')
      .startOf('day').format('YYYY-MM-DD'),
    moment().endOf('day').format('YYYY-MM-DD')
  ]
}

export const DATE_QUERY_OPTIONS = [
  TODAY_OPTION,
  YESTERDAY_OPTION,
  THIS_WEEK_OPTION,
  LAST_WEEK_OPTION,
  THIS_MONTH_OPTION,
  LAST_MONTH_OPTION,
  LAST_30_DAYS_OPTION,
  THIS_YEAR_OPTION,
  LAST_YEAR_OPTION,
  ALL_OPTION,
  CUSTOM_OPTION
]

export const DATE_QUERY_REPORT_OPTIONS = [
  TODAY_OPTION,
  YESTERDAY_OPTION,
  LAST_WEEK_OPTION,
  LAST_15_DAYS_OPTION,
  LAST_30_DAYS_OPTION,
  THIS_MONTH_OPTION,
  LAST_MONTH_OPTION,
  CUSTOM_OPTION
]

export const DATE_QUERY_SALES_BY_ASIN_OPTIONS = [
  ALL_OPTION,
  LAST_7_DAYS_OPTION,
  LAST_30_DAYS_OPTION,
  CUSTOM_OPTION
]

export const DATE_QUERY_VIEW_COMPARISON_TAG_OPTIONS = [
  ALL_OPTION,
  TODAY_OPTION,
  YESTERDAY_OPTION,
  LAST_WEEK_OPTION,
  LAST_30_DAYS_OPTION,
  THIS_MONTH_OPTION,
  LAST_MONTH_OPTION,
  THIS_YEAR_OPTION,
  LAST_YEAR_OPTION,
  CUSTOM_OPTION
]
/**
+ * Date constants for Top Performing Styles widget
+ * Each constant has a different value format based on how it's used by the widget:
+ * All dates use Pacific Time (America/Los_Angeles) as the default time zone
+ * - Daily: Formatted dates for current and previous day
+ * - 30 Days: Year strings with prefix for current and previous year
+ * - MTD: Formatted month and year for current and previous month
+ * - YTD: Year numbers for current and previous year
+ */
export const DATE_QUERY_TOP_PERFORMING_STYLES_OPTIONS = [
  TSTYLE_DAILY,
  TSTYLE_MTD,
  TSTYLE_30_DAYS,
  TSTYLE_YTD
]
