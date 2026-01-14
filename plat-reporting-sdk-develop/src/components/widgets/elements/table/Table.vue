<template>
  <div v-if="configReady" class="cbpo-table-element-container" ref="tableElement"
    :class="`cbpo-compact-mode-${config.compactMode.mode}`" :style="config.style" :css="config.css" :id="config.id"
    v-cbpo-loading="{ loading: loading }">
    <div v-show="!isElementHidden" class="cbpo-table-title" :style="colorStyle" v-if="config.widget.title.enabled">
      {{ config.widget.title.text }}
    </div>
    <!-- Drill down -->
    <div v-if="config.drillDown.enabled" class="cbpo-drill-down-action" :class="{
      '--no-border': !config.widget.title.enabled,
      ' --no-spacing': !config.widget.title.enabled || ($refs.drillDown && !$refs.drillDown.breadcrumbs.length)
    }">
      <drill-down-table ref="drillDown" root-label="Root" :channelId="config.dataSource" :auto-order="false"
        :config-obj="config.drillDown.config" @input="drillDownChange"></drill-down-table>
    </div>
    <!-- end drill down -->

    <div class="cbpo-table-reporting" v-show="!isElementHidden"
      :class="{ '--has-pagination': config.pagination.type !== 'lazy' && !(config.pagination.total < config.pagination.current) && dataTable.items.length > 0 && !config.globalControlOptions.globalGrouping.config.value }">
      <div class="cbpo-screen-cover">
        <template v-if="config.globalControlOptions.globalGrouping.position === 'top'">
          <div v-if="getGlobalControlOptions(config.globalControlOptions, OPTIONS.GLOBAL_GROUPING)"
            class="cbpo-table-global-grouping" :class="{ '--no-border --no-spacing': !config.widget.title.enabled }">
            <b-form-checkbox size="sm" switch :disabled="!config.columns.length" @change="setAggrForAllColumns($event)"
              v-model="config.globalControlOptions.globalGrouping.config.value">
              Global Grouping
            </b-form-checkbox>
          </div>
        </template>
        <div class="cbpo-table-action d-flex" v-if="config.bulkActions.enabled || config.globalSummary.enabled"
          :class="{ 'py-2': (config.globalControlOptions.globalGrouping.position === 'top' && config.bulkActions.enabled) || config.globalSummary.enabled }">
          <div class="w-100 d-flex align-items-center">
            <ActionCheckbox multi v-if="config.bulkActions.enabled" :isSelectedAll="isSelectedAllMatchedItems"
              :checkedState="checkedState" :dataRow="selectedItems" :dataLength="dataTable.items.length"
              :count="dataTable.total" :labels="config.bulkActions.labels" :isCountFetching="isTotalLoading"
              @allItemSelected="allItemsSelected()" @onClick="toggleSelect()" />
            <ActionButtons multi :config="config.bulkActions" :dataRow="selectedItems" :items="dataTable.items"
              v-if="isBulkActionsShown" />

            <!-- global grouping -->
            <div v-if="config.globalControlOptions.globalGrouping.position !== 'top'">
              <div v-if="getGlobalControlOptions(config.globalControlOptions, OPTIONS.GLOBAL_GROUPING)"
                class="cbpo-table-global-grouping --no-border"
                :class="{ '--no-border --no-spacing': !config.widget.title.enabled, 'cpbo-custom-switch d-flex': config.bulkActions.enabled, 'ml-2': !config.bulkActions.enabled }">
                <span class="divider"></span>
                <b-form-checkbox size="sm" switch :disabled="!config.columns.length"
                  @change="setAggrForAllColumns($event)"
                  v-model="config.globalControlOptions.globalGrouping.config.value">
                  Global Grouping
                </b-form-checkbox>
              </div>
            </div>
            <!-- end global grouping -->

            <!-- Global Summaries -->
            <Summaries v-if="config.globalSummary.enabled" :summaries="config.globalSummary.summaries"
              :configObj="config" />
            <!-- End global Summaries -->

            <!-- timezone selector -->
            <TimezoneSelector v-if="config.timezone.enabled" :configObj.sync="config.timezone" class="mr-2" />
            <!-- end timezone -->

            <!-- compact mode -->
            <CompactMode v-if="config.compactMode.enabled" :configObj.sync="config.compactMode" class="mr-2" />
            <!-- end compact mode -->

            <!-- menu widget -->
            <cbpo-widget-menus v-if="configWidget && configWidget.menu.position === 'table'" class="mr-2"
              @input="onClickMenuTable($event)" :builder="builder" :visualizationProps="visualizationProps"
              :configObj="configWidget" />
            <!-- end menu widget -->
          </div>
        </div>
        <!-- table cross-tab -->
        <div v-if="config.crossTab && config.crossTab.enabled" class="cross-tab-container">
          <template v-for="(col, index) of dataTable.columns">
            <div
              :key="col.name"
              :class="{
              'cross-tab-cell': col.cell.crossTab,
              'cross-tab-cell--not-last': col.cell.crossTab && !col.cell.crossTab.isLast,
              'cross-tab-cell--last': col.cell.crossTab && col.cell.crossTab.isLast,
              'non-cross-tab-cell': !col.cell.crossTab,
              'cross-tab-cell--border-right': col.cell.crossTab && col.cell.crossTab.index === config.crossTab.lastIndex
              }"
              :style="getCrossTabCellWidth(col, index)"
            >

              {{ col.cell.crossTab && !col.cell.crossTab.isLast ? `${config.crossTab.data[col.cell.crossTab.index]}` : '' }}
            </div>
          </template>
        </div>
        <!-- table cross-tab -->
        <div class="cbpo-table-container">
          <!--            :enabled="config.styles.beautyScrollbar"-->
          <custom-scrollbar class="cbpo-table" :class="{ '--no-data': dataTable.items.length === 0 }"
            :enabled="config.styles.beautyScrollbar"
            :lazy-load-config="{ enabled: config.pagination.type === 'lazy', isReady: config.pagination.total !== null, callback: handleLoadMore, innerSelector: '.cbpo-table-body' }"
            @scroll-x="$refs.scroller.handleScroll()">
            <!-- table summary header -->
            <div v-if="haveTableSummary('header')" v-show="!firstLoad" class="cbpo-table-header cbpo-table-summary"
              :class="{ 'cbpo-header-sticky': config.header.sticky }">
              <div v-if="isButtonAlwaysShown" class="cbpo-header-col" :style="{ 'width': `${actionWidth}px` }">
                <div class="tbl-col-header">
                  <span class="name text-truncate">{{ this.config.tableSummary.labelActionColumn }}</span>
                </div>
              </div>
              <template v-for="(col, index) of dataTable.columns">
                <div :key="col.name" :data-col="col.name" :style="{ 'width': `${col.cell.width}px` }"
                  v-show="col.visible" class="cbpo-header-col resizable">
                  <!-- header col container -->
                  <div class="tbl-col-header" :style="[getSummaryColumnStyle(col.name)]">
                    <div v-if="dataTable.summaries[index] && dataTable.summaries[index].options"
                      class="w-100 d-flex align-items-start justify-content-between">
                      <b-dropdown :id="`multi-summaries-${index}`"
                        :text="getCurrentSummaryName(dataTable.summaries[index].column, index)" class="custom-summary">
                        <b-dropdown-item v-for="(item, optionIndex) of dataTable.summaries[index].options"
                          :key="optionIndex"
                          @click="changeSummary(item, dataTable.summaries[index].column, optionIndex)"
                          :class="{ 'highlight': getCurrentOption(dataTable.summaries[index].column) === optionIndex }">
                          {{ item.text }}
                        </b-dropdown-item>
                      </b-dropdown>
                      <span class="ml-2 summary-text name text-truncate">{{
                        dataTable.summaries[index].options[getCurrentOption(dataTable.summaries[index].column)].value
                        }}</span>
                    </div>
                    <span v-else class="summary-text name text-truncate">{{ dataTable.summaries[index] ?
                      dataTable.summaries[index].value : '' }}</span>
                  </div>
                  <!-- end header col container -->
                </div>
              </template>
            </div>
            <!-- table summary -->

            <!-- table header -->
            <div v-show="!firstLoad" class="cbpo-table-header"
              :class="{ 'cbpo-header-multi-line': isMultiLineMode, 'cbpo-header-sticky': config.header.sticky }">
              <div v-if="isButtonAlwaysShown" class="cbpo-header-col" :style="{ 'width': `${actionWidth}px` }">
                <div class="tbl-col-header">
                  <span :style="colorStyle" class="name text-truncate">{{ config.bulkActions.labels.actionColumn
                    }}</span>
                </div>
              </div>

              <template v-for="(col, colIndex) of dataTable.columns">
                <div :key="col.name" :data-col="col.name" :style="{ 'width': `${col.cell.width}px` }"
                  :class="{ '--no-sort': !col.sort.enabled }" v-cbpo-connector="{
                    enabled: config.header.draggable,
                    position: {
                      start: 'center',
                      end: 'center'
                    }
                  }" v-cbpo-draggable="{
                    enabled: config.header.draggable,
                    scope: wrapperId,
                    column: col,
                    [EVENT.START_EVENT]: startEvent,
                    [EVENT.STOP_EVENT]: stopEvent
                  }" v-show="col.visible" class="cbpo-header-col resizable">
                  <!-- header col container -->
                  <div class="tbl-col-header">

                    <!-- gear icon -->
                    <span v-if="getGlobalControlOptions(config.globalControlOptions, OPTIONS.EDIT_COLUMN)"
                      @click="show(col, colIndex)" class="cbpo-grouping-setup-icon">
                      <i class="fa fa-gear"></i>
                    </span>
                    <!-- gear icon -->

                    <span :style="colorStyle" class="name text-truncate" :class="{ 'no-order': !col.sort.enabled }">
                      {{ col.displayName }}
                    </span>

                    <!-- sort table -->
                    <div class="sorting-holder" v-if="col.sort.enabled">
                      <span class="sort-link cbpo__sort-up" :class="{ 'active-span': col.sort.direction === 'asc' }"
                        @click="onClickSorting(col, 'asc')">
                      </span>
                      <span class="sort-link cbpo__sort-down" :class="{ 'active-span': col.sort.direction === 'desc' }"
                        @click="onClickSorting(col, 'desc')">
                      </span>
                    </div>
                    <!-- end sort table -->
                  </div>
                  <!-- end header col container -->

                  <!-- aggregation selection -->
                  <div
                    v-if="(col.aggregation && getGlobalControlOptions(config.globalControlOptions, OPTIONS.AGGREGATION)) || getGlobalControlOptions(config.globalControlOptions, OPTIONS.GLOBAL_GROUPING_VALUE)"
                    class="cbpo-aggr-options">
                    <b-form-select v-if="col.aggregation" size="sm" class="grouping-select-box text-truncate"
                      :value="getAggrByNameFactory(col.name)" @change="setAggrAndRefresh($event, col.name)">
                      <template v-for="type of col.aggregation.list">
                        <option :key="type.aggregation" :value="type.aggregation">{{ type.label }}</option>
                      </template>
                    </b-form-select>
                  </div>
                </div>
              </template>
            </div>
            <!-- end table header -->

            <!-- table-body -->
            <RecycleScroller v-if="dataTable.items" ref="scroller" class="cbpo-table-body" keyField="pk_id_sdk"
              v-slot="{ item, index }" :page-mode="config.pagination.type === 'lazy'" :items="dataTable.items"
              :buffer="currentBuffer" @visible="calcColumnSize">
              <!-- bulk actions -->
              <div v-if="isButtonAlwaysShown && !item.viewDetail.isChild" :key="item.key"
                :style="{ 'width': `${actionWidth}px` }" :class="{
                  'row-odd': index % 2 === 0,
                  'cbpo-table-cell--selected': isSelected(item),
                  'cbpo-table-cell--updated': isUpdated(item),
                  '--current-cursor': item.pk_id_sdk === cursor,
                }" class="cbpo-table-cell action-cell">
                <div class="cbpo-cell-actions"
                  :class="{ '--no-checkbox': config.bulkActions.mode === BULK_ACTIONS_MODE.INLINE }">
                  <div v-if="config.bulkActions.enabled && config.bulkActions.mode !== BULK_ACTIONS_MODE.INLINE"
                    @click.prevent="selectItem($event, index, item)">
                    <ActionCheckbox :isChecked="isSelected(item)" />
                  </div>
                  <ActionButtons v-if="config.bulkActions.enableInlineAction" :config="config.rowActions"
                    :dataRow="item" :items="dataTable.items" class="view-actions" />
                  <ViewButton v-if="canShowDetail" :config="config.detailView.action" :dataRow="item" :indexRow="index"
                    @showDetailView="toggleView" />
                  <!--  for cursor style -->
                  <div class="cbpo-cell--for-cursor"></div>
                </div>
              </div>
              <!-- end bulk actions -->

              <!-- table cell -->
              <template v-if="!item.viewDetail.isChild">
                <template v-for="(col, colIndex) of dataTable.columns">
                  <div v-show="col.visible" :key="`${col.name}_${index}_${colIndex}`" :data-col="col.name"
                    :style="[col.cell.style, { 'width': `${col.cell.width}px` }]" :class="[{
                      'c-grouped': colIndex === 0 && item.group.hasGroup,
                      '--expand': colIndex === 0 && item.group.isOpen,
                      'row-odd': index % 2 === 0,
                      'cbpo-table-cell--selected': isSelected(item),
                      'cbpo-table-cell--updated': isUpdated(item),
                      '--current-cursor': item.pk_id_sdk === cursor,
                      'border-bottom': index === dataTable.items.length - 1
                    }, getComputeClass(col.cell.computeClass, item.data[col.name], item.data)]"
                    @dblclick="triggerEventHandler(item)"
                    @click="deactiveAndSelect($event, dataTable.columns[colIndex], item, index), onClickGrouping(dataTable.columns[colIndex], item, index)"
                    class="cbpo-table-cell">
                    <div class="tbl-cell-body">
                      <span class="text text-truncate" v-if="item.data[col.name]" :class="isProgressFormat(col)"
                        :index="index" :style="colorStyle" :title="item.data[col.name].tooltip"
                        v-html="getFormattedValue(item.data, col.name, col.childColumn)">
                      </span>
                      <span v-else></span>
                      <button v-if="config.drillDown.enabled" class="cbpo-drilldown-btn"
                        @click.stop="openDrillDown(item.data[col.name], col)">
                        <i class="fa fa-ellipsis-h"></i>
                      </button>
                    </div>
                    <!--  for cursor style -->
                    <div class="cbpo-cell--for-cursor"></div>
                  </div>
                </template>
              </template>

              <!-- inline view -->
              <InlineDetail v-else :config-obj="config" :tableWidth="tableWidth" :item="item"
                :columns="dataTable.columns" />
              <!-- end table cell -->

            </RecycleScroller>
            <!-- end table-body -->

            <!-- table summary footer -->
            <div v-if="haveTableSummary('footer')" v-show="!firstLoad" class="cbpo-table-footer cbpo-table-summary">
              <div v-if="isButtonAlwaysShown" class="cbpo-header-col" :style="{ 'width': `${actionWidth}px` }">
                <div class="tbl-col-header">
                  <span class="name text-truncate">{{ this.config.tableSummary.labelColumnSummary }}</span>
                </div>
              </div>

              <template v-for="(col, index) of dataTable.columns">
                <div :key="col.name" :data-col="col.name" :style="{ 'width': `${col.cell.width}px` }"
                  v-show="col.visible" class="cbpo-header-col resizable">
                  <!-- header col container -->
                  <div class="tbl-col-header" :style="[getSummaryColumnStyle(col.name)]">
                    <div v-if="dataTable.summaries[index] && dataTable.summaries[index].options"
                      class="w-100 d-flex align-items-start justify-content-between">
                      <b-dropdown :id="`multi-summaries-${index}`"
                        :text="getCurrentSummaryName(dataTable.summaries[index].column, index)" class="custom-summary">
                        <b-dropdown-item v-for="(item, optionIndex) of dataTable.summaries[index].options"
                          :key="optionIndex"
                          @click="changeSummary(item, dataTable.summaries[index].column, optionIndex)"
                          :class="{ 'highlight': getCurrentOption(dataTable.summaries[index].column) === optionIndex }">
                          {{ item.text }}
                        </b-dropdown-item>
                      </b-dropdown>
                      <span class="ml-2 summary-text name text-truncate">{{
                        dataTable.summaries[index].options[getCurrentOption(dataTable.summaries[index].column)].value
                        }}</span>
                    </div>
                    <span v-else class="summary-text name text-truncate">{{ dataTable.summaries[index] ?
                      dataTable.summaries[index].value : '' }}</span>
                  </div>
                  <!-- end header col container -->
                </div>
              </template>
            </div>
            <!-- table summary -->
          </custom-scrollbar>

          <!-- table empty message -->
          <div v-if="dataTable.items.length === 0 && !firstLoad" class="cbpo-table-message">
            <span class="message" v-html="getEmptyMessage"></span>
          </div>
          <!-- end table empty message -->

          <!-- table lazy load -->
          <template v-if="config.pagination.type === 'lazy'">
            <!-- load more action -->
            <div v-if="!lazyLoading
              && dataTable.items.length > 0
              && !config.globalControlOptions.globalGrouping.config.value
              && config.pagination.current < config.pagination.total
              && !isTotalLoading
              && !loading
              && isShowLoadingMoreButton" class="cbpo-table-load-more-container"
              :style="{ 'bottom': `${getPositionOfLazyButton}px` }">
              <button class="cbpo-loading-btn" @click="handleLoadMore">Load more</button>
            </div>

            <!-- loading for lazy load -->
            <div v-if="lazyLoading" class="cbpo-table-loading-container"
              :style="{ 'bottom': `${getPositionOfLazyButton}px` }">
              <span class="message">
                <span class="fa-spin cbpo-spinner"></span>
                <span class="pl-1">Loading ...</span>
              </span>
            </div>
          </template>
          <!--end table lazy load-->
        </div>
      </div>
      <!-- <Pagination v-if="!!config && !!config.id" :configObj.sync="config.pagination"/> -->
    </div>
    <Pagination v-show="!isElementHidden"
      v-if="config.pagination.type !== 'lazy' && !(config.pagination.total < config.pagination.current) && dataTable.items.length > 0 && !config.globalControlOptions.globalGrouping.config.value"
      :configObj.sync="config.pagination" :key="config.pagination.total" @pageChange="handlePageChange()" />
    <ColumnSettings ref="groupingManager" :grouping="config.grouping" :configObj="config.globalControlOptions"
      :rows="dataTable.items" :bins="config.bins" :columns="dataTable.columns" @input="groupingChange($event)">
    </ColumnSettings>
    <div class="warning-size-content" v-show="isElementHidden">
      <span>{{ config.sizeSettings.warningText }}</span>
    </div>
  </div>
</template>
<script>
import $ from 'jquery'
import isEmpty from 'lodash/isEmpty'
import get from 'lodash/get'
import isNumber from 'lodash/isNumber'
import isEqual from 'lodash/isEqual'
import cloneDeep from 'lodash/cloneDeep'
import isFunction from 'lodash/isFunction'
import reduce from 'lodash/reduce'
import countBy from 'lodash/countBy'
import findIndex from 'lodash/findIndex'
import startCase from 'lodash/startCase'
import isObject from 'lodash/isObject'
import debounce from 'lodash/debounce'
import 'jquery-ui/ui/widgets/resizable'
import 'jquery-ui/ui/widgets/draggable'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'

// service
import CBPO from '@/services/CBPO'
import DataManager from '@/services/ds/data/DataManager'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import { getDataTypeFromType } from '@/services/ds/data/DataTypes'
import { BUS_EVENT } from '@/services/eventBusType'
import { EVENT } from '@/utils/dragAndDropUtil'
// component
import ActionButtons from '@/components/widgets/elements/table/action-buttons/ActionButtons'
import ActionCheckbox from '@/components/widgets/elements/table/action-buttons/ActionCheckbox'
import ColumnSettings from './grouping/ColumnSettings'
import CompactMode from '@/components/widgets/elements/table/compact-mode/CompactMode'
import Pagination from '@/components/widgets/elements/table/pagination/Pagination'
import WidgetBase from '@/components/WidgetBase'
import ViewButton from '@/components/widgets/elements/table/action-buttons/ViewButton'
import Menu from '@/components/widgets/menu/Menu'
import DrillDownTable from '@/components/widgets/drillDown/DrillDownTable'
import Summaries from '@/components/widgets/elements/table/summaries/Summaries'
import TimezoneSelector from '@/components/widgets/elements/timezone-selector/TimezoneSelector'
import CustomScrollbar from '@/components/custom-scrollbar/CustomScrollbar'
import { RecycleScroller } from 'vue-virtual-scroller'
// mixins
import ColumnSettingsMixins from './grouping/ColumnSettingsMixins'
import EditableEffectMixin from '@/components/widgets/elements/table/action-buttons/EditableEffectMixin'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
// directive
import connectorDirective from '@/directives/connectorDirective'
import dragDirective from '@/directives/dragDirective'
import formatDirective from '@/directives/formatDirective'
import loadingDirective from '@/directives/loadingDirective'
import lazyLoadDirective from '@/directives/lazyLoadDirective'
import horizontalMoveOnKeyboardEventDirective from '@/directives/horizontalMoveOnKeyboardEventDirective'
// config
import { BULK_ACTION_MODE, COMPACT_MODE, COMPACT_MODE_HEIGHT, makeTableDefaultConfig } from './TableConfig'
// utils
import DataTableBuilder from '@/services/ds/table/DataTableBuilder'
import { findLongestWord, getTextWidth, getWidthOfScrollBar } from '@/utils/DOMUtil'
import InlineDetail from '@/components/widgets/elements/table/InlineDetail'
import { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import { getFileName, getPollingSetting, getPollingIntervalSetting } from '@/utils/multiExportUtil'

$.fn.hasScrollBar = function (direction, additionalPixel = 0) {
  if (direction === 'vertical') {
    return this.get(0).scrollHeight > this.innerHeight() + additionalPixel
  } else if (direction === 'horizontal') {
    return this.get(0).scrollWidth > this.innerWidth() + additionalPixel
  }
  return false
}

export default {
  name: 'Table',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins,
    WidgetLoaderMixins,
    ColumnSettingsMixins,
    EditableEffectMixin
  ],
  components: {
    InlineDetail,
    Pagination,
    ColumnSettings,
    CompactMode,
    ActionButtons,
    ActionCheckbox,
    RecycleScroller,
    ViewButton,
    DrillDownTable,
    Summaries,
    TimezoneSelector,
    CustomScrollbar,
    'cbpo-widget-menus': Menu
  },
  directives: {
    'cbpo-format': formatDirective,
    'cbpo-loading': loadingDirective,
    'cbpo-draggable': dragDirective,
    'cbpo-connector': connectorDirective,
    'cbpo-lazy-load': lazyLoadDirective,
    'cbpo-horizontal-move-on-keyboard': horizontalMoveOnKeyboardEventDirective
  },
  props: {
    channelId: {
      type: String,
      default: null
    },
    autoHeight: {
      type: Boolean,
      default: false
    },
    filterObj: {
      type: Object,
      default() {
        return {}
      }
    },
    wrapperId: {
      type: String,
      default: ''
    },
    colorStyle: {
      type: Object,
      default() {
        return {}
      }
    },
    builder: {
      type: Boolean,
      default: false
    },
    visualizationProps: Object,
    configWidget: Object
  },
  watch: {
    canShowDetail(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.calcColumnSize()
      }
    },
    filterObj: {
      deep: true,
      handler(val, oldVal) {
        if (!isEqual(val, oldVal)) {
          if (this.cancelToken) this.cancelToken.cancel('Cancel token is applied')
          this.config.filter = val
          this.createCancelToken()
          this.saveRootConfig()
          this.widgetResetCurrentPage()
          this.calcTotalPage()
          this.fetch().then(async () => {
            await this.fetchSummaries()
            this.calcColumnSize()
            this.emitDataFetchedAndLastUpdated()
          })
        }
      }
    },
    globalTimezoneState: {
      handler: debounce(async function (val) {
        if (this.currentTimezone === val) {
          return
        }

        this.updateTimezone(val)

        const fetchData = async () => {
          await this.fetch()
          await this.fetchSummaries()
          this.emitDataFetchedAndLastUpdated()
        }

        const fetchAndRenderData = async () => {
          this.widgetResetCurrentPage()
          await this.fetchAndRender()
          await this.fetchSummaries()
          this.emitDataFetchedAndLastUpdated()
        }

        if (!isEmpty(this.config.filter) && this.config.pagination.type !== 'lazy') {
          await fetchData()
        } else {
          await fetchAndRenderData()
        }
      }, 300)
    },
    configReady(val) {
      if (val) {
        this.$nextTick(() => this.saveRootConfig())
      }
    },
    'dataTable.items': {
      deep: true,
      handler() {
        this.$nextTick(() => {
          if (this.config.styles.beautyScrollbar) {
            let $heightMainTable = $(this.$el).find('.cbpo-table')[0].clientHeight
            let $heightTableScroll = $(this.$el).find('.vue-recycle-scroller')[0].clientHeight
            this.isShowLoadingMoreButton = $heightTableScroll < $heightMainTable
          } else {
            let $table = $(this.$el).find('.cbpo-table')
            this.isShowLoadingMoreButton = $table.length
              ? !$(this.$el).find('.cbpo-table').hasScrollBar('vertical')
              : false
          }
        })
      }
    }
  },
  data() {
    return {
      // for query
      currentTimezone: null,
      // for table
      dataBuilder: null,
      firstLoad: true,
      dataTable: {
        columns: [],
        items: [],
        total: 0,
        summaries: []
      },
      // for items view
      isTotalLoading: false,
      isElementHidden: false,
      resizeObserver: null,
      isShowLoadingMoreButton: false,
      canShowDetail: false,
      tableWidth: 0,
      actionWidth: 0,
      currentBuffer: 0,
      // mode
      BULK_ACTIONS_MODE: BULK_ACTION_MODE, // for action click, double click,... on row
      EVENT: EVENT,
      FORMAT_DATA_TYPES: FORMAT_DATA_TYPES,
      cachedColumnsConfig: [], // for drilldown show/hide columns
      currentMultiSummariesList: [],
      isFetchGrouping: false
    }
  },
  computed: {
    isProgressFormat() {
      return col => {
        return [get(col, 'cell.format.type', ''), get(col, 'cell.format.config.fallbackType')].includes(this.FORMAT_DATA_TYPES.PROGRESS) ? 'progress-format' : ''
      }
    },
    getComputeClass() {
      return (computedStyle, value, rowValue) => isFunction(computedStyle) ? computedStyle(value, rowValue) : ''
    },
    getSummaryColumnStyle() {
      return columnName => {
        const sum = this.config.tableSummary.summaries.find(sum => sum.column === columnName)
        return sum ? sum.style : {}
      }
    },
    getPositionOfLazyButton() {
      return this.haveTableSummary('footer') ? 40 : 0
    },
    isButtonAlwaysShown() {
      return (this.config.rowActions.enabled && this.config.rowActions.display === 'always') || this.canShowDetail
    },
    isMultiLineMode() {
      return this.config.header.multiline ||
        this.config.grouping.columns.length ||
        this.config.globalControlOptions.globalGrouping.config.value
    },
    isBulkActionsShown() {
      return this.config.bulkActions.enabled && this.selectedItems.length
    },
    getAggrByNameFactory() {
      return name => {
        let binCol = this.config.bins.find(bin => bin.column.name === name)
        const globalGrouping = get(this.config, 'globalControlOptions.globalGrouping.config.value', false)
        let aggr = this.config.grouping.aggregations.find(aggr => aggr.alias === (binCol && !globalGrouping ? binCol.alias : name))
        return aggr ? aggr.aggregation : null
      }
    },
    getEmptyMessage() {
      return isEmpty(this.config.filter)
        ? this.config.messages.no_data_at_all
        : this.config.messages.no_data_found
    },
    haveTableSummary() {
      return (position = 'footer') => {
        return this.config.tableSummary.enabled &&
          this.config.tableSummary.summaries.length &&
          (this.config.tableSummary.position === position || this.config.tableSummary.position === 'both')
      }
    },
    globalTimezoneState() {
      return CBPO.channelManager()
        .getChannel(this.channelId)
        .getTimezoneSvc()
        .getTimezone()
    },
    getCrossTabCellWidth() {
    /**
     * Calculates the `min-width` style for cross-tab cells.
     *
     * - If the cell is the last cross-tab cell (`cross-tab-cell--border-right`),
     *   it adds 1px to the total width to account for the missing border-right.
     * - If the cell is not the last cross-tab cell, it calculates the combined width
     *   of the current column and the next column.
     * - For non-cross-tab cells, it simply returns the column's width.
     *   Note: This function supports only two columns. Update it if more columns are needed.
     */
      return (col, index) => {
        if (!col || !col.cell) return {}

        const currentColumn = this.dataTable.columns[index]
        const currentWidth = currentColumn && currentColumn.cell ? currentColumn.cell.width : 0
        const nextColumn = this.dataTable.columns[index + 1]
        const nextWidth = nextColumn && nextColumn.cell ? nextColumn.cell.width : 0
        const totalWidth = currentWidth + nextWidth

        if (col.cell.crossTab && col.cell.crossTab.index === this.config.crossTab.lastIndex) {
          return {
            'min-width': `${Math.round((totalWidth + 1) * 10) / 10}px`
          }
        } else if (col.cell.crossTab && !col.cell.crossTab.isLast) {
          return {
            'min-width': `${Math.round(totalWidth * 10) / 10}px`
          }
        } else {
          return {
            'min-width': `${currentWidth}px`
          }
        }
      }
    }
  },
  methods: {
    emitDataFetchedAndLastUpdated() {
      this.$emit('dataFetched', this.dataTable)
      // Get time last updated
      const firstItem = this.dataTable.items && this.dataTable.items[0]
      const lastUpdated = firstItem && (firstItem.modified || (firstItem.data && firstItem.data.modified && firstItem.data.modified.base))

      if (lastUpdated) {
        this.$emit('getLastUpdated', lastUpdated)
      }
    },
    getFormattedValue(data, orgCol, childCol) {
      if (data[orgCol].format) {
        if (data[orgCol].format.label) {
          return data[orgCol].format.label
        } else return data[orgCol].format
      } else if (childCol) {
        const childData = data[childCol]
        if (childData && childData.format) {
          return childData.format.label || childData.format
        }
      } else return data[orgCol].format
    },
    toggleView({ item, index }) {
      let detailItem = cloneDeep(item)

      if (!item.viewDetail.isOpen) {
        detailItem.viewDetail = {
          isOpen: false,
          isChild: true
        }
        detailItem.size = Object.keys(detailItem.data).length * COMPACT_MODE_HEIGHT.NORMAL
        detailItem.pk_id_sdk += '_item_view-detail'
        this.dataTable.items.splice(index + 1, 0, detailItem)
      } else {
        this.dataTable.items.splice(index + 1, 1)
      }

      item.viewDetail.isOpen = !item.viewDetail.isOpen
    },
    calculateInnerWidth(columns, actionWidth) {
      return reduce(columns, (total, col) => {
        if (col.visible) {
          total += col.cell.width
        }
        return total
      }, actionWidth)
    },
    calcColumnSize() {
      this.calcWidthActionColumn()

      const $tableContainer = $(this.$el).find('.cbpo-table')
      const tableWidth = $tableContainer.width()
      const actionWidth = this.actionWidth
      const columns = this.dataTable.columns.length ? this.dataTable.columns : this.config.columns

      let innerWidth = this.calculateInnerWidth(columns, actionWidth)

      const numOfDefaults = countBy(this.dataTable.columns.length ? this.dataTable.columns : this.config.columns, col => col.visible).true || 1

      if (numOfDefaults !== 0) {
        if (innerWidth < tableWidth) {
          // Case columns width < table width
          const totalAdjustableWidth = this.calculateInnerWidth(columns, 0)
          if (totalAdjustableWidth > 0) {
            columns.forEach((col) => {
              if (col.visible) {
                let increaseRatio = col.cell.width / totalAdjustableWidth
                let increasePixel = Math.round(increaseRatio * (tableWidth - innerWidth) * 100) / 100
                col.cell.width += increasePixel
              }
            })

            // Recalculate inner width for the true value
            innerWidth = this.calculateInnerWidth(columns, actionWidth)
          }
        } else if (innerWidth > tableWidth) {
          // case columns width  > table width
          const overflowPixel = innerWidth - tableWidth

          const adjustableColumns = columns.filter(col => col.visible && col.cell.width > 100)
          if (adjustableColumns.length > 0) {
            let totalAdjustableWidth = adjustableColumns.reduce((sum, col) => sum + (col.cell.width - 100), 0)

            adjustableColumns.forEach(col => {
              let reduceRatio = (col.cell.width - 100) / totalAdjustableWidth
              let reducePixel = Math.round(reduceRatio * overflowPixel * 100) / 100

              const calcWidth = getTextWidth(findLongestWord(col.displayName || '')) + 45.5 + 16 + 10
              const minWidth = this.config.header.multiline ? Math.max(calcWidth, 100) : 100
              col.cell.width = Math.max(minWidth, col.cell.width - reducePixel)
            })

            innerWidth = this.calculateInnerWidth(columns, actionWidth)
          }
        }
      }

      columns.forEach(col => {
        const index = findIndex(this.config.columns, column => column.name === col.name)
        if (index !== -1) {
          this.config.columns[index].cell.width = col.cell.width
        }
      })

      $(this.$el).find('.cbpo-table-body, .cbpo-table-header, .cbpo-table-footer')
        .css('width', `${innerWidth}px`)
    },
    calcTableInnerHeight() {
      const border = this.dataTable.items.length > 0 ? 0 : 1
      const $tableContainer = $(this.$el).find('.cbpo-table')
      const $tableHeaderFooter = $(this.$el).find('.cbpo-table-header, .cbpo-table-footer')
      const scrollBarHeight = $tableContainer.hasScrollBar('horizontal') && this.config.styles.beautyScrollbar ? getWidthOfScrollBar() : 0
      const spacing = $tableHeaderFooter.toArray().reduce((total, el) => {
        total += el.clientHeight
        return total
      }, 0)
      this.currentBuffer = $tableContainer.height() - spacing - scrollBarHeight - border
    },
    addEventListenerColumnHeader() {
      const $tableHeader = $(this.$el).find('.cbpo-table-header')
      const $tableFooter = $(this.$el).find('.cbpo-table-footer')
      const $tableBody = $(this.$el).find('.cbpo-table-body')
      let cacheOriginalWidth = 0
      let cacheColWidth = 0;

      (this.dataTable.columns.length ? this.dataTable.columns : this.config.columns)
        // map for run faster
        .map((column, index) => {
          // calc width base on longest word
          const calcWidth = (getTextWidth(findLongestWord(column.displayName || '')) + 45.5 + 16 + 10)
          const minWidth = this.config.header.multiline
            ? (calcWidth > 100 ? calcWidth : 100) // 45.5 for sort and gear icon, 16 for margin and 10 for ... (haven't known yet :D)
            : 100
          const isAllowSetWidth = this.config.columns[index].cell.width < minWidth && !this.config.header.resizeMinWidth

          if (this.config.header.multiline && isAllowSetWidth) {
            this.dataTable.columns[index] && (this.dataTable.columns[index].cell.width = minWidth)
            this.config.columns[index].cell.width = minWidth
          }

          const scrollbarWidth = this.config.styles.beautyScrollbar ? 0 : getWidthOfScrollBar()
          // set resize event for each column
          $(this.$el)
            .find(`.cbpo-header-col.resizable[data-col="${column.name}"]`)
            .resizable({
              handles: 'e',
              minWidth: this.config.header.resizeMinWidth ? this.config.header.resizeMinWidth : minWidth,
              start: (event) => {
                // before resized, cache those width to compare with current change
                cacheOriginalWidth = reduce(this.dataTable.columns, (total, col) => {
                  col.visible && (total += col.cell.width)
                  return total
                }, this.actionWidth)
                cacheColWidth = $(event.target).width() + scrollbarWidth
              },
              resize: (event, ui) => {
                const dif = ui.size.width - cacheColWidth
                const name = $(event.target).data('col')
                const index = this.dataTable.columns.findIndex(column => column.name === name)

                // set new width to current table
                this.dataTable.columns[index].cell.width = ui.size.width
                this.config.columns[index].cell.width = ui.size.width

                // set new width to container
                $tableHeader.css('width', cacheOriginalWidth + dif + scrollbarWidth)
                $tableBody.css('width', cacheOriginalWidth + dif + scrollbarWidth)
                $tableFooter.css('width', cacheOriginalWidth + dif + scrollbarWidth)
              }
            })
        })

      if (this.config.header.multiline) {
        this.calcColumnSize()
      }
    },
    saveRootConfig() {
      let drillDown = this.$refs.drillDown
      if (!drillDown) return false
      if (drillDown.breadcrumbs.length === 0) {
        this.cacheConfig = cloneDeep(this.config)
      }
    },
    getRootConfig() {
      return cloneDeep(this.cacheConfig)
    },
    openDrillDown(value, column) {
      let { bins, grouping, sorting, filter } = this.getRootConfig()
      let drillDownData = {
        value,
        column,
        query: {
          bins,
          grouping,
          filter,
          orders: sorting
        }
      }
      get(this.config, 'drillDown.config.path.enabled')
        ? this.$refs.drillDown.applyPath(drillDownData)
        : this.$refs.drillDown.openModal(drillDownData)
    },
    drillDownChange({ query, columns }) {
      this.widgetResetCurrentPage()
      let { bins, filter, grouping, orders } = query
      this.config.bins = bins
      this.config.filter = filter
      this.config.grouping = grouping
      this.config.sorting = orders

      // hide columns
      this.dataTable.columns.forEach(column => {
        const columnInConfig = this.config.columns.find(col => col.name === column.name)
        const baseColumn = this.cachedColumnsConfig.find(col => col.name === column.name)
        const isVisible = columns.includes(column.name) && get(baseColumn, 'visible', true)

        column.visible = isVisible
        columnInConfig.visible = isVisible
      })

      // fetch API
      return this.fetchAndRender()
    },
    checkCanShowDetail() {
      // check device and config
      if (this.config.detailView.enabled) {
        const breakpoint = this.config.detailView.action.breakpoint
        this.canShowDetail = breakpoint && isNumber(breakpoint) && window.innerWidth < breakpoint
      } else {
        this.canShowDetail = false
      }
    },
    async addCalculatedColumn() {
      await this.fetch().then(() => this.emitDataFetchedAndLastUpdated())
      this.calcColumnSize()
    },
    getFields(columns = []) {
      return columns.map(column => {
        if (column.expr) {
          if (this.isFetchGrouping && column.calculateGroupingValue) {
            return { name: column.name, alias: column.displayName | column.name }
          }
          const { expr, name, type } = column
          return { expr, alias: name, type }
        }
        return { name: column.name, alias: column.name | column.displayName }
      })
    },
    getOrderFields(columns = []) {
      return columns.map(column => {
        if (column.expr) {
          const { expr, displayName, type } = column
          return { expr, alias: displayName, type }
        }
        return { name: column.name, alias: column.displayName }
      })
    },
    handlePageChange() {
      // loading for other pagination
      this.fetch().then(() => {
        this.calcColumnSize()
        this.emitDataFetchedAndLastUpdated()
      })
    },
    handleLoadMore() {
      if (this.config.pagination.type !== 'lazy') return
      if (this.config.pagination.total <= this.config.pagination.current) return
      if (this.loading || this.lazyLoading) return

      this.config.pagination.current++
      this.fetch().then(() => this.emitDataFetchedAndLastUpdated())
    },
    setAggrForAllColumns(e) {
      this.config.globalControlOptions.globalGrouping.config.value = e
      if (e) {
        this.config.grouping.aggregations = this.config.columns.map(column => {
          if (column.type) {
            let aggregation = getDataTypeFromType(column.type).defaultAggregation.aggregation
            return {
              column: column.name,
              alias: column.name,
              aggregation: aggregation
            }
          } else {
            console.err(`${column.name} column has empty data type`)
          }
        })
      } else if (this.config.grouping.columns.length) {
        const columns = this.dataTable.columns.filter(col => col.name !== this.config.grouping.columns[0].name)
        this.config.grouping.aggregations = columns.map(column => {
          let aggregation = getDataTypeFromType(column.type).defaultAggregation.aggregation
          return {
            column: column.name,
            alias: column.name,
            aggregation: aggregation
          }
        })
      } else {
        this.config.grouping.aggregations = []
      }
      this.widgetResetCurrentPage()
      this.fetchAndRender().then(() => this.emitDataFetchedAndLastUpdated())
    },
    changeIndexColumn(columns) {
      this.config.columns = columns
      const { columns: buildColumns, summaries } = this.dataBuilder
        .mapIndexTableColumnsToCurrentConfigColumns(columns, this.dataTable.columns, this.dataTable.summaries, this.config.grouping)
      this.dataTable.summaries = summaries
      this.dataTable.columns = buildColumns
      this.calcColumnSize()
    },
    startEvent({ scope, index }, el) {
      $(el.target).addClass('_disable_cell_box')
      this.$emit('dragColumnChange', this[BUS_EVENT.DRAG_DATA_DIRECTIVE])
    },
    stopEvent({ scope, index }, el) {
      $(el.target).removeClass('_disable_cell_box')
      this.$emit('dragColumnChange', null)
    },
    setAggrAndRefresh(value, name) {
      let binCol = this.config.bins.find(bin => bin.column.name === name)
      let index = findIndex(this.config.grouping.aggregations, ['column', binCol ? binCol.alias : name])
      this.config.grouping.aggregations[index].aggregation = value
      this.fetch().then(() => this.emitDataFetchedAndLastUpdated())
    },
    async groupingChange(newConfig) {
      let { group, bins, column = {} } = newConfig
      let isFormatChange = false
      if (!isEmpty(column)) {
        const dataTableColumnIndex = column.colIndex
        // update current displayName into table
        this.$set(this.dataTable.columns, dataTableColumnIndex, { ...column.col })
        // update current displayName into config
        let configColumn = this.config.columns.find(col => col.name === column.col.name)
        // update current column into config columns
        if (configColumn) {
          isFormatChange = !isEqual(column.col.cell.format, configColumn.cell.format)
          configColumn.displayName = column.col.displayName
          configColumn.cell = column.col.cell
          configColumn.visible = column.col.visible
          // update changed column to channel
          CBPO.channelManager().getChannel(this.channelId).getColumnSvc().setColumn({ ...configColumn })
        }
      }
      if (!isEqual(group, this.config.grouping) || !isEqual(bins, this.config.bins)) {
        this.config.grouping = newConfig.group
        this.config.bins = newConfig.bins
        if (this.config.globalControlOptions.globalGrouping.config.value) {
          this.setAggrForAllColumns(true)
        } else {
          this.widgetResetCurrentPage()
          await this.fetchAndRender().then(() => this.emitDataFetchedAndLastUpdated())
        }
      }
      if (isFormatChange) {
        this.dataTable = { ...this.dataTable, ...this.dataBuilder.formatChange(this.dataTable, column, group, this.config.bins) }
      }
      this.saveRootConfig()
    },
    show(selectedCol, colIndex) {
      let bin = this.config.bins.find(bin => bin.column.name === selectedCol.name)
      let isGrouped = selectedCol.grouped
      this.$refs.groupingManager.show({
        col: cloneDeep(selectedCol),
        colIndex,
        isGrouped,
        bin
      })
    },
    // methods resizableColumns when update data source
    calculateElementHeight() {
      // TODO: change way to get all these settings
      let $title = $(this.$el).find('.cbpo-table-title')
      let $pagination = $(this.$el).find('.cbpo-pagination')
      let $thead = $(this.$el).find('.cbpo-table-header')
      let numberOfPadding = 2
      let sizeOfPadding = 8
      let tableLength = this.dataTable.items.length
      let totalHeight = tableLength > 0
        ? (tableLength + 1) * (this.config.compactMode.enabled ? COMPACT_MODE_HEIGHT.HIGH : COMPACT_MODE_HEIGHT.NORMAL)
        : 100
      this.currentBuffer = totalHeight
      return ($title.length ? $title.height() + 9 * 2 : 0) +
        ($pagination.height() || 0) +
        ($thead.height() || 0) +
        (totalHeight) +
        (numberOfPadding * sizeOfPadding)
    },
    calcWidthActionColumn() {
      if (!this.isButtonAlwaysShown) {
        this.actionWidth = 0
        return
      }
      let { rowActions, detailView, bulkActions } = this.config
      let actionWidth = bulkActions.enabled ? 50 : 20
      if (detailView.enabled && this.canShowDetail) {
        const viewBtnWidth = $(this.$el).find('.view-btn').width() || 72
        if (viewBtnWidth) actionWidth += viewBtnWidth
      }
      if (rowActions.controls && rowActions.controls.length) {
        let [control] = this.config.rowActions.controls
        if (control) actionWidth += getTextWidth(control.label) + 26
        if (control && this.config.bulkActions.mode !== BULK_ACTION_MODE.INLINE) actionWidth += 34
      }
      if (!bulkActions.enableInlineAction) {
        actionWidth = 32
      }
      this.actionWidth = actionWidth
    },
    // count how many pages there are from range size
    async calcTotalPage() {
      try {
        this.isTotalLoading = true
        this.dataTable.total = await CBPO.dsManager()
          .getDataSource(this.config.dataSource)
          .total(this._buildMainQueryParamsCount(), this.cancelToken) || 1

        // to calculate the total record
        const { pagination: { limit } } = this.config
        const rs = Math.ceil(this.dataTable.total / (limit || this.dataTable.total))
        this.config.pagination = Object.assign({}, this.config.pagination, { total: rs })
      } catch (e) {
        this.config.pagination = Object.assign({}, this.config.pagination, { total: 0 })
      } finally {
        this.isTotalLoading = false
      }
    },
    async selectRow($event, column, item, index) {
      if (column.grouped || !(this.event && (this.event.ctrl || this.event.shift))) return
      this.selectItem($event, index, item)
    },
    async onClickGrouping(column, item, index) {
      this.isFetchGrouping = true
      if (get(this.config, 'globalControlOptions.globalGrouping.config.value')) return
      if (!column.grouped || item.group.level !== 0) return
      if (!item.group.isCached) {
        // open flag
        item.group.isOpen = true

        // fetch group item
        let { items } = await this.fetchGroup(item)
        this.emitDataFetchedAndLastUpdated()

        // and cached data into current item
        item.group.cachedData = items

        // add into row
        this.dataTable.items.splice(index + 1, 0, ...items)

        item.group.isCached = true
      } else {
        item.group.isOpen
          ? this.dataTable.items.splice(index + 1, item.group.cachedData.length)
          : this.dataTable.items.splice(index + 1, 0, ...item.group.cachedData)

        item.group.isOpen = !item.group.isOpen
      }
      this.updateSizeItemData(this.config.compactMode.mode)
      this.isFetchGrouping = false
    },
    // sort event
    onClickSorting(column, dir) {
      if (column.sort.direction === dir) {
        this.config.sorting = []
        column.sort.direction = null
      } else {
        this.config.sorting = [{ column: column.name, direction: dir }]
        column.sort.direction = dir
      }
      if (get(this.config, 'pagination.type') === 'lazy') {
        this.config.pagination.current = 1
      }
      this.fetch().then(() => this.emitDataFetchedAndLastUpdated())
    },
    _buildMainQuery() {
      let q = new QueryBuilder()
      if (!isEmpty(this.config.sorting)) {
        let { column, direction } = this.config.sorting[0]
        let binColumn = this.config.bins.find(bin => bin.column.name === column)
        q.addOrder(binColumn ? binColumn.alias : column, direction)
      }
      let { current, limit } = this.config.pagination
      q.setPaging({ current, limit })
      // set aggregations
      let { columns, aggregations } = this.config.grouping
      const globalGrouping = get(this.config, 'globalControlOptions.globalGrouping.config.value', false)
      if (globalGrouping) {
        q.setGroup([], aggregations)
      } else if (!(!isEmpty(columns) && isEmpty(aggregations))) {
        q.setGroup(columns, aggregations)
      }
      // set filter
      if (!isEmpty(this.config.filter)) {
        q.setFilter(this.config.filter)
      }
      // set binning
      if (!isEmpty(this.config.bins) && !globalGrouping) {
        q.setBins(this.config.bins)
      }
      // add timezone
      if (this.config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }
      // add fields
      q.setFields(this.getFields(this.config.columns))
      return q
    },
    /**
     * Call to build data source query params
     * - Input: this.config data.
     * @return Query Params
     */
    _buildMainQueryParams() {
      let query = this._buildMainQuery().getParams()
      CBPO.dataQueryManager().setQuery(this.config.dataSource, cloneDeep(query))
      return query
    },
    _buildMainQueryParamsCount() {
      let query = this._buildMainQuery().getParams()
      query.group.aggregations = isEmpty(query.group.columns) ? query.group.aggregations : []
      return query
    },
    getColumnAliasByName(columns, name) {
      const column = columns.find(col => col.name === name)
      return column ? column.alias : null
    },
    _buildMainQueryParamsExport() {
      const query = cloneDeep(this._buildMainQuery().getParams())
      let { group: { aggregations } } = query
      // add fields query for header title
      let columnVisible = this.config.columns.filter(column => column.visible)
      let columnInTableData = this.dataTable.columns.filter(column => columnVisible.find(col => col.name === column.name))
      query.order_export = this.getOrderFields(columnInTableData)
      if (!isEmpty(aggregations)) {
        query.group.aggregations = aggregations.map(aggr => {
          aggr.alias = `${aggr.column}(${aggr.aggregation})`
          // @TODO: Revise all the `order_export` usage later.
          if (query.order_export) {
            aggr.alias = this.getColumnAliasByName(query.order_export, aggr.column)
          }
          return aggr
        }).filter(aggr => !!aggr.alias)
      }
      // add fields
      if (!isEmpty(query.group.aggregations)) {
        query.fields = []
      } else {
        query.fields = columnVisible.map(col => ({ name: col.name, alias: col.displayName || col.name }))
      }
      Object.keys(query).forEach(item => {
        if (get(this.config.exportConfig, `query.${item}`) !== undefined) {
          query[`${item}`] = this.config.exportConfig.query[`${item}`]
        }
      })
      // set query to window variable for checking if ds has error
      CBPO.dataQueryManager().setQuery(this.config.dataSource, query)
      return query
    },
    _buildFilterByGroupQuery(column, value, isBin = false) {
      let columnStr = column.name
      let q = this._buildMainQuery()
      q.resetGroup().resetPaging()
      let filter = {
        type: 'AND',
        conditions: []
      }
      let conditions = [{
        column: columnStr,
        operator: '==',
        value
      }]
      if (isBin) {
        conditions = [
          {
            column: columnStr,
            value: value.max,
            operator: `$${value.maxOp}`
          },
          {
            column: columnStr,
            value: value.min,
            operator: `$${value.minOp}`
          }
        ]
      }
      filter.conditions = conditions
      if (!isEmpty(q.getFilter())) {
        filter.conditions.push(q.getFilter())
      }
      q.setFilter(filter)
      // add timezone
      if (this.config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }
      return q
    },
    _buildFilterByGroupQueryParams(column, value, isBin) {
      return this._buildFilterByGroupQuery(column, value, isBin).getParams()
    },
    mappingDisplayName(columnsConfig, columnsData) {
      return columnsConfig.map(column => {
        if (isEmpty()) {
          let columnInDataColumns = columnsData.find(col => col.name === column.name)
          if (columnInDataColumns && !column.displayName) {
            column.displayName = columnInDataColumns.label || startCase([columnInDataColumns.name])
          }
        }
        return column
      })
    },
    async fetchSummaries() {
      if (!this.config.tableSummary.enabled) { return }
      this.dataTable.summaries = await this
        .dataBuilder
        .buildSummaries(
          this.dataTable.columns,
          get(this.config, 'tableSummary.summaries', []),
          this.config.filter,
          this.currentTimezone
        )
      this.dataTable.summaries.forEach(sum => {
        if (sum.options) this.currentMultiSummariesList.push({ column: sum.column, currentOptionIndex: 0 })
      })
    },
    async fetchGroup(item) {
      let column = this.dataTable.columns[0] // first item in group is current grouped data
      let cellValue = item.data[column.name].base
      let params = this._buildFilterByGroupQueryParams(
        column,
        cellValue,
        isObject(cellValue) && cellValue.bin
      )
      // expand data should not bin the value of group data again.
      let binLength = params.bins
      let newBinLength = params.bins
      if (params.bins) {
        params.bins = params.bins.filter(bin => column.name !== bin.column.name)
        newBinLength = params.bins
      }
      let newDataTable = {
        columns: [],
        items: []
      }
      try {
        this.showLoading()
        const data = await CBPO.dsManager()
          .getDataSource(this.config.dataSource)
          .query(params, this.cancelToken)
        let configColumns = this.dataBuilder.mapIndexConfigColumnsToCurrentTableColumns(this.config.columns, this.dataTable.columns)
        newDataTable = this.dataBuilder.buildData(
          params,
          data,
          configColumns,
          true,
          binLength !== newBinLength
        )
      } catch (e) {
        console.error(e)
      } finally {
        this.hideLoading()
      }
      return newDataTable
    },
    /**
     * Fetch table data from the configuration object.
     */
    async fetch() {
      if (!(this.config.pagination.type === 'lazy' && this.config.pagination.current !== 1)) {
        this.showLoading()
      } else {
        this.showLazyLoading()
      }
      const query = this._buildMainQueryParams()
      try {
        let data = await CBPO
          .dsManager()
          .getDataSource(this.config.dataSource)
          .query(query, this.cancelToken)
        const { items, columns } = this.dataBuilder.buildData(query, data, this.config.columns)
        const isAppendMore = this.config.pagination.type === 'lazy' && this.config.pagination.current !== 1

        this.dataTable = Object.assign(this.dataTable, {
          items: isAppendMore ? [...this.dataTable.items, ...items] : items,
          columns: columns
        })
        if (!this.autoHeight) {
          this.calcTableInnerHeight()
        }
      } catch (e) {
        console.error(e)
        this.dataTable.items = []
      } finally {
        this.$nextTick(() => {
          this.shouldShowElement()
          this.updateSizeItemData(this.config.compactMode.mode)
        })
        this.hideLoading()
        this.hideLazyLoading()
        this.firstLoad && (this.firstLoad = false)
      }
    },
    /**
     * This method is to avoid multiple data queries a time.
     */
    async fetchAndRender() {
      this.calcTotalPage()
      return this.fetch()
        .then(() => {
          this.addEventListenerColumnHeader()
          this.$nextTick(() => this.$emit('autoHeightEvent', this.config.id))
        })
    },
    /**
     * @override
     */
    widgetConfig(config) {
      this.config = Object.assign({}, cloneDeep(makeTableDefaultConfig(config)))
      this.cachedColumnsConfig = cloneDeep(this.config.columns)
      this.updateTimezone(this.config.timezone.utc)
      CBPO.channelManager().getChannel(this.channelId).getTimezoneSvc().setTimezone(this.currentTimezone)
      this.dataBuilder = new DataTableBuilder(this.config.dataSource)
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id), () => {
        this.isElementHidden = (this.$refs.tableElement.clientWidth < this.config.sizeSettings.defaultMinSize) && !this.loading
        this.$emit('checkHeaderWidget', this.isElementHidden)
        if (!this.isElementHidden) {
          // reset all width
          this.config.columns.forEach(column => {
            column.cell.width = 100
          })
          // calculated new width
          this.$nextTick(() => {
            this.calcColumnSize()
          })
        }
      })
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id), (config) => {
        this.config = config
        this.widgetInit()
      })
    },
    /**
     * @override
     */
    widgetExport(fileType, fileName, polling, pollingInterval, isMulti = false) {
      if (!isMulti) {
        var toast = this.$toasted.show('Downloading...', {
          theme: 'outline',
          position: 'top-center',
          iconPack: 'custom-class',
          className: 'cpbo-toast-export',
          icon: {
            name: 'fa fa-spinner fa-spin fa-fw',
            after: false
          },
          duration: null
        })
      }
      return CBPO
        .dsManager()
        .getDataSource(this.config.dataSource)
        /**
         * Export table data with optional polling support
         * @param {Object} queryParams - The query parameters for export
         * @param {String} fileName - Name of the exported file
         * @param {String} fileType - Type of export (csv, xlsx, etc.)
         * @param {Array} columns - Columns to include in export
         * @param {Boolean} polling - Whether to use polling mode for large exports
         * @param {Number} pollingInterval - How often to check export status in ms
         */
        .export(
          this._buildMainQueryParamsExport(),
          fileName,
          fileType,
          this.config.columns,
          polling,
          pollingInterval
        ).then(
          (fileUri) => {
            if (!isMulti) toast.goAway(0)
            fileUri && this.showDownloadFile(fileUri)
            return true
          },
          /* eslint handle-callback-err: ["error", "error"] */
          (err) => {
            if (!isMulti) toast.goAway(1500)
            return false
          }
        )
    },
    /**
     * @override
     */
    widgetInit() {
      if (!isEmpty(this.filterObj)) {
        this.config.filter = this.filterObj
      }
      this.fetchColumnsAndSaveToService(this.config.dataSource) // widget base mixins
      this.fetchAndRender().then(async () => {
        await this.fetchSummaries()
        this.emitDataFetchedAndLastUpdated()
      })
    },
    widgetResetCurrentPage: function () {
      if (this.config.pagination) {
        this.config.pagination.current = 1
      }
    },
    /**
     * Calculated and hide element if table's size is too small
     * Default min size is 250
     * Will be called inside mounted hook
     * **/
    shouldShowElement() {
      // grid item in widget layout delay this element rendered with full size
      setTimeout(() => {
        this.isElementHidden = $(this.$el).width() < this.config.sizeSettings.defaultMinSize
      }, 0)
    },
    /** Get column info **/
    getColumn(col) {
      let result = col ? { ...col } : {}
      let columns = get(this.config, 'columns', [])
      if (columns.length) {
        result = columns.find(column => col.name.includes(column.name))
      }
      return result
    },
    onClickMenuTable($event) {
      this.$emit('onClickMenuTable', $event)
    },
    updateSizeItemData(mode) {
      switch (mode) {
        case COMPACT_MODE.HIGH:
          this.dataTable = this.dataBuilder.setDataSize(this.dataTable, COMPACT_MODE_HEIGHT.HIGH)
          break
        default:
          this.dataTable = this.dataBuilder.setDataSize(this.dataTable, COMPACT_MODE_HEIGHT.NORMAL)
          break
      }
    },
    async changeSummary(item, column, optionIndex) {
      const index = this.currentMultiSummariesList.findIndex(sum => sum.column === column)
      if (index !== -1 && this.currentMultiSummariesList[index].currentOptionIndex !== optionIndex) {
        this.currentMultiSummariesList[index].currentOptionIndex = optionIndex
      }
    },
    getCurrentSummaryName(column, index) {
      const currentSum = this.currentMultiSummariesList.find(sum => sum.column === column)
      return this.dataTable.summaries[index].options[currentSum.currentOptionIndex].text
    },
    getCurrentOption(column) {
      const currentSum = this.currentMultiSummariesList.find(sum => sum.column === column)
      return currentSum.currentOptionIndex
    },
    showDownloadFile(fileUri) {
      this.$toasted.show(`<span>If your browser does not immediately download the file, please click <a href="${fileUri}" target="_blank" class="btn-export-data">here</a> to download it manually.</span>`, {
        theme: 'outline',
        position: 'top-center',
        iconPack: 'custom-class',
        className: 'cpbo-toast-export',
        fullWidth: false,
        icon: {
          name: 'fa fa-download',
          after: false
        },
        duration: 10000
      })
    },
    updateTimezone(val) {
      const result = this.config.timezone && this.config.timezone.storable
        ? localStorage.getItem('_cbpo_selected_time_zone') || val
        : val
      this.currentTimezone = result
      this.config.timezone.utc = result
    },
    updateConfigAndSummaries() {
      // Preserve the existing column widths
      const existingWidths = this.dataTable.columns.reduce((acc, col) => {
        acc[col.name] = col.cell.width
        return acc
      }, {})

      // Update the column configurations
      this.dataTable.columns = this.config.columns.map(col => {
        const existingCol = this.dataTable.columns.find(c => c.name === col.name)
        return existingCol ? { ...existingCol, ...col, cell: { ...col.cell, width: existingWidths[col.name] || col.cell.width } } : col
      })

      // Update the summaries
      this.dataTable.summaries = this.dataBuilder.updateSummaries(this.dataTable.columns, this.dataTable.summaries)
    },
    debounceResize(func, delay) {
      const self = this
      let timeout
      return function (...args) {
        if (timeout) clearTimeout(timeout)
        timeout = setTimeout(() => {
          func.apply(self, args)
        }, delay)
      }
    }
  },
  updated() {
    this.$nextTick(() => {
      $(this.$el).addClass('cbpo__table-element-ready')
    })
  },
  created() {
    if (this.filterObj) {
      this.config.filter = this.filterObj
    }
    this.dm = new DataManager()
  },
  mounted: function () {
    let self = this
    this.dm.reset()
    const debouncedResizeHandler = this.debounceResize((entries) => {
      for (let entry of entries) {
        if (entry.target.classList.contains('cbpo-table')) {
          // Calculate the table width when browser resize
          self.calcColumnSize()
        }
      }
      self.tableWidth = $(self.$el).width()
      self.checkCanShowDetail()
    }, 200)

    this.resizeObserver = new ResizeObserver(debouncedResizeHandler)
    this.resizeObserver.observe(document.body)
    const $tableContainer = this.$el.querySelector('.cbpo-table')
    if ($tableContainer) {
      this.resizeObserver.observe($tableContainer)
    }
    CBPO.$bus.$on(
      BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA,
      () => {
        this.fetchAndRender().then(async () => {
          await this.fetchSummaries()
          this.emitDataFetchedAndLastUpdated()
        })
      })
    CBPO.$bus.$on(BUS_EVENT.COMPACT_MODE_TRIGGER, (data) => { this.updateSizeItemData(data) })
    CBPO.$bus.$on(BUS_EVENT.EXPORT_WIDGET(this.config.id), async (widget, handleResponse) => {
      this.widgetExport(
        widget.fileType,
        getFileName(this.config),
        getPollingSetting(this.config),
        getPollingIntervalSetting(this.config),
        true
      ).then((res) => {
        handleResponse(res)
      })
    })
  },
  destroyed() {
    this.resizeObserver.disconnect()
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA)
    CBPO.$bus.$off(BUS_EVENT.COMPACT_MODE_TRIGGER)
    CBPO.$bus.$off(BUS_EVENT.EXPORT_WIDGET(this.config.id))
  }
}
</script>

<style scoped lang='scss'>
@import './Table.scss';
</style>
