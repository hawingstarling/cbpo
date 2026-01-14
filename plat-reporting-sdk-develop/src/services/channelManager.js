import { GlobalService } from '@/services/globalService'

class ChannelManager {
  instanceObj = {}

  getChannel(id = null) {
    if (!this.instanceObj[id]) {
      this.instanceObj[id] = new GlobalService()
    }
    return this.instanceObj[id]
  }
}

export default new ChannelManager()
