import Vue from 'vue'

/**
 * @typedef State
 * @type Object
 * @property: {Array} controls - controls of global filter
 * @property: {Object} filter - global filter object
 * @property: {Boolean} isGlobalFilterReady - state of global filter
 * **/
export class GlobalFilterService {
  /** @type {State} **/
  state = null

  constructor() {
    this.state = Vue.observable({
      controls: [],
      // this filter is merged by all filters from Global Filter
      filter: {},
      // undefined mean there is no global filter in dashboard
      // true mean all global filters is ready
      // false mean all global filters is fetching data
      isGlobalFilterReady: undefined
    })
  }

  getGlobalFilterReady() {
    return this.state.isGlobalFilterReady
  }

  setGlobalFilterReady(status) {
    this.state.isGlobalFilterReady = status
  }

  getGlobalFilter() {
    return this.state.filter
  }

  setGlobalFilter(filter) {
    this.state.filter = filter
  }

  setControls(controls = []) {
    this.state.controls = controls
  }

  getControls() {
    return this.state.controls
  }
}

export class GlobalColumnService {
  state = null
  constructor () {
    this.state = Vue.observable({
      columns: []
    })
  }

  getColumns() {
    return this.state.columns
  }

  setColumns(columns) {
    Vue.set(this.state, 'columns', columns)
  }

  setColumn(column = null) {
    if (!column) return
    const columnIndex = this.state.columns.findIndex(col => col.name === column.name)
    if (columnIndex !== -1) {
      Vue.set(this.state.columns, columnIndex, {...column})
    } else {
      this.state.columns.push(column)
    }
    return this.state.columns
  }
}

export class GlobalTimezoneService {
  state = null
  constructor () {
    this.state = Vue.observable({
      timezone: ''
    })
  }

  getTimezone() {
    return this.state.timezone
  }

  setTimezone(timezone) {
    this.state.timezone = timezone
  }
}
export class GlobalThemeService {
  state = null
  constructor () {
    this.state = Vue.observable({
      currentTheme: ''
    })
  }

  getCurrentTheme() {
    return this.state.currentTheme
  }

  setCurrentTheme(theme) {
    this.state.currentTheme = theme
  }
}

export class GlobalService {
  state = null
  constructor () {
    this.createState()
  }

  createState() {
    this.state = {
      filterSvc: new GlobalFilterService(),
      columnSvc: new GlobalColumnService(),
      timezoneSvc: new GlobalTimezoneService(),
      themeSvc: new GlobalThemeService()
    }
  }

  reset() {
    console.log('reset CBPO')
    this.createState()
  }

  getFilterSvc () {
    return this.state.filterSvc
  }

  getColumnSvc () {
    return this.state.columnSvc
  }

  getTimezoneSvc () {
    return this.state.timezoneSvc
  }

  getThemeSvc() {
    return this.state.themeSvc
  }
}
