<template>
  <b-container fluid class="px-2">
    <b-row class="m-0">
      <b-col md="6" lg="6" sm="12" class="p-0">
        <b-card>
          <div slot="header">
            <span>
              <strong><i class="fa fa-wrench mr-1 align-middle"></i>Tools</strong>
            </span>
          </div>
          <b-row v-if="hasPermission(permissions.admin.syncWorkspace) || hasPermission(permissions.admin.generateDS)">
            <b-col md="12" lg="12" sm="12">
              <b-table class="mb-0" hover striped outlined small thead-class="thead-light" responsive="sm" tbody-tr-class="fs-90p" :fields="fields" :items="listTools">
                <template v-slot:cell(name)="row">
                  <i :class="row.item.name.icon" class="mr-2 ml-1"></i>
                  <span>{{ row.item.name.title }}</span>
                </template>
                <template v-slot:cell(status)="row">
                  <div v-if="!row.item.status" :disabled="true">
                    <b-spinner small variant="secondary" label="Loading..."></b-spinner>
                  </div>
                  <b-badge v-else-if="row.item.status.toLowerCase() === `generating`" variant="primary">Generating</b-badge>
                  <b-badge v-else-if="row.item.status.toLowerCase() === `success`" variant="success">Success</b-badge>
                  <b-badge v-else-if="row.item.status.toLowerCase() === `pending`" variant="warning">Pending</b-badge>
                  <b-badge v-else-if="row.item.status.toLowerCase() === `dead`" variant="secondary">Dead</b-badge>
                  <b-badge v-else-if="row.item.status.toLowerCase() === `error`" variant="danger">Error</b-badge>
                </template>
                <template v-slot:cell(action)="row">
                  <b-button
                    variant="primary"
                    v-on:click="handleSync({ idx: row.index, client_id: $route.params.client_id, type: row.item.type })"
                    :disabled="row.item.status.toLowerCase() === 'success'"
                  >
                    Sync
                  </b-button>
                </template>
              </b-table>
            </b-col>
          </b-row>
          <b-alert show variant="warning" v-else>You don't have the access to these tools</b-alert>
        </b-card>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import toastMixin from '@/components/common/toastMixin'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import { convertedPermissions as permissions } from '@/shared/utils'

export default {
  name: 'PFTools',
  data: () => {
    return {
      params: {},
      client_id: '',
      permissions,
      fields: [
        { key: 'name', label: 'Name', tdClass: 'text-nowrap py-3 align-middle', thClass: 'py-3 align-middle' },
        { key: 'status', label: 'Status', tdClass: 'text-nowrap py-3 align-middle', thClass: 'py-3 align-middle' },
        { key: 'action', label: 'Mandatory', tdClass: 'text-nowrap py-3 align-middle text-right', thClass: 'py-3 align-middle text-right' }
      ]
    }
  },
  mixins: [toastMixin, PermissionsMixin],
  computed: {
    ...mapGetters({
      listTools: `pf/tools/listTools`
    })
  },
  methods: {
    ...mapActions({
      getStatusGenerateWorkspace: 'pf/tools/getStatusGenerateWorkspace',
      getStatusDataSource: `pf/tools/getStatusDataSource`,
      getSyncGenerateWorkspace: `pf/tools/getSyncGenerateWorkspace`,
      getSyncDataSource: `pf/tools/getSyncDataSource`,
      getStatus: 'pf/tools/getStatus',
      getSync: `pf/tools/getSync`
    }),
    async handleSync(payload) {
      try {
        await this.getSync(payload)
        this.vueToast('success', `Sync ${payload.type === 'workspace' ? 'Workspace' : 'Data source'} has been completed.`)
      } catch (err) {
        this.vueToast('error', `Sync ${payload.type === 'workspace' ? 'Workspace' : 'Data source'} has been failed.`)
      }
    }
  },
  beforeCreate() {},
  created() {
    this.params.client_id = this.$route.params.client_id
    this.listTools.forEach((item, index) => {
      this.getStatus({ idx: index, type: item.type, client_id: this.params.client_id })
    })
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

.max-width-100 {
  width: 100%;
}
.card {
  margin-bottom: 10px !important;
}

</style>
