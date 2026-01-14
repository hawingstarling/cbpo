import noFormat from './noFormat'
import _ from 'lodash'
/**
 * Create named format function.
 */
export default name => {
  if (_.isFunction(window[name])) {
    return window[name]
  } else {
    console.error('window[' + name + '] must be a function')
    return noFormat
  }
}
