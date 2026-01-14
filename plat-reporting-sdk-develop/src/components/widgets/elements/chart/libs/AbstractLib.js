// import precond from 'precond'

export default class AbstractLib {
  themeStyle = {
    mainColor: '',
    accentColor: '',
    hoverItemColor: ''
  }
  /**
   * @typedef {Object} CallbackObject
   * @property {Function} drillDownCallback
   *
   * Abstract definition.
   *
   * @param el {element}
   * @param componentConfig {Object} Chart.vue component config.
   * @param data {Object} standard data object with rows and cols.
   * @param callbackObj {CallbackObject} Object which contains all callback methods
   */
  render (el, componentConfig, data, callbackObj) {
    // precond.checkState(null, 'Please override')
    console.log('Please override')
  }
}
