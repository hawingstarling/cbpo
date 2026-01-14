const express = require('express')
const app = express()

app.use('/', express.static('dist'))

app.get('/', (req, res) => {
  res.sendFile('index.html')
})

const port = 5000
app.listen(port)
console.log('server started ' + port)
