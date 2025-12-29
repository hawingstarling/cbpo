<template>
    <div class="app">
    <AppHeader fixed>
      <SidebarToggler class="d-lg-none" display="md" mobile />
      <b-link class="navbar-brand" to="#">
        <img class="navbar-brand-full" src="./../assets/img/logo.png" width="89" height="25" alt="CoreUI Logo">
        <img class="navbar-brand-minimized" src="./../assets/img/logo.png" width="30" height="30" alt="CoreUI Logo">
        <p class="brand-name">PRECISE</p>
      </b-link>
      <SidebarToggler class="d-md-down-none" display="lg" />
      <b-navbar-nav class="ml-auto">
        <DefaultHeaderDropdownAccnt/>
      </b-navbar-nav>
    </AppHeader>
    <div class="app-body">
      <AppSidebar fixed>
        <SidebarHeader/>
        <SidebarForm/>
        <PFSidebarNav :navItems="nav"></PFSidebarNav>
        <SidebarFooter/>
        <SidebarMinimizer/>
      </AppSidebar>
      <main class="main" :name="name">
        <!-- <b-breadcrumb :items="list"></b-breadcrumb> -->
        <div class="container-fluid">
          <b-alert
            v-if="alert"
            :variant="alert.type"
            class="mb-2"
            show
            dismissible
            @dismissed="alert = null"
          >
            <span v-html="alert.message"></span>
          </b-alert>
          <router-view></router-view>
        </div>
      </main>
      <AppAside fixed>
        <!--aside-->
        <DefaultAside/>
      </AppAside>
    </div>
    <TheFooter>
      <!--footer-->
      <div class="footer-content d-flex justify-content-end align-items-center vw-100">
        <a href="#">Channel Precision</a>
        <span class="ml-1">2022</span>
      </div>
    </TheFooter>
  </div>
</template>
<script>
import mtNav from '@/_nav'
import { Header as AppHeader, SidebarToggler, Sidebar as AppSidebar, SidebarFooter, SidebarForm, SidebarHeader, SidebarMinimizer, Aside as AppAside, Footer as TheFooter } from '@coreui/vue'
import DefaultAside from './DefaultAside.vue'
import DefaultHeaderDropdownAccnt from './DefaultHeaderDropdownAccnt.vue'
import PFSidebarNav from './PFSidebarNav.vue'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'
import { mapGetters } from 'vuex'
// import _ from 'lodash'

export default {
  name: 'DefaultContainer',
  mixins: [spapiReconnectAlertMixin],
  components: {
    // AsideToggler,
    AppHeader,
    AppSidebar,
    AppAside,
    TheFooter,
    DefaultAside,
    DefaultHeaderDropdownAccnt,
    SidebarForm,
    SidebarFooter,
    SidebarToggler,
    SidebarHeader,
    PFSidebarNav,
    SidebarMinimizer
  },
  data () {
    return {
      nav: mtNav.items,
      customDashboards: [],
      alert: null
    }
  },
  computed: {
    ...mapGetters({settingOption: `pf/settings/settingOption`}),
    name () {
      return this.$route.name
    },
    list () {
      const end = this.$route.matched.length - 1
      let data = this.$route.matched.reduce((newRoutes, route, key) => {
        if (route.meta.label) {
          if (route.meta.label === 'Home') {
            const homeRoute = {
              text: route.meta.label || '',
              to: this.currentClient && this.currentClient.id ? { name: 'ps-dashboard', params: {client_id: this.currentClient.id} }
                : { name: 'ps-dashboard' }
            }
            newRoutes.push(homeRoute)
            return newRoutes
          }
          let item = {}
          if (route.meta.breadcrumbs && route.meta.breadcrumbs.length) {
            route.meta.breadcrumbs.forEach((bc) => {
              if (bc.to && bc.to.params && (bc.to.params.orgId || bc.to.params.orgId === '')) {
                bc.to.params.orgId = this.orgParam || ''
              }
              if (bc.to && bc.to.params && bc.to.params.id) {
                bc.to.params.id = this.currentClient.id || ''
              }
              if (bc.to && bc.params && bc.params.name === 'name_ds') {
                bc.text = this.getOneDataSource.name || this.$route.params.name
              }
              if (bc.to && bc.params && bc.params.name === 'name_data_feed') {
                bc.text = this.getOneDataFeed.name || this.$route.params.name
              }
            })
            newRoutes = newRoutes.concat(route.meta.breadcrumbs)
          }
          if (key === end) {
            item = {
              text: route.meta.label || '',
              active: true
            }
          } else {
            item = {
              text: route.meta.label || '',
              to: { name: route.name }
            }
          }
          newRoutes.push(item)
        }
        return newRoutes
      }, [])
      return data
    }
  },
  methods: {
  },
  watch: {
    isSPAPINeedReconnect(newVal) {
      if (newVal) {
        this.alert = this.spapiReconnectAlert
      } else if (this.alert && this.alert.type === 'danger') {
        this.alert = null
      }
    }
  },
  created() {
    if (this.isSPAPINeedReconnect) {
      this.alert = this.spapiReconnectAlert
    }
  }
}
</script>
<style lang="scss" scoped>
.footer-content {
  font-size: 12px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 2;
  letter-spacing: normal;
  color: #004776;
  a {
    color: #004776;
  }
}
</style>
