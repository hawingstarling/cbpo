import _wg from '@/services/wgManager'
import _ds from '@/services/dsManager'
import _df from '@/services/dataFormatManager'
import _dtQuery from '@/services/dataQueryManager'
import _channel from '@/services/channelManager'
import Vue from 'vue'

const _cbpo = {
  wgManager () {
    return _wg
  },
  dsManager () {
    return _ds
  },
  dataFormatManager () {
    return _df
  },
  dataQueryManager() {
    return _dtQuery
  },
  channelManager() {
    return _channel
  },
  $bus: new Vue()
}

window.CBPO = Object.assign(window.CBPO || {}, _cbpo)
export default _cbpo
