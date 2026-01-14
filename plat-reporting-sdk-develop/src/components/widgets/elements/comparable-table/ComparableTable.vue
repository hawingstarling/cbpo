<template>
    <div v-if="configReady" class="cbpo-table-element-container"
        ref="comparableTableElement"
        :style="config.style"
        :css="config.css"
        :id="config.id"
        v-cbpo-loading="{loading: isLoading}"
       >
    <div class="cbpo-table-title"
         :style="colorStyle"
         v-if="config.widget.title.enabled">
      {{ config.widget.title.text }}
    </div>
    <div class="cbpo-table-reporting">
      <div class="cbpo-screen-cover">
        <div class="cbpo-table-action d-flex py-2">
          <div class="w-100 d-flex align-items-center">
            <!-- timezone selector -->
            <TimezoneSelector
              v-if="config.timezone.enabled"
              :configObj.sync="config.timezone"
              class="mr-2 ml-auto"/>
            <!-- end timezone -->
          </div>
        </div>
        <div class="cbpo-table-container">
          <custom-scrollbar
            class="cbpo-table"
            :class="{'--no-data': dataTable.items.length === 0}"
            :enabled="isBeautyScrollbar"
            :lazy-load-config="{enabled: config.pagination.type === 'lazy', isReady: config.pagination.total !== null, callback: handleLoadMore, innerSelector: '.cbpo-table-body'}"
            @scroll-x="$refs.scroller.handleScroll()">
            <!-- table header -->
            <div v-show="!firstLoad" class="cbpo-table-header" :class="{'cbpo-header-multi-line': isMultiLineMode}">
              <template v-for="(col) of dataTable.columns">
                <div :key="col.alias"
                     :data-col="col.alias"
                     :style="{'width': `${col.cell.width}px`}"
                     v-cbpo-connector="{
                       enabled: config.header.draggable,
                       position: {
                         start: 'center',
                         end: 'center'
                       }
                     }"
                     v-cbpo-draggable="{
                        enabled: config.header.draggable,
                        scope: wrapperId,
                        column: col,
                        [EVENT.START_EVENT]: startEvent,
                        [EVENT.STOP_EVENT]: stopEvent
                     }"
                     v-show="col.visible"
                     class="cbpo-header-col resizable">
                  <!-- header col container -->
                  <div class="tbl-col-header">

                    <span :style="colorStyle" class="name text-truncate">
                      {{ col.displayName }}
                    </span>

                  </div>
                  <!-- end header col container -->

                </div>
              </template>
            </div>
            <!-- end table header -->
            <!-- table-body -->
            <RecycleScroller
              v-if="isReady && dataTable.items"
              class="cbpo-table-body"
              page-mode
              keyField="pk_id_sdk"
              v-slot="{ item, index }"
              :items="dataTable.items"
              :buffer="currentBuffer"
              @visible="calcColumnSize"
            >
              <!-- table cell -->
              <template v-if="!item.viewDetail.isChild">
                <template v-for="(col, colIndex) of dataTable.columns">
                  <div v-show="col.visible"
                       :key="`${col.alias}_${index}_${colIndex}`"
                       :data-col="col.alias"
                       :style="[col.cell.style, { 'width' : `${col.cell.width}px` }]"
                       :class="[{
                      'c-grouped': colIndex === 0 && item.group.hasGroup,
                      '--expand': colIndex === 0 && item.group.isOpen,
                      'row-odd': index % 2 === 0,
                      'border-bottom' :index === dataTable.items.length -1
                     }, getComputeClass(col.cell.computeClass, item.data[col.alias], item.data)]"
                       class="cbpo-table-cell">
                    <div class="tbl-cell-body">
                      <span class="text text-truncate" v-if="item.data[col.alias]"
                            :class="isProgressFormat(col)"
                            :index="index"
                            :style="colorStyle"
                            :title="item.data[col.alias].tooltip"
                            v-html="item.data[col.alias].format && item.data[col.alias].format.label ?  item.data[col.alias].format.label : item.data[col.alias].format">
                      </span>
                      <span v-else></span>
                    </div>
                    <!--  for cursor style -->
                    <div class="cbpo-cell--for-cursor"></div>
                  </div>
                </template>
              </template>
              <!-- end table cell -->

            </RecycleScroller>
            <!-- end table-body -->
          </custom-scrollbar>
          <!-- table empty message -->
          <div v-if="dataTable.items.length === 0 && !firstLoad" class="cbpo-table-message">
            <span class="message">{{ getEmptyMessage }}</span>
          </div>
          <!-- end table empty message -->

        </div>
      </div>
    </div>
  </div>
</template>
<script>
import $ from 'jquery'
import _ from 'lodash'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'

import { COMPACT_MODE_HEIGHT } from '.././table/TableConfig'

// mixin
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
// directive
import connectorDirective from '@/directives/connectorDirective'
import dragDirective from '@/directives/dragDirective'
import formatDirective from '@/directives/formatDirective'
import loadingDirective from '@/directives/loadingDirective'
import lazyLoadDirective from '@/directives/lazyLoadDirective'
import horizontalMoveOnKeyboardEventDirective from '@/directives/horizontalMoveOnKeyboardEventDirective'
// service
import CBPO from '@/services/CBPO'
import DataManager from '@/services/ds/data/DataManager'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import { BUS_EVENT } from '@/services/eventBusType'
import { EVENT } from '@/utils/dragAndDropUtil'

// utils
import DataTableBuilder from '@/services/ds/table/DataTableBuilder'
import dataFormatManager, { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import { findLongestWord, getTextWidth, getWidthOfScrollBar } from '@/utils/DOMUtil'
import { getFileName, getPollingSetting, getPollingIntervalSetting } from '@/utils/multiExportUtil'

import { SHORT_CODES } from '@/utils/exprUtils'
import expressionParser from '@/services/ds/expression/ExpressionParser'

import { RecycleScroller } from 'vue-virtual-scroller'
import TimezoneSelector from '@/components/widgets/elements/timezone-selector/TimezoneSelector'
import CustomScrollbar from '@/components/custom-scrollbar/CustomScrollbar'

export default {
  props: {
    configWidget: Object,
    colorStyle: {
      type: Object,
      default() {
        return {}
      }
    },
    wrapperId: {
      type: String,
      default: ''
    },
    filterObj: {
      type: Object,
      default() {
        return {}
      }
    }
  },
  components: {
    RecycleScroller,
    TimezoneSelector,
    CustomScrollbar
  },
  mixins: [
    WidgetBaseMixins,
    WidgetLoaderMixins
  ],
  directives: {
    'cbpo-format': formatDirective,
    'cbpo-loading': loadingDirective,
    'cbpo-draggable': dragDirective,
    'cbpo-connector': connectorDirective,
    'cbpo-lazy-load': lazyLoadDirective,
    'cbpo-horizontal-move-on-keyboard': horizontalMoveOnKeyboardEventDirective
  },
  data() {
    return {
      isLoading: true,
      isReady: false,
      currentTimezone: null,
      dataTable: {
        columns: [],
        items: [],
        total: 100,
        summaries: []
      },
      tableWidth: 0,
      currentBuffer: 0,
      dataBuilder: null,
      expressionParser,
      FORMAT_DATA_TYPES: FORMAT_DATA_TYPES,
      firstLoad: true,
      EVENT: EVENT
    }
  },
  computed: {
    isBeautyScrollbar() {
      return _.get(this.config, 'styles.beautyScrollbar', false)
    },
    getComputeClass() {
      return (computedStyle, value, rowValue) => _.isFunction(computedStyle) ? computedStyle(value, rowValue) : ''
    },
    isProgressFormat() {
      return col => {
        return [_.get(col, 'cell.format.type', ''), _.get(col, 'cell.format.config.fallbackType')].includes(this.FORMAT_DATA_TYPES.PROGRESS) ? 'progress-format' : ''
      }
    },
    globalTimezoneState() {
      return CBPO.channelManager()
        .getChannel(this.channelId)
        .getTimezoneSvc()
        .getTimezone()
    },
    getEmptyMessage() {
      return _.isEmpty(this.config.filter)
        ? this.config.messages.no_data_at_all
        : this.config.messages.no_data_found
    }
  },
  async created() {
    this.currentTimezone = this.config.timezone.utc
    this.dataTable.columns = this.config.columns
    if (this.filterObj) this.config.filter = _.cloneDeep(this.filterObj)
    this.dm = new DataManager()
  },
  methods: {
    changeIndexColumn(columns) {
      this.config.columns = columns
      this.dataTable.columns = columns
      this.calcColumnSize()
    },
    addEventListenerColumnHeader() {
      let _self = this
      const $tableHeader = $(_self.$el).find('.cbpo-table-header')
      const $tableFooter = $(_self.$el).find('.cbpo-table-footer')
      const $tableBody = $(_self.$el).find('.cbpo-table-body')
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

          // set resize event for each column
          $(_self.$el)
            .find(`.cbpo-header-col.resizable[data-col="${column.alias}"]`)
            .resizable({
              handles: 'e',
              minWidth: this.config.header.resizeMinWidth ? this.config.header.resizeMinWidth : minWidth,
              start: function(event) {
                // before resized, cache those width to compare with current change
                cacheOriginalWidth = _.reduce(_self.dataTable.columns, (total, col) => {
                  if (col.visible) {
                    total += col.cell.width
                  }
                  return total
                }, 0)
                cacheColWidth = $(event.target).width() + getWidthOfScrollBar()
              },
              resize: function(event, ui) {
                const dif = ui.size.width - cacheColWidth
                const alias = $(event.target).data('col')
                const index = _self.dataTable.columns.findIndex(column => column.alias === alias)

                // set new width to current table
                _self.dataTable.columns[index].cell.width = ui.size.width
                _self.config.columns[index].cell.width = ui.size.width

                // set new width to container
                $tableHeader.css('width', cacheOriginalWidth + dif + getWidthOfScrollBar())
                $tableBody.css('width', cacheOriginalWidth + dif + getWidthOfScrollBar())
                $tableFooter.css('width', cacheOriginalWidth + dif + getWidthOfScrollBar())
              }
            })
        })

      if (this.config.header.multiline) {
        this.calcColumnSize()
      }
    },
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
    startEvent({ scope, index }, el) {
      $(el.target).addClass('_disable_cell_box')
      this.$emit('dragColumnChange', this[BUS_EVENT.DRAG_DATA_DIRECTIVE])
    },
    stopEvent({ scope, index }, el) {
      $(el.target).removeClass('_disable_cell_box')
      this.$emit('dragColumnChange', null)
    },
    isMultiLineMode() {
      return this.config.header.multiline ||
            this.config.grouping.columns.length ||
            this.config.globalControlOptions.globalGrouping.config.value
    },
    getFields(columns = []) {
      return columns.map(column => {
        if (column.expr) {
          const { expr, displayName, type } = column
          return { expr, alias: displayName, type }
        }
        return { name: column.name, alias: column.displayName | column.name }
      })
    },
    _buildMainQuery(baseFilter, rowFilter) {
      const filter = {
        conditions: [..._.get(baseFilter, 'conditions', []), ..._.get(rowFilter, 'conditions', [])],
        type: 'AND'
      }
      let q = new QueryBuilder()
      let { aggregations } = this.config.grouping
      q.setGroup([], aggregations)
      // add fields
      q.setFields(this.getFields(this.config.columns))
      // add filter
      q.setFilter(filter)
      // add timezone
      if (this.config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }
      return q
    },
    _buildMainQueryParams(baseFilter, filter) {
      let query = this._buildMainQuery(baseFilter, filter).getParams()
      CBPO.dataQueryManager().setQuery(this.config.dataSource, _.cloneDeep(query))
      return query
    },
    async fetch() {
      this.isLoading = true
      let queryRowDataAll = []
      this.isReady = false
      this.initialDataTableItems()
      const normalQueryCol = this.config.columns.filter(col => {
        if (_.isEmpty(col.expr) && _.isEmpty(_.get(col, 'format.expr', false))) return true
      })
      const exprQueryCol = this.config.columns.filter(col => {
        if (!_.isEmpty(col.expr) || !_.isEmpty(_.get(col, 'format.expr', false))) return true
      })

      for (const [index, row] of _.cloneDeep(this.config.rows).entries()) {
        queryRowDataAll.push(this.queryRowData(normalQueryCol, row.filter, index))
        if (exprQueryCol.length > 0) {
          exprQueryCol.forEach(col => {
            queryRowDataAll.push(this.queryDataByExpr(col, row.filter, index))
          })
        }
      }

      try {
        await Promise.all(queryRowDataAll)
        this.config.rows.forEach((row, index) => {
          this.dataTable.items[index].data[this.config.columns[0].name] = {
            base: row.data.name || row.data.alias, format: row.data.name || row.data.alias, tooltip: row.data.name || row.data.alias
          }
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.isReady = true
        this.isLoading = false
        this.firstLoad && (this.firstLoad = false)
      }
    },
    initialDataTableItems() {
      const itemsDefault = {
        data: {},
        group: {},
        key: null,
        pk_id_sdk: '',
        size: null,
        viewDetail: {}
      }
      this.dataTable.items = []
      this.config.rows.forEach((row, index) => {
        this.dataTable.items.push({})
        this.dataTable.items[index] = itemsDefault
      })
    },
    widgetConfig(config) {
      this.dataBuilder = new DataTableBuilder(this.config.dataSource)
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id), (config) => {
        this.config = config
        this.fetchAndRender()
      })
      CBPO.$bus.$on(BUS_EVENT.EXPORT_WIDGET(this.config.id), async(widget, handleResponse) => {
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
    async queryDataByExpr (column, filter, index) {
      try {
        const expressions = [{
          name: SHORT_CODES.FORMAT,
          attributes: {
            // format: _.get(column, 'format', ''),
            type: _.get(column, 'type', ''), // optional, for format is format string
            expression: _.get(column, 'format.expr', '')
            // prefix: _.get(column, 'format.common.prefix', ''),
            // suffix: _.get(column, 'format.common.suffix', '')
          },
          content: column.expr || '',
          shortCode: column.expr || ''
        }]
        let config = _.cloneDeep(this.config)
        _.set(config, 'filter', {
          conditions: [
            ..._.get(filter, 'conditions', []),
            ..._.get(config, 'filter.conditions', [])
          ],
          type: 'AND'
        })
        const evalData = await this.expressionParser.eval(expressions, config)
        const formatObj = _.get(column, 'format')
        const base = evalData[0].value
        const format = formatObj
          ? dataFormatManager.create(formatObj, true)(base, true)
          : base
        const tooltip = formatObj
          ? dataFormatManager.create(formatObj, false)(base, false)
          : base
        this.dataTable.items[index].data[`${column.alias}`] = {base, format, tooltip}
      } catch (error) {
        console.error(error)
        this.dataTable.items = []
        this.isReady = true
      }
    },
    async queryRowData(columnsConfig, rowFilter, index) {
      const query = this._buildMainQueryParams(this.config.filter, rowFilter)
      try {
        let data = await CBPO
          .dsManager()
          .getDataSource(this.config.dataSource)
          .query(query, this.cancelToken)
        const items = this.dataBuilder.buildDataComparableTable(query, data, columnsConfig)
        this.dataTable.items[index] = {
          data: {...this.dataTable.items[index]['data'], ...items[0].data},
          group: items[0].group,
          key: items[0].key,
          pk_id_sdk: items[0].pk_id_sdk,
          size: items[0].size,
          viewDetail: items[0].viewDetail
        }
      } catch (e) {
        console.error(e)
        this.dataTable.items = []
        this.isReady = true
      }
    },
    calcColumnSize() {
      const $tableContainer = $(this.$el).find('.cbpo-table')
      const tableWidth = $tableContainer.width()
      const actionWidth = 0
      const columns = this.dataTable.columns.length ? this.dataTable.columns : this.config.columns

      const innerWidth = _.reduce(columns, (total, col) => {
        if (col.visible) {
          total += col.cell.width
        }
        return total
      }, actionWidth)

      const numOfDefaults = _.countBy(this.dataTable.columns.length ? this.dataTable.columns : this.config.columns, col => col.cell.width === 100 && col.visible).true || 1 // 100 is default width
      let additionalPixel = 0

      if (numOfDefaults !== 0) {
        if (innerWidth < tableWidth) {
          additionalPixel = Math.round(((tableWidth - innerWidth) / numOfDefaults) * 100) / 100
          _.map(columns, col => {
            if (col.cell.width === 100 && col.visible) {
              col.cell.width += additionalPixel

              // update width
              const index = _.findIndex(this.config.columns, column => column.name === col.name)
              this.config.columns[index].cell.width = col.cell.width
            }
          })
        }
      }

      $(this.$el).find('.cbpo-table-body, .cbpo-table-header, .cbpo-table-footer')
        .css('width',
          innerWidth < tableWidth
            ? additionalPixel * numOfDefaults + innerWidth
            : innerWidth
        )
    },
    async fetchAndRender() {
      await this.fetch().then(() => this.emitDataFetched())
      this.addEventListenerColumnHeader()
    },
    emitDataFetched() {
      this.$emit('dataFetched', this.dataTable)
    },
    widgetExport(fileType, fileName, polling, pollingInterval, isMulti = false) {
      if (this.isLoading) {
        this.$toasted.show('Data is fetching. Please try again when data is ready', {
          theme: 'outline',
          position: 'top-center',
          iconPack: 'custom-class',
          className: 'cpbo-toast-export',
          icon: {
            name: 'fa fa-spinner fa-spin fa-fw',
            after: false
          },
          duration: 3000
        })
        return
      }
      if (!isMulti) {
        var toast = this.$toasted.show('Downloading...', {
          theme: 'outline',
          position: 'top-center',
          iconPack: 'custom-class',
          className: 'cpbo-toast-export',
          icon: {
            name: 'fa fa-times',
            after: false
          },
          duration: null
        })
      }
      const localId = `sdk-comparable-table-${Date.now()}`
      const visibleCols = this.dataTable.columns.filter(col => {
        const column = this.config.columns.find(c => c.alias === col.alias)
        return column ? column.visible : false
      })
      window[localId] = {
        cols: visibleCols,
        rows: this.dataTable.items.map(item =>
          visibleCols.map(col => (item.data[col.alias] || item.data[col.name]).base)
        )
      }
      return CBPO
        .dsManager()
        .getDataSource(localId)
        /**
         * Export table data with optional polling support
         * @param {Object} queryParams - The query parameters for export
         * @param {String} fileName - Name of the exported file
         * @param {String} fileType - Type of export (csv, xlsx, etc.)
         * @param {Array} columns - Columns to include in export
         * @param {Boolean} polling - Whether to use polling mode for large exports
         * @param {Number} pollingInterval - How often to check export status in ms
         */
        .export(new QueryBuilder().getParams(), fileName, fileType, this.config.columns, polling, pollingInterval)
        .then(
          () => {
            if (!isMulti) toast.goAway(1500)
            return true
          },
          /* eslint handle-callback-err: ["error", "error"] */
          (err) => {
            if (!isMulti) toast.goAway(1500)
            return false
          }
        )
    }
  },
  watch: {
    filterObj: {
      deep: true,
      async handler(val, oldVal) {
        if (!_.isEqual(val, oldVal)) {
          this.config.filter = _.cloneDeep(val)
          await this.fetchAndRender()
          this.calcColumnSize()
        }
      }
    },
    globalTimezoneState(timezone) {
      if (timezone === this.currentTimezone) return
      this.currentTimezone = timezone
      this.config.timezone.utc = timezone
      this.fetchAndRender()
    },
    configReady(newIsReady, oldIsReady) {
      if (newIsReady !== oldIsReady && newIsReady) {
        this.$nextTick(() => this.fetchAndRender())
      }
    }
  },
  mounted: function() {
    let self = this
    this.dm.reset()
    this.resizeObserver = new ResizeObserver((entries, observer) => {
      self.tableWidth = $(self.$el).width()
    })
    this.resizeObserver.observe(document.body)
    CBPO.$bus.$on(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA, () => { this.fetchAndRender() })
  },
  beforeDestroy() {
    (this.dataTable.columns.length ? this.dataTable.columns : this.config.columns)
      .map(col => {
        try {
          $(this.$el)
            .find(`.cbpo-header-col.resizable[data-col="${col.alias}"]`)
            .resizable('destroy')
        } catch {
          // prevent instance is not create but called destroy method
        }
      })
  },
  destroyed() {
    this.resizeObserver.disconnect()
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA)
    CBPO.$bus.$off(BUS_EVENT.EXPORT_WIDGET(this.config.id))
  }
}
</script>
<style scoped lang='scss'>
@import '@/components/widgets/elements/table/Table.scss';
</style>
