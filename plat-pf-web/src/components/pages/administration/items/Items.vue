<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="icon-notebook"></i> Items</strong>
          </span>
        </b-col>
        <b-col class="d-flex justify-content-end" v-if="hasPermission(permissions.admin.itemImport)"><b-button size="sm" variant="primary" @click="goImport()"><i class="icon-cloud-upload mr-1"/>Import</b-button></b-col>
      </b-row>
    </div>
    <div>
      <b-row class="justify-content-center align-items-center">
        <b-col md="6" class="mt-0 mb-4 d-flex justify-content-center filter-control">
          <div class="col-4 filter-action pr-2">
            <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Brand</span>
            <v-select
              class="v-brand-select"
              v-if="isBrandListReady"
              v-model="selectedBrand"
              :options="brandOptions"
              :filterable="false"
              @open="onOpenSelectBrand"
              @close="onCloseSelectBrand"
              placeholder="Search Brands"
              @search="(query) => (searchBrands = query)"
            >
              <template #list-footer>
                <li v-show="hasNextPageBrands" ref="load" class="loader">
                  Loading more options...
                </li>
              </template>
              <template #open-indicator="{ attributes }">
                <i class="fa fa-angle-down" v-bind="attributes"></i>
              </template>
              <span slot="no-options">
                  This brand does not exist.
                </span>
            </v-select>
          </div>
          <div class="col-4 filter-action pr-2">
            <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Sales Channel</span>
            <v-select
              class="v-channel-select"
              v-model="selectedChannel"
              :options="channelOptions"
              :filterable="false"
            >
              <template #open-indicator="{ attributes }">
                <i class="fa fa-angle-down" v-bind="attributes"></i>
              </template>
            </v-select>
          </div>
          <b-form-group class="col-7 filter-action mb-0 pr-2">
            <b-input-group class="search cancel-action group-child-margin form-search-custom">
              <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
              <b-form-input class="input-search form-search-input" v-model.trim="key" @keypress.enter="searchChange()" placeholder="Search for keyword"> </b-form-input>
              <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
              <div class="form-search-icon" @click="searchChange()">
                <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
              </div>
            </b-input-group>
          </b-form-group>
          <b-input-group-append class="filter-action pr-2 d-flex align-items-end">
            <b-button class="btn-import" variant="primary" @click="goImport()">
              Import
            </b-button>
          </b-input-group-append>
          <b-input-group-append class="filter-action d-flex align-items-end">
            <b-button class="btn-export" @click="handleExport()">
              Export
            </b-button>
          </b-input-group-append>
        </b-col>
      </b-row>
      <b-form-checkbox
        v-if="listItems.results"
        class="all-checkbox"
        :checked="listItems.results.length && listItems.results.length === selected.length"
        @change="checked => selectAll(checked)"
        :disabled="!listItems.results.length"
      >
        Select All
      </b-form-checkbox>
      <b-table class="tb-item" responsive small outlined striped head-variant="light" :items="listItems.results" :fields="itemsFields" show-empty>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no items to show.</div>
          </div>
        </template>
        <template v-slot:cell(checkboxes)="row">
          <b-form-checkbox v-model="selected" :value="row.item.id" class="checkbox"></b-form-checkbox>
        </template>
        <template v-slot:cell(channel)="row">
          <div>{{ getChannelLabel(row.item.channel) }}</div>
        </template>
        <template v-slot:cell(actions)="row">
          <div class='d-flex justify-content-center'>
            <b-dropdown right variant="secondary" class="dropdown-manage" text="Manage">
              <b-dropdown-item @click="openEditModal(row.item)" :disabled="!hasPermission(permissions.admin.itemEdit)">
                <i class="fa fa-pencil"></i>Edit
              </b-dropdown-item>
              <b-dropdown-item @click="openRemoveModal(row.item)" :disabled="!hasPermission(permissions.admin.itemDelete)">
                <i class="fa fa-trash"></i>Delete
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </template>
        <template v-slot:cell(cogs)="row">
          <ul class="mb-0 pl-3" :key="cog.id" v-for="cog in row.item.cogs">
            <li>{{cog.cog}}
              <span v-if="cog.effect_start_date ||cog.effect_end_date ">
                (<span v-if="cog.effect_start_date">from {{cog.effect_start_date | moment("MM/DD/YYYY")}}&nbsp;</span>
                  <span v-if="cog.effect_end_date">to {{cog.effect_end_date | moment("MM/DD/YYYY")}}</span>)
              </span>
              <span v-else>
                (All the time)
              </span>
            </li>
          </ul>
        </template>
      </b-table>
      <nav class="d-flex justify-content-center">
        <b-pagination @change="goToPage($event)" v-if="listItems && listItems.count > $route.query.limit" :total-rows="listItems.count || 0" :per-page="$route.query.limit" v-model="$route.query.page" hide-goto-end-buttons>
          <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
          <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
        </b-pagination>
      </nav>
    </div>
    <b-modal id="remove-item-confirm-modal" variant="danger" centered title="Please confirm">
      <div>Are you sure you want to remove this item?</div>
      <template v-slot:modal-footer>
        <b-button variant="warning" @click="handleRemoveItem()" :disabled="deleting">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
        </b-button>
        <b-button variant @click="$bvModal.hide('remove-item-confirm-modal')" :disabled="deleting">
            <i class="icon-close"></i> No
        </b-button>
      </template>
    </b-modal>
    <b-modal id="download-export-modal"
             centered
             variant="success"
             body-class="pt-0"
             :hide-footer="true"
             :hide-header="true"
             content-class="modal-download-content" >
      <div class="d-block text-center">
        <h3>The following items were successfully exported!</h3>
        <div v-if="itemIdDownloaded.length" class="d-flex justify-content-center flex-column">
          <span v-for="(ele, index) in itemIdDownloaded" :key="index">{{ ele }}</span>
        </div>
      </div>
      <div class="mt-2 d-flex justify-content-center" >
        <a :href="downloadInfo.downloadUrl" :download="downloadInfo.name">{{downloadInfo.name}}</a>
      </div>
    </b-modal>
    <EditItemModal id="edit-item-modal"/>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import toastMixin from '@/components/common/toastMixin'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import EditItemModal from '@/components/common/ItemsModals/EditItemModal.vue'
import debounce from 'lodash/debounce'
import pickBy from 'lodash/pickBy'
import identity from 'lodash/identity'
import get from 'lodash/get'
import take from 'lodash/take'

import _nav from '@/_nav'

const ALL_OPTION = {code: null, label: 'All'}

export default {
  name: 'ItemModule',
  components: {
    EditItemModal
  },
  data() {
    const headerCenter = 'align-middle text-center'
    return {
      key: '',
      itemsFields: [
        // {key: 'channel', label: 'Channel', tdClass: 'align-middle channel-col'},
        {key: 'checkboxes', label: '', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        {key: 'sku', label: 'SKU', tdClass: 'align-middle text-nowrap text-center', thClass: headerCenter},
        {key: 'upc', label: 'UPC', tdClass: 'align-middle text-center', thClass: headerCenter},
        {key: 'asin', label: 'ASIN', tdClass: 'align-middle text-center', thClass: headerCenter},
        {key: 'brand', label: 'Brand', tdClass: 'align-middle text-nowrap text-center', thClass: headerCenter},
        {key: 'title', label: 'Title', tdClass: 'align-middle text-center', thClass: headerCenter},
        {key: 'description', label: 'Description', tdClass: 'align-middle text-center', thClass: headerCenter},
        // {key: 'style', label: 'Style', tdClass: 'align-middle'},
        // {key: 'size', label: 'Size', tdClass: 'align-middle'},
        // {key: 'est_shipping_cost', label: 'Est. Ship. Cost', tdClass: 'align-middle'},
        // {key: 'est_drop_ship_cost', label: 'Est. Dropship Cost', tdClass: 'align-middle'},
        // {key: 'cogs', label: 'COGs', tdClass: 'align-middle w-50'},
        {key: 'actions', label: 'Actions', tdClass: 'align-middle', thClass: headerCenter}
      ],
      page: 1,
      limit: 10,
      itemToRemove: null,
      deleting: false,
      editData: {},
      permissions,
      isLoading: true,
      nav: _nav,
      channel: null,
      selectedChannel: ALL_OPTION,
      brandsListData: null,
      isBrandListReady: false,
      observerBrand: null,
      brandPage: 1,
      searchBrands: '',
      selectedBrand: ALL_OPTION,
      hasNextPageBrands: false,
      searchBrandOptions: {
        sortField: 'name',
        sortDirection: 'asc',
        limit: 10
      },
      selected: [],
      exportBreakTimer: null,
      currentExportPercent: 0,
      downloadInfo: {},
      itemIdDownloaded: [],
      limitItemDownloadRepresentation: 5
    }
  },
  mixins: [
    toastMixin,
    PermissionsMixin
  ],
  computed: {
    ...mapGetters({
      listItems: `pf/items/listItems`,
      channelList: 'pf/analysis/channelList',
      currentListItemExportId: 'pf/items/currentListItemExportId'
    }),
    channelOptions() {
      let channelList = []
      if (this.channelList && this.channelList.results) {
        channelList = this.channelList.results.reduce((acc, item) => {
          if (item.use_in_global_filter) {
            acc.push({label: item.label, code: item.name})
          }
          return acc
        }, [])
      }
      channelList.unshift(ALL_OPTION)
      return channelList
    },
    brandOptions() {
      return [
        ALL_OPTION, ...(this.brandsListData || []).map(brand => ({ label: brand, code: brand }))
      ]
    }
  },
  methods: {
    ...mapActions({
      getListItems: `pf/items/getListItems`,
      removeItem: `pf/items/removeItem`,
      setEditData: `pf/items/setEditData`,
      getChannelList: 'pf/analysis/getChannelList',
      fetchBrandList: 'pf/brands/fetchBrandList',
      createListItemExport: 'pf/items/createListItemExport',
      getListItemExportPercent: 'pf/items/getListItemExportPercent',
      setCurrentListItemExportId: 'pf/items/setCurrentListItemExportId'
    }),
    ...mapMutations({
      setListItems: `pf/items/setListItems`
    }),
    debounceSearchBrands: debounce(async (newVal, self) => {
      self.brandPage = 1
      const brandRes = await self.fetchBrandList({
        client_id: self.nav.clientId, key: newVal, ...self.searchBrandOptions
      })
      const results = brandRes.results
      self.brandsListData = results.map(ele => ele.name)
      // null keyword
      // back to the default list
      self.hasNextPageBrands = !newVal
    }, 500),
    getChannelLabel (channelName) {
      if (this.channelList && this.channelList.results) {
        const channel = this.channelList.results.find(channel => channel.name === channelName)
        if (channel) return channel.label
      }
      return channelName
    },
    openRemoveModal(item) {
      this.itemToRemove = item
      this.$bvModal.show('remove-item-confirm-modal')
    },
    async handleRemoveItem() {
      this.deleting = true
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          item_id: this.itemToRemove.id,
          page: this.page,
          limit: this.limit,
          key: this.key
        }
        await this.removeItem(payload)
        this.$bvModal.hide('remove-item-confirm-modal')
        this.vueToast('success', 'Removed successfully.')
      } catch {
        this.vueToast('error', 'Removing failed. Please retry or contact administrator.')
      }
      this.deleting = false
    },
    openEditModal(data) {
      let payload = { editData: data }
      this.setEditData(payload)
      this.$nextTick(() => {
        this.$bvModal.show('edit-item-modal')
      })
    },
    async handleQueryData() {
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        key: this.key,
        channel: this.$route.query.channel,
        brand: this.selectedBrand.code || ''
      }
      let data = pickBy({ ...payload }, identity)
      await this.loadingListItems(data)
    },
    async goToPage(event) {
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
    },
    goImport() {
      this.$router.push({name: 'PFStep1ImportItems', params: {module: 'ItemModule'}})
    },
    async loadingListItems(payload) {
      this.isLoading = true
      try {
        await this.getListItems(payload)
      } catch (err) {
        console.log('error', err)
      }
      this.isLoading = false
    },
    async searchChange() {
      this.isLoading = true
      this.setListItems([])
      this.$route.query.page = 1
      if (this.channel === this.$route.query.channel && this.selectedBrand === this.$route.query.brand) {
        this.handleQueryData()
      } else {
        await this.$router.push({
          query: {...this.$route.query, search: this.key, channel: this.channel, brand: JSON.stringify(this.selectedBrand)}
        })
      }
    },
    async onOpenSelectBrand() {
      if (this.hasNextPageBrands) {
        await this.$nextTick()
        this.observer.observe(this.$refs.load)
      }
    },
    onCloseSelectBrand() {
      this.observer.disconnect()
    },
    async infiniteScroll([{isIntersecting, target}]) {
      if (isIntersecting) {
        const ul = target.offsetParent
        const scrollTop = target.offsetParent.scrollTop
        this.brandPage += 1
        // update data
        const res = await this.fetchBrandList({
          client_id: this.nav.clientId, page: this.brandPage, ...this.searchBrandOptions})
        const results = res.results
        this.brandsListData = this.brandsListData.concat(results.map(ele => ele.name))
        this.hasNextPageBrands = !!res.next
        //
        await this.$nextTick()
        ul.scrollTop = scrollTop
      }
    },
    selectAll(active) {
      this.selected = active ? this.listItems.results.map(ele => ele.id) : []
    },
    async handleExport() {
      if (!this.selected.length) {
        this.vueToast('warning', 'Please select items to export!')
        return
      }
      this.downloadInfo = {}
      this.currentExportPercent = 0
      const params = {
        clientId: this.$route.params.client_id,
        payload: {
          item_ids: this.selected
        }
      }
      try {
        await this.createListItemExport(params)
      } catch (err) {
        this.vueToast('error', err.response.data.message)
      }
    },
    async progressiveExport() {
      // clear previous
      clearInterval(this.exportBreakTimer)

      const params = {
        clientId: this.$route.params.client_id,
        userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
        id: this.currentListItemExportId
      }
      this.exportBreakTimer = setInterval(async () => {
        if (this.currentExportPercent < 100) {
          try {
            const data = await this.getListItemExportPercent(params)
            this.currentExportPercent = data.progress
            if (data.status === 'reported') {
              const metaData = get(data, 'meta_data', [])
              this.itemIdDownloaded = take(metaData, this.limitItemDownloadRepresentation)
              this.itemIdDownloaded.length < metaData.length && this.itemIdDownloaded.push('...')
              this.downloadInfo = {
                downloadUrl: data.download_url,
                name: data.name
              }
              this.$bvModal.show('download-export-modal')
              // stop
              clearInterval(this.exportBreakTimer)
              this.setCurrentListItemExportId(null)
            }
          } catch (err) {
            clearInterval(this.exportBreakTimer)
            this.setCurrentListItemExportId(null)
          }
        }
      }, 2000)
    }
  },
  async created() {
    await this.getChannelList({client_id: this.nav.clientId})
    const brandRes = await this.fetchBrandList(
      {client_id: this.nav.clientId, page: 1, ...this.searchBrandOptions})
    const results = brandRes.results
    this.brandsListData = results.map(ele => ele.name)
    this.isBrandListReady = true
    this.hasNextPageBrands = !!brandRes.next

    this.key = this.$route.query.search || ''
    this.channel = this.$route.query.channel || null
    this.selectedChannel = this.$route.query.channel ? { code: this.channel, label: this.getChannelLabel(this.channel) } : ALL_OPTION
    this.selectedBrand = this.$route.query.brand ? JSON.parse(this.$route.query.brand) : ALL_OPTION

    if (this.$route.query.limit && this.$route.query.page) await this.handleQueryData()
    else {
      await this.$router.push({
        params: { client_id: this.nav.clientId },
        query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.key, brand: JSON.stringify(this.selectedBrand) }
      })
    }
  },
  watch: {
    async $route(to, from) {
      this.key = this.$route.query.search || ''
      this.channel = this.$route.query.channel || null
      await this.handleQueryData()
    },
    async searchBrands(newVal) {
      await this.debounceSearchBrands(newVal, this)
    },
    selectedBrand(newVal) {
      this.$router.push({query: {page: this.$route.query.page, limit: this.$route.query.limit, brand: JSON.stringify(this.selectedBrand), channel: this.channel, search: this.key}})
    },
    selectedChannel(newVal) {
      this.$router.push({query: {page: this.$route.query.page, limit: this.$route.query.limit, channel: newVal.code, brand: JSON.stringify(this.selectedBrand), search: this.key}})
    },
    currentListItemExportId(newVal) {
      !!newVal && this.progressiveExport()
    }
  },
  mounted() {
    /**
     *
     * brand name select view
     * You could do this directly in data(), but since these docs
     * are server side rendered, IntersectionObserver doesn't exist
     * in that environment, so we need to do it in mounted() instead.
     */
    this.observer = new IntersectionObserver(this.infiniteScroll)

    // export
    !!(this.currentListItemExportId) && this.progressiveExport()
  },
  beforeDestroy() {
    clearInterval(this.exportBreakTimer)
  }
}
</script>

<style lang="scss" scoped>
  @import '@/assets/scss/button.scss';
  ::v-deep .channel-col {
    width: 30%
  }

  .thin-spinner {
    border-width: .14em;
  }

  .btn-import,
  .btn-export {
    height: 36px;
  }

  .btn-import {
    @include button-icon(true, 'upload.svg', 20px, 20px);
  }

  .btn-export {
    @include button-icon(true, 'download-blue.svg', 20px, 20px);
  }

  .tb-item {
    overflow: auto;

    ::v-deep thead {
      height: 56px;
    }
    ::v-deep table {
      border-collapse: separate;
      border-spacing: 0;
      border-radius: 4px;
      overflow: hidden;
    }
  }

  .filter-action {
    padding-left: 0;
  }

  .filter-control {
    height: 60px;
    ::v-deep select, input {
      min-height: unset !important;
      height: 36px !important;
    }
    .v-brand-select, .v-channel-select {
      border-color: #254164;
      ::v-deep .vs__dropdown-toggle {
        border-radius: 1px;
        height: 36px;
      }
      ::v-deep .vs__actions .vs__clear {
        display: none;
      }
    }

    .loader {
      text-align: center;
      margin-top: 10px;
      margin-bottom: 5px;
    }
  }

  ::v-deep .modal-download-content {
    width: 500px;
    //height: 157px;
    padding: 30px;

    a {
      color: black;
    }
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
    padding-left: 28px !important;
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
</style>
