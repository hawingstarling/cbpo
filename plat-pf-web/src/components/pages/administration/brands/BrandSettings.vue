<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="icon-flag"></i> Brand Settings</strong>
          </span>
        </b-col>
        <!-- <b-col class="d-flex justify-content-end">
          <b-button v-if="hasPermission(permissions.brand.export)" class="mr-1" size="sm" variant="primary" @click="handelExportBrandSettings()"><i class="icon-cloud-download mr-1"/>Export</b-button>
          <b-button v-if="hasPermission(permissions.brand.import)" size="sm" variant="primary" @click="goImport()"><i class="icon-cloud-upload mr-1"/>Import</b-button>
        </b-col> -->
      </b-row>
    </div>
    <div>
      <b-row class="justify-content-center align-items-center">
        <b-col md="8" class="mt-0 d-flex justify-content-center brand-filter-group">
          <div class="pr-2 col-3">
            <div class="d-flex flex-wrap">
              <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Sales Channel</span>
              <b-form-select class="custom-form-brand"
                v-model="channel"
                :options="channelOptions"
                @change="handleSearchChange()"
              />
            </div>
          </div>
          <b-form-group class="mb-0 d-flex flex-wrap">
            <b-input-group class="search cancel-action form-search-custom">
              <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
              <b-form-input class="input-search form-search-input custom-form-brand" v-model.trim="key" @keypress.enter="searchChange()" placeholder="Search for Brand, Fulfillment">
              </b-form-input>
              <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
              <div class="form-search-icon" @click="searchChange()">
                <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
              </div>
            </b-input-group>
          </b-form-group>
          <div class="pl-2 col-4 d-flex align-items-end">
            <b-button v-if="hasPermission(permissions.brand.import)" class="btn-import mr-2" variant="primary" @click="goImport()">Import</b-button>
            <b-button v-if="hasPermission(permissions.brand.export)" class="btn-export mr-2" variant="primary" @click="handelExportBrandSettings()">Export</b-button>
            <b-button class="btn-add-brand" @click="openAddBrandModal()">Add Brand</b-button>
          </div>
        </b-col>
      </b-row>
      <b-form-checkbox
        class="all-checkbox"
        :checked="brandSettingList && brandSettingList.results && brandSettingList.results.length && brandSettingList.results.length === selected.length"
        @change="checked => selectAll(checked)"
        :disabled="!brandSettingList || !brandSettingList.results || !brandSettingList.results.length"
      >
        Select All
      </b-form-checkbox>
      <b-table class="none-table-border" outlined striped head-variant="light" :items="brandSettingList.results" :fields="listOfBrandFields" show-empty>
        <template v-slot:head(est_first_item_shipcost)="row">
          <span>{{ row.label }}</span>
          <span :id="`question-tooltip-${row.column}`" class="ml-1" v-html="tooltipInfo[0].trigger">
          </span>
          <b-popover :target="`question-tooltip-${row.column}`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[0].text"></div>
          </b-popover>
        </template>
        <template v-slot:head(est_add_item_shipcost)="row">
          <span>{{ row.label }}</span>
          <span :id="`question-tooltip-${row.column}`" class="ml-1" v-html="tooltipInfo[1].trigger">
          </span>
          <b-popover :target="`question-tooltip-${row.column}`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[1].text"></div>
          </b-popover>
        </template>
        <template v-slot:head(po_dropship_cost)="row">
          <span>{{ row.label }}</span>
          <span :id="`question-tooltip-${row.column}`" class="ml-1" v-html="tooltipInfo[2].trigger">
          </span>
          <b-popover :target="`question-tooltip-${row.column}`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[2].text"></div>
          </b-popover>
        </template>
        <template v-slot:head(est_fba_fees)="row">
          <span>{{ row.label }}</span>
          <span :id="`question-tooltip-${row.column}`" class="ml-1" v-html="tooltipInfo[3].trigger">
          </span>
          <b-popover :target="`question-tooltip-${row.column}`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[3].text"></div>
          </b-popover>
        </template>
        <template v-slot:head(est_unit_inbound_freight_cost)="row">
          <span>{{ row.label }}</span>
          <span :id="`question-tooltip-${row.column}`" class="ml-1" v-html="tooltipInfo[4].trigger">
          </span>
          <b-popover :target="`question-tooltip-${row.column}`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[4].text"></div>
          </b-popover>
        </template>
        <template v-slot:head(est_unit_outbound_freight_cost)="row">
          <span>{{ row.label }}</span>
          <span :id="`question-tooltip-${row.column}`" class="ml-1" v-html="tooltipInfo[5].trigger">
          </span>
          <b-popover :target="`question-tooltip-${row.column}`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[5].text"></div>
          </b-popover>
        </template>
        <template v-slot:head(mfn_formula)="row">
          <span>{{ row.label }}</span>
          <span :id="`question-tooltip-${row.column}`" class="ml-1" v-html="tooltipInfo[6].trigger">
          </span>
          <b-popover :target="`question-tooltip-${row.column}`" triggers="hover" placement="bottom">
            <div v-html="tooltipInfo[6].text"></div>
          </b-popover>
        </template>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no brands to show.</div>
          </div>
        </template>
        <template v-slot:cell(channel)="row">
          <div>{{row.item.channel && row.item.channel.label ? row.item.channel.label: null}}</div>
        </template>
        <template v-slot:cell(checkboxes)="row">
          <b-form-checkbox v-model="selected" :value="row.item.id" class="checkbox"></b-form-checkbox>
        </template>
        <template v-slot:cell(brand)="row">
          <div
            @click="$router.push({
              name: 'PFItems',
              params: { client_id: $route.params.client_id },
              query: { brand: row.item.brand.name }
            })"
          >
            {{row.item.brand && row.item.brand.name ? row.item.brand.name : '&lt;Default&gt;'}}
          </div>
        </template>
        <template v-slot:cell(actions)=row>
          <div class="d-flex justify-content-center">
            <b-dropdown right variant="secondary" class="dropdown-manage" text="Manage">
              <b-dropdown-item @click="openEditBrandSettingModal(row.item)" :disabled="!hasPermission(permissions.brand.edit)">
                <i class="fa fa-pencil"></i>Edit
              </b-dropdown-item>
              <!-- <b-dropdown-item :disabled="!hasPermission(permissions.brand.delete)">
                <i class="fa fa-trash"></i>Delete
              </b-dropdown-item>
              <b-dropdown-item :disabled="!hasPermission(permissions.brand.updateItems)">
                <i class="fa fa-cog"></i>Update Items
              </b-dropdown-item> -->
              <b-dropdown-item @click="openUpdateSalesModal(row.item)" :disabled="!hasPermission(permissions.brand.updateSales)">
                <i class="fa fa-cog"></i>Update Sales
              </b-dropdown-item>
              <b-dropdown-item @click="openConfirmModalDeleteBrand(row.item)" :disabled="!hasPermission(permissions.brand.delete)">
                <i class="fa fa-trash-o"></i>Delete Brand
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </template>
      </b-table>
      <nav class="d-flex justify-content-center">
        <b-pagination class="btn-pagination-width" @change="goToPage($event)" v-if="brandSettingList && brandSettingList.count > $route.query.limit" :total-rows="brandSettingList.count || 0" :per-page="$route.query.limit" v-model="$route.query.page" prev-text="Prev" next-text="Next" hide-goto-end-buttons>
          <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
          <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
        </b-pagination>
      </nav>
    </div>
    <b-modal
      id="update-sales-modal"
      centered
      size="xl">
      <UpdateSalesModal ref="updateSaleModal" @checkCountUpdateSales="checkCountUpdateSales" :brand="brandOfUpdateSalesModal" :channel="channelOfUpdateSalesModal"/>
      <template v-slot:modal-header>
        <div class="d-flex justify-content-center w-100">
          <h4 class="mb-0">Brand Estimated Ship Cost - Update Sales</h4>
        </div>
      </template>
      <template v-slot:modal-footer>
        <b-button :disabled="countUpdateSales['count-sales'] === 0" @click="handleUpdate" variant="primary">Update ({{countUpdateSales['count-sales']}})</b-button>
      </template>
    </b-modal>
    <b-modal
      id="edit-brand-setting-modal"
      centered
      size="lg">
      <EditBrandSettingModal :item="itemOfEditModal" :tooltipInfo="tooltipInfo" ref="editBrandSetting"/>
      <template v-slot:modal-header>
        <div class="d-flex justify-content-center w-100">
          <h4 class="mb-0">Edit for {{brandOfEditModal}} on the channel {{channelOfEditModal.label}}</h4>
        </div>
      </template>
      <template v-slot:modal-footer>
        <b-button @click="handleEditBrandSetting" variant="primary">Update</b-button>
      </template>
    </b-modal>
    <b-modal
        id="add-brand-settings"
        title="Add Brand"
        centered
        size="lg"
    >
        <EditBrandSettingModal :item="itemOfEditModal" :tooltipInfo="tooltipInfo" ref="refAddBrandSetting"/>
        <template v-slot:modal-footer>
          <div class="w-100">
              <b-button class="float-right" variant="primary" @click="handleAddBrand">Save</b-button>
              <b-button class="float-left" @click="$bvModal.hide('add-brand-settings')">Cancel</b-button>
          </div>
        </template>
    </b-modal>
    <b-modal
        id="confirm-delete-brand"
        title="Delete Brand"
        centered
    >
      <p class="mb-0">Do you want to delete this brand?</p>
        <template v-slot:modal-footer>
          <div class="w-100">
            <b-button variant="outline-dark"  @click="$bvModal.hide('confirm-delete-brand')">Cancel</b-button>
            <b-button variant="danger" class="float-right"  @click="handleDeleteBrand">Delete</b-button>
          </div>
        </template>
    </b-modal>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import moment from 'moment'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import toastMixin from '@/components/common/toastMixin'
import _ from 'lodash'

import UpdateSalesModal from '@/components/pages/administration/brands/UpdateSalesModal'
import EditBrandSettingModal from '@/components/pages/administration/brands/EditBrandSettingModal'

export default {
  name: 'Brands',
  components: {
    UpdateSalesModal,
    EditBrandSettingModal
  },
  data() {
    return {
      permissions,
      listOfBrandFields: [
        {key: 'channel', label: 'Channel', tdClass: 'fmtObsolete', thClass: 'align-middle text-center border-top-left-rad'},
        {key: 'checkboxes', label: '', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        {key: 'brand', label: 'Brand', tdClass: 'align-middle text-center brand-column', thClass: 'align-middle text-center'},
        {key: 'segment', label: 'Segment', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        {key: 'est_first_item_shipcost', label: 'Est. 1st Item Shipcost', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: 'fmtRowValCurrency'},
        {key: 'est_add_item_shipcost', label: 'Est. Add. Item Shipcost', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: 'fmtRowValCurrency'},
        {key: 'po_dropship_method', label: 'PO Dropship Method', tdClass: 'align-middle text-right', thClass: 'align-middle right-header'},
        {key: 'po_dropship_cost', label: 'PO Dropship', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: (value, _key, item) => item.po_dropship_method === 'Cost' ? this.fmtRowValCurrency(value) : this.fmtPercent(value)},
        {key: 'est_unit_inbound_freight_cost', label: 'Est. Unit Inbound Freight Cost', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: 'fmtRowValCurrency'},
        {key: 'est_unit_outbound_freight_cost', label: 'Est. Unit Outbound Freight Cost', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: 'fmtRowValCurrency'},
        {key: 'est_fba_fees', label: 'Estimated FBA Fees', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: 'fmtRowValCurrency'},
        {key: 'mfn_formula', label: 'MFN Formula', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        {key: 'add_user_provided_cost', label: 'Add. User-Provided Cost', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: 'fmtRowValCurrency'},
        {key: 'add_user_provided_method', label: 'Add. User-Provided Method', tdClass: 'align-middle text-right', thClass: 'align-middle right-header', formatter: 'fmtRowValCurrency'},
        {key: 'actions', label: 'Actions', tdClass: 'align-middle', thClass: 'align-middle text-center border-top-right-rad'}
      ],
      key: '',
      isLoading: true,
      channel: null,
      brandOfUpdateSalesModal: '',
      channelOfUpdateSalesModal: '',
      brandIdOfUpdateSalesModal: '',
      brandIdOfForDelete: null,
      page: 1,
      limit: 10,
      brandOfEditModal: '',
      channelOfEditModal: '',
      itemOfEditModal: {},
      tooltipInfo: [
        {
          name: 'est_first_item_shipcost',
          trigger: '<i class="fa fa-question-circle" aria-hidden="true"></i>',
          text: `This amount is deducted on every MFN sale with items of this brand, through the Shipping Cost field. As an estimate (shown in bold), it is ideally overriden later by invoices, imports.`
        },
        {
          name: 'est_add_item_shipcost',
          trigger: '<i class="fa fa-question-circle" aria-hidden="true"></i>',
          text: `This amount is deducted on every MFN sale with items of this brand, through the Shipping Cost field, but only for every additional item after the first one. It has no effect on sales of just one unit. As an estimate (shown in bold), it is ideally overriden later by invoices, imports.`
        },
        {
          name: 'po_dropship_cost',
          trigger: '<i class="fa fa-question-circle" aria-hidden="true"></i>',
          text: `This amount is deducted on every MFN sale with items of this brand, through the Dropship Fee field. As an estimate (shown in bold), it is ideally overriden later by invoices, imports.`
        },
        {
          name: 'est_fba_fees',
          trigger: '<i class="fa fa-question-circle" aria-hidden="true"></i>',
          text: `This amount is deducted on every FBA sale with items of this brand, through the Shipping Cost Fee field. As an estimate (shown in bold), it is ideally overriden later by invoices, imports.`
        },
        {
          name: 'est_unit_inbound_freight_cost',
          trigger: '<i class="fa fa-question-circle" aria-hidden="true"></i>',
          text: `This amount is deducted on every MFN sale with items of this brand, through the Inbound Freight Cost Fee field. As an estimate (shown in bold), it is ideally overriden later by invoices, imports.`
        },
        {
          name: 'est_unit_outbound_freight_cost',
          trigger: '<i class="fa fa-question-circle" aria-hidden="true"></i>',
          text: `This amount is deducted on every MFN sale with items of this brand, through the Outbound Freight Cost Fee field. As an estimate (shown in bold), it is ideally overriden later by invoices, imports.`
        },
        {
          name: 'mfn_formula',
          trigger: '<i class="fa fa-question-circle" aria-hidden="true"></i>',
          text: `This determines how each non-prime MFN sale should be calculated in terms of shipping costs and other fees. Please choose the best fulfillment that matches most or all of that brand's MFN fulfillment.`
        }
      ],
      brandName: '',
      selected: []
    }
  },
  mixins: [ PermissionsMixin, toastMixin ],
  computed: {
    ...mapGetters({
      brandSettingList: `pf/brands/brandSettingList`,
      countUpdateSales: `pf/brands/countUpdateSales`,
      channelList: 'pf/analysis/channelList'
    }),
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
      channelList.push({text: 'All', value: null})
      return channelList
    }
  },
  methods: {
    ...mapActions({
      getBrandSettingList: `pf/brands/getBrandSettingList`,
      postBrandSettingUpdateSales: `pf/brands/postBrandSettingUpdateSales`,
      postCountUpdateSales: `pf/brands/postCountUpdateSales`,
      editBrandSetting: `pf/brands/editBrandSetting`,
      getChannelList: 'pf/analysis/getChannelList',
      exportBrandSetting: `pf/brands/exportBrandSetting`,
      fetchAddBrandSetting: `pf/brands/fetchAddBrandSetting`,
      deleteBrand: `pf/brands/deleteBrandAsync`
    }),
    ...mapMutations({
      setBrandSettingList: `pf/brands/setBrandSettingList`
    }),
    searchChange() {
      if (this.$route.query.search !== this.key) this.handleSearchChange()
    },
    async handleSearchChange() {
      this.isLoading = true
      this.setBrandSettingList([])
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.key, channel: this.channel } })
    },
    openConfirmModalDeleteBrand(item) {
      this.brandIdOfForDelete = item.brand && item.brand.id ? item.brand.id : null
      this.$bvModal.show('confirm-delete-brand')
    },
    openUpdateSalesModal(item) {
      this.brandOfUpdateSalesModal = item && item.brand ? item.brand.name : '<Default>'
      this.channelOfUpdateSalesModal = item.channel.label
      this.brandIdOfUpdateSalesModal = item.id
      this.$nextTick(() => {
        this.$bvModal.show('update-sales-modal')
      })
    },
    openEditBrandSettingModal(item) {
      this.itemOfEditModal = _.cloneDeep(item)
      this.brandOfEditModal = item && item.brand ? item.brand.name : '<Default>'
      this.channelOfEditModal = item.channel
      this.itemOfEditModal.channel = item.channel.name
      this.itemOfEditModal.brand = item && item.brand ? item.brand.name : null
      this.$nextTick(() => {
        this.$bvModal.show('edit-brand-setting-modal')
      })
    },
    handleUpdate() {
      try {
        let params = {
          client_id: this.$route.params.client_id,
          brand_setting_id: this.brandIdOfUpdateSalesModal,
          sale_date_from: moment.parseZone(this.$refs.updateSaleModal.saleDateFrom).utc(true).format(),
          sale_date_to: moment.parseZone(moment(this.$refs.updateSaleModal.saleDateTo).endOf('day')).utc(true).format(),
          recalculate: this.$refs.updateSaleModal.recalculate
        }
        this.postBrandSettingUpdateSales(params)
        this.vueToast('success', 'Updated successfully.')
        this.$nextTick(() => {
          this.$bvModal.hide('update-sales-modal')
        })
      } catch {
        this.vueToast('error', 'Updating failed. Please retry or contact administrator.')
      }
    },
    checkCountUpdateSales() {
      let payload = {
        client_id: this.$route.params.client_id,
        brand_setting_id: this.brandIdOfUpdateSalesModal,
        sale_date_from: moment.parseZone(this.$refs.updateSaleModal.saleDateFrom).utc(true).format(),
        sale_date_to: moment.parseZone(moment(this.$refs.updateSaleModal.saleDateTo).endOf('day')).utc(true).format(),
        recalculate: this.$refs.updateSaleModal.recalculate
      }
      this.postCountUpdateSales(payload)
    },
    async goToPage(event) {
      this.isLoading = true
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
      this.isLoading = false
    },
    goImport() {
      this.$router.push({name: 'PFStep1ImportBrandSetting', params: {module: 'BrandSettingModule'}})
    },
    async handelExportBrandSettings() {
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          query: {}
        }
        if (this.$route.query.channel) {
          payload.query.channel = this.$route.query.channel
        }
        if (this.$route.query.search) {
          payload.query.keyword = this.$route.query.search
        }
        if (!_.isEmpty(this.selected)) {
          payload.query.items_ids = this.selected.join(',')
        }
        this.exportBrandSetting(payload).then(res => {
          window.location.href = res.data.file_url
        })
      } catch {
        this.vueToast('error', 'Export failed. Please retry or contact administrator.')
      }
    },
    async handleQueryData() {
      this.isLoading = true
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        key: this.$route.query.search,
        channel: this.$route.query.channel
      }
      let data = _.pickBy({ ...payload }, _.identity)
      await this.getBrandSettingList(data)
      this.isLoading = false
    },
    async handleEditBrandSetting() {
      if (!this.dropshipValidation(this.$refs.editBrandSetting.itemEdit)) return
      if (this.$refs.editBrandSetting.$v.itemEdit.$invalid) return

      try {
        let payload = {
          client_id: this.$route.params.client_id,
          brand_setting_id: this.$refs.editBrandSetting.itemEdit.id,
          item_edit: this.$refs.editBrandSetting.itemEdit
        }
        await this.editBrandSetting(payload)
        this.vueToast('success', 'Brand Setting has been saved.')
        this.$bvModal.hide('edit-brand-setting-modal')
        this.isLoading = true
        await this.handleQueryData()
        this.isLoading = false
      } catch (err) {
        this.vueToast('error', 'Saving failed. Please retry or contact administrator.')
      }
    },
    openAddBrandModal() {
      this.itemOfEditModal = {}
      this.$bvModal.show('add-brand-settings')
    },
    async handleDeleteBrand() {
      try {
        await this.deleteBrand({clientId: this.$route.params.client_id, brandId: this.brandIdOfForDelete})
        this.brandIdOfForDelete = null
        await this.handleQueryData()
        this.$bvModal.hide('confirm-delete-brand')
        this.vueToast('success', 'Delete the brand successfully!')
      } catch (err) {
        this.vueToast('error', 'Deleting failed. Please retry or contact administrator.')
      }
    },
    async handleAddBrand() {
      this.$refs.refAddBrandSetting.$v.itemEdit.$touch()
      if (!this.dropshipValidation(this.$refs.refAddBrandSetting.itemEdit)) return
      if (this.$refs.refAddBrandSetting.$v.itemEdit.$invalid) return
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          item_add: this.$refs.refAddBrandSetting.itemEdit
        }
        await this.fetchAddBrandSetting(payload)
        this.vueToast('success', 'Brand Setting has been added.')
        this.$bvModal.hide('add-brand-settings')
        this.isLoading = true
        await this.handleQueryData()
        this.isLoading = false
      } catch (err) {
        this.vueToast('error', 'Add failed. Please retry or contact administrator.')
      }
    },
    /**
     * format row value to US Dollar
     */
    fmtRowValCurrency(val) {
      if (typeof val !== 'number') {
        return val
      }
      var formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      })
      return formatter.format(val)
    },
    fmtObsolete(value, key, item) {
      const obsoleteBar = _.isEqual(_.get(item, 'brand.is_obsolete', false), true) ? 'after-bar-red' : 'after-bar-green'
      return `align-middle text-center ${obsoleteBar}`
    },
    fmtPercent(val) {
      if (typeof val !== 'number') {
        return val
      }
      var formatter = new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
      return formatter.format(val / 100)
    },
    dropshipValidation(itemEdit) {
      const { po_dropship_method: method, po_dropship_cost: cost } = itemEdit
      return method === 'Percent' ? cost >= 0 && cost <= 100 : true
    },
    selectAll(active) {
      this.selected = active ? this.brandSettingList.results.map(brandSetting => brandSetting.id) : []
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
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

$brand-color: #0645AD;

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

.btn-import, .btn-export {
  height: 36px;
}
.btn-add-brand {
  height: 36px;
  min-width: 124px;
}

.btn-import {
  @include button-icon(true, 'upload.svg', 20px, 20px);
}

.btn-export {
  @include button-icon(true, 'download.svg', 20px, 20px);
}

.btn-add-brand {
  @include button-icon(false, 'plus.svg', 14px, 14px);
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
  .brand-column div {
    color: $brand-color;
    cursor: pointer;
  }

  tr:hover .brand-column div {
    color: fade-out($brand-color, 0.5);

    &:hover {
      color: $brand-color;
    }
  }
}

.brand-filter-group {
  height: 60px;
}
::v-deep .custom-form-brand {
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

</style>
