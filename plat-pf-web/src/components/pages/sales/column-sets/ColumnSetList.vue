<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="fa fa-columns"></i> Column Sets</strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <div>
      <b-row class="justify-content-center align-items-center">
        <b-col md="4" class="mt-0 mb-4">
          <b-form-group class="mb-0">
            <b-input-group class="search cancel-action">
              <b-form-input class="input-search" v-model="key" v-on:keyup.enter="searchChange()" placeholder="Search for name">
              </b-form-input>
              <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon"></i>
              <b-input-group-append>
                <b-button @click="searchChange()">
                  <i class="icons icon-magnifier"></i>
                </b-button>
              </b-input-group-append>
            </b-input-group>
          </b-form-group>
        </b-col>
      </b-row>
      <b-table outlined striped head-variant="light" table-variant="secondary" :fields="filteredFields" :items="columnSetList.results" empty-text="There are no column sets to show" show-empty>
        <template v-slot:empty>
          <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="isLoading">
            <div class="spinner-border spinner-border-sm thin-spinner"></div>&nbsp;Loading...
          </div>
          <div class="align-middle d-flex justify-content-center" v-else>
            <div>There are no column sets to show</div>
          </div>
        </template>
        <template v-slot:cell(actions)="row">
          <div class="d-flex">
            <b-button
              v-if="hasPermission(permissions.sale.viewAll) || hasPermission(permissions.sale.view24h)"
              variant="primary" text="Small" size="sm"
              @click="$router.push({name: 'PFAnalysis', params: { selectedColumnSet: row.item }, query: { columnSetId: row.item.id }})"
            >
              <i class="fa fa-check-circle mr-1"></i>Open
            </b-button>
            <ManageDropdown typeDropdown="columnSet" class="ml-2" @openShareModal="openModal(row.item)" @openDeleteConfirmModal="openConfirmModal(row.item)"/>
          </div>
        </template>
        <template v-slot:cell(name)="row">
          <div>{{row.item.name}} <i class="fa fa-star text-warning" v-if="row.item.featured" /> {{showCreater(row.item)}}</div>
        </template>
        <template v-slot:cell(preview)="row">
          <div class="alert alert-warning expr-table" v-html="getColumnSetExpr(row.item.ds_column.config.columns)"></div>
        </template>
        <template v-slot:cell(created)="row">
          <span>{{row.item.created | moment("from", "now")}}</span>
        </template>
        <template v-slot:cell(modified)="row">
          <span>{{row.item.modified | moment("from", "now")}}</span>
        </template>
      </b-table>
      <b-modal
        id="share-center"
        title="Confirmation"
        size="xl"
        centered
        hide-footer
      >
        <PFShareCenter :id_item="id_item" :share_mode="share_mode" type="column-set"></PFShareCenter>
      </b-modal>
      <b-modal id="delete-confirm" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to delete this item?</div>
        <template v-slot:modal-footer>
          <b-button variant="warning" @click="handleRemoveColumnSet()" :disabled="deleting">
              <i class="icon-check"></i> Yes, I understand &amp; confirm!
          </b-button>
          <b-button variant @click="$bvModal.hide('delete-confirm')" :disabled="deleting">
              <i class="icon-close"></i> No
          </b-button>
        </template>
      </b-modal>
    </div>
    <nav class="d-flex justify-content-center">
      <b-pagination @change="goToPage($event)" v-if="columnSetList && columnSetList.count > $route.query.limit" :total-rows="columnSetList.count || 0" :per-page="$route.query.limit" v-model="$route.query.page" prev-text="Prev" next-text="Next" hide-goto-end-buttons />
    </nav>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import PFShareCenter from '@/components/common/ShareCenter'
import ManageDropdown from '@/components/common/ManageDropdown'
import toastMixin from '@/components/common/toastMixin'
import exprUtil from '@/services/exprUtil'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import { convertedPermissions as permissions, showCreaterName } from '@/shared/utils'
import _ from 'lodash'
import _nav from '@/_nav'

export default {
  name: 'PFColumnSetList',
  data() {
    return {
      saveTableFields: [
        {key: 'name', lable: 'Name', tdClass: 'align-middle'},
        {key: 'preview', lable: 'Preview', tdClass: 'align-middle w-50'},
        {key: 'created', lable: 'Created', tdClass: 'align-middle'},
        {key: 'modified', lable: 'Modified', tdClass: 'align-middle'},
        {key: 'actions', lable: 'Actions', tdClass: 'align-middle action-col'}
      ],
      id_item: '',
      share_mode: null,
      pagingColumnSets: {
        page: 1,
        limit: 10
      },
      key: '',
      deleting: false,
      permissions,
      nav: _nav,
      isLoading: true
    }
  },
  mixins: [
    toastMixin,
    PermissionsMixin
  ],
  computed: {
    ...mapGetters({
      columnSetList: `pf/analysis/columnSetList`,
      getUserId: `ps/userModule/GET_USER_ID`
    }),
    getColumnSetExpr() {
      return columns => exprUtil.buildColumnSetExpr(columns)
    },
    filteredFields() {
      if (!(this.hasPermission(this.permissions.sale.viewAll) ||
        this.hasPermission(this.permissions.sale.view24h) ||
        this.hasPermission(this.permissions.columnSet.share) ||
        this.hasPermission(this.permissions.columnSet.delete))
      ) {
        return this.saveTableFields.filter(f => f.key !== 'actions')
      } else {
        return this.saveTableFields
      }
    },
    showCreater() {
      return (qSelecter) => {
        let userId = this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
        return showCreaterName(qSelecter, userId)
      }
    }
  },
  components: {
    PFShareCenter,
    ManageDropdown
  },
  methods: {
    ...mapActions({
      getColumnSets: `pf/analysis/getColumnSets`,
      removeColumnSet: `pf/analysis/removeColumnSet`
    }),
    ...mapMutations({
      setColumnSetList: `pf/analysis/setColumnSetList`
    }),
    async handleRemoveColumnSet() {
      this.deleting = true
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id_item: this.id_item,
          search: this.key
        }
        payload.limit = this.pagingColumnSets.limit
        payload.page = this.pagingColumnSets.page
        await this.removeColumnSet(payload)
        await this.getColumnSets(payload)
        this.$bvModal.hide('delete-confirm')
        this.vueToast('success', 'Removed successfully.')
      } catch {
        this.vueToast('error', 'Removing failed. Please retry or contact administrator.')
      }
      this.deleting = false
    },
    openModal(item) {
      this.id_item = item.id
      this.share_mode = item.share_mode
      this.$nextTick(() => {
        this.$bvModal.show(`share-center`)
      })
    },
    openConfirmModal(item) {
      this.id_item = item.id
      this.$nextTick(() => {
        this.$bvModal.show(`delete-confirm`)
      })
    },
    async goToPage(event) {
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
    },
    async searchChange() {
      this.setColumnSetList([])
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.key, page: this.$route.query.page } })
      this.handleFetchColumnsData()
    },
    getQueryRouter() {
      let payload = {
        search: this.key,
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
      }
      return payload
    },
    async handleFetchColumnsData() {
      this.isLoading = true
      let data = _.pickBy({ ...this.getQueryRouter() }, _.identity)
      await this.getColumnSets(data)
      this.isLoading = false
    }
  },
  async created() {
    this.key = this.$route.query.search || ''
    if (!this.$route.query.limit && !this.$route.query.page) {
      await this.$router.push({
        name: 'PFColumnSetList',
        params: { client_id: this.nav.clientId },
        query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search }
      })
    } else {
      this.handleFetchColumnsData()
    }
  },
  watch: {
    async $route(to, from) {
      if (from.fullPath !== to.fullPath) {
        await this.handleFetchColumnsData()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '@/assets/scss/listSaved.scss';
</style>
