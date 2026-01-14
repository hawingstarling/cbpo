export default {
  format: 'L LT', // any moment format
  date: {
    format: 'L' // used when only date
  },
  time: {
    format: 'LT' // used when only time
  },
  options: { // used when time is rounded
    year: 'YYYY',
    quarter: 'YYYY [Q]Q',
    month: 'YYYY MMM',
    week: 'YYYY [w]w',
    day: 'YYYY-MM-DD',
    hour: 'YYYY-MM-DD kk',
    minute: 'YYYY-MM-DD kk:mm',
    second: 'YYYY-MM-DD kk:mm:ss'
  }
}
