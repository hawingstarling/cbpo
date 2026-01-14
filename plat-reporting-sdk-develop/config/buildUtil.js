const fs = require('fs')
const path = require('path')
const sass = require('node-sass')

const source = '../src/assets/css/themes'
const dist = '../dist'

const resolvePath = (...args) => {
  const pathFile = [__dirname, ...args]
  return path.join.apply(null, pathFile)
}

const getFiles = (source) => {
  return fs.readdirSync(resolvePath(source)).filter(file => {
    return !fs.statSync(resolvePath(source, file)).isDirectory()
  })
}

module.exports = () => {
  let themeDest = resolvePath(dist)

  // create dist folder if it's not exist
  if (!fs.existsSync(themeDest)) {
    fs.mkdirSync(themeDest)
  }

  // get all scss files
  let themeFiles = getFiles(source)

  // write content of each scss file
  themeFiles.forEach(theme => {
    let themePath = resolvePath(path.join(source, theme))
    let themeContents = fs.readFileSync(themePath, 'utf8')

    if (themeContents) {
      // read scss content
      const { css } = sass.renderSync({
        data: themeContents,
        outFile: themeDest,
        includePaths: [resolvePath(source)],
        outputStyle: 'compressed'
      })

      // write file
      fs.writeFileSync(path.join(themeDest, theme.replace('.scss', '.css')), css, 'utf8')
    }
  })
}
