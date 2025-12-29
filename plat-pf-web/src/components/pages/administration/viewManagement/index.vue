<template>
  <b-col md="12" lg="12">
    <b-nav  class="tab-header nav-tabs">
      <b-nav-item :to="{ name: 'PFViewList'}" class="btn" active-class="active-tab"><i class="icon icon-screen-desktop"></i> Views</b-nav-item>
      <b-nav-item :to="{ name: 'PFCustomReports'}" :class="'btn'" active-class="active-tab"><i class="icon icon-flag"></i> Custom Reports</b-nav-item>
    </b-nav>
    <router-view class="tab-body"></router-view>
  </b-col>
</template>

<script>

export default {
  name: 'PFViewManagement',
  data() {
    return {
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
