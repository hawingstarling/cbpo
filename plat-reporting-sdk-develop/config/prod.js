const CopyWebpackPlugin = require('copy-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const path = require('path')

module.exports = [
  new HtmlWebpackPlugin({
    filename: 'live-docs/index.html',
    template: 'live-docs/index.html',
    inject: true
  }),
  // copy custom static assets
  new CopyWebpackPlugin([
    {
      from: path.resolve(__dirname, '../live-docs'),
      to: 'live-docs',
      ignore: ['.*']
    }
  ])
]
