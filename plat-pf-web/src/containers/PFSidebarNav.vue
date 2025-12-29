<template>
  <SidebarNav :navItems="nav"></SidebarNav>
</template>

<script>
import SidebarNav from './SidebarNav'
import { mapGetters, mapActions } from 'vuex'
import _nav from '@/_nav'
import isEmpty from 'lodash/isEmpty'
import get from 'lodash/get'

export default {
  name: 'PFSidebar',
  components: {
    SidebarNav
  },
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters({
      pfPermissions: 'pf/getPermissions'
    }),
    nav () {
      // check permissions
      if (this.pfPermissions && this.pfPermissions.module_enabled) {
        if (!isEmpty(this.pfPermissions.permissions)) {
          const permissionsFromStore = get(this.pfPermissions, 'permissions', [])
          const activedPermissions = Object.keys(permissionsFromStore).filter(p => permissionsFromStore[p])
          return _nav.items.filter(nav => {
            return nav && (!nav.permissions || (nav.permissions && nav.permissions.find(permission => activedPermissions.includes(permission))))
          })
        } else {
          return _nav.items.filter(nav => nav && !nav.permissions)
        }
      }
      return _nav.items.filter(nav => nav && !nav.permissions)
    }
  },
  methods: {
    ...mapActions({
      fetchPermissions: 'pf/fetchPermissions'
    })
  },
  async mounted () {
    try {
      await this.fetchPermissions()
    } catch (e) {
      console.log(e)
    }
  }
}
</script>

<style lang="scss" scoped>
  .sidebar {
    /deep/ .router-link-active {
      color: #fff;
      background: #3a4248;
      .nav-icon {
        color: #20a8d8;
      }
    }
  }
</style>
