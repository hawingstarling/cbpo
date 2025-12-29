<template>
  <b-card class="card-custom">
    <div class="reports">
      <div class="mb-1 header">
        <div>
          <h5 class="mb-0">
            Reports
          </h5>
        </div>
        <div class="today">
          <span>{{todayFormat}}</span>
        </div>
      </div>
      <b-row class="row-wrapper">
        <div class="d-flex justify-content-start align-items-center">
          <div class="row-custom">
            <div class="column column-0">
              <div class="space-column flex-fill">
                <MultiDropdown
                  class="select-layout"
                  label="Report Type"
                  v-model="currentReportCategory"
                  :options="optionsReportCategory"
                  :text="getNameReportCategory"
                  :default="defaultReportCategory"
                ></MultiDropdown>
              </div>
            </div>
            <div class="column column-0">
              <b-button-group class="flex-fill">
                <div class="warp-save flex-fill">
                  <div class="d-flex align-items-start flex-fill">
                    <div class="space-column flex-fill">
                      <ComplexRangeDatepickerForReport
                        class="d-flex justify-content-center select-date"
                        v-model="currentDateQuery"
                        :currentQueryObj="currentQuery"
                      ></ComplexRangeDatepickerForReport>
                    </div>
                  </div>
                </div>
              </b-button-group>
            </div>
            <div class="column-2">
              <b-button @click="generateReport()" variant="primary" size="sm" title="Run Report" class="btn-generate"></b-button>
              <b-button @click="refreshReport()" variant="primary" size="sm" title="Refresh" class="mr-3 btn-refresh"></b-button>
            </div>
          </div>
        </div>
      </b-row>
      <b-row class="row-wrapper">
        <b-table class="fedex-table" @sort-changed="sortChanged" :no-local-sorting="true" outlined striped head-variant="light" :items="reportsList.results" :fields="listOfReportFields" show-empty>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>
            &nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no report to show.</div>
          </div>
        </template>
        <template v-slot:cell(download_urls)="row">
          <b-button v-if="isReportV2SettlementReportDataFlatFileV2(row.item.report_type.value)" @click="showDownloadFilesModal(row.item)" variant="primary" :disabled="row.item.status !== 'Ready'" class="btn-source" >Download</b-button>
          <b-button v-else variant="primary" :disabled="row.item.status !== 'Ready'" class="btn-source" @click="downloadAll(row.item.download_urls, row.item.report_type.name)">Download</b-button>
        </template>
        <template v-slot:cell(date_completed)="row">
          {{row.item.date_completed | moment("MM/DD/YYYY hh:mm A")}}
        </template>
        <template v-slot:cell(batch_ids)="row">
          <p class="mb-1" v-for="batchId in row.item.batch_ids" :key="batchId">{{ batchId }}</p>
        </template>
        <template v-slot:cell(date_requested)="row">
          {{row.item.date_requested | moment("MM/DD/YYYY hh:mm A")}}
        </template>
        <template v-slot:cell(status)="row">
          <div class="label-status" :id="`popover-${row.item.id}`">{{row.item.status}}</div>
          <b-popover v-if="row.item.status === 'Cancelled' || row.item.status === 'Error'" :target="`popover-${row.item.id}`" triggers="hover" placement="top">
            <template #title>Error message</template>
            <strong>Retry:</strong> {{ row.item.retry }} <br/>
            <strong>Message:</strong> {{ row.item.msg_error }}
          </b-popover>
        </template>
        <template v-slot:cell(date_range_covered)="row">
          {{row.item.date_range_covered_start | moment("MM/DD/YYYY hh:mm A") }} - {{row.item.date_range_covered_end | moment("MM/DD/YYYY hh:mm A") }}
        </template>
      </b-table>
      <nav class="d-flex justify-content-center w-100">
        <b-pagination
          @change="goToPage($event)"
          v-if="reportsList && reportsList.count > $route.query.limit && !isLoading"
          :total-rows="reportsList.count || 0"
          v-model="$route.query.page"
          :per-page="$route.query.limit"
          hide-goto-end-buttons
        >
          <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
          <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
        </b-pagination>
      </nav>
      </b-row>
      <b-modal id="download-files-modal" centered hide-footer title="Download files">
        <p v-for="(item, index) in currentReport.download_urls" :key="item" class="modal-download-item" @click="downloadAll([item], currentReport.report_type.name)">
          <img src="@/assets/img/icon/download-blue.svg" class="mr-2"> {{ currentReport.file_names[index] }}
        </p>
      </b-modal>
    </div>
  </b-card>
</template>

<script>
// lib
import {mapActions, mapGetters, mapState} from 'vuex'
import { StaticExpression } from 'plat-sdk'
import isEmpty from 'lodash/isEmpty'
// mixins
import baseQueryMixins from '@/mixins/baseQueryMixins'
import toastMixin from '@/components/common/toastMixin'

// components
import MultiDropdown from '@/components/common/MultiDropdown/MultiDropdown'
import ComplexRangeDatepickerForReport from '@/components/common/ComplexRangeDatepicker/ComplexRangeDatepickerForReport'
import { REPORT_CATEGORIES } from '@/shared/constants'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'
import PermissionsMixin from '@/components/common/PermissionsMixin'

export default {
  name: 'PFReports',
  components: {
    MultiDropdown,
    ComplexRangeDatepickerForReport
  },
  data() {
    const thClassTextCenter = 'align-middle text-center'
    const tdClassTextCenter = 'align-middle text-center'
    return {
      isLoading: true,
      configInitialized: false,
      currentReportCategory: '',
      listOfReportFields: [
        { key: 'report_type.name', label: 'Report Type', tdClass: 'align-middle', sortable: true, thClass: thClassTextCenter },
        { key: 'batch_ids', label: 'Batch ID', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'date_range_covered', label: 'Date Range Covered', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'date_requested', label: 'Date and Time Requested', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'date_completed', label: 'Date and Time Completed', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'status', label: 'Report Status', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter },
        { key: 'download_urls', label: 'Downloads', tdClass: tdClassTextCenter, sortable: true, thClass: thClassTextCenter }
      ],
      currentQuery: {},
      currentDateQuery: null,
      sortBy: null,
      sortDirection: null,
      currentReport: {}
    }
  },
  mixins: [ baseQueryMixins, toastMixin, spapiReconnectAlertMixin, PermissionsMixin ],
  computed: {
    ...mapGetters({
      reportCategoriesList: 'pf/reports/reportCategoriesList'
    }),
    ...mapState('pf/reports', [
      'reportsList'
    ]),
    todayFormat() {
      return this.$moment().format('dddd, MMMM Do, YYYY')
    },
    optionsReportCategory() {
      return this.reportCategoriesList
    },
    defaultReportCategory() {
      return this.reportCategoriesList[0] && this.reportCategoriesList[0].value
    },
    params() {
      return {
        clientId: this.$route.params.client_id
      }
    },
    getNameReportCategory () {
      return this.currentReportCategory ? this.currentReportCategory.text : 'Select Report Type'
    },
    isReportV2SettlementReportDataFlatFileV2 () {
      return reportType => reportType === REPORT_CATEGORIES.getV2SettlementReportDataFlatFileV2
    }
  },
  methods: {
    ...mapActions({
      getReportsList: 'pf/reports/getReportsList',
      getReportCategoriesList: 'pf/reports/getReportCategoriesList',
      generateReports: 'pf/reports/generateReports'
    }),
    async queryData() {
      try {
        this.isLoading = true
        const params = this.params
        const query = {
          page: this.$route.query.page,
          limit: this.$route.query.limit,
          sort_field: this.sortBy,
          sort_direction: this.sortDirection
        }
        await this.getReportsList({
          params,
          query
        })
      } catch (err) {
        this.vueToast('error', 'Get list report failed. Please retry or contact administrator.')
      }
      this.isLoading = false
    },
    async goToPage(event) {
      this.isLoading = true
      if (this.$route.query.page !== event) {
        await this.$router.replace({ query: { ...this.$route.query, page: event } })
      }
      this.isLoading = false
    },
    downloadAll(urls) {
      let delay = 0
      for (var i = 0; i < urls.length; i++) {
        let link = document.createElement('a')
        link.setAttribute('download', null)
        link.style.display = 'none'
        link.setAttribute('href', urls[i])
        document.body.appendChild(link)
        link.click()
        setTimeout(() => link.click(), delay)
        delay += 1000
        document.body.removeChild(link)
      }
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
    async refreshReport() {
      await this.queryData()
    },
    async generateReport() {
      if (!this.currentReportCategory) {
        this.vueToast('warning', 'Please select report type.')
        return
      }
      if (isEmpty(this.currentDateQuery) && this.currentReportCategory.key !== REPORT_CATEGORIES.getV2SettlementReportDataFlatFileV2) {
        this.vueToast('warning', 'Please select date range.')
        return
      }
      if (!isEmpty(this.currentDateQuery) && this.$moment(this.currentDateQuery[1]).diff(this.$moment(this.currentDateQuery[0]), 'days') > 30) {
        this.vueToast('warning', 'Please select a date range no more than 30 days.')
        return
      }
      // SPAPI report Flat File V2 Settlement without date range covered
      if (this.currentReportCategory.key === REPORT_CATEGORIES.getV2SettlementReportDataFlatFileV2 && !isEmpty(this.currentDateQuery)) {
        this.vueToast('warning', `Please not select the date range with the report type: ${this.currentReportCategory.text}`)
        this.currentDateQuery = null
        return
      }
      try {
        this.isLoading = true
        const params = this.params
        let query = {
          channel: 'amazon.com',
          report_type: this.currentReportCategory.value
        }
        if (this.currentReportCategory.key !== REPORT_CATEGORIES.getV2SettlementReportDataFlatFileV2) {
          query = {
            ...query,
            date_range_covered_start: StaticExpression.isValid(this.currentDateQuery[0]) ? this.$moment(StaticExpression.eval(this.currentDateQuery[0])).format('YYYY-MM-DD') : this.currentDateQuery[0],
            date_range_covered_end: StaticExpression.isValid(this.currentDateQuery[1]) ? this.$moment(StaticExpression.eval(this.currentDateQuery[1])).format('YYYY-MM-DD') : this.currentDateQuery[1]
          }
        }
        await this.generateReports({
          params,
          query
        })
        this.vueToast('success', 'Generate Report successfully')
        await this.queryData()
      } catch (err) {
        if (err.response.data.code === 3000) {
          this.vueToast('success', 'Report is already existing.')
        } else {
          this.vueToast('error', 'Generate report failed. Please retry or contact administrator.')
        }
      }
      this.isLoading = false
    },
    async sortChanged(e) {
      this.sortBy = e.sortBy
      this.sortDirection = e.sortDesc ? 'desc' : 'asc'
      await this.queryData()
    },
    showDownloadFilesModal(item) {
      this.currentReport = item
      this.$bvModal.show('download-files-modal')
    }
  },
  async created() {
    this.$router.replace({
      name: 'PFReports',
      params: { client_id: this.$route.params.client_id },
      query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10 }
    })
    await this.getReportCategoriesList({ clientId: this.$route.params.client_id })
    await this.queryData()
  },
  watch: {
    async $route(to, from) {
      if (from.fullPath !== to.fullPath) {
        await this.queryData()
      }
    },
    currentDateQuery() {
      if (this.currentReportCategory && this.currentReportCategory.key === REPORT_CATEGORIES.brandsSummaryMonthlyDataReport) {
        if (this.currentDateQuery[0] !== "DATE_START_OF(DATE_LAST(1,'month'), 'month')" && this.currentDateQuery[1] !== "DATE_END_OF(DATE_LAST(1,'month'), 'month')") {
          this.currentDateQuery = ["DATE_START_OF(DATE_LAST(1,'month'), 'month')", "DATE_END_OF(DATE_LAST(1,'month'), 'month')"]
        }
      }
    },
    currentReportCategory() {
      if (this.currentReportCategory && this.currentReportCategory.key === REPORT_CATEGORIES.brandsSummaryMonthlyDataReport) {
        this.currentDateQuery = ["DATE_START_OF(DATE_LAST(1,'month'), 'month')", "DATE_END_OF(DATE_LAST(1,'month'), 'month')"]
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';
.header {
  padding-left: 25px;
  padding-right: 25px;
}
.btn-source {
  @include button-icon(true, 'download-blue.svg', 20px, 20px);
}
.row-wrapper {
  padding: 40px;
  padding-bottom: 0;
}

::v-deep .column-2 {
  .btn.btn-generate {
    @include button-color(#91E4AB);
  }
  .btn.btn-refresh {
    @include button-color(#D5D9DF
);
  }
}
.btn-refresh {
  padding: 8px 8px !important;
  height: 36px;
  @include button-icon(true, 'refresh.svg', 20px, 20px);
  &::before {
    margin: 0;
  }
}
.btn-generate {
  @include button-icon(true, 'generate.svg', 16px, 16px);
  background-color: #91E4AB !important;
  height: 40px;
  color: #FFFFFF;
  padding: 8px 10px !important;
  font-weight: 600;
  font-size: 12px;
  line-height: 16px;
  height: 36px;
  border: 1px solid #146EB4;
  margin-right: 10px;
  box-shadow: 0px 1px 2px rgba(16, 24, 40, 0.05);
  i {
    font-size: 16px;
  }
  &::before {
    margin: 0;
  }
}
.row-custom {
  display: flex;
  /* justify-content: flex-end; */
  align-items: flex-end;
  width: 100%;
  flex-wrap: wrap;

  .column {
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 240px;

    .space-column {
      padding-right: 18px;
    }
  }
}

::v-deep .select-dropdown .dropdown-toggle i {
    padding-left: 8px
}

::v-deep .select-layout .show > .btn-secondary.dropdown-toggle {
  background-color: #F2F4F7 !important;
}
::v-deep .dropdown-item {
  overflow: hidden;
  text-overflow: ellipsis;
  display: block !important;
  padding: 8px 25px 8px 10px !important;
  i {
    position: absolute;
    right: 5px;
  }
}
.label-status {
  cursor: pointer;
}
.modal-download-item {
  cursor: pointer;
  &:last-child {
    margin-bottom: 0;
  }
  &:hover {
    text-decoration: underline;
  }
}
::v-deep #download-files-modal {
  .modal-dialog {
    max-width: 340px !important;
  }
}

::v-deep .btn-primary.disabled, .btn-primary:disabled {
  background-color: #F4F6F9 !important;
  border-color: #254164 !important;
  color: #254164 !important;
  &::before {
    background-color: #254164 !important;
  }
}
</style>
