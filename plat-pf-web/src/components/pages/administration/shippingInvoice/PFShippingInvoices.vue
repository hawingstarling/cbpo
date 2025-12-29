<template>
  <b-card class="fedex">
    <!-- search -->
    <b-row class="justify-content-center align-items-center">
      <b-col class="mt-0 mb-4 d-flex justify-content-center align-items-end">
        <div class="d-flex flex-wrap padding-filter-tab dropdown-shipping">
          <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Source</span>
          <b-form-select v-model="params.source" :options="shipmentSrcOptions" @change="changeOptions()"> </b-form-select>
        </div>
        <div class="d-flex flex-wrap padding-filter-tab dropdown-shipping">
          <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Status</span>
          <b-form-select v-model="params.status" :options="shipmentStatusOptions" @change="changeOptions()"> </b-form-select>
        </div>
        <div class="d-flex flex-wrap padding-filter-tab dropdown-shipping">
          <span class="d-flex align-items-center mr-1 w-100 font-weight-normal title-filter">Invoice Date</span>
          <date-picker v-model="invoiceDateRange" @input="changeInvoiceDate" format="MM-DD-YYYY" range-separator=" - " range>
            <template slot="icon-calendar">
              <img src="@/assets/img/icon/date-icon.png">
            </template>
          </date-picker>
        </div>
        <b-form-group class="mb-0 padding-filter-tab dropdown-shipping">
          <b-input-group class="search cancel-action d-flex flex-wrap form-search-custom">
            <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
            <b-form-input class="form-search-input" v-model.trim="params.key" @keypress.enter="searchChange()" placeholder="Search for keywords"> </b-form-input>
            <i
              v-show="params.key"
              @click="
                params.key = ''
                searchChange()
              "
              class="icon-close cancel-icon form-cancel-icon"
            ></i>
            <div class="form-search-icon" @click="searchChange()">
              <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
            </div>
          </b-input-group>
        </b-form-group>
        <div v-if="hasPermission(permissions.fedEx.import)" class="d-flex flex-wrap padding-filter-tab">
          <b-button variant="primary" class="btn-import" @click="goImport()">
            Import
          </b-button>
        </div>
        <div v-if="hasPermission(permissions.fedEx.import)" class="d-flex flex-wrap padding-filter-tab">
          <b-button variant="secondary" class="btn-export" @click="clickExportShipmentBreaks()">
            Export Shipment Breaks
          </b-button>
        </div>
      </b-col>
    </b-row>
    <b-form-checkbox
      class="all-checkbox pl-2"
      :checked="shippingInvoicesList.results && shippingInvoicesList.results.length === selected.length"
      @change="checked => selectAll(checked)"
    >
      Select All
    </b-form-checkbox>
    <div class="overflow-auto w-100">
      <b-table class="fedex-table" @sort-changed="handleSortFedex" :no-local-sorting="true" outlined striped head-variant="light" :items="shippingInvoicesList.results" :fields="listOfshippingInvoicesFields" show-empty>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>
            &nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no Shipping Invoices to show.</div>
          </div>
        </template>
        <template v-slot:cell(checkboxes)="row">
          <b-form-checkbox v-model="selected" :value="row.item.id" class="checkbox"></b-form-checkbox>
        </template>
        <template v-slot:cell(status)="row">
          {{ row.item.status | removeSpecialCharacter }}
        </template>
        <template v-slot:cell(invoice_balances)="row" >
          ${{ new Number(row.item.invoice_balances || 0).toLocaleString('en') }}
        </template>
        <template v-slot:cell(total_transactions)="row">
          <p :class="highlightNumber(row.item.total_transactions)">{{ Intl.NumberFormat().format(row.item.total_transactions)}}</p>
        </template>
        <template v-slot:cell(matched_transactions)="row">
          <p :class="highlightNumber(row.item.matched_transactions)">{{ Intl.NumberFormat().format(row.item.matched_transactions)}}</p>
        </template>
        <template v-slot:cell(unmatched_transactions)="row">
          <div class="d-flex align-items-center justify-content-end">
            <p :class="highlightNumber(row.item.unmatched_transactions, true)">{{ Intl.NumberFormat().format(row.item.unmatched_transactions)}}</p>
            <div
             v-if="row.item.unmatched_transactions"
             @click="openUnmatchedTransactionsModal(row.item)"
             class="ml-2 export-unmatched-transactions-img"
            >
            </div>
          </div>
        </template>
        <template v-slot:cell(matching_status)="row">
          <p class="font-weight-bold m-0">{{ row.item.matching_status}}</p>
        </template>
        <template v-slot:cell(matched_sales)="row">
          <a
            :disabled="!checkCondition(row.item.matched_sales)"
            :event="checkCondition(row.item.matched_sales) ? 'click' : ''"
            class="cursor-pointer router--custom text-blue"
            role="button"
            :class="{ disabled: !checkCondition(row.item.matched_sales)}"
            @click="goToAnalysisPage(row.item.id)"
            v-b-popover.hover.bottom.html="arrayToString(row.item.matched_sales)"
          >
            {{ arrayToString(row.item.matched_sales) }}
          </a>
        </template>
        <template v-slot:cell(shipment_date)="row" >{{ row.item.shipment_date | moment("MM/DD/YYYY") }}</template>
        <template v-slot:cell(invoice_number)="row">
          <router-link class="link-invoice" :to="{ name: 'PFShippingInvoiceTransactions', params: { shipping_invoice_id: row.item.id }, query: { invoice_number: row.item.invoice_number} }">
            {{ row.item.invoice_number }}
          </router-link>
        </template>
        <template v-slot:cell(source_files)="row">
          <div v-for="item in row.item.source_files" v-bind:key="item.id">
            <!-- <a :href="item.source_file_url" target="_blank">{{ item.source_file_name }}</a> -->
            <b-button variant="primary" class="btn-source" @click="downloadURL(item.source_file_url, item.source_file_name)">Source</b-button>
          </div>
        </template>
        <template v-slot:cell(matched_time)="row">
          {{row.item.matched_time | moment("MM/DD/YYYY hh:mm A")}}
        </template>
        <template v-slot:cell(invoice_date)="row" >{{ row.item.invoice_date | moment("MM/DD/YYYY") }}</template>
      </b-table>
    </div>
    <nav class="d-flex justify-content-center">
      <b-pagination
        @change="goToPage($event)"
        v-if="shippingInvoicesList && shippingInvoicesList.count > $route.query.limit && !isLoading"
        :total-rows="shippingInvoicesList.count || 0"
        v-model="$route.query.page"
        :per-page="$route.query.limit"
        hide-goto-end-buttons
      >
        <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
        <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
      </b-pagination>
    </nav>
    <b-modal
        id="confirm-modal"
        centered
        :hide-footer="true"
        :hide-header="true"
        body-class="pt-0"
        content-class="modal-confirm-download-content"
      >
      <div class="d-block text-center mt-1">
        <h3>Confirm</h3>
      </div>
      <div class="mt-2 d-flex justify-content-center">
        <span style="color: #667085">You can only export items within 1 month.</span>
      </div>
      <div class="mt-4 d-flex flex-column align-items-center">
        <button class="btn-primary confirm-export-btn" @click="handleExportShipmentBreaks">Export
          <img class="pl-2 pb-1" src="@/assets/img/icon/download.svg" alt="">
        </button>
        <button class="mt-3 btn-primary confirm-cancel-btn" @click="closeRequireModal">Cancel</button>
      </div>
    </b-modal>
    <b-modal id="download-export-modal"
             centered
             variant="success"
             body-class="pt-0"
             :hide-footer="true"
             :hide-header="true"
             content-class="modal-download-content" >
      <div class="d-block text-center">
        <h3>The following shipment break was successfully exported!</h3>
        <div v-if="itemIdDownloaded.length" class="d-flex justify-content-center flex-column">
          <span v-for="(ele, index) in itemIdDownloaded" :key="index">{{ ele }}</span>
        </div>
      </div>
      <div class="mt-2 d-flex justify-content-center" >
        <a :href="downloadInfo.downloadUrl" :download="downloadInfo.name">{{downloadInfo.name}}</a>
      </div>
    </b-modal>
    <b-modal id="unmatched-transactions-modal" variant="danger" centered title="Please confirm">
      <div>Are you sure you want to download this unmatched transactions?</div>
      <template v-slot:modal-footer>
        <b-button variant="warning" @click="handExportUnmatchedTransactions()">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
        </b-button>
        <b-button variant @click="$bvModal.hide('unmatched-transactions-modal')">
            <i class="icon-close"></i> No
        </b-button>
      </template>
    </b-modal>
     <div v-if="isProgressingExport" id="progress-bar">
       <div style="width:500px" class="d-flex align-items-center">
         <span class="mr-2 text-nowrap">Download progress:</span>
         <b-progress :max="100" class="w-100" show-progress>
           <b-progress-bar class="text-dark" :value="currentExportPercent">{{ currentExportPercent ? currentExportPercent : 0}}%</b-progress-bar>
         </b-progress>
       </div>
     </div>
     <div v-if="Object.keys(downloadInfo).length > 0" id="completed-export">
       <span class="text-dark">Bingo! Please download the file
         <b-button size="sm" variant="primary" @click="downloadFile(downloadInfo)">Download</b-button>
       </span>
     </div>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import { numeral } from '@/shared/filters'
import get from 'lodash/get'
import take from 'lodash/take'
import pickBy from 'lodash/pickBy'
import identity from 'lodash/identity'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import DatePicker from 'vue2-datepicker'
import 'vue2-datepicker/index.css'
import toastMixin from '@/components/common/toastMixin'

export default {
  name: 'PFShippingInvoicesModule',
  data() {
    const thClassTextCenter = 'align-middle text-center'
    const thClassTextRight = 'align-middle text-right'
    const tdClassTextCenter = 'align-middle text-center'
    const tdClassTextRight = 'align-middle text-right'
    return {
      listOfshippingInvoicesFields: [
        {key: 'checkboxes', label: '', tdClass: 'align-middle text-center', thClass: 'align-middle text-center'},
        { key: 'invoice_number', label: 'Invoice Number', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'invoice_date', label: 'Invoice Date', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'payer_account_id', label: 'Payer Account ID', tdClass: 'align-middle net-charge-col', sortable: true, thClass: thClassTextCenter },
        { key: 'payee_account_id', label: 'Payee Account ID', tdClass: 'align-middle', sortable: true, thClass: thClassTextCenter },
        { key: 'invoice_balances', label: 'Invoice Balances', tdClass: tdClassTextRight, sortable: true, thClass: thClassTextCenter },
        { key: 'matching_status', label: 'Matching Status', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'total_transactions', label: 'Total Transactions', tdClass: tdClassTextRight, sortable: true, thClass: thClassTextRight },
        { key: 'matched_transactions', label: 'Matched Transactions', tdClass: tdClassTextRight, sortable: true, thClass: thClassTextRight },
        { key: 'unmatched_transactions', label: 'Unmatched Transactions', tdClass: tdClassTextRight, sortable: true, thClass: thClassTextRight },
        { key: 'matched_sales', label: 'Matched Sales', tdClass: `${tdClassTextRight} text-truncate`, thClass: `${thClassTextRight} text-truncate`, sortable: true },
        { key: 'matched_time', label: 'Matched Time', tdClass: `${tdClassTextCenter} status-col`, sortable: true, thClass: thClassTextCenter },
        { key: 'source_files', label: 'Source Files(s)', tdClass: 'd-flex justify-content-center', sortable: true, thClass: thClassTextCenter }
      ],
      params: {
        page: 1,
        limit: 10,
        key: '',
        status: null,
        source: null
      },
      isLoading: true,
      shipmentStatusOptions: [
        { text: 'All', value: null },
        { text: 'Pending', value: 'Pending' },
        { text: 'Done With Errors', value: 'DoneWithErrors' },
        { text: 'Done', value: 'Done' }
      ],
      shipmentSrcOptions: [
        { text: 'All', value: null },
        { text: 'Import', value: 'Import' },
        { text: 'FTP EDI', value: 'FTP EDI' },
        { text: 'FTP CSV', value: 'FTP CSV' }
      ],
      permissions,
      currentExportPercent: 0,
      exportShipmentBreaksTimer: null,
      exportUnmatchedTransactionsTimer: null,
      downloadInfo: {},
      isProgressingExport: false,
      invoiceDateRange: [null, null],
      selected: [],
      itemIdDownloaded: [],
      limitItemDownloadRepresentation: 5,
      currentShippingInvoices: null
    }
  },
  components: { DatePicker },
  mixins: [
    PermissionsMixin,
    toastMixin
  ],
  computed: {
    ...mapGetters({
      shippingInvoicesList: `pf/fedex/shippingInvoicesList`,
      currentExportShipmentBreaksId: `pf/fedex/currentExportShipmentBreaksId`,
      currentExportUnmatchedTransactionsId: `pf/fedex/currentExportUnmatchedTransactionsId`,
      getUserId: `ps/userModule/GET_USER_ID`,
      matchedSales: `pf/fedex/matchedSales`
    }),
    fromDateFormat() {
      return this.invoiceDateRange[0] ? this.$moment(this.invoiceDateRange[0]).format('YYYY-MM-DD') : ''
    },
    toDateFormat() {
      return this.invoiceDateRange[1] ? this.$moment(this.invoiceDateRange[1]).format('YYYY-MM-DD') : ''
    },
    highlightNumber() {
      return (type, isBold) => {
        return type > 0 ? isBold ? 'text-blue font-weight-bold m-0' : 'text-blue m-0' : 'm-0'
      }
    },
    arrayToString() {
      return array => {
        if (Array.isArray(array)) return array.join(', ')
        return array
      }
    }
  },
  filters: {
    numeral,
    removeSpecialCharacter: string => {
      if (!string) return ''
      return string.slice(15, string.length).toLowerCase()
    }
  },
  methods: {
    ...mapActions({
      getshippingInvoicesList: `pf/fedex/getshippingInvoicesList`,
      createshippingInvoicesExport: `pf/fedex/createshippingInvoicesExport`,
      getShippingInvoicesExportPercent: `pf/fedex/getShippingInvoicesExportPercent`,
      setCurrentExportShipmentBreaksId: `pf/fedex/setCurrentExportShipmentBreaksId`,
      setCurrentExportUnmatchedTransactionsId: `pf/fedex/setCurrentExportUnmatchedTransactionsId`,
      getMatchedSales: `pf/fedex/getMatchedSales`,
      createExportUnmatchedTransactions: `pf/fedex/createExportUnmatchedTransactions`,
      getExportUnmatchedTransactionsPercent: `pf/fedex/getExportUnmatchedTransactionsPercent`
    }),
    ...mapMutations({
      setShippingInvoicesList: `pf/fedex/setShippingInvoicesList`
    }),
    checkCondition(list) {
      return list && list.length !== 0
    },
    handleClickMatchedSale(list) {
      let routerData = this.$router.resolve({ name: 'PFAnalysis', query: { sale_id: JSON.stringify(list) } })
      window.open(routerData.href, '_blank')
    },
    // Function search
    async searchChange() {
      this.setShippingInvoicesList([])
      this.$route.query.page = 1
      this.shippingInvoicesList.results = []
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, source: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
      this.handleQueryData()
    },
    async changeOptions() {
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, source: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
    },
    goImport() {
      this.$router.push({ name: 'PFStep1ImportFedex', params: { module: 'FedExShipmentModule' } })
    },
    async goToPage(event) {
      this.isLoading = true
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
      this.isLoading = false
    },
    async handleQueryData() {
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        key: this.params.key,
        status: this.$route.query.status,
        source: this.$route.query.source,
        sortDirection: this.$route.query.sortDirection,
        sortField: this.$route.query.sortField,
        fromDate: this.fromDateFormat,
        toDate: this.toDateFormat
      }
      let data = pickBy({ ...payload }, identity)
      try {
        this.isLoading = true
        await this.getshippingInvoicesList(data)
      } catch (err) {
      } finally {
        this.isLoading = false
      }
    },
    handleSortFedex(context) {
      this.$router.push({query: { ...this.$route.query, sortDirection: context.sortDesc ? 'desc' : 'asc', sortField: context.sortBy }})
    },
    clickExportShipmentBreaks() {
      const isWithinOneMonth = this.checkWithinOneMonth(this.invoiceDateRange[0], this.invoiceDateRange[1])
      if (this.selected.length) {
        // select item ids is a slight job
        // ignore date range validation
        this.handleExportShipmentBreaks()
        return
      }
      if (this.invoiceDateRange[0] && isWithinOneMonth) {
        this.handleExportShipmentBreaks()
      } else if (this.invoiceDateRange[0] && !isWithinOneMonth) {
        this.vueToast('error', 'Just allow 1 month to be exported')
      } else this.$bvModal.show('confirm-modal')
    },
    closeRequireModal() {
      this.$bvModal.hide('confirm-modal')
    },
    handleExportShipmentBreaks() {
      this.downloadInfo = {}
      this.isProgressingExport = false
      this.currentExportPercent = 0
      const params = {
        clientId: this.$route.params.client_id,
        payload: {
          item_ids: this.selected,
          bulk_operations: [
            {
              column: 'source',
              action: 'equal',
              value: this.params.source
            },
            {
              column: 'status',
              action: 'equal',
              value: this.params.status
            },
            {
              column: 'keyword',
              action: 'contain',
              value: this.params.key
            }
          ]
        }
      }
      if (!this.invoiceDateRange[0]) {
        params.payload.bulk_operations.push(
          {
            column: 'from_date',
            action: 'equal',
            value: this.$moment().add(-1, 'month').format('YYYY-MM-DD')
          }
        )
        params.payload.bulk_operations.push(
          {
            column: 'to_date',
            action: 'equal',
            value: this.$moment().startOf('day').format('YYYY-MM-DD')
          }
        )
      } else {
        params.payload.bulk_operations.push(
          {
            column: 'from_date',
            action: 'equal',
            value: this.$moment(this.invoiceDateRange[0]).format('YYYY-MM-DD')
          }
        )
        params.payload.bulk_operations.push(
          {
            column: 'to_date',
            action: 'equal',
            value: this.$moment(this.invoiceDateRange[1]).format('YYYY-MM-DD')
          }
        )
      }
      this.createshippingInvoicesExport(params)
        .catch(err => {
          this.vueToast('error', err.response.data.message)
        })
        .finally(() => {
          this.closeRequireModal()
        })
    },
    async getExportPercent() {
      clearInterval(this.exportShipmentBreaksTimer)
      const params = {
        clientId: this.$route.params.client_id,
        userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
        id: this.currentExportShipmentBreaksId
      }

      this.exportShipmentBreaksTimer = setInterval(() => {
        if (this.currentExportPercent < 100) {
          this.getShippingInvoicesExportPercent(params).then(res => {
            this.currentExportPercent = res.data.progress
            if (res.data.status === 'reported') {
              this.isProgressingExport = false
              this.currentExportPercent = 0
              const metaData = get(res.data, 'meta_data', [])
              this.itemIdDownloaded = take(metaData, this.limitItemDownloadRepresentation)
              this.itemIdDownloaded.length < metaData.length && this.itemIdDownloaded.push('...')
              this.downloadInfo = {
                downloadUrl: res.data.download_url,
                name: res.data.name
              }
              this.$bvModal.show('download-export-modal')
              this.setCurrentExportShipmentBreaksId(null)
              clearInterval(this.exportShipmentBreaksTimer)
            }
          })
        }
      }, 2500)
    },
    downloadFile(downloadInfo) {
      this.setCurrentExportUnmatchedTransactionsId(null)
      const { downloadUrl, name } = downloadInfo
      this.downloadURL(downloadUrl, name)
      this.downloadInfo = {}
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
    async changeInvoiceDate(date) {
      if (date[0] && date[1]) {
        await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, source: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
        this.handleQueryData()
      } else {
        await this.$router.push({
          name: 'PFShippingInvoices',
          params: { client_id: this.$route.params.client_id },
          query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search || this.params.key, status: this.$route.query.status || this.params.status, source: this.$route.query.source || this.params.source }
        })
      }
    },
    checkWithinOneMonth(fromDate, toDate) {
      const diff = this.$moment(toDate).diff(this.$moment(fromDate), 'months', true)
      if (diff >= 0 & diff <= 1) return true
      else return false
    },
    async goToAnalysisPage(shippingInvoiceId) {
      const payload = {
        client_id: this.$route.params.client_id,
        shipping_invoice_id: shippingInvoiceId
      }
      const saleIds = await this.getMatchedSales(payload)
      if (saleIds) {
        let routeData = this.$router.resolve({name: 'PFAnalysis', query: { sale_id: JSON.stringify(saleIds) }})
        window.open(routeData.href, '_blank')
      }
    },
    selectAll(active) {
      this.selected = active ? this.shippingInvoicesList.results.map(shippingInvoice => shippingInvoice.id) : []
    },
    openUnmatchedTransactionsModal(data) {
      this.currentShippingInvoices = data
      this.$bvModal.show('unmatched-transactions-modal')
    },
    async handExportUnmatchedTransactions() {
      this.currentExportPercent = 0
      await this.createExportUnmatchedTransactions({
        client_id: this.$route.params.client_id,
        payload: {
          bulk_operations: [
            {
              column: 'shipping_invoice_id',
              value: this.currentShippingInvoices.id
            }
          ]
        }
      })
      this.getExportUnmatchedTransactionsStatus()
      this.$bvModal.hide('unmatched-transactions-modal')
    },
    async getExportUnmatchedTransactionsStatus() {
      clearInterval(this.exportUnmatchedTransactionsTimer)
      const params = {
        clientId: this.$route.params.client_id,
        userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
        id: this.currentExportUnmatchedTransactionsId
      }

      this.exportUnmatchedTransactionsTimer = setInterval(() => {
        if (this.currentExportPercent < 100) {
          this.getExportUnmatchedTransactionsPercent(params).then(res => {
            this.currentExportPercent = res.data.progress
            if (res.data.status === 'reported') {
              this.isProgressingExport = false
              this.currentExportPercent = 0
              this.downloadInfo = {
                downloadUrl: res.data.download_url,
                name: res.data.name
              }
              clearInterval(this.exportUnmatchedTransactionsTimer)
            }
          })
        }
      }, 2500)
    }
  },
  async created() {
    this.params.key = this.$route.query.search || ''
    this.params.status = this.$route.query.status || null
    this.params.source = this.$route.query.source || null
    this.invoiceDateRange[0] = this.$route.query.from_date ? this.$moment(this.$route.query.from_date).toDate() : null
    this.invoiceDateRange[1] = this.$route.query.to_date ? this.$moment(this.$route.query.to_date).toDate() : null
    if (this.$route.query.limit && this.$route.query.page) {
      await this.handleQueryData()
    } else {
      await this.$router.push({
        name: 'PFShippingInvoices',
        params: { client_id: this.$route.params.client_id },
        query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search || this.params.key, status: this.$route.query.status || this.params.status, source: this.$route.query.source || this.params.source }
      })
    }
  },
  mounted() {
    if (this.currentExportShipmentBreaksId) {
      this.getExportPercent()
    }
    if (this.currentExportUnmatchedTransactionsId) {
      this.getExportUnmatchedTransactionsStatus()
    }
  },
  watch: {
    async $route(to, from) {
      this.params.key = this.$route.query.search || ''
      await this.handleQueryData()
    },
    currentExportShipmentBreaksId(newValue) {
      if (newValue) {
        this.getExportPercent()
      }
    }
  },
  beforeDestroy() {
    clearInterval(this.exportShipmentBreaksTimer)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

::v-deep .net-charge-col {
  width: 100px;
}
::v-deep .status-col {
  text-transform: capitalize;
}
.thin-spinner {
  border-width: 0.14em;
}
.router--custom {
  text-decoration: underline;
  // to show text-truncate
  width: 150px;
}
// disabled event click
.disabled {
  opacity: 0.6;
  pointer-events: none;
}
.spinner-container {
  height: 50px;

  .thin-spinner {
    border-width: 1px;
  }
}

::v-deep .fedex-table {
  border-color: #E6E8F0 !important;
}

::v-deep.fedex .fedex-table th {
  vertical-align: middle;
}
::v-deep .mx-datepicker {
  flex: 1;

  .mx-input {
    box-shadow: none;
    padding-left: 30px;
  }

  .mx-icon-calendar {
    right: unset !important;
    left: 8px;
  }
}
#completed-export, #progress-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 6px 10px;
  height: 42px;
  background-color: rgb(228, 231, 234);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border: solid 1px rgb(200,206,211);
}

.padding-filter-tab {
  padding-left: 4px;
  padding-right: 4px;
}

.btn-import,
.btn-export {
  height: 40px;
}

.btn-import {
  @include button-icon(true, 'upload.svg', 20px, 20px);
}

.btn-export {
  @include button-icon(true, 'download-blue.svg', 20px, 20px);
}

.btn-source {
  @include button-icon(false, 'download-blue.svg', 20px, 20px);
}

.mx-datepicker-range, .dropdown-shipping {
  width: 180px;
}

.table {
  tbody {
    tr {
      .text-blue {
        color: #232F3E;
      }
      &:hover {
        .text-blue {
          color: #999999 !important;
        }
        .link-invoice {
          color: #20a8d870 !important;
        }
      }
    }
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

::v-deep .modal-confirm-download-content {
  padding: 30px;
  width: 500px;
  height: 256px;
}

::v-deep .modal-download-content {
  width: 500px;
  //height: 157px;
  padding: 30px;

  a {
    color: black;
  }
}

::v-deep .modal-confirm-download-content {
  .confirm-export-btn {
    color: #FFFFFF !important;
    background-color: #254164 !important;
    border: 1px solid #232F3E;
    &:hover {
      color: #FFFFFF !important;
      background-color: #254164 !important;
      border-color: #254164 !important;
    }
  }

  .confirm-cancel-btn {
    color: #232F3E !important;
    background-color: unset !important;
    border: 1px solid #232F3E;
    box-shadow: 0px 1px 2px rgba(16, 24, 40, 0.05);
    border-radius: 1px
  }
}
.export-unmatched-transactions-img {
  width: 12px;
  height: 12px;
  background-image: url('~@/assets/img/icon/download-blue.svg');
  background-size: 100%;
  background-repeat: no-repeat;
  cursor: pointer;
}
.form-search-custom {
  .form-search-input {
    padding-right: 30px !important;
  }
}
</style>
