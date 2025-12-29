<template>
  <b-col md="12" lg="12">
    <b-nav class="tab-header nav-tabs">
      <b-nav-item :to="{ name: 'PFBrands'}" class="btn" active-class="active-tab"><i class="icon icon-flag"></i> Brand Settings</b-nav-item>
      <b-nav-item :to="{ name: 'PFItems'}" :class="'btn'" active-class="active-tab"><i class="icon icon-notebook"></i> Items</b-nav-item>
      <b-nav-item v-if="hasPermission(permissions.topASINs.view)" :to="{ name: 'PFTopASINs'}" :class="'btn'" active-class="active-tab"><i class="icon icon-star"></i> Top ASINs</b-nav-item>
    </b-nav>
    <router-view class="tab-body"></router-view>
  </b-col>
</template>

<script>

import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import { convertedPermissions as permissions } from '@/shared/utils'

export default {
  name: 'PFBrandManagement',
  data() {
    return {
      permissions
    }
  },
  mixins: [ spapiReconnectAlertMixin, PermissionsMixin ],
  created() {
  }
}
</script>

<style lang="scss" scoped>
.nav.tab-header.nav-tabs {
  li:first-child {
    border-left-width: 0 !important;
  }
}
</style>
