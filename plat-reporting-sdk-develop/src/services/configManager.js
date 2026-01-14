class ConfigManager {
  async get (configId) {
    return window[configId]
  }
}

export default new ConfigManager()
