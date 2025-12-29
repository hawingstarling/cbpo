import Vue from 'vue'
import {
  ValidationObserver,
  ValidationProvider,
  extend,
  localize
} from 'vee-validate'
import * as rules from 'vee-validate/dist/rules'

Vue.component('ValidationProvider', ValidationProvider)
Vue.component('ValidationObserver', ValidationObserver)
// Install rules
Object.keys(rules).forEach((rule) => {
  extend(rule, {
    ...rules[rule] // copies rule configuration
  })
})
extend('upc', {
  validate: value => {
    let upcRegex = /^[0-9]{12,13}$/
    return upcRegex.test(value)
  },
  message: '{_field_} must contain 12-13 digits.'
})
extend('currency', {
  validate: value => {
    let currencyRegex = /^[-]{0,1}\d{1,4}([.]{1}\d{1,2}){0,1}$/gm
    return currencyRegex.test(value)
  },
  message: '{_field_} must have a maximum of 4 digits before the decimal point and 2 digits after.'
})
extend('positive', {
  validate: value => {
    return value >= 0
  },
  message: '{_field_} must be a positive value.'
})
extend('beforeDate', {
  params: ['target'],
  validate(value, { target }) {
    return !target ? true : value <= target
  },
  message: '{_field_} must be before {target}'
})
localize({
  en: {
    messages: {
      required: '{_field_} is required.',
      length: (field, params) => `${field} must be ${params.length} characters.`,
      max: (field, params) => `${field} only allows ${params.length} characters maximum.`,
      is_not: () => `Invalid math operation.`,
      between: (field, params) => `${field} must between ${params.min} and ${params.max}`
    }
  }
})
