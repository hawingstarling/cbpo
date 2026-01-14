import numericFormatConfig from './numericFormatConfig'
import { cloneDeep } from 'lodash'
export default {
  maximum: 5, // maximum 5 stars (above $maxium will be max),
  value: {
    display: 'none', // left, right, none, default none
    format: {
      type: 'numeric', // numeric - just numeric for now
      config: cloneDeep(numericFormatConfig)
    }
  },
  style: {
    color: 'orange',
    half: true
  }
}
