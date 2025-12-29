<template>
  <b-card class="fedex">
    <!-- search -->
    <b-row class="filter-control justify-content-center align-items-center">
      <b-col md="10" class="justify-content-center mt-0 mb-1 d-flex col-md-8">
<!--        <div class="pr-1 col-3 d-flex flex-wrap">-->
<!--          <span class="d-flex align-items-center mr-1 title-filter">Type</span>-->
<!--          <b-form-select class="form-select-custom" v-model="params.source" :options="importModuleKeysOption" @change="changeOptions()"> </b-form-select>-->
<!--        </div>-->
        <div class="filter-control__status">
          <div class="d-flex flex-wrap">
            <span class="d-flex align-items-center title-filter">Status</span>
            <b-form-select class="form-select-custom" v-model="params.status" :options="importHistoryStatusOptions"
                           @change="changeOptions()"></b-form-select>
          </div>
        </div>
        <div class="filter-control__date">
          <div class="d-flex flex-wrap">
            <span class="d-flex align-items-center title-filter">Import Date</span>
            <date-picker v-model="invoiceDateRange" @input="changeImportDate" format="MM-DD-YYYY" range-separator=" - "
                         range>
              <template slot="icon-calendar">
                <img src="@/assets/img/icon/date-icon.png">
              </template>
            </date-picker>
          </div>
        </div>
        <b-form-group class="filter-control__search d-flex flex-wrap">
          <b-input-group class="search cancel-action form-search-custom">
            <span class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</span>
            <b-form-input class="input-search form-search-input custom-form-brand" v-model="params.key" @keypress.enter="searchChange()" placeholder="Search for keywords">
            </b-form-input>
            <i v-if="params.key" @click="params.key='', searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
            <div class="form-search-icon" @click="searchChange()">
              <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
            </div>
          </b-input-group>
        </b-form-group>
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
<!--      <b-col md="2" class="mt-0 mb-4 d-flex justify-content-center">-->
<!--        <span v-if="importHistoryList && importHistoryList.count" class="ml-1 total-count-text">Total Count: {{ importHistoryList.count | numeral}}</span>-->
<!--      </b-col>-->
    </b-row>
    <div class="overflow-auto w-100">
      <b-table :no-local-sorting="true" outlined striped head-variant="light" :items="importHistoryList.results" :fields="listOfshippingInvoicesFields" show-empty>
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
          {{ upperCaseFirstLetter(row.item.status)}}
        </template>
        <template v-slot:cell(progress)="row">
          {{row.item.progress}}%
        </template>
        <template v-slot:cell(row_count)="row">
          {{Intl.NumberFormat().format(row.item.row_count)}}
        </template>
        <template v-slot:cell(created)="row">
          {{ formatDate(row.item.created) }}
        </template>
        <template v-slot:cell(id)="row">
          <router-link :to="{ name: 'PFStep4ResultFedex', params: { import_id: row.item.id, module: row.item.module } }">
            {{ row.item.id }}
          </router-link>
        </template>
        <template v-slot:cell(source_files)="row">
          <b-button v-if="row.item.file.url" class="btn-source" variant="primary" @click="handleClickDownloadFile(row.item.file.url, row.item.file.name)">Source</b-button>
        </template>
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
<!--    <div v-if="isProgressingExport" id="progress-bar">-->
<!--      <div style="width:500px" class="d-flex align-items-center">-->
<!--        <span class="mr-2 text-nowrap">Download progress:</span>-->
<!--        <b-progress :max="100" class="w-100" show-progress>-->
<!--          <b-progress-bar class="text-dark" :value="currentExportPercent">{{ currentExportPercent ? currentExportPercent : 0}}%</b-progress-bar>-->
<!--        </b-progress>-->
<!--      </div>-->
<!--    </div>-->
<!--    <div v-if="Object.keys(downloadInfo).length > 0" id="completed-export">-->
<!--        <span class="text-dark">Bingo! Please download the file-->
<!--          <b-button size="sm" variant="primary" @click="downloadFile(downloadInfo)">Download</b-button>-->
<!--        </span>-->
<!--    </div>-->
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import pickBy from 'lodash/pickBy'
import identity from 'lodash/identity'
import { numeral } from '@/shared/filters'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import DatePicker from 'vue2-datepicker'
import 'vue2-datepicker/index.css'
import toastMixin from '@/components/common/toastMixin'

export default {
  name: 'PFShippingInvoiceHistoryModule',
  data() {
    const commonThClass = 'text-center align-middle'
    const commonTdClass = 'text-center align-middle'
    return {
      listOfshippingInvoicesFields: [
        { key: 'id', label: 'Import ID', tdClass: commonTdClass, thClass: commonThClass },
        // { key: 'module_label', label: 'Import Type', tdClass: 'align-middle' },
        { key: 'created', labedl: 'Import Date', tdClass: commonTdClass, thClass: commonThClass },
        { key: 'username', label: 'Username', tdClass: commonTdClass, thClass: commonThClass },
        { key: 'source_files', label: 'File Name', tdClass: `${commonTdClass} status-col d-flex justify-content-center`, thClass: commonThClass },
        // { key: 'file.name', label: 'File Name', tdClass: 'align-middle', thClass: commonThClass },
        { key: 'status', label: 'Processing Status', tdClass: commonTdClass, thClass: commonThClass },
        { key: 'progress', label: 'Progress', tdClass: commonTdClass, thClass: commonThClass },
        { key: 'row_count', label: 'Row Count', tdClass: 'align-middle text-right', thClass: 'align-middle text-right' }
        // { key: 'row_processed', label: 'Row Processed', tdClass: 'align-middle', thClass: commonThClass },
        // { key: 'row_errors', label: 'Row Errored', tdClass: 'align-middle', thClass: commonThClass },
        // { key: 'entries_created', label: 'Entries Created', tdClass: 'align-middle' },
        // { key: 'entries_modified', label: 'Entries Modified', tdClass: 'align-middle ', thClass: 'text-left' },
        // { key: 'entries_ignored', label: 'Entries Ignored', tdClass: 'align-middle status-col' }
      ],
      params: {
        page: 1,
        limit: 10,
        key: '',
        status: null,
        // type: null,
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
      // importHistoryTypeOptions: this.importModuleKeys,
      permissions,
      // currentExportPercent: 0,
      // exportShipmentBreaksTimer: null,
      // downloadInfo: {},
      // isProgressingExport: false,
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
      // importModuleKeys: `pf/fedex/importModuleKeys`,
      // currentExportShipmentBreaksId: `pf/fedex/currentExportShipmentBreaksId`,
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
    }
    // importModuleKeysOption() {
    //   return this.importModuleKeys
    // }
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
      getImportHistoryList: `pf/fedex/getImportHistoryList`
      // getImportModuleKeys: `pf/fedex/getImportModuleKeys`
    }),
    ...mapMutations({
      setEmptyImportHistoryList: `pf/fedex/setEmptyImportHistoryList`
    }),
    // Function search
    async searchChange() {
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, from_date: this.fromDateFormat, to_date: this.toDateFormat, field_search: this.params.fieldSearch } })
    },
    async changeOptions() {
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.params.key, status: this.params.status, from_date: this.fromDateFormat, to_date: this.toDateFormat } })
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
        type: 'FedExShipmentModule',
        sortDirection: this.$route.query.sortDirection,
        sortField: this.$route.query.sortField,
        fromDate: this.fromDateFormat,
        toDate: this.toDateFormat,
        fieldSearch: this.$route.query.field_search
      }
      let data = pickBy({ ...payload }, identity)
      try {
        this.isLoading = true
        await this.getImportHistoryList(data)
      } catch (err) {
        console.log('err', err)
      } finally {
        this.isLoading = false
      }
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
    handleClickDownloadFile(url, fileName) {
      const a = document.createElement('a')
      a.href = url
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    },
    upperCaseFirstLetter(word) {
      return word[0].toUpperCase() + word.substr(1)
    }
  },
  async created() {
    this.params.key = this.$route.query.search || ''
    this.params.status = this.$route.query.status || null
    // this.params.source = this.$route.query.type || null
    this.params.fieldSearch = this.$route.query.field_search || 'All'
    this.invoiceDateRange[0] = this.$route.query.from_date ? this.$moment(this.$route.query.from_date).toDate() : null
    this.invoiceDateRange[1] = this.$route.query.to_date ? this.$moment(this.$route.query.to_date).toDate() : null

    if (this.$route.query.limit && this.$route.query.page) {
      await this.handleQueryData()
    } else {
      await this.$router.push({
        name: 'PFShippingInvoiceHistory',
        params: {client_id: this.$route.params.client_id},
        query: {
          page: this.$route.query.page || 1,
          limit: this.$route.query.limit || 10,
          search: this.$route.query.search || this.params.key,
          status: this.$route.query.status || this.params.status
          // type: this.$route.query.type || this.params.source
        }
      })
    }
  },
  watch: {
    async $route(to, from) {
      this.params.key = this.$route.query.search || ''
      await this.handleQueryData()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

.table-border-radius {
  border-top-left-radius: 5px;
  border-top-right-radius: 5px;
  overflow: hidden;
}

.filter-control {
  div {
    padding-right: 8px;
  }

  span {
    color: #232F3E !important;
  }

  ::v-deep input, select {
    box-shadow: unset !important;
  }

  &__status {
    width: 180px;

    ::v-deep select {
      height: 36px !important;
      min-height: unset !important;
    }
  }

  &__date {
    width: 180px;

    div:first-child {
      width: 180px !important;
    }

    ::v-deep input {
      height: 36px !important;
      min-height: unset;
    }

    ::v-deep .mx-datepicker {
      .mx-icon-calendar {
        right: unset !important;
        left: 8px;
      }
    }
  }

  &__search {
    width: 252px;

    ::v-deep input {
      height: 36px !important;
      width: 252px !important;
      min-height: unset;
    }
  }
  }

::v-deep .status-col {
  text-transform: capitalize;
}

.btn-source {
  @include button-icon(false, 'download-blue.svg', 20px, 20px);
}
::v-deep .mx-input-wrapper {
  .mx-input {
    padding: 6px 30px;
  }
}
.form-search-custom {
  .form-cancel-icon {
    right: 18px !important;
  }
}
</style>
