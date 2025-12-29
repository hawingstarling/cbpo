<template>
    <b-card class="custom-reports">
        <div slot="header">
            <b-row class="justify-content-between" align-v="center">
                <b-col class="col-6">
                <span>
                    <strong><i class="fa fa-flag"></i> Custom Reports</strong>
                </span>

                <span class="ml-1">(Total: {{ reportsCount }})</span>
                </b-col>
                <div>
                  <b-button @click="refreshData()" variant="secondary" text="Small" size="sm" title="Refresh" class="mr-3">
                    <i class="fa fa-refresh mr-1"></i>
                    Refresh
                  </b-button>
                </div>
            </b-row>
        </div>
        <!-- search -->
        <div>
            <b-row class="justify-content-center align-items-center">
                <b-col md="3" class="mt-0 mb-4 px-1 d-flex justify-content-center">
                  <b-form-group class="mb-0 w-100 form-search-custom">
                    <b-input-group class="search cancel-action">
                      <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
                      <b-form-input class="input-search form-search-input" v-model="key" @keypress.enter="searchChange()" placeholder="Search"></b-form-input>
                      <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
                      <div class="form-search-icon" @click="searchChange()">
                        <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
                      </div>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="1" class="mt-0 px-1">
                  <b-button variant="primary" class="btn-refresh" @click="queryData">Refresh</b-button>
                </b-col>
            </b-row>
            <b-table class="custom-report-table" outlined striped head-variant="light" :items="customReportsList" :fields="itemsFields" show-empty>
                <template v-slot:empty>
                  <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
                      <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
                  </div>
                  <div class="align-items-center d-flex justify-content-center" v-else>
                      <div>There are no reports to show.</div>
                  </div>
                </template>
                <template v-slot:cell(preview)="row">
                  <b-button class="btn-preview" @click="currentReport = row.item; $bvModal.show('preview-modal')">Preview</b-button>
                </template>
                <template v-slot:cell(progress)="row">
                  <span>{{ row.item.progress }}%</span>
                </template>
                <template v-slot:cell(action)="row">
                    <div class="d-flex" style="justify-content: center">
                    <ul v-if="row.item.bulk_operations.length <= 3" class="progress-table__list">
                        <li v-for="index in row.item.bulk_operations.length" :key="index" v-html="buildExpression(row.item.bulk_operations[index -1])" />
                    </ul>
                    <ul v-else class="progress-table__list">
                        <li v-for="index in Math.min(row.item.bulk_operations.length, 3)" :key="index" v-html="buildExpression(row.item.bulk_operations[index -1])" />
                        <li>
                          <a class="progress-table__id-list ml-0" :id="`condition-list-${row.item.id}`">
                            <i class="fa fa-ellipsis-h" />
                          </a>
                          <b-popover :target="`condition-list-${row.item.id}`" triggers="hover" placement="top">
                            <template v-slot:title>
                              Action
                            </template>
                            <ul class="progress-table__list">
                              <li v-for="index in row.item.bulk_operations.length" :key="index" v-html="buildExpression(row.item.bulk_operations[index -1])" />
                            </ul>
                          </b-popover>
                        </li>
                    </ul>
                    </div>
                </template>
                <template v-slot:cell(actions)="row">
                  <div class='d-flex justify-content-center'>
                    <b-dropdown right variant="secondary" class="dropdown-manage" text="Manage">
                      <b-dropdown-item @click="openEditModal(row.item)">
                          <i class="fa fa-pencil"></i>Edit
                      </b-dropdown-item>
                      <b-dropdown-item @click="openDeleteReportModal(row.item)">
                          <i class="fa fa-trash"></i>Delete
                      </b-dropdown-item>
                      <b-dropdown-item v-if="row.item.status === 'reported' && hasPermission(permissions.customReport.export)" @click="handleDownload(row.item)">
                          <i class="fa fa-download"></i>Download
                      </b-dropdown-item>
                      <b-dropdown-item v-if="row.item.status !== 'revoked'" @click="handleCancelReport(row.item)">
                          <i class="fa fa-trash"></i>Cancel
                      </b-dropdown-item>
                    </b-dropdown>
                  </div>
                </template>
                <template v-slot:cell(status)="row">
                    <span :class="['status', row.item.status]">{{ upperCaseFirstLetter(row.item.status) }}</span>
                </template>
            </b-table>
        </div>
        <nav class="d-flex justify-content-center">
            <b-pagination @change="goToPage($event)" v-if="customReportsList && reportsCount > limit && !isLoading" v-model="page" :total-rows="reportsCount || 0" :per-page="limit" prev-text="Prev" next-text="Next" hide-goto-end-buttons>
              <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
              <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
            </b-pagination>
        </nav>
        <b-modal id="delete-report-confirm-modal" variant="danger" centered title="Please confirm">
          <div>Are you sure you want to delete this report?</div>
          <template v-slot:modal-footer>
            <b-button variant="warning" @click="handleDeleteReport()">
                <i class="icon-check"></i> Yes, I understand &amp; confirm!
            </b-button>
            <b-button variant @click="$bvModal.hide('delete-report-confirm-modal')" >
                <i class="icon-close"></i> No
            </b-button>
          </template>
        </b-modal>
        <b-modal
          id="edit-custom-export"
          title="Edit Custom Report"
          centered
        >
          <label class="mb-2">Name</label>
          <b-form-input class="mb-2" placeholder="Enter name" v-model="editName" @keypress.enter="handleEditReport"></b-form-input>
          <template v-slot:modal-footer>
            <div class="w-100">
              <b-button class="float-right" variant="primary" @click="handleEditReport" :disabled="editName ? false : true">Save</b-button>
              <b-button class="float-left" @click="$bvModal.hide('edit-custom-export')">Cancel</b-button>
            </div>
          </template>
        </b-modal>
        <b-modal id="preview-modal" title="Preview" content-class="preview-modal" centered hide-footer>
          <template slot="modal-header-close">
            <img src="@/assets/img/icon/x.svg" @click="$bvModal.hide('preview-modal')" />
          </template>
          <div v-if="currentReport" class="ml-3" v-html="getReportsExpr(currentReport.ds_query.filter)"></div>
        </b-modal>
    </b-card>
</template>
<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import exprUtil from '@/services/exprUtil'
import bulkProgressMixins from '@/mixins/bulkProgressMixins'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import toastMixin from '@/components/common/toastMixin'
export default {
  name: 'CustomReports',
  data() {
    return {
      key: '',
      itemsFields: [
        {key: 'name', label: 'Name', thClass: 'align-middle text-center', tdClass: 'align-middle'},
        {key: 'preview', label: 'Preview', thClass: 'align-middle text-center', tdClass: 'text-center'},
        {key: 'action', label: 'Bulk Edit', thClass: 'align-middle w-25 text-center', tdClass: 'align-middle'},
        {key: 'progress', label: 'Progress', thClass: 'align-middle text-center', tdClass: 'text-center align-middle'},
        {key: 'status', label: 'Status', thClass: 'align-middle text-center', tdClass: 'text-center align-middle'},
        {key: 'actions', label: 'Actions', thClass: 'align-middle text-center', tdClass: 'text-center align-middle'}
      ],
      isLoading: true,
      page: 1,
      limit: 10,
      permissions,
      currentReportId: null,
      currentReport: null,
      editName: null
    }
  },
  mixins: [bulkProgressMixins, PermissionsMixin, toastMixin],
  async created() {
    this.key = this.$route.query.search || ''
    await this.$router.push({
      name: 'PFCustomReports',
      params: { client_id: this.$route.params.client_id },
      query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.key }
    })
    this.queryData()
  },
  computed: {
    ...mapGetters({
      customReportsList: 'pf/reports/customReportsList',
      getUserId: `ps/userModule/GET_USER_ID`,
      reportsCount: 'pf/reports/reportsCount',
      dsColumns: `pf/analysis/dsColumns`
    }),
    params() {
      return {
        clientId: this.$route.params.client_id,
        userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
      }
    }
  },
  methods: {
    ...mapActions({
      getCustomReportsList: 'pf/reports/getCustomReportsList',
      deleteReport: 'pf/reports/deleteReport',
      cancelReport: 'pf/reports/cancelReport',
      editReport: 'pf/reports/editReport'
    }),
    ...mapMutations({
      setCustomReportsList: 'pf/reports/setCustomReportsList'
    }),
    async searchChange() {
      this.page = 1
      await this.$router.push({
        name: 'PFCustomReports',
        params: { client_id: this.$route.params.client_id },
        query: { page: this.page, limit: this.$route.query.limit || 10, search: this.key }
      })
    },
    getReportsExpr(query) {
      return exprUtil.buildReportExpr(query, this.dsColumns)
    },
    async goToPage(event) {
      if (this.$route.query.page !== event) {
        await this.$router.push({
          name: 'PFCustomReports',
          params: { client_id: this.$route.params.client_id },
          query: { page: event, limit: this.$route.query.limit || 10, search: this.key }
        })
      }
    },
    handleDownload(data) {
      if (data.status === 'reported') {
        this.downloadURL(data.download_url, data.name)
      }
    },
    downloadURL(url, name) {
      var link = document.createElement('a')
      link.download = name
      link.href = url
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      link = null
    },
    upperCaseFirstLetter(word) {
      return word[0].toUpperCase() + word.substr(1)
    },
    queryData() {
      this.setCustomReportsList([])
      this.isLoading = true
      const params = this.params
      const query = {
        page: this.$route.query.page,
        limit: this.$route.query.limit,
        search: this.key
      }
      this.getCustomReportsList({
        params,
        query
      }).finally(() => {
        this.isLoading = false
      })
    },
    handleEditReport() {
      const params = this.params
      this.editReport({ params: params, id: this.currentReportId, name: this.editName }).then(() => {
        this.editName = null
        this.queryData()
        this.vueToast('success', 'The report has been edited successfully.')
      })
        .catch(err => {
          this.vueToast('error', err.response.data.message)
        })
        .finally(() => {
          this.$bvModal.hide('edit-custom-export')
        })
    },
    openDeleteReportModal(data) {
      this.currentReportId = data.id
      this.$bvModal.show('delete-report-confirm-modal')
    },
    handleDeleteReport() {
      const params = this.params
      this.deleteReport({ params: params, id: this.currentReportId }).then(() => {
        this.queryData()
        this.vueToast('success', 'The report has been deleted successfully.')
      })
        .catch(error => {
          console.log('error', error.response.data)
          // this.vueToast('error', error.response.data)
        })
        .finally(() => {
          this.$bvModal.hide('delete-report-confirm-modal')
        })
    },
    handleCancelReport(data) {
      const params = this.params
      this.cancelReport({ params: params, id: data.id }).then(() => {
        this.queryData()
        this.vueToast('success', 'The report has been cancelled successfully.')
      })
    },
    openEditModal(data) {
      this.currentReportId = data.id
      this.editName = data.name
      this.$bvModal.show('edit-custom-export')
    },
    refreshData() {
      this.queryData()
    }
  },
  watch: {
    async $route(to, from) {
      this.key = this.$route.query.search || ''
      await this.queryData()
    }
  }
}
</script>
<style lang="scss" scoped>
@import './CustomReports.scss';
</style>
