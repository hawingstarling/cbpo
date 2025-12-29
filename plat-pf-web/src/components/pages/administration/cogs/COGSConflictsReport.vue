<template>
  <b-card class="card-custom">
    <div class="mb-4 header">
      <div>
        <h5 class="mb-0">
          COGS Conflicts Report
        </h5>
      </div>
    </div>
    <b-row class="justify-content-center align-items-center">
      <b-col md="10" class="mt-0 ml-5 d-flex justify-content-center channel-filter-group">
        <div class="pr-2 col-2">
          <div class="d-flex flex-wrap">
            <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Channel</span>
            <b-form-select class="custom-form-item" id="filter-channel" v-model="filters.channel"
              :options="channelOptions" @change="onFilterChange" />
          </div>
        </div>
        <div class="pr-2 col-2">
          <div class="d-flex flex-wrap">
            <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Used COG</span>
            <b-form-select class="custom-form-item" id="filter-priority" v-model="filters.used_cog"
              :options="usedCOGOptions" @change="onFilterChange" />
          </div>
        </div>
        <div class="pr-2 col-2">
          <div class="d-flex flex-wrap">
            <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Status</span>
            <b-form-select class="custom-form-item" id="filter-status" v-model="filters.status" :options="statusOptions"
              @change="onFilterChange" />
          </div>
        </div>
        <div class="pr-2 col-2">
          <b-form-group class="mb-0 d-flex flex-wrap">
            <b-input-group class="search cancel-action form-search-custom">
              <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
              <b-form-input class="input-search form-search-input custom-form-item" v-model.trim="filters.search"
                @keypress.enter="onFilterChange()" placeholder="Search for keywords">
              </b-form-input>
              <i v-if="filters.search" @click="filters.search='', onFilterChange()"
                class="icon-close cancel-icon form-cancel-icon"></i>
              <div class="form-search-icon" @click="onFilterChange()">
                <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
              </div>
            </b-input-group>
          </b-form-group>
        </div>
        <div class="pl-2 col-2 d-flex align-items-end" v-if="hasPermission(permissions.cogsConflictsReport.export)">
          <b-dropdown right class="dropdown-manage dropdown-icon-export"
            :class="{ 'hovering-menu': isHoveringExportDropdownItem }">
            <template #button-content>
              <span class="export-icon"></span>Export
            </template>
            <div @mouseover="isHoveringExportDropdownItem = true" @mouseleave="isHoveringExportDropdownItem = false">
              <b-dropdown-item @click="handleExportConflictsSelected()">
                Export Selected
              </b-dropdown-item>
              <b-dropdown-item @click="handleExportConflicts()">
                Export All
              </b-dropdown-item>
            </div>
          </b-dropdown>
        </div>
      </b-col>
    </b-row>
    <div>
      <b-form-checkbox class="all-checkbox" :checked="allSelected" @change="toggleSelectAll" aria-label="Select All">
        Select All
      </b-form-checkbox>
      <b-table outlined striped head-variant="light" @sort-changed="handleSortCogsConflicts" :no-local-sorting="true"
        :items="cogsConflictList" :fields="fields" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc" show-empty
        class="none-table-border">
        <template v-slot:cell(select)="row">
          <b-form-checkbox v-model="selected" :value="row.item.id || row.item.sale_id || row.index"
            :aria-label="'Select row ' + (row.item.sku || row.item.sale_id)" />
        </template>
        <template v-slot:cell(sale_ids)="row">
          <template v-if="Array.isArray(row.item.sale_ids)">
            <router-link
              :to="{ name: 'PFAnalysis', query: { sale_id: JSON.stringify(row.item.sale_ids) } }"
              target="_blank"
              class="router--custom"
            >
              <div v-for="(id, index) in row.item.sale_ids" :key="index">
                {{ id }}
              </div>
            </router-link>
          </template>
          <template v-else-if="row.item.sale_ids">
            <router-link
              :to="{ name: 'PFAnalysis', query: { sale_id: row.item.sale_ids } }"
              target="_blank"
              class="router--custom"
            >
              {{ row.item.sale_ids }}
            </router-link>
          </template>
        </template>
        <template v-slot:cell(channel_sale_ids)="row">
          <div v-for="(id, index) in row.item.channel_sale_ids" :key="index">
            {{ id }}
          </div>
        </template>
        <template v-slot:cell(extensiv_cog)="row">
          <span :class="{ 'font-weight-600': row.item.status === 'In conflict' && row.item.used_cog === 'Extensiv' }">
            {{ row.item.extensiv_cog }}
          </span>
        </template>
        <template v-slot:cell(dc_cog)="row">
          <span :class="{ 'font-weight-600': row.item.status === 'In conflict' && row.item.used_cog === 'Data Central' }">
            {{ row.item.dc_cog }}
          </span>
        </template>
        <template v-slot:cell(pf_cog)="row">
          <span :class="{ 'font-weight-600': row.item.status === 'In conflict' && row.item.used_cog === 'PF' }">
            {{ row.item.pf_cog }}
          </span>
        </template>
        <template v-slot:cell(created)="row">
          {{ row.item.created | formatDate('MM/DD/YYYY') }}
        </template>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no conflicts to show.</div>
          </div>
        </template>
      </b-table>
      <nav class="d-flex justify-content-center">
        <b-pagination class="btn-pagination-width" @input="goToPage"
          v-if="cogsConflictList && cogsConflictCount > ($route.query.limit || 20)" :total-rows="cogsConflictCount || 0"
          :per-page="Number($route.query.limit) || 20" v-model="page" prev-text="Prev" next-text="Next"
          hide-goto-end-buttons
        >
          <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span
              class="pl-2"> Previous</span></template>
          <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg"
              class="pagination-icon"></template>
        </b-pagination>
      </nav>
    </div>

    <!-- Download Export Modal -->
    <b-modal id="download-export-modal" centered variant="success" body-class="p-4" :hide-footer="true"
      :hide-header="true" content-class="modal-download-content">
      <div class="d-block text-center">
        <h3>The following items were <br> successfully exported!</h3>
        <div v-if="itemIdDownloaded.length" class="d-flex justify-content-center flex-column">
          <span v-for="(ele, index) in itemIdDownloaded" :key="index">{{ ele }}</span>
        </div>
      </div>
      <div class="mt-3 d-flex justify-content-center">
        <a :href="downloadInfo.downloadUrl" :download="downloadInfo.name">{{downloadInfo.name}}</a>
      </div>
    </b-modal>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import toastMixin from '@/components/common/toastMixin'
import { formatDate } from '@/shared/filters'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import { convertedPermissions as permissions } from '@/shared/utils'
import _ from 'lodash'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'

export default {
  name: 'COGSConflictsReport',
  data() {
    return {
      isLoading: true,
      permissions,
      filters: {
        channel: this.$route.query.channel || '',
        used_cog: this.$route.query.usedCog || '',
        status: this.$route.query.status || 'In Conflict',
        search: this.$route.query.search || ''
      },
      sortBy: this.$route.query.sortField || null,
      sortDesc: this.$route.query.sortDirection === 'desc',
      page: Number(this.$route.query.page) || 1,
      channelOptions: [
        { value: '', text: 'All' }
      ],
      usedCOGOptions: [
        { value: '', text: 'All' },
        { value: 'Extensiv', text: 'Extensiv' },
        { value: 'Data Central', text: 'Data Central' },
        { value: 'PF', text: 'PF' }
      ],
      statusOptions: [
        { value: 'In conflict', text: 'In Conflict' },
        { value: 'No conflict', text: 'No Conflict' },
        { value: '', text: 'All' }
      ],
      fields: [
        { key: 'select', label: '', thClass: 'align-middle text-center', tdClass: 'align-middle text-center', thStyle: { width: '40px' } },
        { key: 'sku', label: 'SKU', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'sale_ids', label: 'Sale ID', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'channel_sale_ids', label: 'Channel Sale ID', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'extensiv_cog', label: 'Extensiv COG', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'dc_cog', label: 'Data Central COG', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'pf_cog', label: 'PF COG', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'used_cog', label: 'Used COG', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'status', label: 'Status', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' },
        { key: 'created', label: 'Detected At', sortable: true, thClass: 'align-middle text-center', tdClass: 'align-middle text-center' }
      ],
      selected: [],

      // Export variables
      downloadInfo: {},
      limitItemDownloadRepresentation: 5,
      itemIdDownloaded: [],
      exportBreakTimer: null,
      isHoveringExportDropdownItem: false
    }
  },
  mixins: [ toastMixin, spapiReconnectAlertMixin, PermissionsMixin ],
  filters: {
    formatDate
  },
  computed: {
    ...mapGetters({
      cogsConflictList: 'pf/cogsConflicts/cogsConflictsList',
      cogsConflictCount: 'pf/cogsConflicts/cogsConflictsCount',
      currentCogsConflictsExportId: 'pf/cogsConflicts/currentCogsConflictsExportId',
      channelsFromStore: 'pf/cogsConflicts/channelList'
    }),
    allSelected() {
      return this.cogsConflictList.length > 0 && this.selected.length === this.cogsConflictList.length
    }
  },
  methods: {
    ...mapActions({
      getCogsConflictsList: 'pf/cogsConflicts/getCogsConflictsList',
      exportCogsConflicts: 'pf/cogsConflicts/exportCogsConflicts',
      getCogsConflictsExportPercent: 'pf/cogsConflicts/getCogsConflictsExportPercent',
      setCurrentCogsConflictsExportId: 'pf/cogsConflicts/setCurrentCogsConflictsExportId',
      getChannelsForCogsConflicts: 'pf/cogsConflicts/getChannelList'
    }),
    ...mapMutations({
      setCogsConflictsList: `pf/cogsConflicts/setCogsConflictsList`
    }),
    async fetchChannels() {
      try {
        const clientId = this.$route.params.client_id
        await this.getChannelsForCogsConflicts({ clientId })

        if (this.channelsFromStore && this.channelsFromStore.length) {
          // Keep option 'All'
          const allOption = this.channelOptions.find(option => option.value === '')

          this.channelOptions = [
            allOption,
            ...this.channelsFromStore.map(channel => ({
              value: channel.name,
              text: channel.label || channel.name
            }))
          ]
        }
      } catch (error) {
        console.error('Error fetching channels:', error)
        this.vueToast('warning', 'Could not load channels. You can still use other filters')
      }
    },
    async fetchConflicts() {
      this.isLoading = true
      try {
        const clientId = this.$route.params.client_id
        const params = { ...this.$route.query, clientId: clientId }
        await this.getCogsConflictsList(params)
      } catch (e) {
        console.error('fetchConflicts error:', e)
      }
      this.isLoading = false
    },
    toggleSelectAll(checked) {
      if (checked) {
        this.selected = this.cogsConflictList.map(item => item.id || item.sale_id || item.sku)
      } else {
        this.selected = []
      }
    },
    async onFilterChange() {
      const params = {
        channel: this.filters.channel,
        usedCog: this.filters.used_cog,
        status: this.filters.status,
        search: this.filters.search.trim(),
        page: 1
      }
      const newQuery = { ...this.$route.query, ...params }
      Object.keys(newQuery).forEach(key => {
        if ((newQuery[key] === '' && key !== 'status') || newQuery[key] == null) {
          delete newQuery[key]
        }
      })

      await this.$router.push({
        query: newQuery
      })
    },
    async handleExportConflictsSelected() {
      if (!this.selected.length) {
        this.vueToast('warning', 'Please select items to export!')
        return
      }
      this.downloadInfo = {}
      const params = {
        clientId: this.$route.params.client_id,
        payload: {
          item_ids: this.selected
        }
      }
      try {
        await this.exportCogsConflicts(params)
      } catch (err) {
        const errMessage =
          err.response && err.response.data && err.response.data.message
            ? err.response.data.message
            : 'Export failed. Please retry or contact administrator.'
        this.vueToast('error', errMessage)
      }
    },
    async handleExportConflicts() {
      this.downloadInfo = {}
      const bulkOperations = []

      // Add filters to bulk operations
      if (this.filters.channel) {
        bulkOperations.push({
          column: 'channel',
          value: this.filters.channel
        })
      }
      if (this.filters.status) {
        bulkOperations.push({
          column: 'status',
          value: this.filters.status
        })
      }
      if (this.filters.used_cog) {
        bulkOperations.push({
          column: 'used_cog',
          value: this.filters.used_cog
        })
      }
      if (this.filters.search) {
        bulkOperations.push({
          column: 'keyword',
          value: this.filters.search
        })
      }

      // If no filters, export all
      if (bulkOperations.length === 0) {
        bulkOperations.push({
          column: 'all',
          value: 'all'
        })
      }

      const params = {
        clientId: this.$route.params.client_id,
        payload: {
          bulk_operations: bulkOperations
        }
      }
      try {
        await this.exportCogsConflicts(params)
      } catch (err) {
        const errMessage =
          err.response && err.response.data && err.response.data.message
            ? err.response.data.message
            : 'Export failed. Please retry or contact administrator.'
        this.vueToast('error', errMessage)
      }
    },

    async progressiveExport() {
      clearInterval(this.exportBreakTimer)

      const params = {
        clientId: this.$route.params.client_id,
        userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
        id: this.currentCogsConflictsExportId
      }

      this.exportBreakTimer = setInterval(async () => {
        try {
          const data = await this.getCogsConflictsExportPercent(params)
          if (data.status === 'reported') {
            const metaData = _.get(data, 'meta_data', [])
            this.itemIdDownloaded = _.take(metaData, this.limitItemDownloadRepresentation)
            this.itemIdDownloaded.length < metaData.length && this.itemIdDownloaded.push('...')
            this.downloadInfo = {
              downloadUrl: data.download_url,
              name: data.name
            }
            this.$bvModal.show('download-export-modal')
            clearInterval(this.exportBreakTimer)
            this.setCurrentCogsConflictsExportId(null)
          }
        } catch (err) {
          clearInterval(this.exportBreakTimer)
          this.setCurrentCogsConflictsExportId(null)
          this.vueToast('error', 'Export failed. Please retry or contact administrator.')
        }
      }, 2000)
    },
    async goToPage(page) {
      this.isLoading = true
      this.page = page
      await this.$router.push({
        query: {
          ...this.$route.query,
          page: page
        }
      })
      this.isLoading = false
    },
    handleSortCogsConflicts(context) {
      this.sortBy = context.sortBy
      this.sortDesc = context.sortDesc ? 'desc' : 'asc'
      this.page = 1 // Reset to first page on sort change
      this.$router.push({query: { ...this.$route.query, sortDirection: this.sortDesc, sortField: this.sortBy, page: this.page }})
    }
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler(query) {
        this.filters = {
          channel: query.channel || '',
          used_cog: query.usedCog || '',
          status: query.status || '',
          search: query.search || ''
        }
        this.sortBy = query.sortField || null
        this.sortDesc = query.sortDirection === 'desc'
        this.page = Number(query.page) || 1
        this.fetchConflicts()
      }
    },
    currentCogsConflictsExportId(newVal) {
      !!newVal && this.progressiveExport()
    }
  },
  async created() {
    if (this.$route.query.status === null || this.$route.query.status === undefined) {
      const newQuery = { ...this.$route.query, status: 'In conflict' }
      await this.$router.push({
        query: newQuery
      })
    }

    await this.fetchChannels()
    await this.fetchConflicts()
  },
  mounted() {
    !!(this.currentCogsConflictsExportId) && this.progressiveExport()
  },
  beforeDestroy() {
    clearInterval(this.exportBreakTimer)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

.mb-4 {
  margin-bottom: 1.5rem;
}
.thin-spinner {
  width: 1.5rem;
  height: 1.5rem;
}
.min-width-150 {
  min-width: 150px;
}
.gap-2 {
  gap: 0.5rem;
}

.export-icon {
  @include button-icon(true, 'download.svg', 20px, 20px);

  &::before {
    background-color: #254164;
  }
}

.dropdown-icon-import {
  &:hover .import-icon::before {
    background-color: #254164;
  }

  &.hovering-menu .import-icon::before {
    background-color: #FFFFFF !important;
  }
}
.dropdown-icon-export {
  ::v-deep .dropdown-toggle {
    min-height: 40px;
  }

  &:hover .export-icon::before {
    background-color: #FFFFFF;
  }

  &.hovering-menu .export-icon::before {
    background-color: #254164;
  }
}
.font-weight-600 {
  font-weight: 600;
}

::v-deep .custom-checkbox {
  padding-left: 1rem;

  .custom-control-input {
    &:checked {
      & ~ .custom-control-label::before {
        border-color: #205FDC;
        background-color: #205FDC;
      }

      & ~ .custom-control-label::after {
        background-image: url('~@/assets/img/icon/check-icon.svg');
        background-size: 0.6rem;
      }
    }

    &:focus {
      & ~ .custom-control-label::before {
        box-shadow: 0 0 0 0.2rem rgba(32, 95, 220, 0.25);
      }

      &:not(:checked) ~ .custom-control-label::before {
        border-color: #205FDC;
      }
    }
  }

  .custom-control-label {
    &::before,
    &::after {
      left: -1rem;
    }
  }
}

::v-deep .all-checkbox {
  .custom-control-input:checked ~ .custom-control-label::after {
    background-size: 0.8rem;
  }

  .custom-control-label {
    margin: 0 0 10px 16px;
    padding: 0 0 0 10px;
    font-size: 16px;

    &::before {
      top: 0.1rem;
      width: 20px;
      height: 20px;
      border-color: #E6E8F0;
    }

    &::after {
      top: 0;
      left: -1.1rem;
      width: 1.5rem;
      height: 1.5rem;
    }
  }
}
</style>
