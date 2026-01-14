const configDev = require('./config/dev')
const configPro = require('./config/prod')
const generateThemes = require('./config/buildUtil')

function CallbackPlugin(cb) {
  this.apply = function(compiler) {
    if (compiler.hooks && compiler.hooks.done) {
      compiler.hooks.done.tap('webpack-arbitrary-code', cb)
    }
  }
}

module.exports = {
  css: {
    loaderOptions: {
      sass: {
        data: `
          @import "@/assets/css/core/variables.scss";
        `
      }
    }
  },
  filenameHashing: false,
  runtimeCompiler: true,
  productionSourceMap: false,
  configureWebpack: config => {
    config.plugins = [
      new CallbackPlugin(generateThemes),
      ...config.plugins
    ]
    if (!process.env.CUSTOM_ENV) {
      const configDev = require('./config/dev')
      config.plugins = [...config.plugins, ...configDev]
    }
  },
  chainWebpack: config => {
    config.module
      .rule('images')
      .use('url-loader')
      .loader('url-loader')
      .tap(options => {
        options.limit = undefined
        return options
      })
  }
}
