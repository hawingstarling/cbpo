import numericFormatConfig from './numericFormatConfig'
import { cloneDeep } from 'lodash'
export default {
  segmentType: 'trend', // trend | custom
  // segments is used for custom type only
  value: {
    format: {
      type: 'numeric', // numeric - just numeric for now
      config: cloneDeep(numericFormatConfig)
    }
  },
  segments: [{ // default 3 arrows (up, none, down)
    conditions: {
      gt: 0
    },
    iconClass: 'fa fa-caret-up', // css class
    iconStyle: { color: 'green' }, // css styles
    labelClass: '', // css class
    labelStyle: {} // css styles
  },
  {
    conditions: {
      lt: 0
    },
    iconClass: 'fa fa-caret-down', // css class
    iconStyle: { color: 'red' }, // css styles
    labelClass: '', // css class
    labelStyle: {} // css styles
  },
  {
    conditions: {
      eq: 0
    },
    iconClass: 'fa fa-minus', // css class
    iconStyle: { color: 'grey' }, // css styles
    labelClass: '', // css class
    labelStyle: {} // css styles
  }]
}
