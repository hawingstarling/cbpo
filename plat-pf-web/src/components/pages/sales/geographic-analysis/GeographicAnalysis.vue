<template>
<b-card>
  <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="!isReady">
    <div class="spinner-border thin-spinner spinner-border-sm cls-loading-geo"></div>&nbsp;Loading...
  </div>
  <div v-if="isReady && isGetFullDsId" class="custom-dashboard row">
    <div class="col-12 global-filter pr-1">
      <cbpo-widget :config-obj="configs.GlobalFiltter.config"/>
    </div>
    <div class="col-12 pr-1">
      <cbpo-widget :config-obj="configs.SalesPerState.config"/>
    </div>
    <div class="col-12 pr-1">
      <cbpo-widget :config-obj="configs.HeatMapSummary.config"/>
    </div>
  </div>
  <div v-else-if="!isGetFullDsId" class="alert alert-warning" role="alert">
    The data source is not ready.
  </div>
</b-card>
</template>

<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'
import dashboardWidget from './WidgetConfig/DetailWidgetConfig'

import toastMixin from '@/components/common/toastMixin'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'

export default {
  name: 'GeographicAnalysis',
  components: {
  },
  mixins: [
    toastMixin,
    PermissionsMixin,
    spapiReconnectAlertMixin
  ],
  data() {
    return {
      configs: _.cloneDeep(dashboardWidget),
      isReady: false,
      isGetFullDsId: true,
      permissions
    }
  },
  computed: {
    ...mapGetters({
      dsIdForMapping: `pf/overview/dsIdForMapping`
    })
  },
  methods: {
    ...mapActions({
      fetchDSIdForMapping: `pf/overview/fetchDSIdForMapping`
    }),
    mapDSIdToWidgetConfig() {
      for (let config in this.configs) {
        let dsId = this.configs[config].config.elements[0].config.dataSource
        this.configs[config].config.elements[0].config.dataSource = this.dsIdForMapping[dsId]
          ? this.dsIdForMapping[dsId].data_source_id
          : dsId
        if (this.configs[config].config.filter.form.config.controls.length > 0) {
          this.configs[config].config.filter.form.config.controls.forEach(control => {
            let dsFilterId = control.config.dataSource
            control.config.dataSource = this.dsIdForMapping[dsFilterId]
              ? this.dsIdForMapping[dsFilterId].data_source_id
              : dsFilterId
          })
        }
      }
      if (_.isEmpty(this.dsIdForMapping)) {
        this.isGetFullDsId = false
      }
    }
  },
  async created() {
    await this.fetchDSIdForMapping({client_id: this.$route.params.client_id})
    this.mapDSIdToWidgetConfig()
    this.isReady = true
  }
}
</script>

<style lang="scss" scoped>
.custom-dashboard {
  background-color: white;
  padding: 0.5rem 0;

  [class^="col"] {
    height: 600px;
    padding-bottom: 0.5rem;
    padding-right: 0.5rem;
    padding-left: 0.5rem;
  }
}
.widget-component {
  padding-bottom: 0.5rem;
}
.custom-dashboard .global-filter {
  height: 250px;
}
.cls-loading-geo {
  border-width: 0.1em !important
}
::v-deep .cbpo-filter-control-select {
  .cbpo-custom-select {
    padding: 0.2rem 0 !important;
    margin-left: 8px;
  }
}
</style>
