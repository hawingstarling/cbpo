<template>
  <b-card class="fedex">
    <!-- search -->
    <b-row class="justify-content-center align-items-center">
      <b-col class="mt-0 mb-4 d-flex justify-content-center align-items-end filter-control">
        <div class="pr-2 filter-control__source">
          <span class="d-flex align-items-center mr-1 title-filter">Source</span>
          <b-form-select v-model="params.source" :options="shipmentSrcOptions" @change="changeOptions()"> </b-form-select>
        </div>
        <div class="pr-2 filter-control__status">
          <span class="d-flex align-items-center mr-1 title-filter">Status</span>
          <b-form-select v-model="params.status" :options="shipmentStatusOptions" @change="changeOptions()"> </b-form-select>
        </div>
        <b-form-group class="col-2 m-0 p-0 pr-2 filter-control__search">
          <span class="d-flex align-items-center mr-1 title-filter">Search</span>
          <b-input-group class="search cancel-action form-search-custom">
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
        <b-button variant="primary" class="btn-import mr-2" @click="goImport()">
          Import
        </b-button>
        <b-button variant="secondary" class="btn-export" @click="clickExportShipmentBreaks()">
          Export Shipment Breaks
        </b-button>
      </b-col>
    </b-row>
    <div class="overflow-auto w-100">
      <b-table class="fedex-table" @sort-changed="handleSortFedex" :no-local-sorting="true" outlined striped head-variant="light" :items="shippingInvoiceTransactionList.results" :fields="listOfShippingInvoiceTransactionFields" show-empty>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>
            &nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no Shipping Invoices to show.</div>
          </div>
        </template>
        <template v-slot:cell(status)="row">
          {{ row.item.status | removeSpecialCharacter }}
        </template>
        <template v-slot:cell(invoice_balances)="row" >
          <p class="m-0">{{ row.item.invoice_balances | toUSD }}</p>
        </template>
        <template v-slot:cell(total_transactions)="row">
          <p :class="highlightNumber(row.item.total_transactions)">{{ row.item.total_transactions}}</p>
        </template>
        <template v-slot:cell(matched_transactions)="row">
          <p :class="highlightNumber(row.item.matched_transactions)">{{ row.item.matched_transactions}}</p>
        </template>
        <template v-slot:cell(invoice_number)="row">
          <p :class="highlightNumber(row.item.invoice_number)">{{ row.item.invoice_number}}</p>
        </template>
        <template v-slot:cell(matched_channel_sale_ids)="row">
          <p class="m-0">{{ arrayToString(row.item.matched_channel_sale_ids) }}</p>
        </template>
        <template v-slot:cell(shipment_date)="row" >{{ row.item.shipment_date | moment("MM/DD/YYYY") }}</template>
        <template v-slot:cell(matched_time)="row">
          {{row.item.matched_time | moment("MM/DD/YYYY hh:mm A")}}
        </template>
        <template v-slot:cell(invoice_date)="row" >{{ row.item.invoice_date | moment("MM/DD/YYYY") }}</template>
        <template v-slot:cell(matched_sales)="row">
          <router-link
            :to="{ name: 'PFAnalysis', query: { sale_id: JSON.stringify(row.item.matched_sales) } }"
            target="_blank"
            :disabled="!checkCondition(row.item.matched_sales)"
            :event="checkCondition(row.item.matched_sales) ? 'click' : ''"
            :class="{ disabled: !checkCondition(row.item.matched_sales) }"
            class="router--custom"
            v-b-popover.hover.bottom.html="arrayToString(row.item.matched_sales)"
          >
            {{ arrayToString(row.item.matched_sales) }}
          </router-link>
        </template>
      </b-table>
    </div>
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
        <b-button class="confirm-export-btn" variant="primary" @click="handleExportShipmentBreaks">Export
          <img class="pl-2 pb-1" src="@/assets/img/icon/download.svg" alt="">
        </b-button>
        <b-button class="mt-3" @click="closeRequireModal">Cancel</b-button>
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
        <h3>Transactions were successfully exported!</h3>
      </div>
      <div class="mt-2 d-flex justify-content-center" >
        <a :href="downloadInfo.downloadUrl" :download="downloadInfo.name">{{downloadInfo.name}}</a>
      </div>
    </b-modal>
    <nav class="d-flex justify-content-center">
      <b-pagination
        @change="goToPage($event)"
        v-if="shippingInvoiceTransactionList && shippingInvoiceTransactionList.count > $route.query.limit && !isLoading"
        :total-rows="shippingInvoiceTransactionList.count || 0"
        v-model="$route.query.page"
        prev-text="Prev"
        next-text="Next"
        :per-page="$route.query.limit"
        hide-goto-end-buttons
      >
        <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
        <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
      </b-pagination>
    </nav>
  </b-card>
</template>

<script>
import {mapActions, mapGetters, mapMutations} from 'vuex'
import { numeral } from '@/shared/filters'
import _ from 'lodash'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import 'vue2-datepicker/index.css'
import toastMixin from '@/components/common/toastMixin'

export default {
  name: 'PFTransactions',
  data() {
    return {
      invoice_number: null,
      listOfShippingInvoiceTransactionFields: [
        { key: 'transaction_id', label: 'Transaction ID', tdClass: 'align-middle', sortable: true },
        { key: 'invoice_number', label: 'Invoice Number', tdClass: 'align-middle', sortable: true },
        { key: 'invoice_date', label: 'Invoice Date', tdClass: 'align-middle net-charge-col', sortable: true },
        { key: 'net_charge_amount', label: 'Transaction Amount', tdClass: 'align-middle', sortable: true },
        { key: 'status', label: 'Matching Status', tdClass: 'align-middle', sortable: true },
        { key: 'matched_sales', label: 'Matched Sales', tdClass: 'align-middle text-left text-truncate', thClass: 'text-left text-truncate', sortable: true },
        { key: 'matched_channel_sale_ids', label: 'Matched Channel Sale Ids', tdClass: 'align-middle', sortable: true },
        { key: 'matched_time', label: 'Matched Time', tdClass: 'align-middle', sortable: true },
        { key: 'tracking_id', label: 'Tracking ID', tdClass: 'align-middle', sortable: true }
      ],
      params: {
        page: 1,
        limit: 10,
        key: '',
        status: null,
        source: null
      },
      isLoading: false,
      shipmentStatusOptions: [
        { text: 'All', value: null },
        { text: 'Pending', value: 'FEDEX_SHIPMENT_PENDING' },
        { text: 'One', value: 'FEDEX_SHIPMENT_ONE' },
        { text: 'Multi', value: 'FEDEX_SHIPMENT_MULTI' },
        { text: 'Completed', value: 'FEDEX_SHIPMENT_COMPLETED' },
        { text: 'None', value: 'FEDEX_SHIPMENT_NONE' }
      ],
      shipmentSrcOptions: [
        { text: 'All', value: null },
        { text: 'Import', value: 'Import' },
        { text: 'FTP EDI', value: 'FTP EDI' },
        { text: 'FTP CSV', value: 'FTP CSV' }
      ],
      permissions,
      currentExportPercent: 0,
      downloadInfo: {},
      exportBreakTimer: null
    }
  },
  mixins: [
    PermissionsMixin,
    toastMixin
  ],
  computed: {
    ...mapGetters({
      shippingInvoiceTransactionList: `pf/fedex/shippingInvoiceTransactionList`,
      currentExportShippingInvoicesTransactionsBreaksId: `pf/fedex/currentExportShippingInvoicesTransactionsBreaksId`,
      getUserId: `ps/userModule/GET_USER_ID`
    }),
    highlightNumber() {
      return (type, isBold) => {
        return type > 0 ? isBold ? 'text-blue font-weight-bold m-0' : 'text-blue m-0' : ''
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
    },
    toUSD (value) {
      return `$${value.toLocaleString()}`
    }
  },
  methods: {
    ...mapActions({
      getShippingInvoiceTransactionList: `pf/fedex/getShippingInvoiceTransactionList`,
      createShippingInvoiceTransactionExport: `pf/fedex/createShippingInvoiceTransactionExport`,
      setCurrentExportShippingInvoicesTransactionsBreaksId: `pf/fedex/setCurrentExportShippingInvoicesTransactionsBreaksId`,
      // from custom report
      getShippingInvoiceTransactionExportPercent: `pf/fedex/getShippingInvoicesExportPercentAsync`
    }),
    ...mapMutations({
      setCurrentShippingInvoiceNumber: 'pf/fedex/setCurrentShippingInvoiceNumber'
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
      this.$route.query.page = 1
      this.shippingInvoiceTransactionList.results = []
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, source: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
      this.handleQueryData()
    },
    async changeOptions() {
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, source: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
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
        shipping_invoice_id: this.$route.params.shipping_invoice_id,
        key: this.params.key,
        status: this.$route.query.status,
        source: this.$route.query.source,
        sortDirection: this.$route.query.sortDirection,
        sortField: this.$route.query.sortField,
        fromDate: this.fromDateFormat,
        toDate: this.toDateFormat
      }
      let data = _.pickBy({ ...payload }, _.identity)
      try {
        this.isLoading = true
        await this.getShippingInvoiceTransactionList(data)
      } catch (err) {
        console.log('err', err)
      } finally {
        this.isLoading = false
      }
    },
    handleSortFedex(context) {
      this.$router.push({query: { ...this.$route.query, sortDirection: context.sortDesc ? 'desc' : 'asc', sortField: context.sortBy }})
    },
    goImport() {
      this.$router.push({ name: 'PFStep1ImportFedex', params: { module: 'FedExShipmentModule' } })
    },
    closeRequireModal() {
      this.$bvModal.hide('confirm-modal')
    },
    clickExportShipmentBreaks() {
      this.$bvModal.show('confirm-modal')
    },
    async handleExportShipmentBreaks() {
      this.$bvModal.hide('confirm-modal')
      const params = {
        clientId: this.$route.params.client_id,
        payload: {
          item_ids: [],
          bulk_operations: [
            {
              column: 'shipping_invoice_id',
              value: this.$route.params.shipping_invoice_id
            },
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
            },
            {
              column: 'from_date',
              action: 'equal',
              value: this.$moment().add(-1, 'month').format('YYYY-MM-DD')
            },
            {
              column: 'to_date',
              action: 'equal',
              value: this.$moment().startOf('day').format('YYYY-MM-DD')
            }
          ]
        }
      }
      await this.createShippingInvoiceTransactionExport(params)
    },
    async progressiveExport() {
      // clear previous
      clearInterval(this.exportBreakTimer)

      const params = {
        clientId: this.$route.params.client_id,
        userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
        id: this.currentExportShippingInvoicesTransactionsBreaksId
      }
      this.exportBreakTimer = setInterval(async () => {
        if (this.currentExportPercent < 100) {
          try {
            const data = await this.getShippingInvoiceTransactionExportPercent(params)
            this.currentExportPercent = data.progress
            if (data.status === 'reported') {
              this.downloadInfo = {
                downloadUrl: data.download_url,
                name: data.name
              }
              this.$bvModal.show('download-export-modal')
              // stop
              clearInterval(this.exportBreakTimer)
              this.setCurrentExportShippingInvoicesTransactionsBreaksId(null)
            }
          } catch (err) {
            clearInterval(this.exportBreakTimer)
            this.setCurrentExportShippingInvoicesTransactionsBreaksId(null)
          }
        }
      }, 2000)
    }
  },
  async created() {
    this.invoice_number = this.$route.query.invoice_number || null
    this.setCurrentShippingInvoiceNumber(this.invoice_number)
    this.params.key = this.$route.query.search || ''
    this.params.status = this.$route.query.status || null
    this.params.source = this.$route.query.source || null
    if (this.$route.query.limit && this.$route.query.page) {
      await this.handleQueryData()
    } else {
      await this.$router.push({
        name: 'PFShippingInvoiceTransactions',
        params: { client_id: this.$route.params.client_id },
        query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search || this.params.key, status: this.$route.query.status || this.params.status, source: this.$route.query.source || this.params.source, invoice_number: this.invoice_number }
      })
    }
  },
  watch: {
    async $route(to, from) {
      this.params.key = this.$route.query.search || ''
      await this.handleQueryData()
    },
    currentExportShippingInvoicesTransactionsBreaksId: {
      immediate: true,
      handler(newVal) {
        !!newVal && this.progressiveExport()
      }
    }
  },
  beforeDestroy() {
    clearInterval(this.exportBreakTimer)

    this.setCurrentShippingInvoiceNumber(null)
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

::v-deep.fedex .fedex-table th {
  vertical-align: middle;
}
::v-deep .mx-datepicker {
  flex: 1;
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
        .router--custom {
          color: #20a8d870 !important;
        }
      }
    }
  }
}

::v-deep .filter-control {
  &__source, &__status {
    width: 180px;
  }
  &__import {
    height: 40px !important;
    border-radius: 2px !important;

    &:hover {
      color: #FFF !important;
      background-color: #254164 !important;
    }
  }
  &__export {
    height: 40px !important;
    border-radius: 2px !important;
    background-color: unset !important;
    color:#146EB4 !important;
    border: 1px solid #146EB4 !important;
    font-weight: 600 !important;

    &:hover {
      color: #254164 !important;
      background-color: #FFFFFF !important;
      border-color: #254164 !important;
    }
  }
}

::v-deep .modal-confirm-download-content {
  padding: 30px;
  width: 500px;
  height: 256px;

  .confirm-export-btn {
    &:hover {
      color: #FFFFFF !important;
      background-color: #254164 !important;
      border-color: #254164 !important;
    }
  }
}

::v-deep .modal-download-content {
  width: 500px;
  height: 157px;
  padding: 30px;

  a {
    color: black;
  }
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
.form-search-custom {
  .form-cancel-icon {
    top: 50% !important;
  }
}
</style>
