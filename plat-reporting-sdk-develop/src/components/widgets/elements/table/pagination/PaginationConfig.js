import PaginationButtons from './PaginationButtons'
import PaginationNumbers from './PaginationNumbers'
import PaginationInput from './PaginationInput'
import _ from 'lodash'

export const DEFAULT_PAGINATION_CONFIG = {
  limit: 50, // item per page
  current: 1, // default 1
  total: null, // will be override by the logic
  type: 'auto',
  // auto auto choice depends on total (now default to buttons)
  // lazy TBD
  // numbers <first> <prev> ... <current-1> <current-2> <current> <current+1> <current+2> ... <next> <last>
  // input <first> <prev> Page <input> of ${total} </next> <last>
  // buttons <first> <prev> Page <current> of ${total} <next> <last>
  buttons: { // for type = numbers, buttons, input
    /**
     * visibility: show button
     * label: name of button
     * style: style css for button
     * **/
    first: {
      visibility: true,
      label: 'First',
      style: {}
    },
    last: {
      visibility: true,
      label: 'Last',
      style: {}
    },
    prev: {
      visibility: true,
      label: 'Previous',
      style: {}
    },
    next: {
      visibility: true,
      label: 'Next',
      style: {}
    }
  },
  numbers: { // for type = numbers only
    beforeCurrent: 2,
    afterCurrent: 2
  },
  default: 'auto'
}

const MAP_PAGINATION_COMPONENTS = {
  auto: PaginationNumbers,
  numbers: PaginationNumbers,
  buttons: PaginationButtons,
  input: PaginationInput
}

export const getSuitablePagination = paginationType => {
  return MAP_PAGINATION_COMPONENTS[`${paginationType.type}`] || MAP_PAGINATION_COMPONENTS[`${DEFAULT_PAGINATION_CONFIG.default}`]
}

export const makeDefaultPaginationConfig = (paginationConfig) => {
  _.defaultsDeep(paginationConfig, DEFAULT_PAGINATION_CONFIG)
}
