<script>
import _nav from '@/_nav'
import get from 'lodash/get'
import store from '@/store/store'

const hasPermissionFn = (permissions, permission = '') => {
  const activedPermissions = Object.keys(permissions).filter(p => permissions[p])
  return activedPermissions.includes(permission)
}

const checkPermissions = (permissionsMeta) => {
  if (!permissionsMeta || !permissionsMeta.length) return true
  const permissionsFromStore = store.getters['pf/getPermissions']
  const permissions = get(permissionsFromStore, 'permissions', [])
  const canAccess = permissionsMeta.find(per => hasPermissionFn(permissions, per))
  return canAccess
}

export default {
  methods: {
    getNamePage: function () {
      return this.$route.meta.label
    },
    getIconPage: function () {
      return _nav.items.find(item => item.name === this.$route.meta.label).icon
    }
  },
  created () {},
  computed: {
    pfPermissions () {
      return this.$store.getters['pf/getPermissions']
    },
    hasPermission () {
      return (permission = '') => {
        const permissions = get(this.pfPermissions, 'permissions', [])
        return hasPermissionFn(permissions, permission)
      }
    }
  },
  async beforeRouteEnter (to, from, next) {
    if (!get(to, 'meta.reloadPermissions', false)) return next()
    await store.dispatch('pf/fetchPermissions', {clientId: get(to, 'params.client_id', '')})
    const permissionsMeta = get(to, 'meta.permissions', [])
    return checkPermissions(permissionsMeta)
      ? next()
      : next({name: 'PSNoAccess'})
  },
  async beforeRouteUpdate (to, from, next) {
    if (!get(to, 'meta.reloadPermissions', false)) return next()
    await store.dispatch('pf/fetchPermissions', {clientId: get(to, 'params.client_id', '')})
    const permissionsMeta = get(to, 'meta.permissions', [])
    return checkPermissions(permissionsMeta)
      ? next()
      : next({name: 'PSNoAccess'})
  }
}
</script>
