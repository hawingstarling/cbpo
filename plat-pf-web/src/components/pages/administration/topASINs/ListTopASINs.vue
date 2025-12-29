<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="icon-flag"></i> Top ASINs</strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <div>
      <b-row class="justify-content-center align-items-center">
        <b-col md="8" class="mt-0 d-flex justify-content-center channel-filter-group">
          <div class="pr-2 col-3">
            <div class="d-flex flex-wrap">
              <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Sales Channel</span>
              <b-form-select class="custom-form-item"
                v-model="channel"
                :options="channelOptions"
                @change="handleSearchChange()"
              />
            </div>
          </div>
          <b-form-group class="mb-0 d-flex flex-wrap">
            <b-input-group class="search cancel-action form-search-custom">
              <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
              <b-form-input class="input-search form-search-input custom-form-item" v-model.trim="key" @keypress.enter="searchChange()" placeholder="Search for keywords">
              </b-form-input>
              <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
              <div class="form-search-icon" @click="searchChange()">
                <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
              </div>
            </b-input-group>
          </b-form-group>
          <div class="pl-2 col-4 d-flex align-items-end">
            <b-dropdown v-if="hasPermission(permissions.topASINs.import)" right variant="primary" class="dropdown-manage dropdown-icon-import mr-2"
              :class="{ 'hovering-menu': isHoveringImportDropdownItem }">
              <template #button-content>
                <span class="import-icon"></span>Import
              </template>
              <div @mouseover="isHoveringImportDropdownItem = true" @mouseleave="isHoveringImportDropdownItem = false">
                <b-dropdown-item @click="goImport()">
                  Import to Add/Update
                </b-dropdown-item>
                <b-dropdown-item @click="goImportToDelete()">
                  Import to Delete
                </b-dropdown-item>
              </div>
            </b-dropdown>
            <b-dropdown v-if="hasPermission(permissions.topASINs.export)" right class="dropdown-manage dropdown-icon-export"
              :class="{ 'hovering-menu': isHoveringExportDropdownItem }">
              <template #button-content>
                <span class="export-icon"></span>Export
              </template>
              <div @mouseover="isHoveringExportDropdownItem = true" @mouseleave="isHoveringExportDropdownItem = false">
                <b-dropdown-item @click="handleExportTopASINsSelected()">
                  Export Selected
                </b-dropdown-item>
                <b-dropdown-item @click="handleExportTopASINs()">
                  Export All
                </b-dropdown-item>
              </div>
            </b-dropdown>
          </div>
        </b-col>
      </b-row>
      <b-form-checkbox
        class="all-checkbox"
        :checked="topASINsList && topASINsList.results && topASINsList.results.length && topASINsList.results.length === selectedForExport.length"
        @change="checked => selectAll(checked)"
        :disabled="!topASINsList || !topASINsList.results || !topASINsList.results.length"
      >
        Select All
      </b-form-checkbox>
      <b-table class="none-table-border" @sort-changed="handleSortFedex" outlined striped head-variant="light" :items="(topASINsList && topASINsList.results) ? topASINsList.results : []" :fields="filteredListOfFields" show-empty>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no Top ASINs to show.</div>
          </div>
        </template>
        <template v-slot:cell(checkboxes)="row">
          <b-form-checkbox v-model="selectedForExport" :value="row.item.id" class="checkbox"></b-form-checkbox>
        </template>
        <template v-slot:cell(actions)="row">
          <div class="d-flex justify-content-center">
            <b-dropdown right variant="secondary" class="dropdown-manage" text="Manage">
              <b-dropdown-item v-if="hasPermission(permissions.topASINs.edit)" @click="openEditTopASIN(row.item)">
                <i class="fa fa-pencil"></i>Edit
              </b-dropdown-item>
              <b-dropdown-item v-if="hasPermission(permissions.topASINs.delete)" @click="openConfirmModalDelete(row.item)">
                <i class="fa fa-trash-o"></i>Delete
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </template>
      </b-table>
      <nav class="d-flex justify-content-center">
        <b-pagination class="btn-pagination-width" @change="goToPage($event)" v-if="topASINsList && topASINsList.count > $route.query.limit" :total-rows="topASINsList.count || 0" :per-page="$route.query.limit" v-model="$route.query.page" prev-text="Prev" next-text="Next" hide-goto-end-buttons>
          <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
          <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
        </b-pagination>
      </nav>
    </div>
    <EditTopASINs :item="itemOfEditModal" ref="editTopASIN" @handleEditTopASIN="handleEditTopASIN" :channelOfEditModal="channelOfEditModal"/>
    <b-modal id="confirm-delete-record" variant="danger" centered title="Please confirm">
      <div>Are you sure you want to delete this item?</div>
      <template v-slot:modal-footer>
        <b-button variant="warning" @click="handleDeleteRecord" :disabled="deleting">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
        </b-button>
        <b-button variant @click="$bvModal.hide('confirm-delete-record')" :disabled="deleting">
            <i class="icon-close"></i> No
        </b-button>
      </template>
    </b-modal>
    <b-modal id="download-export-modal"
      centered
      variant="success"
      body-class="p-4"
      :hide-footer="true"
      :hide-header="true"
      content-class="modal-download-content"
    >
      <div class="d-block text-center">
        <h3>The following items were <br> successfully exported!</h3>
        <div v-if="itemIdDownloaded.length" class="d-flex justify-content-center flex-column">
          <span v-for="(ele, index) in itemIdDownloaded" :key="index">{{ ele }}</span>
        </div>
      </div>
      <div class="mt-3 d-flex justify-content-center" >
        <a :href="downloadInfo.downloadUrl" :download="downloadInfo.name">{{downloadInfo.name}}</a>
      </div>
    </b-modal>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import toastMixin from '@/components/common/toastMixin'
import _ from 'lodash'
import EditTopASINs from '@/components/pages/administration/topASINs/EditTopASINs'

export default {
  name: 'Top-ASINs',
  components: {
    EditTopASINs
  },
  data() {
    return {
      permissions,
      listOfFields: [
        {key: 'checkboxes', label: '', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        {key: 'channel', label: 'Channel', tdClass: 'align-middle text-center item-column', thClass: 'align-middle text-center'},
        {key: 'parent_asin', label: 'Parent ASIN', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        {key: 'child_asin', label: 'Child ASIN', tdClass: 'align-middle text-center item-column', thClass: 'align-middle text-center'},
        {key: 'segment', label: 'Segment', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        {key: 'actions', label: 'Actions', tdClass: 'align-middle', thClass: 'align-middle text-center border-top-right-rad'}
      ],
      key: '',
      isLoading: true,
      channel: null,
      channelOfUpdateSalesModal: '',
      itemIdOfForDelete: null,
      page: 1,
      limit: 10,
      channelOfEditModal: '',
      itemOfEditModal: {},
      deleting: false,
      // Variable for export function
      selectedForExport: [],
      downloadInfo: {},
      limitItemDownloadRepresentation: 5,
      itemIdDownloaded: [],
      exportBreakTimer: null,
      isHoveringImportDropdownItem: false,
      isHoveringExportDropdownItem: false
    }
  },
  mixins: [ PermissionsMixin, toastMixin ],
  computed: {
    ...mapGetters({
      topASINsList: `pf/topAsins/topASINsList`,
      channelList: 'pf/analysis/channelList',
      currentListTopASINsExportId: `pf/topAsins/currentListTopASINsExportId`
    }),
    // Filter table fields based on permissions
    filteredListOfFields() {
      let fields = [...this.listOfFields]

      // Hide actions column if user has neither edit nor delete permission
      if (!this.hasPermission(this.permissions.topASINs.edit) && !this.hasPermission(this.permissions.topASINs.delete)) {
        fields = fields.filter(field => field.key !== 'actions')
      }

      return fields
    },
    channelOptions() {
      let channelList = []
      if (this.channelList && this.channelList.results) {
        channelList = this.channelList.results.reduce((acc, item) => {
          if (item.use_in_global_filter) {
            acc.push({ text: item.label, value: item.name })
          }
          return acc
        }, [])
      }
      channelList.unshift({text: 'All', value: null})
      return channelList
    }
  },
  methods: {
    ...mapActions({
      getTopASINsList: `pf/topAsins/getTopASINsList`,
      editTopASIN: `pf/topAsins/editTopASIN`,
      getChannelList: 'pf/analysis/getChannelList',
      exportTopASINs: `pf/topAsins/exportTopASINs`,
      deleteTopASIN: `pf/topAsins/deleteTopASIN`,
      getListTopASINsExportPercent: `pf/topAsins/getListTopASINsExportPercent`,
      setCurrentListTopASINsExportId: `pf/topAsins/setCurrentListTopASINsExportId`
    }),
    ...mapMutations({
      setTopASINsList: `pf/topAsins/setTopASINsList`
    }),
    searchChange() {
      if (this.$route.query.search !== this.key) this.handleSearchChange()
    },
    async handleSearchChange() {
      this.isLoading = true
      this.setTopASINsList([])
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.key, channel: this.channel } })
    },
    openConfirmModalDelete(item) {
      // Check delete permission before proceeding
      if (!this.hasPermission(this.permissions.topASINs.delete)) {
        this.$toasted.global.error('You do not have permission to delete Top ASINs')
        return
      }
      this.itemIdOfForDelete = item && item.id ? item.id : null
      this.$bvModal.show('confirm-delete-record')
    },
    openEditTopASIN(item) {
      // Check edit permission before proceeding
      if (!this.hasPermission(this.permissions.topASINs.edit)) {
        this.$toasted.global.error('You do not have permission to edit Top ASINs')
        return
      }
      this.itemOfEditModal = _.cloneDeep(item)
      this.channelOfEditModal = item.channel
      this.itemOfEditModal.channel = item.channel
      this.$nextTick(() => {
        this.$bvModal.show('edit-top-asin-setting-modal')
      })
    },
    async goToPage(event) {
      this.isLoading = true
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
      this.isLoading = false
    },
    goImport() {
      // Check import permission before proceeding
      if (!this.hasPermission(this.permissions.topASINs.import)) {
        this.$toasted.global.error('You do not have permission to import Top ASINs')
        return
      }
      this.$router.push({name: 'PFStep1ImportTopASIN', params: {module: 'TopASINs'}})
    },
    goImportToDelete() {
      // Check import permission before proceeding
      if (!this.hasPermission(this.permissions.topASINs.import)) {
        this.$toasted.global.error('You do not have permission to import Top ASINs')
        return
      }
      this.$router.push({name: 'PFStep1ImportToDeleteTopASIN', params: {module: 'TopASINsDelete'}})
    },
    async handleExportTopASINs() {
      // Check export permission before proceeding
      if (!this.hasPermission(this.permissions.topASINs.export)) {
        this.$toasted.global.error('You do not have permission to export Top ASINs')
        return
      }
      this.downloadInfo = {}
      this.currentExportPercent = 0
      const params = {
        clientId: this.$route.params.client_id,
        payload:
        {
          bulk_operations: [{
            column: 'all',
            value: 'all'
          }]
        }
      }
      try {
        await this.exportTopASINs(params)
      } catch (err) {
        const errMessage =
          err.response && err.response.data && err.response.data.message
            ? err.response.data.message
            : 'Export failed. Please retry or contact administrator.'
        this.vueToast('error', errMessage)
      }
    },
    async handleExportTopASINsSelected() {
      // Check export permission before proceeding
      if (!this.hasPermission(this.permissions.topASINs.export)) {
        this.$toasted.global.error('You do not have permission to export Top ASINs')
        return
      }
      if (!this.selectedForExport.length) {
        this.vueToast('warning', 'Please select items to export!')
        return
      }
      this.downloadInfo = {}
      this.currentExportPercent = 0
      const params = {
        clientId: this.$route.params.client_id,
        payload: {
          item_ids: this.selectedForExport
        }
      }
      try {
        await this.exportTopASINs(params)
      } catch (err) {
        const errMessage =
          err.response && err.response.data && err.response.data.message
            ? err.response.data.message
            : 'Export failed. Please retry or contact administrator.'
        this.vueToast('error', errMessage)
      }
    },
    async handleQueryData() {
      this.isLoading = true
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        clientId: this.$route.params.client_id,
        // Default sort
        sortDirection: this.$route.query.sortDirection || 'desc',
        sortField: this.$route.query.sortField || 'created',
        key: this.$route.query.search,
        channel: this.$route.query.channel
      }
      let data = _.pickBy({ ...payload }, _.identity)
      await this.getTopASINsList(data)
      this.isLoading = false
    },
    async handleEditTopASIN(itemEdit) {
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          id: itemEdit.id,
          item_edit: itemEdit
        }
        await this.editTopASIN(payload)
        this.vueToast('success', 'Item has been saved.')
        this.$bvModal.hide('edit-top-asin-setting-modal')
        this.isLoading = true
        await this.handleQueryData()
        this.isLoading = false
      } catch (err) {
        this.vueToast('error', 'Saving failed. Please retry or contact administrator.')
      }
    },
    async handleDeleteRecord() {
      this.deleting = true
      try {
        await this.deleteTopASIN({clientId: this.$route.params.client_id, id: this.itemIdOfForDelete})
        this.itemIdOfForDelete = null
        await this.handleQueryData()
        this.$bvModal.hide('confirm-delete-record')
        this.vueToast('success', 'Delete the record successfully!')
      } catch (err) {
        this.vueToast('error', 'Deleting failed. Please retry or contact administrator.')
      }
      this.deleting = false
    },
    selectAll(active) {
      this.selectedForExport = active ? this.topASINsList.results.map(item => item.id) : []
    },
    async progressiveExport() {
      // clear previous
      clearInterval(this.exportBreakTimer)

      const params = {
        clientId: this.$route.params.client_id,
        userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
        id: this.currentListTopASINsExportId
      }
      this.exportBreakTimer = setInterval(async () => {
        if (this.currentExportPercent < 100) {
          try {
            const data = await this.getListTopASINsExportPercent(params)
            this.currentExportPercent = data.progress
            if (data.status === 'reported') {
              const metaData = _.get(data, 'meta_data', [])
              this.itemIdDownloaded = _.take(metaData, this.limitItemDownloadRepresentation)
              this.itemIdDownloaded.length < metaData.length && this.itemIdDownloaded.push('...')
              this.downloadInfo = {
                downloadUrl: data.download_url,
                name: data.name
              }
              this.$bvModal.show('download-export-modal')
              // stop
              clearInterval(this.exportBreakTimer)
              this.setCurrentListTopASINsExportId(null)
            }
          } catch (err) {
            clearInterval(this.exportBreakTimer)
            this.setCurrentListTopASINsExportId(null)
          }
        }
      }, 2000)
    },
    handleSortFedex(context) {
      this.$router.push({query: { ...this.$route.query, sortDirection: context.sortDesc ? 'desc' : 'asc', sortField: context.sortBy }})
    }
  },
  async created() {
    await this.$router.push({
      params: { client_id: this.$route.params.client_id },
      query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search || this.key, channel: this.$route.query.channel || this.channel }
    })
    this.key = this.$route.query.search || this.key
    this.channel = this.$route.query.channel || this.channel
    await this.getChannelList({client_id: this.$route.params.client_id})
    this.handleQueryData()
  },
  watch: {
    async $route(to, from) {
      this.key = this.$route.query.search || ''
      await this.handleQueryData()
    },
    currentListTopASINsExportId(newVal) {
      !!newVal && this.progressiveExport()
    }
  },
  mounted() {
    // export
    !!(this.currentListTopASINsExportId) && this.progressiveExport()
  },
  beforeDestroy() {
    clearInterval(this.exportBreakTimer)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

$main-color: #0645AD;

.card-body {
  padding: 1.25rem 2.25rem;
}

.thin-spinner {
  border-width: .14em;
}

::v-deep .right-header {
  width: 128px;
  height: 60px;
  padding: 8px;
  text-align: right;
}

.dropdown-icon-export, .dropdown-icon-import {
  height: 36px;
}

::v-deep .after-bar-red {
  position: relative;
  &::after {
    content: '';
    background-color: #FF9A9A;
    position: absolute;
    top: 0;
    left: 0;
    width: 8px;
    height: 100%;
  }
}

::v-deep .after-bar-green {
  position: relative;
  &::after {
    content: '';
    background-color: #91E4AB;
    position: absolute;
    top: 0;
    left: 0;
    width: 8px;
    height: 100%;
  }
}

.none-table-border {
  border: none !important;
}

::v-deep .table thead th {
  border-top: none;
}

::v-deep .table tbody {
  tr:last-child {
    td:first-child:after {
      border-bottom-left-radius: 3px;
    }
    td:last-child {
      border-bottom-right-radius: 3px;
    }
  }
}

::v-deep .border-top-left-rad {
  border-top-left-radius: 5px;
}
::v-deep .border-top-right-rad {
  border-top-right-radius: 5px;
}

::v-deep .table tbody {
  .item-column div {
    color: $main-color;
    cursor: pointer;
  }

  tr:hover .item-column div {
    color: fade-out($main-color, 0.5);

    &:hover {
      color: $main-color;
    }
  }
}

.channel-filter-group {
  height: 60px;
}
::v-deep .custom-form-item {
  min-height: unset !important;
  height: 36px;
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
    margin: 0 0 10px 20px;
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
.form-search-custom {
  .form-search-input {
    padding-right: 30px !important;
  }
}

::v-deep #update-sales-modal {
  .custom-control-label {
    padding-left: 6px;
  }
}

.icon-export,
.icon-import {
  margin-top: 4px !important;
  display: inline-flex;
  align-items: center;

  &::before {
    flex-shrink: 0;
  }
}

.import-icon {
  @include button-icon(true, 'upload.svg', 20px, 20px);

  &::before {
    background-color: #FFFFFF;
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

.export-icon {
  @include button-icon(true, 'download.svg', 20px, 20px);

  &::before {
    background-color: #254164;
  }
}

.dropdown-icon-export {
  &:hover .export-icon::before {
    background-color: #FFFFFF;
  }

  &.hovering-menu .export-icon::before {
    background-color: #254164;
  }
}
</style>
