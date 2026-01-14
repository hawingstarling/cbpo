<template>
  <div :id="config.id"
       ref="crosstabTable"
       v-if="configReady"
       v-cbpo-loading="{loading: loading}"
       class="cbpo-crosstab-table">
    <div v-show="!isElementHidden" class="cbpo-crosstab-widget-header"
         v-if="config.widget.title.enabled">
      <span :style="colorStyle" class="text">{{config.widget.title.text}}</span>
    </div>
    <div v-show="!isElementHidden && cm.y.length !== 0" class="cbpo-crosstab-table-container">
      <div class="cbpo-crosstab-table-container__inner" :class="{'table__empty-data': cm.y.length === 0}">
        <div class="cbpo-crosstab-left-side">
          <div :style="{'min-height': `${emptyCell.height}px`}" class="cross-tab-x-header" :class="{'crosstab-empty-cell': !config.xColumns.length}">
            <template  v-if="config.xColumns.length">
              <!--Name of first element of X Columns-->
              <div class="cbpo-first-x-column">
                <span :style="colorStyle" class="cbpo-text-value">
                  {{config.xColumns[0].displayName}}
                </span>
              </div>
              <!--Sort Order First X Column-->
              <div v-if="config.xColumns[0].sort.enabled" class="cbpo-sorting-holder">
                <span class="cbpo-sort-link cbpo__sort-up"
                      :class="{'active': isActiveSort('asc')}"
                      @click="sort(config.xColumns[0], 'asc')">
                </span>
                <span class="cbpo-sort-link cbpo__sort-down"
                      :class="{'active': isActiveSort('desc')}"
                      @click="sort(config.xColumns[0], 'desc')">
                </span>
              </div>
            </template>
          </div>

          <div class="cbpo-crosstab-table--tab-scroll-container">
            <!--Table Tab-->
            <CrosstabTableRowHeader
              ref="crosstab-tab"
              :x-values="cm.x"
              :x-headers="cm.xHeaders"
              :x-bin-columns="cm.binColumns.x"
              :x-columns="config.xColumns"
              :dm="cm.dm"
              :colorStyle="colorStyle"
            />
          </div>
        </div>
        <div class="cbpo-crosstab-right-side">
          <div :style="{'min-height': `${emptyCell.height}px`}" class="cbpo-crosstab-table--header-scroll-container">
            <!--Table header-->
            <CrosstabTableColHeader
              ref="crosstab-header"
              :t-values="cm.t"
              :t-bin-columns="cm.binColumns.t"
              :t-columns="config.tColumns"
              :dm="cm.dm"
              @heightChange="updateEmptyCellHeight($event)"
              :colorStyle="colorStyle"
            />
          </div>

          <div class="cbpo-crosstab-table--body-scroll-container">
            <!--Table Cell-->
            <CrosstabTableBody
              ref="crosstab-body"
              :y-values="cm.y"
              :y-bin-columns="cm.binColumns.y"
              :y-columns="config.yColumns"
              :dm="cm.dm"
              :colorStyle="colorStyle"
            />
          </div>
        </div>
      </div>
    </div>
    <!--Warning Text-->
    <div class="warning-size-content" :class="{'show': (!isElementHidden && cm.y.length === 0) || isElementHidden}">
      <span class="error-text">
        <template v-if="!isElementHidden && cm.y.length === 0 && !loading">
          {{ config.filter ? config.messages.no_data_found : config.messages.no_data_at_all }}
        </template>
        <template v-if="isElementHidden">
          {{ config.sizeSettings.warningText }}
        </template>
      </span>
    </div>
    <Pagination v-show="!isElementHidden"
                v-if="(config.pagination.total >= config.pagination.current) && cm.y.length > 0"
                :configObj.sync="config.pagination"
                @pageChange="fetch"/>
  </div>
</template>

<script>
import CBPO from '@/services/CBPO'
import CrosstabTableRowHeader from '@/components/widgets/elements/crosstab-table/CrosstabTableRowHeader'
import CrosstabTableColHeader from '@/components/widgets/elements/crosstab-table/CrosstabTableColHeader'
import CrosstabTableBody from '@/components/widgets/elements/crosstab-table/CrosstabTableBody'
import WidgetBase from '@/components/WidgetBase'
import Pagination from '@/components/widgets/elements/table/pagination/Pagination'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import CrosstabTableManager from '@/services/ds/crosstab/CrosstabTable'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import { makeCrosstabTableDefaultConfig } from './CrosstableTableConfig'
import { BUS_EVENT } from '@/services/eventBusType'
import isEmpty from 'lodash/isEmpty'
import uniqBy from 'lodash/uniqBy'
import cloneDeep from 'lodash/cloneDeep'
import startCase from 'lodash/startCase'
import range from 'lodash/range'
import loadingDirective from '@/directives/loadingDirective'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import { getFileName, getPollingSetting, getPollingIntervalSetting } from '@/utils/multiExportUtil'
import $ from 'jquery'

export default {
  name: 'CrosstabTable',
  data() {
    return {
      emptyCell: {
        height: 0
      },
      currentTimezone: null,
      cm: null,
      range: range,
      isElementHidden: false
    }
  },
  props: {
    filterObj: {
      type: Object,
      default: () => {}
    },
    colorStyle: {
      type: Object,
      default() {
        return {}
      }
    }
  },
  directives: {
    'cbpo-loading': loadingDirective
  },
  extends: WidgetBase,
  mixins: [WidgetBaseMixins, WidgetLoaderMixins],
  components: {
    CrosstabTableBody,
    CrosstabTableColHeader,
    CrosstabTableRowHeader,
    Pagination
  },
  computed: {
    isActiveSort() {
      return direction => {
        let name = this.config.xColumns[0].name
        let binColumn = this.config.bins.find(bin => bin.column.name === name)
        let sortColumn = this.config.sorting.find(col => (binColumn ? binColumn.alias : name) === col.column)
        return sortColumn ? sortColumn.direction === direction : false
      }
    }
  },
  watch: {
    filterObj: {
      deep: true,
      handler(val) {
        if (this.cancelToken) this.cancelToken.cancel('Cancel token is applied')
        this.createCancelToken()
        this.config.filter = val
        this.widgetResetCurrentPage()
        this.fetchAndRender()
      }
    }
  },
  methods: {
    sort(column, direction) {
      let {sorting} = this.config
      let name = column.name
      let binColumn = this.config.bins.find(bin => bin.column.name === name)
      name = binColumn ? binColumn.alias : name
      let current = sorting.find(col => col.column === name)
      // remove current sorting if it existed
      sorting = sorting.filter(col => col.column !== name)
      // only add new if direction change
      if (!current || current.direction !== direction) {
        sorting = [...sorting, {column: name, direction}]
      }
      this.config.sorting = sorting
      this.fetch()
    },
    convertNameIntoDisplayName(config) {
      let callback = (column) => {
        if (!column.displayName) {
          column.displayName = startCase(column.name)
        }
        return column
      }
      this.config.xColumns = this.config.xColumns.map(callback)
      this.config.yColumns = this.config.yColumns.map(callback)
      this.config.tColumns = this.config.tColumns.map(callback)
    },
    updateEmptyCellHeight(value) {
      this.emptyCell.height = value
    },
    widgetInit() {
      this.config.filter = this.filterObj
      this.fetchAndRender()
    },
    // extend config from default config and start to listen events
    widgetConfig(config) {
      makeCrosstabTableDefaultConfig(config)
      this.currentTimezone = this.config.timezone.utc
      this.convertNameIntoDisplayName(config)
      // hide element when element is too small
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id), () => {
        this.isElementHidden = this.$refs.crosstabTable.clientWidth < this.config.sizeSettings.defaultMinSize
        this.$emit('checkHeaderWidget', this.isElementHidden)
      })
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id), (config) => {
        this.$set(this, 'config', config)
        this.widgetInit()
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
    // get total page
    async calcTotalPage() {
      const total = await CBPO
        .dsManager()
        .getDataSource(this.config.dataSource)
        .total(this._buildMainQueryParams(), this.cancelToken)
      // to calculate the total record
      const {
        pagination: { limit }
      } = this.config
      const rs = Math.ceil(total / (limit || total))
      this.config.pagination = { ...this.config.pagination, total: rs }
    },
    // calculate with between table
    calculatedWidthTables() {
      this.$nextTick(() => {
        let $emptyCell = $(this.$el).find('.cross-tab-x-header')
        let $headerRef = this.$refs['crosstab-header']
        let $bodyRef = this.$refs['crosstab-body']
        if ($headerRef && $bodyRef) {
          let $header = $headerRef.$el
          let $body = $bodyRef.$el
          let width = $($header).width() > $($body).width() ? $($header).width() : $($body).width()
          $($header).width(width)
          $($body).width(width)
          $emptyCell.width(Math.round($emptyCell.width()))
        }
      })
    },
    registerScrollEvent() {
      let $bodyScroller = $(this.$el).find('.cbpo-crosstab-table--body-scroll-container')
      let $headerScroller = $(this.$el).find('.cbpo-crosstab-table--header-scroll-container')
      let $tabScroller = $(this.$el).find('.cbpo-crosstab-table--tab-scroll-container')

      $bodyScroller
        .off('scroll')
        .on('scroll', function() {
          let _left = $(this).scrollLeft()
          let _top = $(this).scrollTop()
          $headerScroller.scrollLeft(_left, 0)
          $tabScroller.scrollTop(_top, 0)
        })
    },
    // call API when render, this method will call fetch method
    fetchAndRender() {
      this
        .fetch()
        .then(() => {
          // handle render after fetch
          this.calcTotalPage()
          this.registerScrollEvent()
        })
    },
    // call API from dataSource
    fetch() {
      this.showLoading()
      return CBPO
        .dsManager()
        .getDataSource(this.config.dataSource)
        .query(this._buildMainQueryParams(), this.cancelToken)
        .then(data => {
          this.handleResponseData(data)
          this.calculatedWidthTables()
        }, err => {
          console.log(err)
          this.handleResponseData({rows: [], cols: []})
        })
    },
    handleResponseData(data) {
      let {xColumns, yColumns, tColumns, bins, sorting} = this.config
      this
        .cm
        .setDataSource(data)
        .mappingStatusColumns(bins, xColumns, yColumns, tColumns)
        .mappingDataSourceWithColumns(bins, xColumns, yColumns, tColumns, sorting)
      this.$nextTick(() => {
        this.hideLoading()
      })
    },
    /**
     * Call to build data source query params
     * - Input: this.config data.
     * @return Query Params
     */
    // Call method build query and set that query into CBPO query manager
    _buildMainQueryParams () {
      let query = this._buildMainQuery().getParams()
      CBPO.dataQueryManager().setQuery(this.config.dataSource, cloneDeep(query))
      return query
    },
    _buildMainQueryParamsExport() {
      let query = cloneDeep(this._buildMainQuery().getParams())
      let { group: { aggregations } } = query
      if (!isEmpty(aggregations)) {
        query.group.aggregations = aggregations.map(aggr => {
          aggr.alias = `${aggr.column}(${aggr.aggregation})`
          return aggr
        })
      }
      CBPO.dataQueryManager().setQuery(this.config.dataSource, query)
      return query
    },
    // Build query
    _buildMainQuery () {
      let q = new QueryBuilder()

      // set sorting query
      if (!isEmpty(this.config.sorting)) {
        this.config.sorting.forEach(sorting => {
          let { column, direction } = sorting
          q.addOrder(column, direction)
        })
      }

      // set pagination query
      let { current, limit } = this.config.pagination
      q.setPaging({ current, limit })

      // set group query
      let {columns, aggregations} = this._buildGroupingQueryFromColumns()
      q.setGroup(columns, aggregations)

      // set filter query
      if (!isEmpty(this.config.filter)) {
        q.setFilter(this.config.filter)
      }

      // set bins query
      if (!isEmpty(this.config.bins)) {
        q.setBins(this.config.bins)
      }
      // add timezone
      if (this.config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }
      return q
    },
    // Build group query from 3 type columns (x, y, t)
    _buildGroupingQueryFromColumns() {
      let columns = []
      let aggregations = []
      let {xColumns, yColumns, tColumns, bins} = this.config
      if (isEmpty(xColumns) || isEmpty(yColumns) || isEmpty(tColumns)) throw Error('Crosstab Table must have at least 1 xColumns, 1 yColumns and 1 tColumns')
      if (!isEmpty(bins)) {
        xColumns.forEach(xColumn => {
          let xBin = bins.find(bin => bin.column.name === xColumn.name)
          columns = [...columns, xBin ? {name: xBin.alias} : xColumn]
          if (xBin) {
            aggregations = [
              ...aggregations,
              {
                column: xBin.column.name,
                alias: xBin.column.name,
                aggregation: 'count' // This column will not be shown so set any valid aggregation
              }
            ]
          }
        })
        tColumns.forEach(tColumn => {
          let tBin = bins.find(bin => bin.column.name === tColumn.name)
          columns = [...columns, tBin ? {name: tBin.alias} : tColumn]
          if (tBin) {
            aggregations = [
              ...aggregations,
              {
                column: tBin.column.name,
                alias: tBin.column.name,
                aggregation: 'count' // This column will not be shown so set any valid aggregation
              }
            ]
          }
        })
        yColumns.forEach(yColumn => {
          let {aggregation: {aggregation}, name} = yColumn
          let yBin = bins.find(bin => bin.column.name === name)
          if (yBin) {
            aggregations = [...aggregations, {
              column: yBin.alias,
              alias: yBin.alias,
              aggregation
            }]
          }
        })
      } else {
        columns = [...xColumns, ...tColumns]
      }
      let yAggregations = yColumns
        .map(yColumn => {
          let {aggregation: {alias, aggregation}, name} = yColumn
          return {
            column: name,
            aggregation,
            alias
          }
        })
      aggregations = [...aggregations, yAggregations[0]].filter(yColumn => !!yColumn)
      aggregations = uniqBy(aggregations, 'alias')
      columns = uniqBy(columns, 'name')
      return { columns, aggregations }
    },
    widgetResetCurrentPage: function() {
      if (this.config.pagination) {
        this.config.pagination.current = 1
      }
    },
    /**
     * @override
     */
    widgetExport (fileType, fileName, polling, pollingInterval, isMulti = false) {
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
        .export(this._buildMainQueryParamsExport(), fileName, fileType, this.config.columns, polling, pollingInterval)
        .then(() => {
          if (!isMulti) toast.goAway(1500)
          return true
        },
        /* eslint handle-callback-err: ["error", "error"] */
        (err) => {
          if (!isMulti) toast.goAway(1500)
          return false
        })
    }
  },
  mounted() {
    CBPO.$bus.$on(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA, () => {
      this.fetchAndRender()
    })
  },
  created() {
    if (!isEmpty(this.filterObj)) {
      this.config.filter = this.filterObj
    }
    this.cm = new CrosstabTableManager()
  },
  destroyed() {
    CBPO.$bus.$off(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA)
    // cancel resize event
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id))
    // cancel element refresh data event
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id))

    CBPO.$bus.$off(BUS_EVENT.EXPORT_WIDGET(this.config.id))
  }
}
</script>
<style lang="scss" scoped>
  @import "CrosstabTable";
</style>
