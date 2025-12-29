<template>
  <b-col md="12" lg="12">
    <b-nav class="tab-header nav-tabs">
      <b-nav-item :to="{ name: 'PFStep1Import', params: { client_id: getClientID, module: 'SaleItem' }}" class="btn" active-class="active-tab"><i class="icon icon-cloud-upload"></i> Import</b-nav-item>
      <b-nav-item :to="{ name: 'PFImportHistory'}" :class="'btn'" active-class="active-tab"><i class="fa fa-clock-o"></i> Import History</b-nav-item>
      <b-nav-item :to="{ name: 'PFActivities'}" :class="'btn'" active-class="active-tab"><i class="icon icon-clock"></i> Activities</b-nav-item>
      <b-nav-item :to="{ name: 'PFBulkProgress'}" :class="'btn'" active-class="active-tab"><i class="fa fa-tasks"></i> Bulk Process Tasks</b-nav-item>
      <b-nav-item :to="{ name: 'PFRepricing'}" :class="'btn'" active-class="active-tab"><i class="fa fa-users"></i> Repricing</b-nav-item>
      <b-nav-item :to="{ name: 'PFTools'}" :class="'btn'" active-class="active-tab"><i class="fa fa-wrench"></i> Tools</b-nav-item>
    </b-nav>
    <router-view class="tab-body"></router-view>
  </b-col>
</template>

<script>

import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'

export default {
  name: 'PFUserAdministration',
  data() {
    return {
      client_id: this.$route.params.client_id
    }
  },
  mixins: [ spapiReconnectAlertMixin ],
  computed: {
    getClientID() {
      return this.$route.params.client_id
    }
  },
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
