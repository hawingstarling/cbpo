import isArray from 'lodash/isArray'
import isEqual from 'lodash/isEqual'
import cloneDeep from 'lodash/cloneDeep'

const cachedHeaders = []

const getAllHeadersCase = (headers) => {
  if (headers.length === 1) {
    return headers[0].map(header => [header])
  } else {
    let result = []
    let cases = getAllHeadersCase(headers.slice(1))
    for (let j = 0; j < headers[0].length; j++) {
      for (let i = 0; i < cases.length; i++) {
        if (isArray(cases[i])) {
          result.push([headers[0][j], ...cases[i]])
        } else {
          result.push([headers[0][j], cases[i]])
        }
      }
    }
    return result
  }
}

class HeaderColumnsMatching {
  static getHeaders(headers) {
    let cached = cachedHeaders.find(cache => isEqual(cache.headers, headers))
    if (!cached) {
      cached = {
        values: getAllHeadersCase(headers),
        headers
      }
      cachedHeaders.push(cached)
    }
    return cloneDeep(cached.values)
  }
}

export default HeaderColumnsMatching
