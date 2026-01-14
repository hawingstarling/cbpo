import _ from 'lodash'
import dataFormatManager from '@/services/dataFormatManager'

const formatAndBind = (el, binding) => {
  if (!_.isObject(binding.value)) {
    return console.error('Format directive requires binding data as { data: ..., format: ... }')
  }
  let { data, dataType, aggr, aggrFormats, bin, format } = binding.value
  if (bin) {
    el.innerHTML = dataFormatManager.formatBin(data, format, true)
  } else if (!aggr) {
    el.innerHTML = dataFormatManager.format(data, format, true)
  } else {
    el.innerHTML = dataFormatManager.formatAggr(data, dataType, format, aggr, aggrFormats, true)
  }
}

export default {
  bind (el, that) {
    return formatAndBind(el, that)
  },
  update (el, that) {
    if (_.isEqual(that.value, that.oldValue)) {
      return // no need re-rendering when no change
    }
    return formatAndBind(el, that)
  },
  unbind (el, that) {
    // no need doing any thing for now
  }
}
