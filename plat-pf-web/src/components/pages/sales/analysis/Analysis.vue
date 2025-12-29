<template>
  <b-card class="card-custom">
    <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="!isReady">
      <div class="spinner-border thin-spinner spinner-border-sm cls-loading-analysis"></div>&nbsp;Loading...
    </div>
    <div v-if="isReady" class="analysis">
      <div class="mb-1">
        <div>
          <h5 class="mb-0">
            {{ sdkConfig.widget.title.text }}
          </h5>
        </div>
        <div class="today">
          <span>{{ todayFormat }}</span>
        </div>
      </div>
      <b-row class="row-wrapper">
        <b-col class="d-flex justify-content-end align-items-center">
          <div class="row-custom">
            <div class="column column-0">
              <div class="pr-2 flex-fill">
                <SelectInput class="select-layout layer-overlay-2000" label="Table Layout" v-model="currentView" :options="optionsView"
                  :default="defaultView"></SelectInput>
              </div>
            </div>
            <div class="column column-1">
              <b-button-group class="flex-fill">
                <div class="warp-save flex-fill">
                  <div class="d-flex align-items-end flex-fill">
                    <div class="pr-2 flex-fill" v-if="channelOptions.length">
                      <SelectInput class="select-sale-channel layer-overlay-2000" label="Sales Channel" v-model="currentChannel"
                        :options="channelOptions" :ignoreState="sdkConfig.filter.builder.config.ignore"
                        @change="onChangeBaseQuery" />
                    </div>
                    <div class="pr-2 flex-fill">
                      <ComplexRangeDatepicker class="d-flex justify-content-center select-date"
                        :ignoreState="sdkConfig.filter.builder.config.ignore" v-model="currentDateQuery"
                        :currentQueryObj="currentQuery" @onChangeDate="onChangeBaseQuery"></ComplexRangeDatepicker>
                    </div>
                  </div>
                  <div v-if="filterCurrentExpression" class="
                    item-load
                    d-flex
                    load-save-condition-for-filter
                    mr-1
                    rounded
                    position-absolute
                  "
                    v-b-popover.hover="{ html: true, content: filterCurrentExpression, customClass: 'customPopover', placement: 'bottom' }">
                    <template class="load-save-condition">
                      <span class="overflow-hidden filter-expr">
                        <div class="text-truncate">
                          <i class="fa fa-gears mr-1"></i>
                          <span v-html="filterCurrentExpression"> </span>
                        </div>
                      </span>
                    </template>
                  </div>
                </div>
              </b-button-group>
            </div>
            <div class="column column-2">
              <b-button-group class="mr-2 flex-fill">
                <div class="warp-save flex-fill">
                  <div class="d-flex">
                    <div class="pr-2 flex-fill">
                      <CommonFilter :ignoreState="sdkConfig.filter.builder.config.ignore" v-model="currentCommonFilter"
                        @change="onChangeBaseQuery" />
                    </div>
                    <div class="
                      d-flex
                      justify-content-center
                      align-items-center
                      pr-2
                    ">
                      <cbpo-builder-filter class="d-flex" v-if="configInitialized" :key="sdkUniqueState"
                        :elements="sdkConfig.elements" :configObj.sync="getConfigObj" @filterChange="updateFilter"
                        @updateItems="handleUpdateItemsQueryBuilder" :updateItemsObj.sync="updateItemsQueryBuilder">
                        <template v-slot:button="{ openModal, isFieldsReady }">
                          <b-button :disabled="!enabledFeature('filter') ||
                            !isFilterReady ||
                            !isFieldsReady
                            " @click="openModal" text="Small" size="sm" variant="success"
                            class="d-flex align-items-center justify-content-center">
                            <img src="@/assets/img/icon/filter-icon.svg" alt="filter-icon">
                          </b-button>
                        </template>
                      </cbpo-builder-filter>
                    </div>
                    <div>
                      <cbpo-manage-columns :key="sdkUniqueState" v-if="configInitialized"
                        :columns="getColumnsForColumnManager" :configObj.sync="sdkConfig.columnManager.config"
                        @input="handleUpdateColumns">
                        <template v-slot:button="{ openModal }">
                          <b-button :disabled="!enabledFeature('columnSet')" @click="openModal" text="Small" size="sm"
                            variant="success" class="d-flex align-items-center justify-content-center">
                            <img src="@/assets/img/icon/manage-columns.svg" alt="">
                          </b-button>
                        </template>
                      </cbpo-manage-columns>
                    </div>
                  </div>
                  <div v-if="columnSetCurrentExpression" class="
                    item-load
                    d-flex
                    load-save-condition
                    mr-1
                    rounded
                    position-absolute
                  " v-b-popover.hover.bottom.html="columnSetCurrentExpression">
                    <template>
                      <span class="overflow-hidden">
                        <div class="text-truncate">
                          <span v-html="columnSetCurrentExpression"> </span>
                        </div>
                      </span>
                    </template>
                  </div>
                </div>
              </b-button-group>
            </div>
            <div class="column column-4">
              <b-button-group class="mr-1">
                <div class="warp-save">
                  <div v-if="viewName" class="item-load name overflow-hidden d-flex" v-b-popover.hover.top="viewName">
                    <span class="text-truncate"><i class="fa fa-hashtag"></i> {{ viewName }}</span>
                  </div>
                  <div>
                    <b-dropdown text="Views" right variant="secondary" size="sm" :disabled="!hasPermission(permissions.view.edit) &&
                      !hasPermission(permissions.view.create) &&
                      !hasPermission(permissions.view.delete)
                      " class="drop-down-view--custom">
                      <template v-slot:button-content>
                        <span class="fa view-combine-icon mr-1">
                          <img class="mb-1" src="@/assets/img/icon/view-icon.svg" alt="view-icon">
                        </span>
                        Views
                      </template>
                      <b-dropdown-item v-if="canSave('view')">
                        <div @click="openModal('view')" :disabled="isViewPermission">
                          <i class="fa fa-save"></i> Save
                        </div>
                      </b-dropdown-item>
                      <b-dropdown-item v-if="
                        viewCopiable && hasPermission(permissions.view.create)
                      " @click="openModal('as-view')">
                        <i class="fa fa-clone"></i> Save as
                      </b-dropdown-item>
                      <b-dropdown-item v-if="
                        viewDiscardable &&
                        hasPermission(permissions.view.delete)
                      " @click="$bvModal.show(`discard-view-confirm-modal`)">
                        <i class="fa fa-reply-all"></i> Discard
                      </b-dropdown-item>
                      <b-dropdown-item v-if="hasPermission(permissions.view.create)" @click="handleResetAllToDefault"
                        :disabled="!viewRenewable && !columnSetRenewable && !filterRenewable">
                        <i class="fa fa-file-o"></i> Reset all to default
                      </b-dropdown-item>
                      <template v-if="
                        hasPermission(permissions.view.viewAll) ||
                        hasPermission(permissions.view.view24h)
                      ">
                        <b-dropdown-divider v-if="
                          (quickFavoriteSelectViews.length &&
                            canHaveDivider('view')) || hasSearchView
                        "></b-dropdown-divider>
                        <b-input-group v-if="hasSearchView" class="search-view">
                          <b-form-input class="border form-select rounded-left pr-4" size="sm" v-model.trim="searchView"
                            placeholder="Search by name, user" @keyup.enter="handleSearchView()">
                          </b-form-input>
                          <i class="fa fa-times-circle clear-keyword" v-if="searchView" @click="clearKeyword()"></i>
                          <b-input-group-append>
                            <button class="icon cursor-pointer search-view-btn" @click="handleSearchView()">
                              <i class="fa fa-search"></i>
                            </button>
                          </b-input-group-append>
                        </b-input-group>
                        <div class="align-items-center d-flex justify-content-center" v-if="isLoadingView">
                          <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
                        </div>
                        <div class="align-items-center d-flex justify-content-center"
                          v-if="!isLoadingView && !quickSelectViews.length && !quickFavoriteSelectViews.length">
                          <div>There are no views to show.</div>
                        </div>
                        <template v-if="!isLoadingView">
                          <template v-for="qView in quickFavoriteSelectViews">
                            <b-dropdown-item :key="'quick-filter-' + qView.id" class="filter-item">
                              <span @click="handleClickView(qView)" :class="{ 'active': qView.id === viewCopiable }">
                                <i class="fa fa-star text-warning" />{{ qView.name }} {{ showCreater(qView) }}
                              </span>
                              <div class="d-flex">
                                <button class="quick-filter__view" @click="setFilter(qView)">
                                  <i class="fa fa-filter" />
                                </button>
                                <button class="quick-filter__columns" @click="handleSetColumnSet(qView)">
                                  <i class="fa fa-columns" />
                                </button>
                              </div>
                            </b-dropdown-item>
                          </template>

                        </template>
                        <b-dropdown-divider
                          v-if="quickSelectViews.length && canHaveDivider('view') && !isLoadingView" />
                        <template v-if="!isLoadingView">
                          <template v-for="qView in quickSelectViews">
                            <b-dropdown-item :key="'quick-filter-' + qView.id" class="filter-item">
                              <span @click="handleClickView(qView)" :class="{ 'active': qView.id === viewCopiable }">
                                <i class="fa fa-hashtag" /> {{ qView.name }} {{ showCreater(qView) }}
                              </span>
                              <div class="d-flex">
                                <button class="quick-filter__view" @click="setFilter(qView)">
                                  <i class="fa fa-filter" />
                                </button>
                                <button class="quick-filter__columns" @click="handleSetColumnSet(qView)">
                                  <i class="fa fa-columns" />
                                </button>
                              </div>
                            </b-dropdown-item>
                          </template>
                        </template>
                        <b-dropdown-divider v-if="
                          viewList && viewList.count > quickSelectViews.length
                        "></b-dropdown-divider>
                        <b-dropdown-item v-if="
                          viewList && viewList.count > quickSelectViews.length
                        " v-b-modal.table-views><i class="fa fa-folder"></i> More views
                          ...</b-dropdown-item>
                      </template>
                    </b-dropdown>
                  </div>
                </div>
              </b-button-group>
            </div>
            <div class="column column-3">
              <BulkProgressDropdown />
            </div>
            <div class="column column-5">
              <b-button-group class="mr-2 ml-1">
                <div class="warp-save">
                  <b-button id="refresh-table-btn" variant="secondary" text="Small" size="sm" @click="refreshData()"
                    :disabled="!isFilterReady">
                    <img src="@/assets/img/icon/refresh-icon.svg" alt="">
                  </b-button>
                  <b-tooltip custom-class="custom-btn-tooltip" target="refresh-table-btn" triggers="hover"
                    placement="top">
                    Refresh Table
                  </b-tooltip>
                </div>
              </b-button-group>
              <div class="align-self-center">
                <div class="warp-save">
                  <div class="d-flex">
                    <b-button-group class="mr-2">
                      <b-button id="highlight-costs-and-fees-btn" :variant="isCheckHighlights ? 'danger' : 'secondary'"
                        :class="{ 'checked-highlight': isCheckHighlights }" text="Small" size="sm"
                        @click="checkHighlights">
                        <img src="@/assets/img/icon/highlight-icon.svg" alt="">
                      </b-button>
                      <b-tooltip custom-class="custom-btn-tooltip" target="highlight-costs-and-fees-btn"
                        triggers="hover" placement="bottom">
                        Highlight Costs and Fees
                      </b-tooltip>
                    </b-button-group>
                    <ViewMode :element="widgetElement" @calculateTableHeight="setContainerHeight()" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </b-col>
      </b-row>
      <div class="cbpo-widget-wrapper">
        <cbpo-widget class="none-table-border" ref="widgetSDK" :key="sdkUniqueState" @customExport="customExport"
          v-if="configInitialized" :configObj.sync="sdkConfig">
          <template v-slot:queryBuilder>
            <div class="d-none"></div>
          </template>
          <template v-slot:columnManager>
            <div class="d-none"></div>
          </template>
        </cbpo-widget>
      </div>
      <b-modal :id="modalId" :title="modalTitle" centered>
        <SaveModal ref="saveModal" :type="modalId" :callback="setSaveType()" :sdkConfig="sdkConfig"></SaveModal>
        <template v-slot:modal-footer>
          <div class="w-100">
            <b-button class="float-right" variant="primary" @click="handleSaveItem" :disabled="isSaving">Save</b-button>
            <b-button class="float-left" @click="handleCloseModal">Cancel</b-button>
          </div>
        </template>
      </b-modal>
      <b-modal id="table-views" title="Saved views" centered ok-only size="lg">
        <b-table outlined striped :fields="saveTableFields" :items="viewList.results" v-if="viewList">
          <template v-slot:cell(name)="row">
            <div>
              {{ row.item.name }}
              <i class="fa fa-star text-warning" v-if="row.item.featured" />
              {{ showCreater(row.item) }}
            </div>
          </template>
          <template v-slot:cell(actions)="row">
            <b-button class="d-flex align-items-center" variant="primary" text="Small" size="sm"
              @click="setView(row.item)"><i class="fa fa-check-circle mr-1"></i> Select</b-button>
          </template>
          <template v-slot:cell(preview)="row">
            <div @click="$bvModal.show(`preview-modal-${row.item.id}`)" class="alert alert-warning expr-table">
              <span class="overflow-hidden preview-content">
                <div v-html="getFilterExpr(row.item.ds_filter)"></div>
                <div class='h-75 text-truncate' v-html="getColumnSetExpr(row.item.ds_column.config.columns)"></div>
              </span>
            </div>
            <b-modal :id="`preview-modal-${row.item.id}`" centered title="Preview">
              <div>
                <div v-html="getFilterExpr(row.item.ds_filter)"></div>
                <div v-html="getColumnSetExpr(row.item.ds_column.config.columns)"></div>
              </div>
              <template v-slot:modal-footer>
                <b-button variant @click="$bvModal.hide(`preview-modal-${row.item.id}`)">
                  <i class="icon-close"></i> Close
                </b-button>
              </template>
            </b-modal>
          </template>
        </b-table>
        <nav class="d-flex justify-content-center">
          <b-pagination @click.native="goToPage('views')" v-if="viewList && viewList.count > pagingViews.limit"
            :total-rows="viewList.count || 0" :per-page="pagingViews.limit" v-model="pagingViews.page" prev-text="Prev"
            next-text="Next" hide-goto-end-buttons />
        </nav>
      </b-modal>
      <b-modal id="discard-filter-confirm-modal" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to discard this filter?</div>
        <template v-slot:modal-footer>
          <b-button variant="warning" @click="handleDiscardFilter()">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
          </b-button>
          <b-button variant @click="$bvModal.hide('discard-filter-confirm-modal')">
            <i class="icon-close"></i> No
          </b-button>
        </template>
      </b-modal>
      <b-modal id="discard-column-set-confirm-modal" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to discard this column set?</div>
        <template v-slot:modal-footer>
          <b-button variant="warning" @click="handleDiscardColumnSet()">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
          </b-button>
          <b-button variant @click="$bvModal.hide('discard-column-set-confirm-modal')">
            <i class="icon-close"></i> No
          </b-button>
        </template>
      </b-modal>
      <b-modal id="discard-view-confirm-modal" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to discard this view?</div>
        <template v-slot:modal-footer>
          <b-button variant="warning" @click="handleDiscardView()">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
          </b-button>
          <b-button variant @click="$bvModal.hide('discard-view-confirm-modal')">
            <i class="icon-close"></i> No
          </b-button>
        </template>
      </b-modal>
      <BulkEditModal id="bulk-edit-modal" :sdkID="sdkConfig.elements[0].config.id" :currentChannel="currentChannel"
        :dataRow="bulkEditableData" :columns="getColumnNames(sdkConfig.elements[0].config.columns)"
        :isCustomExport="isCustomExport" />
      <ConfirmationModal id="delete-modal" :sdkID="sdkConfig.elements[0].config.id" :dataRow="deletableData"
        :columns="getColumnNames(sdkConfig.elements[0].config.columns)" />
      <EditModal id="edit-modal" :sdkID="sdkConfig.elements[0].config.id" :currentChannel="currentChannel"
        :dataRow="editableData" :columns="getColumnNames(sdkConfig.elements[0].config.columns)"
        :timezone="sdkConfig.elements[0].config.timezone" />
      <ChangeLogModal id="changelog-modal" :dataRow="changelogData"
        :columns="getColumnNames(sdkConfig.elements[0].config.columns)" :timezone="timezoneCurrent" />
      <SyncModal id="sync-modal" :sdkID="sdkConfig.elements[0].config.id" :dataRow="syncData" />
      <ReturnLogModal id="returnlog-modal" :timezone="timezoneCurrent" :dataRow="returnLogData" />
    </div>
    <div v-if="allDataSourceLoaded && !dsIdOfStandardView && !dsIdOfFinancialView" class="alert alert-warning"
      role="alert">
      The data source is not ready.
    </div>
    <div v-if="isProgressingCustomExport && isReady" id="progress-bar"
      class="d-flex align-items-center justify-content-center">
      <span class="mr-2 text-nowrap">Download progress:</span>
      <b-progress :max="100" class="w-100" show-progress>
        <b-progress-bar class="text-dark" :value="currentCustomExportPercent">{{
          currentCustomExportPercent ? currentCustomExportPercent : 0
          }}%</b-progress-bar>
      </b-progress>
    </div>
    <div v-if="
      Object.keys(downloadInfo).length > 0 &&
      isReady &&
      !isProgressingCustomExport
    " id="completed-export">
      <span class="text-dark">Bingo! Please download the file
        <b-button size="sm" variant="primary" @click="downloadFile(downloadInfo)">Download</b-button>
      </span>
    </div>
  </b-card>
</template>

<script>
// lib
import cloneDeep from 'lodash/cloneDeep'
import get from 'lodash/get'
import omit from 'lodash/omit'
import set from 'lodash/set'
import uniqBy from 'lodash/uniqBy'
import isArray from 'lodash/isArray'
import debounce from 'lodash/debounce'
import isEmpty from 'lodash/isEmpty'

import { mapActions, mapGetters } from 'vuex'
// mixins
import baseQueryMixins from '@/mixins/baseQueryMixins'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import scrollbarMixins from '@/mixins/scrollbarMixins'
import sdkMixins from '@/components/pages/sdkMixins'
import toastMixin from '@/components/common/toastMixin'
// utils
import exprUtil from '@/services/exprUtil'
import { addVariantData, convertedPermissions as permissions, makeDefaultFilterConfig, saleItems, showCreaterName } from '@/shared/utils'
import { DSType } from '@/shared/constants/ds.constant'
import { DEFAULT_SUMMARIES, DEFAULT_TABLE_SUMMARY } from '@/shared/constants.js'
// component
import BulkEditModal from '@/components/common/ActionModals/BulkEditModal.vue'
import ChangeLogModal from '@/components/common/ActionModals/ChangeLogModal.vue'
import ConfirmationModal from '@/components/common/ActionModals/ConfirmationModal.vue'
import EditModal from '@/components/common/ActionModals/EditModal.vue'
import SyncModal from '@/components/common/ActionModals/SyncModal.vue'
import ReturnLogModal from '@/components/common/ActionModals/ReturnLogModal.vue'

import BulkProgressDropdown from '@/components/common/BulkProgressDropdown/BulkProgressDropdown.vue'
import SelectInput from '@/components/common/SelectInput/SelectInput.vue'
import CommonFilter from '@/components/common/CommonFilter/CommonFilter.vue'
import ComplexRangeDatepicker from '@/components/common/ComplexRangeDatepicker/ComplexRangeDatepicker.vue'
import ViewMode from '@/components/common/ViewMode/ViewMode.vue'
import SaveModal from '@/components/pages/sales/analysis/SaveModal.vue'
import { DEFAULT_VIEW, OPTIONS_VIEW } from '@/shared/constants'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'

/* eslint-disable */
const REMOVE_FIELDS = [{
  name: "item_tax_cost"
}
]
export default {
  name: 'PFAnalysis',
  components: {
    BulkEditModal,
    BulkProgressDropdown,
    ChangeLogModal,
    ReturnLogModal,
    SelectInput,
    ConfirmationModal,
    CommonFilter,
    ComplexRangeDatepicker,
    EditModal,
    SaveModal,
    SyncModal,
    ViewMode
  },
  data() {
    return {
      // render flags
      isReady: false,
      configInitialized: false,
      isFilterReady: false,
      // editable data
      changelogData: null,
      editableData: null,
      bulkEditableData: null,
      deletableData: null,
      syncData: null,
      returnLogData: null,

      modalId: '',
      modalTitle: '',
      saveTableFields: [
        { key: 'name', lable: 'Name', tdClass: 'align-middle' },
        { key: 'preview', lable: 'Preview', tdClass: 'align-middle' },
        { key: 'actions', lable: 'Actions', tdClass: 'align-middle' }
      ],
      pagingColumnSets: {
        page: 1,
        limit: 10
      },
      pagingFilters: {
        page: 1,
        limit: 10
      },
      pagingViews: {
        page: 1,
        limit: 10
      },
      permissions,
      isViewPermission: false,
      filterOptionsMapping: [
        { name: 'item_sale_status', slug: 'sale-status', operator: 'in' },
        { name: 'item_profit_status', slug: 'profit-status', operator: 'in' },
        { name: 'fulfillment_type', slug: 'fulfillment-types' }
      ],
      isSaving: false,
      currentView: '',
      currentQuery: {},
      currentQueryId: cloneDeep(this.$route.query['ref']),
      // cancel debounce
      debounceFlag: true,
      isCheckHighlights: false,
      defaultTableSummaries: null,
      isCustomExport: false,
      currentCustomExportPercent: 0,
      isProgressingCustomExport: false,
      downloadInfo: {},
      customExportTimer: null,
      searchView: '',
      isLoadingView: true,
      updateItemsQueryBuilder: {}
    }
  },
  mixins: [
    baseQueryMixins,
    scrollbarMixins,
    sdkMixins,
    toastMixin,
    PermissionsMixin,
    spapiReconnectAlertMixin
  ],
  computed: {
    ...mapGetters({
      // columnSetList: `pf/analysis/columnSetList`,
      // filterList: `pf/analysis/filterList`,
      // filterName: 'pf/analysis/filterName',
      // filterDiscardable: 'pf/analysis/filterDiscardable',
      filterRenewable: 'pf/analysis/filterRenewable',
      // filterCopiable: 'pf/analysis/filterCopiable',
      // columnSetName: `pf/analysis/columnSetName`,
      // columnSetDiscardable: `pf/analysis/columnSetDiscardable`,
      // columnSetCopiable: `pf/analysis/columnSetCopiable`,
      columnSetRenewable: `pf/analysis/columnSetRenewable`,
      // quickSelectFilters: 'pf/analysis/quickSelectFilters',
      // quickSelectColumnSets: 'pf/analysis/quickSelectColumnSets',
      // quickFavoriteSelectFilters: 'pf/analysis/quickFavoriteSelectFilters',
      // quickFavoriteSelectColumnSets: 'pf/analysis/quickFavoriteSelectColumnSets',
      userToken: 'ps/userModule/GET_TOKEN',
      viewList: `pf/analysis/viewList`,
      quickSelectViews: 'pf/analysis/quickSelectViews',
      quickFavoriteSelectViews: 'pf/analysis/quickFavoriteSelectViews',
      dsColumns: `pf/analysis/dsColumns`,
      dsIdOfStandardView: `pf/analysis/dsIdOfStandardView`,
      dsIdOfFinancialView: `pf/analysis/dsIdOfFinancialView`,
      allDataSourceMap: `pf/analysis/allDataSourceMap`,
      allDataSourceLoaded: `pf/analysis/allDataSourceLoaded`,
      sdkUniqueState: `pf/analysis/sdkUniqueState`,
      filterCurrentExpression: `pf/analysis/filterCurrentExpression`,
      columnSetCurrentExpression: `pf/analysis/columnSetCurrentExpression`,
      currentCustomExportId: `pf/analysis/currentCustomExportId`,
      // this is from Vuex state, need this name to separate it with the sdkMixin data attribute
      localSDKConfig: `pf/analysis/sdkConfig`,
      getUserId: `ps/userModule/GET_USER_ID`,
      view: `pf/analysis/view`,
      viewName: `pf/analysis/viewName`,
      filter: `pf/analysis/filter`,
      columnSet: `pf/analysis/columnSet`,
      viewDiscardable: `pf/analysis/viewDiscardable`,
      viewRenewable: `pf/analysis/viewRenewable`,
      viewCopiable: `pf/analysis/viewCopiable`,
      formFilterOptions: `pf/analysis/formFilterOptions`,
      getCustomObject: `pf/analysis/getCustomObject`
    }),
    getConfigObj: {
      get() {
        let configBuilderFilter = cloneDeep(this.sdkConfig.filter.builder.config)
        let formOptions = cloneDeep(this.formFilterOptions)
        // assign new config form columns
        formOptions = formOptions.map(formSet => {
          if (formSet.name === 'brand') {
            formSet = {
              ...formSet,
              ...{
                typeForMultipleOperator: 'dropdown-select',
                config: {
                  headerText: 'Brand Selection'
                }
              }
            }
          }
          return formSet
        })
        formOptions = formOptions.map(formSet => {
          if (formSet.name === 'style') {
            formSet = {
              ...formSet,
              ...{
                typeForMultipleOperator: 'dropdown-select',
                config: {
                  headerText: 'Style Selection',
                  lazyLoading: true,
                  limit: 20
                }
              }
            }
          }
          return formSet
        })
        formOptions = formOptions.map(formSet => {
          if (formSet.name === 'size') {
            formSet = {
              ...formSet,
              ...{
                typeForMultipleOperator: 'dropdown-select',
                config: {
                  headerText: 'Size Selection',
                  lazyLoading: true,
                  limit: 20
                }
              }
            }
          }
          return formSet
        })
        // set list options which get from server
        this.$set(configBuilderFilter, 'form', { columns: formOptions })
        return configBuilderFilter
      },
      set(value) {
        return value
      }
    },
    getFilterExpr() {
      return filter => exprUtil.buildFilterExpr({ filter }, this.sdkConfig.elements[0].config.columns)
    },
    getColumnSetExpr() {
      return columns => exprUtil.buildColumnSetExpr(columns)
    },
    getColumnNames() {
      return columns => columns.map(column => column.name)
    },
    actionConfig() {
      if (!this.hasPermission(this.permissions.sale.singleEdit) &&
        !this.hasPermission(this.permissions.sale.auditLog) &&
        !this.hasPermission(this.permissions.sale.singleDelete)) {
        return { enabled: false, controls: [] }
      }
      let controls = []
      if (this.hasPermission(this.permissions.sale.singleEdit)) {
        const editControl = {
          display: true,
          props: { size: 'sm', variant: 'secondary' },
          style: { padding: '0px 5px', borderRight: '2px solid #acb5bc' },
          icon: 'fa-pencil',
          label: 'Edit',
          event: dataRow => this.openEditModal(dataRow)
        }
        controls.push(editControl)
      }
      if (this.hasPermission(this.permissions.sale.auditLog)) {
        const logControl = {
          display: true,
          props: { size: 'sm' },
          style: {},
          icon: 'fa-flag',
          label: 'Change Log',
          event: dataRow => this.openChangelogModal(dataRow)
        }
        controls.push(logControl)
      }
      if (this.hasPermission(this.permissions.sale.singleDelete)) {
        const deleteControl = {
          display: true,
          props: { size: 'sm', variant: 'danger' },
          style: {},
          icon: 'fa-trash',
          label: 'Delete',
          event: dataRow => this.openDeleteModal(dataRow)
        }
        controls.push(deleteControl)
      }
      return { enabled: true, controls }
    },
    bulkActionConfig() {
      if (!this.hasPermission(this.permissions.sale.bulkDelete) && !this.hasPermission(this.permissions.sale.bulkEdit)) {
        return { enabled: false, controls: [] }
      }
      let controls = []
      if (this.hasPermission(this.permissions.sale.bulkEdit)) {
        const editControl = {
          display: true,
          props: { size: 'sm', variant: 'secondary' },
          style: {},
          icon: 'align-middle icon-action-edit',
          label: 'Edit',
          event: dataRow => this.openEditModal(dataRow)
        }
        controls.push(editControl)
      }
      if (this.hasPermission(this.permissions.sale.auditLog)) {
        const historyControl = {
          display: true,
          props: { size: 'sm', variant: 'secondary' },
          style: {},
          icon: 'fa-clock-o',
          label: 'History',
          condition: (_button, _index, dataRow) => dataRow.length === 1,
          event: dataRow => this.openChangelogModal(dataRow)
        }
        controls.push(historyControl)
      }
      const returnLogControl = {
        display: true,
        props: { size: 'sm', variant: 'secondary' },
        style: {},
        icon: 'fa-clock-o',
        label: 'Return Log',
        condition: (_button, _index, _dataRow, dataRow) => {
          const saleStatusHasReturnLog = ['Refunded', 'Cancelled']
          return _dataRow.length === 1 ? saleStatusHasReturnLog.includes(dataRow.data.item_sale_status.base) : false
        },
        event: dataRow => this.openReturnLogModal(dataRow)
      }
      controls.push(returnLogControl)
      if (this.hasPermission(this.permissions.sale.auditLog)) {
        const syncControl = {
          display: true,
          props: { size: 'sm', variant: 'secondary' },
          style: {},
          icon: 'align-middle icon-action-sync',
          label: 'Sync',
          event: dataRow => this.openSyncModal(dataRow)
        }
        controls.push(syncControl)
      }
      if (this.hasPermission(this.permissions.sale.bulkDelete) && !this.isFinancialView) {
        const deleteControl = {
          display: true,
          props: { size: 'sm', variant: 'danger' },
          style: {},
          icon: 'align-middle icon-action-delete',
          label: 'Delete',
          event: dataRow => this.openDeleteModal(dataRow)
        }
        controls.push(deleteControl)
      }
      return { enabled: true, controls, enableInlineAction: false }
    },
    enabledFeature() {
      return (type) => {
        if (!type || !saleItems.includes(type)) return false
        const createPermission = this.permissions[type].create
        const editPermission = this.permissions[type].edit
        return (this.hasPermission(editPermission)) ||
          (this.hasPermission(createPermission))
      }
    },
    canSave() {
      return (type) => {
        if (!type || !saleItems.includes(type)) return false
        const createPermission = this.permissions[type].create
        const editPermission = this.permissions[type].edit
        return (this.hasPermission(editPermission)) ||
          (this.hasPermission(createPermission))
      }
    },
    canHaveDivider() {
      return (type) => {
        if (!type || !saleItems.includes(type)) return false
        const createPermission = this.permissions[type].create
        const deletePermission = this.permissions[type].delete
        return this.canSave(type) ||
          this.hasPermission(createPermission) ||
          (type === 'view' && this.hasPermission(deletePermission) && this.viewDiscardable) || // for only view feature
          (this.hasPermission(deletePermission) && this[`${type}Discardable`] && !this.view) || // for filter or column set
          (this[`${type}Discardable`] && this[type].id)
      }
    },
    isFinancialView() {
      return this.currentView === DSType.FINANCIAL_LAYOUT
    },
    showCreater() {
      return (qSelecter) => {
        let userId = this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
        return showCreaterName(qSelecter, userId)
      }
    },
    timezoneCurrent() {
      return get(this.sdkConfig, 'elements[0].config.timezone.utc', 'America/Los_Angeles')
    },
    hasSearchView() {
      return this.viewList && (this.viewList.count > this.quickSelectViews.length || this.viewList.count > this.quickFavoriteSelectViews.length)
    },
    userId() {
      return this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
    },
    todayFormat() {
      return this.$moment().format('dddd, MMMM Do, YYYY')
    },
    optionsView() {
      return OPTIONS_VIEW
    },
    defaultView() {
      return DEFAULT_VIEW
    }
  },
  methods: {
    ...mapActions({
      getViews: `pf/analysis/getViews`,
      getColumnSets: `pf/analysis/getColumnSets`,
      getFilters: `pf/analysis/getFilters`,
      setFilter: `pf/analysis/setFilter`,
      updateCurrentFilter: `pf/analysis/updateCurrentFilter`,
      updateCurrentColumnSet: `pf/analysis/updateCurrentColumnSet`,
      updateCurrentView: `pf/analysis/updateCurrentView`,
      setOriginalFilter: `pf/analysis/setOriginalFilter`,
      discardFilter: 'pf/analysis/discardFilter',
      newFilter: 'pf/analysis/newFilter',
      setColumnSet: `pf/analysis/setColumnSet`,
      setView: `pf/analysis/setView`,
      fetchDSColumns: `pf/analysis/fetchDSColumns`,
      fetchAllDataSourceIDs: `pf/analysis/fetchAllDataSourceIDs`,
      setReloadKeySDK: `pf/analysis/setReloadKeySDK`,
      setSDKConfig: `pf/analysis/setSDKConfig`,
      setDefaultColumnSet: `pf/analysis/setDefaultColumnSet`,
      setOriginalColumnSet: `pf/analysis/setOriginalColumnSet`,
      discardColumnSet: 'pf/analysis/discardColumnSet',
      newColumnSet: 'pf/analysis/newColumnSet',
      setOriginalView: `pf/analysis/setOriginalView`,
      discardView: `pf/analysis/discardView`,
      newView: `pf/analysis/newView`,
      initSaleItemAnalyisTable: 'pf/analysis/initSaleItemAnalyisTable',
      getFavoriteQuickSelectViews: 'pf/analysis/getFavoriteQuickSelectViews',
      getQuickSelectViews: 'pf/analysis/getQuickSelectViews',
      resetAllConditions: 'pf/analysis/resetAllConditions',
      getSaleItemVariation: 'pf/analysis/getSaleItemVariation',
      getAllBrands: 'pf/analysis/getAllBrands',
      setFormFilterOptions: 'pf/analysis/setFormFilterOptions',
      getDataRowByChannelSaleId: 'pf/analysis/getDataRowByChannelSaleId',
      getCustomExport: `pf/bulk/getCustomExport`,
      setCurrentCustomExportId: 'pf/analysis/setCurrentCustomExportId',
      createCustomObject: 'pf/analysis/createCustomObject',
      fetchCustomObject: 'pf/analysis/fetchCustomObject'
    }),
    refreshData() {
      this.$root.$emit('bv::hide::tooltip', 'refresh-table-btn')
      this.$set(this.sdkConfig.elements[0].config.pagination, 'current', 1)
      this.$set(this.sdkConfig.elements[0].config.bulkActions, 'filterMode', false)
      this.setReloadKeySDK()
    },
    isBulkData(data) {
      const bulkKey = ['item_ids']
      return bulkKey.every(key => Object.keys(data).includes(key))
    },
    openEditModal(data) {
      let dataWithoutDuplicate = cloneDeep(data)
      if (this.isBulkData(dataWithoutDuplicate) && this.isFinancialView) {
        dataWithoutDuplicate.item_ids = uniqBy(dataWithoutDuplicate.item_ids, 'data.channel_id.base')
        if (dataWithoutDuplicate.item_ids.length === 1) {
          dataWithoutDuplicate = dataWithoutDuplicate.item_ids[0]
        }
      }
      this.$nextTick(async () => {
        if (this.isBulkData(dataWithoutDuplicate)) {
          this.isCustomExport = false
          this.$bvModal.show('bulk-edit-modal')
          if (this.isFinancialView) {
            this.bulkEditableData = dataWithoutDuplicate
          } else {
            this.bulkEditableData = data
          }
        } else {
          if (this.isFinancialView) {
            let editData = cloneDeep(dataWithoutDuplicate)
            editData.data = {}
            let payload = {
              channel_sale_id: dataWithoutDuplicate.data.channel_id.base
            }
            // on financial view, need to get data from the original view
            let rawData = await this.getDataRowByChannelSaleId(payload)
            rawData.cols.forEach((col, index) => {
              editData.data = {
                ...{
                  [col.name]: { base: rawData.rows[0][index] }
                },
                ...editData.data
              }
            })
            this.$bvModal.show('edit-modal')
            this.editableData = editData
          } else {
            this.$bvModal.show('edit-modal')
            this.editableData = data
          }
        }
      })
    },
    openChangelogModal(data) {
      this.$nextTick(() => {
        this.changelogData = isArray(data) ? data[0] : data
        this.$bvModal.show('changelog-modal')
      })
    },
    openReturnLogModal(data) {
      this.$nextTick(async () => {
        this.returnLogData = data
        this.$bvModal.show('returnlog-modal')
      })
    },
    openSyncModal(data) {
      this.$nextTick(() => {
        this.syncData = data
        this.$bvModal.show('sync-modal')
      })
    },
    openDeleteModal(data) {
      this.$nextTick(() => {
        if (this.isFinancialView) {
          this.vueToast('error', 'Do not allow to delete in the Financial Layout')
        } else {
          this.deletableData = data
          this.$bvModal.show('delete-modal')
        }
      })
    },
    openModal(type) {
      if (type === 'as-filter') {
        this.modalTitle = 'Save as a new filter'
      } else if (type === 'as-column-set') {
        this.modalTitle = 'Save as a new column set'
      } else if (type === 'as-view') {
        this.modalTitle = 'Save as a new view'
      } else {
        this.modalTitle = `Save ${type}`.replace('-', ' ')
      }
      this.modalId = `save-${type}`
      this.$nextTick(() => {
        this.$bvModal.show(`save-${type}`)
      })
    },
    updateFilter(filter) {
      const baseQueryFilter = this.setBaseQueryFilter()
      this.$set(filter, 'base', baseQueryFilter.config.query)
      // Case applying new filter: filter.ignore
      // Case reset filter: filter.builder.config.ignore
      const ignore = filter.ignore || filter.builder.config.ignore
      this.sdkConfig.filter.builder.config.ignore = ignore
      if (this.$refs && this.$refs.widgetSDK) {
        this.$refs.widgetSDK.updateFilter(filter)
      }
      this.sdkConfig.filter.builder.config.query = filter.builder
      this.setSDKConfig(cloneDeep(this.sdkConfig))
    },
    handleUpdateColumns(columns) {
      this.currentQuery['configColumns'] = this.sdkConfig.elements[0].config.columns
      this.updateColumns(columns)
    },
    updateColumns(columns) {
      if (this.$refs && this.$refs.widgetSDK) {
        this.$refs.widgetSDK.columnChange(columns)
        this.refreshUrl()
      }
    },
    handleBeforeLoadFilter(filter) {
      const data = cloneDeep(filter)
      data.ds_filter.timezone ? this.setTimezone(data.ds_filter.timezone) : this.setTimezone(this.getDefaultConfig().elements[0].config.timezone)
      data.ds_filter = omit(data.ds_filter, ['timezone'])
      this.setFilter(cloneDeep(data))
    },
    loadFilter() {
      const data = cloneDeep(this.filter)
      this.setFilterConfig(data.ds_filter, 'forceUpdateBaseQuery')
      this.setOriginalFilter(data)
      this.forceSDKRenderAndHideSelectionModals()
    },
    handleBeforeLoadColumnSet(columnSet) {
      const newColumnSet = cloneDeep(columnSet)
      const tableElement = cloneDeep(this.sdkConfig.elements[0])
      const { columns, id } = newColumnSet.ds_column.config
      tableElement.config = { ...tableElement.config, ...{ columns, id } }
      newColumnSet.ds_column.config = tableElement.config
      this.setElementConfig(tableElement)
      this.setColumnSet(newColumnSet)
    },
    loadColumnSet() {
      this.setOriginalColumnSet(cloneDeep(this.columnSet))
      this.forceSDKRenderAndHideSelectionModals()
    },
    loadView(view) {
      this.handleNewFilter()
      this.handleNewColumnSet()
      const newView = cloneDeep(view)
      const tableElement = get(this.sdkConfig, 'elements[0]', '')
      const { columns, id } = newView.ds_column.config
      tableElement.config = { ...tableElement.config, ...{ columns, id } }
      set(this.sdkConfig, 'elements[0].config', tableElement.config)
      this.setElementConfig(tableElement)
      this.setFilterConfig(newView.ds_filter, 'forceUpdateBaseQuery')
      this.setOriginalView(cloneDeep(this.view))
      this.setBulkActions(this.bulkActionConfig)
      this.forceSDKRenderAndHideSelectionModals()
    },
    forceSDKRenderAndHideSelectionModals() {

      // set config
      this.setReloadKeySDK()
      this.setActions(this.actionConfig)
      this.setBulkActions(this.bulkActionConfig)
      this.setFormOptions({ columns: this.formFilterOptions })

      this.$bvModal.hide('table-column-sets')
      this.$bvModal.hide('table-filters')
      this.$bvModal.hide('table-views')
      this.$bvModal.hide('discard-filter-confirm-modal')
      this.$bvModal.hide('discard-column-set-confirm-modal')
      this.$bvModal.hide('discard-view-confirm-modal')
    },
    setSaveType() {
      if (this.modalId === 'save-column-set' || this.modalId === 'save-as-column-set') {
        return this.getElementConfig
      } if (this.modalId === 'save-view' || this.modalId === 'save-as-view') {
        return this.getConfig
      } if (this.modalId === 'save-filter' || this.modalId === 'save-as-filter') {
        return this.getFilter
      }
    },
    async handleDiscardFilter() {
      this.discardFilter()
      this.setFilterConfig(this.filter.ds_filter, 'forceUpdateBaseQuery')
      this.setSDKConfig(cloneDeep(this.sdkConfig))
      this.updateFilter(this.filter.ds_filter)
      this.forceSDKRenderAndHideSelectionModals()
    },
    async handleDiscardColumnSet() {
      this.discardColumnSet()
      this.setElementConfig({
        type: 'cbpo-element-table',
        config: cloneDeep(get(this.columnSet, 'ds_column.config', {}))
      })
      this.setSDKConfig(cloneDeep(this.sdkConfig))
      let columnSet = [this.columnSet.ds_column.config]
      this.updateColumns(columnSet)
      this.forceSDKRenderAndHideSelectionModals()
    },
    async handleDiscardView() {
      this.discardView()
      this.setElementConfig({
        type: 'cbpo-element-table',
        config: cloneDeep(get(this.view, 'ds_column.config', {}))
      })
      this.setFilterConfig(this.view.ds_filter, 'forceUpdateBaseQuery')
      this.forceSDKRenderAndHideSelectionModals()
    },
    refreshUrl: debounce(function () {
      if (this.debounceFlag) {
        const payload = {
          clientId: this.$route.params.client_id,
          data: this.currentQuery
        }
        this.createCustomObject(payload)
          .then(res => {
            this.$router.replace({ name: 'PFAnalysis', query: { 'ref': res.data.id } })
          })
          .catch(err => {
            console.log('err', err)
          })
      }
    }, 3000),
    removeParamsFromUrl(...params) {
      this.currentQuery = omit(this.currentQuery, params)
      this.refreshUrl()
    },
    handleNewFilter() {
      this.resetToHighlightDefault()
      this.resetBaseQuery()
      this.newFilter()
      this.setFilterConfig(this.filter.ds_filter)
      this.setSDKConfig(cloneDeep(this.sdkConfig))
      this.updateFilter(this.filter.ds_filter)
      this.setReloadKeySDK()
      this.setFormOptions({ columns: this.formFilterOptions })
      this.isViewPermission = false
      this.removeParamsFromUrl('filterId')
    },
    handleNewColumnSet() {
      this.resetToHighlightDefault()
      this.newColumnSet()
      this.setElementConfig({
        type: 'cbpo-element-table',
        config: this.columnSet.ds_column.config
      })
      this.setSDKConfig(cloneDeep(this.sdkConfig))
      let columnSet = [this.columnSet.ds_column.config]
      this.isViewPermission = false
      this.updateColumns(columnSet)
      this.setReloadKeySDK()
      this.removeParamsFromUrl('columnSetId')
    },
    handleResetAllToDefault() {
      this.resetToHighlightDefault()
      this.resetBaseQuery()
      this.newFilter()
      this.newColumnSet()
      this.newView()
      this.setFilterConfig(this.view.ds_filter)
      this.setElementConfig({
        type: 'cbpo-element-table',
        config: this.view.ds_column.config
      })
      this.setSDKConfig(cloneDeep(this.sdkConfig))
      this.updateFilter(this.view.ds_filter)
      let columnSet = [this.view.ds_column.config]
      this.isViewPermission = false
      this.updateColumns(columnSet)
      this.setReloadKeySDK()
      this.setFormOptions({ columns: this.formFilterOptions })
      this.removeParamsFromUrl(['viewId', 'filterId', 'columnSetId'])
    },
    goToPage(type) {
      let payload = {
        client_id: this.$route.params.client_id,
        user_id: this.userId
      }
      if (type === 'column-sets') {
        payload.limit = this.pagingColumnSets.limit
        payload.page = this.pagingColumnSets.page
        this.getColumnSets(payload)
      }
      if (type === 'filters') {
        payload.limit = this.pagingFilters.limit
        payload.page = this.pagingFilters.page
        this.getFilters(payload)
      }
      if (type === 'views') {
        payload.limit = this.pagingViews.limit
        payload.page = this.pagingViews.page
        this.getViews(payload)
      }
    },
    onChangeBaseQuery() {
      this.sdkConfig.filter.builder.config.ignore.base.value = false
      this.setFilterConfig(this.sdkConfig.filter)
      this.forceSDKRenderAndHideSelectionModals()
    },
    handleUpdateConfigSDK() {
      this.setDataSource(this.allDataSourceMap[this.currentView].data_source_id)
      this.forceSDKRenderAndHideSelectionModals()
    },
    async handleSaveItem() {
      this.isSaving = true
      await this.$refs.saveModal.handleSaveItem()
      this.isSaving = false
    },
    handleCloseModal() {
      this.$refs.saveModal.handleCloseModal()
    },
    async initQueryParams() {
      let query = {}
      if (this.currentQueryId) {
        query = this.getCustomObject
        this.currentQuery = cloneDeep(query)
      }
      let filter = makeDefaultFilterConfig(cloneDeep(this.sdkConfig.filter))
      if (query && query.q) {
        try {
          if (query.q === 'all') {
            filter.base.config.query = {}
            this.setFilterConfig(filter, 'forceUpdateBaseQuery')
          } else {
            const filter = makeDefaultFilterConfig(query.q)
            this.setFilterConfig(filter, 'forceUpdateBaseQuery')
          }
        } catch {
          console.error('Invalid query params')
          this.setFilterConfig(filter, '')
        }
      }
    },
    checkFilterEmpty(filterObj) {
      const queryBase = get(filterObj, 'base.config.query', {})
      const queryBuilder = get(filterObj, 'builder.config.query', {})
      const queryForm = get(filterObj, 'builder.config.controls', [])
      return isEmpty(queryBase) && (isEmpty(queryBuilder) || isEmpty(queryBuilder.conditions)) && isEmpty(queryForm)
    },
    async initFormFilterOptions() {
      const defaultPayload = {
        clientId: this.$route.params.client_id,
        hasVariation: false
      }
      await this.filterOptionsMapping.forEach((item, index) => {
        const payload = Object.assign(defaultPayload, { type: item.slug })
        this.getSaleItemVariation(payload).then(response => {
          if (response.data) {
            const results = response.data.results.map(item => ({ text: item.name, value: item.value || item.name }))
            Object.assign(this.filterOptionsMapping[index], { type: 'select', options: results })
          }
        })
      })
      await this.getSaleItemVariation({ type: 'style', hasVariation: true, clientId: this.$route.params.client_id, }).then(res => {
        if (res.data) {
          const results = res.data.results.map(item => ({ text: item.name, value: item.value || item.name }))
          this.filterOptionsMapping.push({ name: 'style', options: results, type: 'select', operator: 'in' })
        }
      })
      await this.getSaleItemVariation({ type: 'size', hasVariation: true, clientId: this.$route.params.client_id, }).then(res => {
        if (res.data) {
          const results = res.data.results.map(item => ({ text: item.name, value: item.value || item.name }))
          this.filterOptionsMapping.push({ name: 'size', options: results, type: 'select', operator: 'in' })
        }
      })
      await this.getAllBrands(defaultPayload).then(res => {
        if (res.data) {
          const results = res.data.results.map(item => ({ text: item.name, value: item.value || item.name }))
          this.filterOptionsMapping.push({ name: 'brand', options: results, type: 'select', operator: 'in' })
        }
      })
      addVariantData(this.filterOptionsMapping)
      addVariantData(this.formFilterOptions)
      await this.setFormFilterOptions(this.filterOptionsMapping).then(() => {
        this.setFormOptions({ columns: this.formFilterOptions })
      })
    },
    addComputeClass(columns) {
      columns.forEach(column => {
        switch (column.name) {
          case 'fulfillment_type':
            column.cell.computeClass = (valueObj, rowValue) => {
              return rowValue.fulfillment_type_accuracy && rowValue.fulfillment_type_accuracy.base < 100 ? 'inaccurate-style' : ''
            }
            break
          case 'inbound_freight_cost': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
          case 'outbount_freight_cost': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
          case 'cog': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => 'highlight_style'
            }
            break
          }
          case 'user_provided_cost': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
          case 'item_reimbursement_costs': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
          case 'actual_shipping_cost': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.shipping_cost_accuracy && rowValue.shipping_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'estimated_shipping_cost': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.shipping_cost_accuracy && rowValue.shipping_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'item_shipping_cost': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.shipping_cost_accuracy && rowValue.shipping_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'warehouse_processing_fee': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
          case 'item_channel_listing_fee': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
          case 'return_postage_billing': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
          case 'item_other_channel_fees': {
            column.cell.width = 105
            if (this.isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            }
            break
          }
        }
      })
    },
    checkHighlights() {
      if (this.$refs && this.$refs.widgetSDK) {
        this.isCheckHighlights = !this.isCheckHighlights
        this.handleHighlightsTableSummary(this.isCheckHighlights)
        this.highlightCostsAndFees(this.isCheckHighlights)
        this.$refs.widgetSDK.applyNewConfigColumnsForSummaries()
      } else {
        this.vueToast('error', 'Failed to highlight Costs and Fees, please try again later!')
      }
    },
    highlightCostsAndFees(isCheckHighlights) {
      this.sdkConfig.elements[0].config.columns = cloneDeep(this.sdkConfig.elements[0].config.columns).map(column => {
        switch (column.name) {
          case 'item_other_channel_fees': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return ''
              }
            }
            break
          }
          case 'item_channel_listing_fee': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.channel_listing_fee_accuracy && rowValue.channel_listing_fee_accuracy.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'warehouse_processing_fee': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.warehouse_processing_fee_accuracy && rowValue.warehouse_processing_fee_accuracy.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'item_total_cost': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return ''
              }
            }
            break
          }
          case 'cog': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return ''
              }
            }
            break
          }
          case 'item_shipping_cost': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.item_shipping_cost && rowValue.item_shipping_cost.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'actual_shipping_cost': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.actual_shipping_cost && rowValue.actual_shipping_cost.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'estimated_shipping_cost': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.estimated_shipping_cost && rowValue.estimated_shipping_cost.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'inbound_freight_cost': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.inbound_freight_cost_accuracy && rowValue.inbound_freight_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'outbound_freight_cost': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return rowValue.outbound_freight_cost_accuracy && rowValue.outbound_freight_cost_accuracy.base < 100 ? 'inaccurate-style' : ''
              }
            }
            break
          }
          case 'user_provided_cost': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return ''
              }
            }
            break
          }
          case 'item_reimbursement_costs': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return ''
              }
            }
            break
          }
          case 'refund_admin_fee': {
            column.cell.width = 105
            if (isCheckHighlights) {
              column.cell.computeClass = (value, rowValue) => {
                return 'highlights-style'
              }
            } else {
              column.cell.computeClass = (valueObj, rowValue) => {
                return ''
              }
            }
            break
          }
        }
        return column
      })
    },
    handleHighlightsTableSummary(isCheckHighlights) {
      if (isCheckHighlights) {
        const summaries = get(this.sdkConfig, 'elements[0].config.tableSummary.summaries', [])
        this.defaultTableSummaries = cloneDeep(summaries)
        summaries.forEach((summary, index) => {
          switch (summary.column) {
            case 'actual_shipping_cost':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'estimated_shipping_cost':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'item_channel_listing_fee':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'item_total_cost':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'item_other_channel_fees':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'item_reimbursement_costs':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'inbound_freight_cost':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'outbound_freight_cost':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'user_provided_cost':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'refund_admin_fee':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
            case 'cog':
              summaries[index].style.color = 'rgb(255,0,0)'
              break
          }
        })
        set(this.sdkConfig, 'elements[0].config.tableSummary.summaries', summaries)
      } else if (this.defaultTableSummaries) {
        set(this.sdkConfig, 'elements[0].config.tableSummary.summaries', this.defaultTableSummaries)
      }
    },
    handleSetColumnSet(columnSet) {
      this.resetToHighlightDefault()
      this.setColumnSet(columnSet)
    },
    resetToHighlightDefault() {
      this.isCheckHighlights = false
      this.handleHighlightsTableSummary(this.isCheckHighlights)
      this.highlightCostsAndFees(this.isCheckHighlights)
    },
    removeSDKConfigLegacyFields(sdkConfig) {
      let nameColumn = REMOVE_FIELDS.map(col => col.name)
      sdkConfig.ds_column.config.columns = sdkConfig.ds_column.config.columns.filter(item => {
        return nameColumn.indexOf(item.name) === -1
      })
    },
    migrateTableSummaries(sdkConfig) {
      if (!sdkConfig.ds_column.config.tableSummary) {
        sdkConfig.ds_column.config.tableSummary = cloneDeep(DEFAULT_TABLE_SUMMARY)
      } else {
        sdkConfig.ds_column.config.tableSummary.summaries = cloneDeep(DEFAULT_SUMMARIES)
      }
    },
    handleClickView(qView) {
      this.removeColumnsUrl()
      this.resetToHighlightDefault()
      this.setView(qView)
    },
    customExport() {
      this.isCustomExport = true
      this.$bvModal.show('bulk-edit-modal')
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
    handleDownloadFile(data) {
      const { progress, status, downloadUrl, name } = data
      this.currentCustomExportPercent = progress
      if (status === 'reported') {
        this.downloadInfo = {
          downloadUrl,
          name
        }
        this.isProgressingCustomExport = false
        this.currentCustomExportPercent = 0
      }
    },
    downloadFile(downloadInfo) {
      this.setCurrentCustomExportId({ clientId: this.$route.params.client_id, userId: this.userId, id: null })
      const { downloadUrl, name } = downloadInfo
      this.downloadURL(downloadUrl, name)
      this.downloadInfo = {}
    },
    async customReportQueued(id) {
      try {
        clearInterval(this.customExportTimer)
        const data = {
          params: {
            userID: this.userId,
            clientID: this.$route.params.client_id
          },
          id: id
        }
        let res = await this.getCustomExport(data)
        if (res.data.status === 'revoked') {
          this.hiddenProgressExport()
        } else if (res.data.status !== 'reported') this.isProgressingCustomExport = true
        this.handleDownloadFile({ progress: res.data.progress, status: res.data.status, downloadUrl: res.data.download_url, name: res.data.name })
        this.customExportTimer = setInterval(async () => {
          if (this.isProgressingCustomExport) {
            try {
              let res = await this.getCustomExport(data)
              this.handleDownloadFile({ progress: res.data.progress, status: res.data.status, downloadUrl: res.data.download_url, name: res.data.name })
              if (res.data.status === 'reported') {
                this.isProgressingCustomExport = false
                clearInterval(this.customExportTimer)
              }
              if (res.data.status === 'revoked') {
                this.hiddenProgressExport()
              }
            } catch (error) {
              this.hiddenProgressExport()
            }
          }
        }, 2500)
      } catch (error) {
        this.hiddenProgressExport()
      }
    },
    addExportCustom() {
      this.sdkConfig.menu.config.selection.options.push({
        label: 'Export Custom CSV',
        icon: 'fa fa-cog',
        value: 'custom-csv',
        type: 'item'
      })
    },
    hiddenProgressExport() {
      this.isProgressingCustomExport = false
      this.setCurrentCustomExportId({ clientId: this.$route.params.client_id, userId: this.userId, id: null })
      clearInterval(this.customExportTimer)
    },
    handleSearchView() {
      this.isLoadingView = true
      const params = {
        client_id: this.$route.params.client_id,
        user_id: this.userId,
        search: this.searchView
      }
      Promise.all([this.getFavoriteQuickSelectViews(params), this.getQuickSelectViews(params)]).finally(() => {
        this.isLoadingView = false
      })
    },
    clearKeyword() {
      this.searchView = ''
      this.handleSearchView()
    },
    removeColumnsUrl() {
      if (this.currentQuery.configColumns) {
        delete this.currentQuery.configColumns
      }
    },
    async handleUpdateItemsQueryBuilder(data) {
      try {
        const saleItemVariationList = ['style', 'size']
        if (saleItemVariationList.includes(data.columnName)) {
          const res = await this.getSaleItemVariation({ clientId: this.$route.params.client_id, type: data.columnName, hasVariation: true, page: data.page, keyword: data.search, limit: data.limit })
          if (res.data) {
            const results = res.data.results.map(item => ({ text: item.name, value: item.value || item.name }))
            const items = cloneDeep(this.updateItemsQueryBuilder)
            items[data.columnName] = { page: data.page, items: results, search: data.search, count: res.data.count }
            this.updateItemsQueryBuilder = items
          }
        }
      } catch (error) {
        console.log(error)
      }
    }
  },
  async created() {
    await this.fetchAllDataSourceIDs({ client_id: this.$route.params.client_id })

    /* START: Handle SDK's builder filter columns preparation */
    this.$store.subscribeAction(mutation => {
      if (mutation.type === `pf/analysis/setReloadKeySDK`) {
        this.isFilterReady = false
      }
    })
    this.$CBPO.$bus.$on('BUILDER_FILTER_COLUMNS_READY', () => {
      this.isFilterReady = true
    })
    /* END: Handle SDK's builder filter columns preparation */
    let payload = {
      client_id: this.$route.params.client_id,
      user_id: this.userId
    }
    if (this.currentQueryId) {
      await this.fetchCustomObject({ clientId: this.$route.params.client_id, id: this.currentQueryId })
    }
    // Init analysis table config
    await this.initSaleItemAnalyisTable(payload)
    // Init SDK data
    this.setDataSource(this.dsIdOfStandardView)
    this.setColumns(this.dsColumns)
    this.setDefaultWidth()
    // Reset all conditions
    await this.resetAllConditions()
    // TODO this is very confused, we need to deal with it later
    this.sdkConfig.elements[0].config.header.sticky = true
    await this.setDefaultColumnSet({
      tableConfig: this.sdkConfig.elements[0].config,
      hiddenColumns: {
        columnManager: get(this.sdkConfig, 'columnManager.config.hiddenColumns', []),
        queryBuilder: get(this.sdkConfig, 'filter.builder.config.hiddenColumns', [])
      }
    })
    // Setup SDK config
    // TODO consider moving this to inside the analysis vuex state
    this.setActions(this.actionConfig)
    this.setBulkActions(this.bulkActionConfig)
    this.setFilterConfig(this.sdkConfig.filter)
    await this.initQueryParams()
    this.setDefaultConfig(this.sdkConfig)
    // Reload name filter, columnSet, view
    if (!this.currentQueryId) {
      this.currentQuery = {
        q: this.sdkConfig.filter
      }
    }
    if (this.currentQuery.viewId) {
      this.updateCurrentView({ ...payload, item_id: this.currentQuery.viewId })
    }
    if (this.currentQuery.filterId) {
      this.updateCurrentFilter({ ...payload, item_id: this.currentQuery.filterId })
    }
    if (this.currentQuery.columnSetId) {
      this.updateCurrentColumnSet({ ...payload, item_id: this.currentQuery.columnSetId })
    }
    if (this.currentQuery.configColumns) {
      set(this.sdkConfig, 'columnManager.config.managedColumns[0]', this.currentQuery.configColumns)
      set(this.sdkConfig, 'elements[0].config.columns', this.currentQuery.configColumns)
    }
    if (this.$route.params.selectedView) {
      this.isViewPermission = this.$route.params.selectedView.permission === 'view'
      this.setView(cloneDeep(this.$route.params.selectedView))
    } else if (this.$route.query.sale_id) {
      let filter = cloneDeep(this.sdkConfig.filter)
      let matchSales = JSON.parse(this.$route.query.sale_id)
      filter.builder.conditions = [{
        operator: 'in',
        parentId: null,
        column: {
          name: 'sale_id',
          type: 'number',
          displayName: 'Sale ID'
        },
        value: matchSales
      }]
      filter.builder.type = 'OR'
      filter.builder.config.ignore = {
        global: {
          visible: false,
          value: false
        },
        base: {
          visible: true,
          value: true
        }
      }
      this.updateFilter(filter)
    }
    // UI is ready to be rendered (e.g hide loading)
    this.isReady = true
    // Init SDK UI (this is parent mixin attribute)
    this.configInitialized = true
    // this.currentQuery = query
    this.currentView = this.$route.query.currentView || DSType.STANDARD_LAYOUT
    this.refreshUrl()
    // check permission for export custom
    if (this.hasPermission(permissions.customReport.export)) {
      this.addExportCustom()
    }
    // set current custom export id default
    this.setCurrentCustomExportId({ clientId: this.$route.params.client_id, userId: this.userId, id: localStorage.getItem(`customExportId-${this.$route.params.client_id}-${this.userId}`) })

    this.initFormFilterOptions()
  },
  beforeDestroy() {
    this.debounceFlag = false
    clearInterval(this.customExportTimer)
  },
  destroyed() {
    this.setFilter(null)
    this.setColumnSet(null)
    this.setView(null)
  },
  watch: {
    userToken() {
      this.setReloadKeySDK()
    },
    // TODO cho nay rat la lung cung, khong duoc
    sdkConfig: {
      deep: true,
      handler(newObj) {
        this.setSDKConfig(cloneDeep(newObj))
      }
    },
    filterCurrentExpression() {
      if (this.isReady) {
        const filter = this.sdkConfig.filter
        const isEmpty = this.checkFilterEmpty(filter)
        if (isEmpty) this.currentQuery.q = 'all'
        else this.currentQuery.q = filter
        this.refreshUrl()
      }
    },
    isReady(val) {
      if (!this.hasPermission(permissions.sale.viewAll) && this.hasPermission(permissions.sale.view24h)) {
        this.vueToast('warning', 'You can access the sales within 24 hours only.')
      }
    },
    'columnSet': {
      immediate: true,
      deep: true,
      handler(newVal, oldVal) {
        if (newVal && newVal.id && ((oldVal && newVal.id !== oldVal.id) || !oldVal)) {
          this.currentQuery['columnSetId'] = newVal.id
          this.removeSDKConfigLegacyFields(newVal)
          this.migrateTableSummaries(newVal)
          this.refreshUrl()
          this.handleBeforeLoadColumnSet(newVal)
          this.loadColumnSet()
        }
      }
    },
    'view': {
      immediate: true,
      deep: true,
      handler(newVal, oldVal) {
        if (newVal && newVal.id && ((oldVal && newVal.id !== oldVal.id) || !oldVal)) {
          this.currentQuery['viewId'] = newVal.id
          this.removeSDKConfigLegacyFields(newVal)
          this.migrateTableSummaries(newVal)
          this.addComputeClass(get(newVal, 'ds_column.config.columns', []))
          this.refreshUrl()
          this.loadView(newVal)
        }
      }
    },
    'filter': {
      immediate: true,
      deep: true,
      handler(newVal, oldVal) {
        if (newVal && newVal.id && ((oldVal && newVal.id !== oldVal.id) || !oldVal)) {
          this.currentQuery['filterId'] = newVal.id
          this.refreshUrl()
          this.handleBeforeLoadFilter(newVal)
          this.loadFilter()
        }
      }
    },
    currentView() {
      this.currentQuery['currentView'] = this.currentView
      this.handleUpdateConfigSDK()
      this.refreshUrl()
    },
    'currentCustomExportId': {
      immediate: true,
      handler(newValue) {
        if (newValue) {
          this.customReportQueued(newValue)
        }
      }
    },
    'quickSelectViews': {
      immediate: true,
      handler(newVal) {
        if (newVal.length > 0) {
          this.isLoadingView = false
        }
      }
    },
    'quickFavoriteSelectViews': {
      immediate: true,
      handler(newVal) {
        if (newVal.length > 0) {
          this.isLoadingView = false
        }
      }
    }
  },
  beforeRouteLeave(to, from, next) {
    if (this.debounceFlag) {
      // To prevent the page from refreshing when you are navigating to another page while data is still loading.
      this.debounceFlag = false
      clearTimeout(this.refreshUrl)
    }
    next()
  }
}
</script>

<style lang="scss" scoped>
@import "./Analysis.scss";
</style>
