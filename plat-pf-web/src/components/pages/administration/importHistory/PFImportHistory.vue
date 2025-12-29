<template>
  <b-card class="fedex">
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="fa fa-clock-o"></i> Import History</strong>
          </span>
          <span v-if="importHistoryList && importHistoryList.count" class="ml-1">(Total: {{ importHistoryList.count | numeral}})</span>
        </b-col>
      </b-row>
    </div>
    <!-- search -->
    <b-row class="justify-content-center align-items-center flex-nowrap">
      <b-col md="10" class="mt-0 mb-4 d-flex">
        <div class="pr-1 col-3 d-flex flex-wrap">
          <span class="d-flex align-items-center mr-1 title-filter">Type</span>
          <b-form-select class="form-select-custom" v-model="params.source" :options="importModuleKeysOption" @change="changeOptions()"> </b-form-select>
        </div>
        <div class="pr-1 col-3 d-flex flex-wrap">
          <span class="d-flex align-items-center mr-1 title-filter">Processing Status</span>
          <b-form-select class="form-select-custom" v-model="params.status" :options="importHistoryStatusOptions" @change="changeOptions()"> </b-form-select>
        </div>
        <div class="pr-1 col-3 d-flex flex-wrap mr-3">
          <span class="d-flex align-items-center mr-1 w-100 title-filter">Import Date</span>
          <date-picker v-model="invoiceDateRange" @input="changeImportDate" format="MM-DD-YYYY" range-separator=" - " range></date-picker>
        </div>
        <!-- <b-form-group class="mb-0">
          <b-input-group class="search cancel-action">
            <template #prepend>
              <b-dropdown :text="params.fieldSearch">
                <b-dropdown-item @click="params.fieldSearch='All'">All</b-dropdown-item>
                <b-dropdown-item @click="params.fieldSearch='File Name'">File Name</b-dropdown-item>
                <b-dropdown-item @click="params.fieldSearch='Username'">Username</b-dropdown-item>
                <b-dropdown-item @click="params.fieldSearch='Import ID'">Import ID</b-dropdown-item>
              </b-dropdown>
            </template>
            <b-form-input v-model.trim="params.key" @keypress.enter="searchChange()" placeholder="Search for keywords"> </b-form-input>
            <i
              v-show="params.key"
              @click="
                params.key = ''
                searchChange()
              "
              class="icon-close cancel-icon"
            ></i>
            <b-input-group-append>
              <b-button @click="searchChange()">
                <i class="icons icon-magnifier"></i>
              </b-button>
            </b-input-group-append>
          </b-input-group>
        </b-form-group> -->
      </b-col>
      <b-col md="2" class="mt-0 mb-4 d-flex justify-content-center">
        <span v-if="importHistoryList && importHistoryList.count" class="ml-1 total-count-text">Total Count: {{ importHistoryList.count | numeral}}</span>
      </b-col>
    </b-row>
    <div class="overflow-auto w-100">
      <b-table class="fedex-table" @sort-changed="handleSortFedex" :no-local-sorting="true" outlined striped head-variant="light" :items="importHistoryList.results" :fields="listOfshippingInvoicesFields" show-empty>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>
            &nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no import history to show.</div>
          </div>
        </template>
        <template v-slot:cell(status)="row">
          {{upperCaseFirstLetter(row.item.status)}}
        </template>
        <template v-slot:cell(progress)="row">
          {{row.item.progress}}%
        </template>
        <template v-slot:cell(row_count)="row">
          {{Intl.NumberFormat().format(row.item.row_count)}}
        </template>
        <template v-slot:cell(row_processed)="row">
          {{Intl.NumberFormat().format(row.item.row_processed)}}
        </template>
        <template v-slot:cell(entries_created)="row">
          {{Intl.NumberFormat().format(row.item.entries_created)}}
        </template>
        <template v-slot:cell(entries_ignored)="row">
          {{Intl.NumberFormat().format(row.item.entries_ignored)}}
        </template>
        <template v-slot:cell(entries_modified)="row">
          {{Intl.NumberFormat().format(row.item.entries_modified)}}
        </template>
        <template v-slot:cell(file.name)="row">
          <a :href="row.item.file.url" target="_blank">{{ row.item.file.name }}</a>
        </template>
        <template v-slot:cell(created)="row">
          {{ formatDate(row.item.created) }}
        </template>
        <template v-slot:cell(total_transactions)="row">
          <p :class="highlightNumber(row.item.row_errors, true)">{{ Intl.NumberFormat().format(row.item.row_errors)}}</p>
        </template>
        <template v-slot:cell(shipment_date)="row" >{{ row.item.shipment_date | moment("MM/DD/YYYY") }}</template>
        <template v-slot:cell(id)="row">
          <router-link :to="{ name: 'PFStep4ResultFedex', params: { import_id: row.item.id, module: row.item.module } }">
            {{ row.item.id }}
          </router-link>
        </template>
        <template v-slot:cell(source_files)="row">
          <p v-for="item in row.item.source_files" v-bind:key="item.id">
            <a :href="item.source_file_url" target="_blank">{{ item.source_file_name }}</a>
          </p>
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
        v-if="importHistoryList && importHistoryList.count > $route.query.limit && !isLoading"
        :total-rows="importHistoryList.count || 0"
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
import _ from 'lodash'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import DatePicker from 'vue2-datepicker'
import 'vue2-datepicker/index.css'
import toastMixin from '@/components/common/toastMixin'

export default {
  name: 'PFImportHistoryModule',
  data() {
    return {
      listOfshippingInvoicesFields: [
        { key: 'id', label: 'Import ID', tdClass: 'align-middle' },
        { key: 'module_label', label: 'Import Type', tdClass: 'align-middle' },
        { key: 'created', labedl: 'Import Date', tdClass: 'align-middle' },
        { key: 'username', label: 'Username', tdClass: 'align-middle net-charge-col' },
        { key: 'file.name', label: 'File Name', tdClass: 'align-middle' },
        { key: 'status', label: 'Processing Status', tdClass: 'align-middle' },
        { key: 'progress', label: 'Progress', tdClass: 'align-middle' },
        { key: 'row_count', label: 'Row Count', tdClass: 'align-middle' },
        { key: 'row_processed', label: 'Row Processed', tdClass: 'align-middle' },
        { key: 'row_errors', label: 'Row Errored', tdClass: 'align-middle' },
        { key: 'entries_created', label: 'Entries Created', tdClass: 'align-middle' },
        { key: 'entries_modified', label: 'Entries Modified', tdClass: 'align-middle ', thClass: 'text-left' },
        { key: 'entries_ignored', label: 'Entries Ignored', tdClass: 'align-middle status-col' }
      ],
      params: {
        page: 1,
        limit: 10,
        key: '',
        status: null,
        type: null,
        fieldSearch: 'All'
      },
      isLoading: true,
      importHistoryStatusOptions: [
        { text: 'All', value: null },
        { text: 'Uploading', value: 'uploading' },
        { text: 'Uploaded', value: 'uploaded' },
        { text: 'Validated', value: 'validated' },
        { text: 'Validating', value: 'validating' },
        { text: 'Processing', value: 'processing' },
        { text: 'Processed', value: 'processed' }
      ],
      importHistoryTypeOptions: this.importModuleKeys,
      permissions,
      currentExportPercent: 0,
      exportShipmentBreaksTimer: null,
      downloadInfo: {},
      isProgressingExport: false,
      invoiceDateRange: [null, null]
    }
  },
  components: { DatePicker },
  mixins: [
    PermissionsMixin,
    toastMixin
  ],
  computed: {
    ...mapGetters({
      importHistoryList: `pf/fedex/importHistoryList`,
      importModuleKeys: `pf/fedex/importModuleKeys`,
      currentExportShipmentBreaksId: `pf/fedex/currentExportShipmentBreaksId`,
      getUserId: `ps/userModule/GET_USER_ID`
    }),
    fromDateFormat() {
      return this.invoiceDateRange[0] ? this.$moment(this.invoiceDateRange[0]).format('YYYY-MM-DD') : ''
    },
    toDateFormat() {
      return this.invoiceDateRange[1] ? this.$moment(this.invoiceDateRange[1]).format('YYYY-MM-DD') : ''
    },
    formatDate() {
      return date => {
        return this.$moment(date).format('MM/DD/YYYY hh:mm A z')
      }
    },
    highlightNumber() {
      return (type, isBold) => {
        return type > 0 ? isBold ? 'text-danger font-weight-bold' : 'text-danger' : ''
      }
    },
    importModuleKeysOption() {
      return this.importModuleKeys
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
      getImportHistoryList: `pf/fedex/getImportHistoryList`,
      getImportModuleKeys: `pf/fedex/getImportModuleKeys`
    }),
    ...mapMutations({
      setEmptyImportHistoryList: `pf/fedex/setEmptyImportHistoryList`
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
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, type: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat, field_search: this.params.fieldSearch } })
    },
    async changeOptions() {
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, type: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
    },
    async goToPage(event) {
      this.isLoading = true
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
      this.isLoading = false
    },
    async handleQueryData() {
      this.setEmptyImportHistoryList([])
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        key: this.params.key,
        status: this.$route.query.status,
        type: this.$route.query.type,
        sortDirection: this.$route.query.sortDirection,
        sortField: this.$route.query.sortField,
        fromDate: this.fromDateFormat,
        toDate: this.toDateFormat,
        fieldSearch: this.$route.query.field_search
      }
      let data = _.pickBy({ ...payload }, _.identity)
      try {
        this.isLoading = true
        await this.getImportHistoryList(data)
      } catch (err) {
        console.log('err', err)
      } finally {
        this.isLoading = false
      }
    },
    handleSortFedex(context) {
      this.$router.push({query: { ...this.$route.query, sortDirection: context.sortDesc ? 'desc' : 'asc', sortField: context.sortBy }})
    },
    closeRequireModal() {
      this.$bvModal.hide('confirm-modal')
    },
    async changeImportDate(date) {
      if (date[0] && date[1]) {
        await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, type: this.params.source, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
        this.handleQueryData()
      } else {
        await this.$router.push({
          name: 'PFImportHistory',
          params: { client_id: this.$route.params.client_id },
          query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search || this.params.key, status: this.$route.query.status || this.params.status, type: this.$route.query.type || this.params.source }
        })
      }
    },
    checkWithinOneMonth(fromDate, toDate) {
      const diff = this.$moment(toDate).diff(this.$moment(fromDate), 'months', true)
      if (diff >= 0 & diff <= 1) return true
      else return false
    },
    upperCaseFirstLetter(word) {
      return word[0].toUpperCase() + word.substr(1)
    }
  },
  async created() {
    this.params.key = this.$route.query.search || ''
    this.params.status = this.$route.query.status || null
    this.params.source = this.$route.query.type || null
    this.params.fieldSearch = this.$route.query.field_search || 'All'
    this.invoiceDateRange[0] = this.$route.query.from_date ? this.$moment(this.$route.query.from_date).toDate() : null
    this.invoiceDateRange[1] = this.$route.query.to_date ? this.$moment(this.$route.query.to_date).toDate() : null
    if (this.$route.query.limit && this.$route.query.page) {
      await this.handleQueryData()
    } else {
      await this.$router.push({
        name: 'PFImportHistory',
        params: { client_id: this.$route.params.client_id },
        query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search || this.params.key, status: this.$route.query.status || this.params.status, type: this.$route.query.type || this.params.source }
      })
    }
    await this.getImportModuleKeys({ client_id: this.$route.params.client_id })
  },
  watch: {
    async $route(to, from) {
      this.params.key = this.$route.query.search || ''
      await this.handleQueryData()
    }
  },
  beforeDestroy() {
    clearInterval(this.exportShipmentBreaksTimer)
  }
}
</script>

<style lang="scss" scoped>
/deep/ .net-charge-col {
  width: 100px;
}
/deep/ .status-col {
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
  width: 100%;
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
.total-count-text {
  font-size: 16px;
  font-weight: 500;
}
::v-deep .mx-input, .form-select-custom {
  border-radius: 8px !important;
  box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.05);
  border: solid 1px #d0d5dd !important;
}
.card-body {
  padding-bottom: 0;
}
</style>
