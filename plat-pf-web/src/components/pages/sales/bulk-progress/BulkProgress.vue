<template>
  <b-card>
    <!-- header -->
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-12">
          <span>
            <strong><i class="fa fa-tasks mr-1"></i> Bulk Progress</strong>
          </span>
          <span class="pull-right">
            <small :key="updateRenderKey"> Updated {{ getDateTime(lastListAPICallAt) }}. </small>&nbsp;
            <b-button variant="secondary" text="Small" size="sm" @click="refreshData()" title="Refresh"> <i class="fa fa-refresh mr-1"></i>Refresh </b-button>
          </span>
        </b-col>
      </b-row>
    </div>
    <!-- select -->
    <b-row class="justify-content-center">
      <b-col md="2" class="mt-0 mb-4 px-1">
        <b-form-group class="mb-0">
          <b-form-select v-on:change="initQueryParams" v-model="params.status" :options="listBulkType">
            <template v-slot:first>
              <option :value="null">All status</option>
            </template>
          </b-form-select>
        </b-form-group>
      </b-col>
      <b-col md="4" class="mt-0 mb-4 px-1">
        <b-form-group class="mb-0">
          <b-input-group class="search cancel-action form-search-custom">
            <b-form-input class="input-search form-search-input" v-model="params.search" @keypress.enter="initQueryParams()" placeholder="Search for user, action and data">
            </b-form-input>
            <i v-if="params.search" @click="params.search=null, initQueryParams()" class="icon-close cancel-icon form-cancel-icon"></i>
            <div class="form-search-icon" @click="initQueryParams()">
              <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
            </div>
          </b-input-group>
        </b-form-group>
      </b-col>
    </b-row>
    <!-- table -->
    <b-row>
      <b-col class="table-responsive col-12">
        <b-table
          id="progress-table"
          show-empty
          hover
          outlined
          striped
          responsive="sm"
          thead-class="thead-light"
          :fields="fields"
          :items="bulkList.results"
          class="progress-table"
        >
          <template v-slot:empty>
            <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="isLoading">
              <div class="spinner-border thin-spinner spinner-border-sm thin-spinner"></div>&nbsp;Loading...
            </div>
            <div class="align-middle d-flex justify-content-center" v-else>
              <div>There is no progress to show.</div>
            </div>
          </template>
          <template v-slot:cell(user)="row">
            <div class="d-flex" v-if="row.item.meta.user_info">
<!--              <img :src="row.item.meta.user_info.avatar || placeholderURL" alt="" class="progress-table__avatar" />-->
              <div>
                <div class="progress-table__name">
                  {{ getFullName(row.item.meta.user_info) }}
                </div>
                <div>{{ row.item.meta.user_info.email }}</div>
              </div>
            </div>
            <div v-else>Anonymous</div>
          </template>
          <template v-slot:cell(created)="row">
            <div>{{ getDateTime(row.item.created) }}</div>
          </template>
          <template v-slot:cell(modified)="row">
            <div>{{ getDateTime(row.item.modified) }}</div>
          </template>
          <template v-slot:cell(total)="row">
            <div>
              Total:
              <strong>{{ numberFormat(row.item.summary.total) }} items</strong>
              <a class="progress-table__id-list" :id="`id-list-${row.item.id}`">
                <i class="fa fa-ellipsis-h" />
              </a>
              <b-popover :target="`id-list-${row.item.id}`" triggers="hover" placement="top">
                <template v-slot:title>
                  Item IDs
                </template>
                <ul class="progress-table__list">
                  <li v-for="index in Math.min(row.item.meta.ids.length, 5)" :key="index">
                    {{ row.item.meta.ids[index - 1] }}
                  </li>
                  <li v-if="row.item.meta.ids.length > 5">...</li>
                </ul>
                <div v-if="isPropertyExisted(row.item.meta.query, 'filter')" class="progress-table__list">
                  <strong>Filter</strong>
                  <div v-html="$CBPO.dataQueryManager().getFilterReadableFromFilter(row.item.meta.query.filter, dsColumns)" />
                </div>
                <div v-if="isPropertyExisted(row.item.meta.query, 'timezone')" class="progress-table__list mt-2 d-flex">
                  <strong>Timezone: </strong>
                  <div class="ml-1">
                    {{ getTimezoneTitle(row.item.meta.query.timezone) }}
                  </div>
                </div>
              </b-popover>
            </div>
            <div class="d-flex align-items-center">
              <div class="d-flex align-items-center">
                <span class="badge badge--success">
                  <i class="fa fa-check" />
                </span>
                {{ numberFormat(row.item.summary.success) }} items
              </div>
              <div class="d-flex align-items-center ml-2">
                <span class="badge badge--error"><i class="fa fa-times"/></span>
                {{ numberFormat(row.item.summary.error) }} items
              </div>
            </div>
          </template>
          <template v-slot:cell(condition)="row">
            <div class="d-flex align-items-center progress-table__list mb-1" v-if="row.item.meta.command">
              <b-badge pill :variant="getAssetsByCommand(row.item.meta.command, 'variant')" class="font-weight-normal">
                <i :class="[`fa fa-${getAssetsByCommand(row.item.meta.command, 'icon')}`]" />
                <span class="ml-1 text-capitalize">
                  {{ row.item.meta.command.split('_').join(' ') }}
                </span>
              </b-badge>
            </div>
            <div class="d-flex flex-column" v-if="row.item.meta">
              <ul class="progress-table__list" v-if="row.item.meta.sources">
                <li v-for="(source, index) in row.item.meta.sources" :key="index">
                  {{ DATASOURCES_MAPPING[source] }}
                </li>
              </ul>
              <ul class="progress-table__list" v-if="row.item.meta[DATASOURCES_OPTIONS.PF_SHIPPING_COST]">
                <li>
                  [
                  {{ DATASOURCES_OPTIONS_MAPPING[DATASOURCES_OPTIONS.PF_SHIPPING_COST] }}
                  ]
                </li>
              </ul>
            </div>
            <div class="d-flex" v-if="row.item.meta.updates">
              <ul class="progress-table__list">
                <li v-for="index in Math.min(row.item.meta.updates.length, 3)" :key="index" v-html="buildExpression(row.item.meta.updates[index - 1])" />
                <li v-if="row.item.meta.updates.length > 3">
                  <a class="progress-table__id-list ml-0" :id="`condition-list-${row.item.id}`">
                    <i class="fa fa-ellipsis-h" />
                  </a>
                  <b-popover :target="`condition-list-${row.item.id}`" triggers="hover" placement="top">
                    <template v-slot:title>
                      Conditions
                    </template>
                    <ul class="progress-table__list">
                      <li v-for="(update, index) in row.item.meta.updates" :key="index" v-html="buildExpression(update)" />
                    </ul>
                  </b-popover>
                </li>
              </ul>
            </div>
          </template>
          <template v-slot:cell(progress)="row">
            <div>
              <span class="badge badge--success" :class="`badge--${isProgressCompleted(row.item.progress) ? 'success' : 'error'}`"> {{ row.item.progress }}% </span>
            </div>
          </template>

          <template v-slot:cell(status)="row">
            <div>
              <span class="badge" :class="checkClassName(row.item.status)">{{ row.item.status | capitalize }}</span>
            </div>
          </template>
          <template v-slot:cell(action)="row">
            <b-btn-group size="sm">
              <b-button
                variant="primary"
                class="btn-view"
                @click="
                  $router.push({
                    name: 'PFBulkProgressDetail',
                    params: { bulk_id: row.item.id, module: row.item.meta.module }
                  })
                "
              >
                View
              </b-button>
              <b-btn v-if="!isProgressCompleted(row.item.progress)" class="d-inline-flex align-items-center" @click="handleOpenModalConfirmCancelBulkProgress(row.item)"> <i class="fa fa-times-circle mr-2" /> Cancel </b-btn>
            </b-btn-group>
          </template>
        </b-table>
        <b-modal id="modal-confirm-cancel-bulk-progress" variant="danger" centered title="Please confirm">
          <div>Are you sure you want to cancel this bulk progress?</div>
          <template v-slot:modal-footer>
            <b-button variant="warning" @click="handleCancelBulkProgress()"> <i class="icon-check"></i> Yes, I understand &amp; confirm! </b-button>
            <b-button variant @click="$bvModal.hide('modal-confirm-cancel-bulk-progress')"> <i class="icon-close"></i> No </b-button>
          </template>
        </b-modal>
        <nav class="d-flex justify-content-center" v-if="bulkList">
          <b-pagination
            @click.native="goToPage"
            v-if="bulkList.count && bulkList.count > params.limit"
            :total-rows="bulkList.count || 0"
            :per-page="params.limit"
            v-model="params.page"
            first-text="First"
            prev-text="Prev"
            next-text="Next"
            last-text="Last"
          />
        </nav>
      </b-col>
    </b-row>
  </b-card>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import bulkProgressMixins from '@/mixins/bulkProgressMixins'
import placeholderURL from '@/assets/img/profile-placeholder.png'
import toastMixin from '@/components/common/toastMixin'
import _ from 'lodash'
export default {
  name: 'PFBulkProgress',
  mixins: [PermissionsMixin, bulkProgressMixins, toastMixin],
  data: () => {
    const commonThClass = 'text-center align-middle'
    const commonTdClass = 'text-center align-middle'
    return {
      fields: [
        { key: 'user', label: 'User', class: 'user-td', thClass: commonThClass, tdClass: commonTdClass },
        { key: 'created', label: 'Created', class: 'created-td', thClass: commonThClass, tdClass: commonTdClass },
        { key: 'modified', label: 'Modified', class: 'modified-td', thClass: commonThClass, tdClass: commonTdClass },
        { key: 'total', label: 'Total', class: 'total-td', thClass: commonThClass, tdClass: commonTdClass },
        { key: 'condition', label: 'Command', thClass: commonThClass, tdClass: 'align-middle text-right' },
        { key: 'progress', label: 'Progress', thClass: commonThClass, tdClass: [commonTdClass, 'pr-2'] },
        { key: 'status', label: 'Status', thClass: commonThClass, tdClass: [commonTdClass, 'text-truncate', 'pr-2'] },
        { key: 'action', label: 'Action', thClass: commonThClass, tdClass: commonTdClass }
      ],
      optionStatus: [{ text: '', value: 'abc' }],
      params: {
        page: 1,
        limit: 10,
        status: null,
        search: null
      },
      placeholderURL,
      updateRenderKey: false,
      renderTime: null,
      itemSelected: null,
      isLoading: true
    }
  },
  filters: {
    capitalize: function (value) {
      return _.startCase(value)
    }
  },
  computed: {
    ...mapGetters({
      bulkList: `pf/bulk/bulkList`,
      dsColumns: `pf/analysis/dsColumns`,
      lastListAPICallAt: `pf/bulk/lastListAPICallAt`,
      bulkTypeFilterList: `pf/bulk/bulkTypeFilterList`
    }),
    listBulkType() {
      return this.bulkTypeFilterList.map(item => {
        item['value'] = item['key']
        item['text'] = item['label']
        return item
      })
    }
  },
  methods: {
    ...mapActions({
      getBulkList: `pf/bulk/getBulkList`,
      fetchDSColumns: `pf/analysis/fetchDSColumns`,
      cancelationBulkProgress: `pf/bulk/cancelBulkProgress`,
      getListBulkTypeFilter: `pf/bulk/getListBulkTypeFilter`,
      fetchAllDataSourceIDs: `pf/analysis/fetchAllDataSourceIDs`
    }),
    // loading
    async loadingListBulk(payload) {
      this.isLoading = true
      try {
        await this.getBulkList(payload)
      } catch (err) {
        console.log('error', err)
      }
      this.isLoading = false
    },
    async handleQueryData() {
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        status: this.$route.params.status
      }
      let data = _.pickBy({ ...payload }, _.identity)
      await this.loadingListBulk(data)
    },
    checkClassName(status) {
      switch (status) {
        case 'revoked':
          return 'badge-warning'
        case 'failure':
          return 'badge-danger'
        case 'processed':
          return 'badge-success'
        case 'processing':
          return 'badge-primary'
        case 'reverted':
          return 'badge-dark'
        default:
          return 'badge-secondary'
      }
    },
    handleOpenModalConfirmCancelBulkProgress(item) {
      this.itemSelected = item
      this.$bvModal.show('modal-confirm-cancel-bulk-progress')
    },
    async handleCancelBulkProgress() {
      try {
        await this.cancelationBulkProgress({ clientId: this.itemSelected.client_id, id: this.itemSelected.id })

        this.vueToast('success', 'Cancel bulk progress successfully.')

        let index = this.bulkList.results.findIndex(bulk => bulk.id === this.itemSelected.id)
        this.$set(this.bulkList.results[index], 'status', 'revoked')
        this.$set(this.bulkList.results[index], 'progress', 100)
      } catch (err) {
        this.vueToast('error', 'Cancel bulk progress failed. Please retry or contact administrator.')
      } finally {
        this.$bvModal.hide('modal-confirm-cancel-bulk-progress')
      }
    },
    goToPage() {
      this.getBulkList(this.params).then(() => {
        window.scrollTo(0, top)
      })
    },
    async initQueryParams() {
      const query = this.$route.query
      this.isLoading = true
      if (query && query.page) {
        this.params.page = query.page
        try {
          await this.getBulkList(this.params)
        } catch (e) {
          this.params.page = 1
          this.getBulkList(this.params)
        }
      } else {
        try {
          await this.getBulkList(this.params)
        } catch (e) {
          console.log(e)
        }
      }
      this.isLoading = false
    },
    async refreshData() {
      await this.initQueryParams()
      this.updateRenderKey = !this.updateRenderKey
    },
    reRenderTimeUpdate() {
      this.renderTime = setInterval(() => {
        this.updateRenderKey = !this.updateRenderKey
      }, 60000)
    }
  },
  async created() {
    this.params.client_id = this.$route.params.client_id
    await this.fetchAllDataSourceIDs({client_id: this.params.client_id})
    await this.getListBulkTypeFilter(this.params)
    await this.initQueryParams()
    await this.fetchDSColumns(this.params)
    this.reRenderTimeUpdate()
    this.handleQueryData()
  },
  beforeDestroy() {
    clearInterval(this.renderTime)
  },
  watch: {
    'params.page': function() {
      this.$router.replace({
        name: 'PFBulkProgress',
        query: { page: this.params.page }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
@import './BulkProgress.scss';
.group--control {
  width: 60%;
}
.card-body {
  padding-bottom: 0;
}
.table-responsive {
  margin-bottom: 0;
}
</style>
