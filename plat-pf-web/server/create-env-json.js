const fs = require('fs')

const variable = {
  ...process.env
}

fs.writeFileSync('env.json', JSON.stringify(variable))
