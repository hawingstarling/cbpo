import _nav from '@/_nav'

export function getCurrentClientId () {
  return _nav.clientId || ''
}

export default {
  getCurrentClientId
}
