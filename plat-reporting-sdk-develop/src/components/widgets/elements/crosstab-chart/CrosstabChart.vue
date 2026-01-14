<template>
  <div v-if='configReady' class='crosstab-chart-element'>
    <div v-cbpo-loading="{ loading: loading }">
      <chart-element v-if='chartConfig'
                     ref='chart-element'
                     :config-obj.sync='chartConfig'
                     :style='colorStyle'
                     :colorStyle='colorStyle'
                     @autoHeightEvent='checkAutoHeightConfig()'
                     @checkHeaderWidget='checkHeaderWidget'>
      </chart-element>
    </div>
  </div>
</template>

<script>
import Chart from '@/components/widgets/elements/chart/Chart'
import WidgetBase from '@/components/WidgetBase'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import $ from 'jquery'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import CBPO from '@/services/CBPO'
import { get, isFunction, cloneDeep, isEmpty, flatten } from 'lodash'
import { BUS_EVENT } from '@/services/eventBusType'
import { makeDefaultChartConfig } from '@/components/widgets/elements/chart/ChartConfig'
import { generateIdIfNotExist } from '@/utils/configUtil'
import { CrosstabChart } from '@/services/ds/crosstab/CrosstabChart'
import loadingDirective from '@/directives/loadingDirective'

export default {
  name: 'CrosstabChart',
  extends: WidgetBase,
  mixins: [WidgetBaseMixins, WidgetLoaderMixins],
  props: {
    filterObj: {
      type: Object,
      default() {
        return {}
      }
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
  components: {
    'chart-element': Chart
  },
  data() {
    return {
      // config to calculated query params
      basicChartConfig: null,
      crosstabChartConfig: null,
      // config of chart after build crosstab
      chartConfig: null
    }
  },
  methods: {
    /**
     * Default config and init listening event on busEvent
     * **/
    widgetConfig(config) {
      this.config = Object.assign(
        {},
        cloneDeep(makeDefaultChartConfig(config))
      )
      this.currentTimezone = this.config.timezone.utc
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id), ({ wpx, colSize }) => {
        this.resizeChart()
      })
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id), (config) => {
        this.$set(this, 'config', config)
        this.widgetInit()
      })
    },
    widgetInit() {
      this.fetchColumnsAndSaveToService(this.config.dataSource) // widget base mixins
      this.fetchAndRender()
    },
    fetchAndRender() {
      this.buildChartConfig()
      this.fetch()
    },
    async fetch() {
      this.showLoading()
      try {
        // build queries
        const basicQuery = !isEmpty(this.basicChartConfig.charts[0].series)
          ? this._buildBasicQueryParams(this.basicChartConfig)
          : null
        const crosstabQuery = this._buildCrosstabQueryParams(this.crosstabChartConfig)
        // build promise
        const promiseBasicQuery = basicQuery
          ? CBPO
            .dsManager()
            .getDataSource(this.config.dataSource)
            .query(basicQuery)
            .then(data => CrosstabChart.buildBasicChartData(data, this.basicChartConfig))
          : null

        const promiseCrosstabQuery = CBPO
          .dsManager()
          .getDataSource(this.config.dataSource)
          .query(crosstabQuery)
          .then(data => CrosstabChart.buildCrosstabChartData(data, this.crosstabChartConfig))

        const queriesArray = basicQuery
          ? [promiseBasicQuery, promiseCrosstabQuery]
          : [promiseCrosstabQuery]
        const promiseQueries = Promise.all(queriesArray)
        const response = await promiseQueries

        // render chart
        this.render(response)
      } catch (err) {
        console.error(err)
        console.error(('Exec is error at crosstab chart'))
      } finally {
        this.hideLoading()
        this.$emit('autoHeightEvent', this.config.id)
      }
    },
    buildChartConfig() {
      this.basicChartConfig = cloneDeep(this.config)
      this.crosstabChartConfig = cloneDeep(this.config)

      // basic type will have normal type as Chart.vue
      this.basicChartConfig.charts[0].series = this.basicChartConfig.charts[0].series
        .filter(item => !item.type.includes('crosstab'))

      // crosstab will have prefix crosstab in type series
      this.crosstabChartConfig.charts[0].series = this.crosstabChartConfig.charts[0].series
        .filter(item => item.type.includes('crosstab'))
        .map(item => {
          delete item.id
          generateIdIfNotExist(item)
          return item
        })
      // crosstab must reset grouping
      this.crosstabChartConfig.grouping = { columns: [], aggregations: [] }
    },
    /**
     * * Call to build data source query params
     * - Input: this.config data.
     * @return Query Params
     */
    _buildBasicQueryParams(config) {
      let q = new QueryBuilder()
      if (!isEmpty(config.sorting)) {
        let { column, direction } = config.sorting[0]
        let binColumn = config.bins.find(
          (bin) => bin.column.name === column
        )
        q.addOrder(binColumn ? binColumn.alias : column, direction)
      } else {
        const xCol = get(config.charts[0], 'series[0].data.x', '')
        if (xCol) {
          config.sorting[0] = { column: xCol, direction: 'asc' }
          let { column, direction } = config.sorting[0]
          let binColumn = config.bins.find(
            (bin) => bin.column.name === column
          )
          q.addOrder(binColumn ? binColumn.alias : column, direction)
        }
      }
      let { current, limit } = config.pagination
      q.setPaging({ current, limit })
      let { columns, aggregations } = config.grouping
      if (!isEmpty(aggregations)) {
        q.setGroup(columns, aggregations)
      }
      if (!isEmpty(config.filter)) {
        q.setFilter(config.filter)
      }
      if (!isEmpty(config.bins)) {
        q.setBins(config.bins)
      }
      // add timezone
      if (config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }
      return q.getParams()
    },
    _buildCrosstabQueryParams(config) {
      let q = new QueryBuilder()
      if (!isEmpty(config.sorting)) {
        let { column, direction } = config.sorting[0]
        let binColumn = config.bins.find(
          (bin) => bin.column.name === column
        )
        q.addOrder(binColumn ? binColumn.alias : column, direction)
      } else {
        const xCol = get(config.charts[0], 'series[0].data.x', '')
        if (xCol) {
          config.sorting[0] = { column: xCol, direction: 'asc' }
          let { column, direction } = config.sorting[0]
          let binColumn = config.bins.find(
            (bin) => bin.column.name === column
          )
          q.addOrder(binColumn ? binColumn.alias : column, direction)
        }
      }
      let { current, limit } = config.pagination
      q.setPaging({ current, limit })
      // build grouping
      let { columns, aggregations } = this.buildGroupingCrosstab(config)
      if (!isEmpty(aggregations)) {
        q.setGroup(columns, aggregations)
      }
      if (!isEmpty(config.filter)) {
        q.setFilter(config.filter)
      }
      if (!isEmpty(config.bins)) {
        q.setBins(config.bins)
      }
      // add timezone
      if (config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }

      return q.getParams()
    },
    buildGroupingCrosstab(config) {
      let columns = []
      let aggregations = []

      if (config.charts[0].series.length) {
        const x = [config.charts[0].series[0].data.x]
        const t = [config.charts[0].series[0].data.t]
        const y = config.charts[0].series.map(item => {
          return {
            ...item.data.y,
            ...{ id: item.id }
          }
        })

        if (isEmpty(config.bins)) {
          columns = [
            { name: x[0] },
            { name: t[0] }
          ]
        } else {
          const groupX = x.map(x => {
            const bin = config.bins.find(bin => bin.column.name === x)
            return { name: bin ? bin.alias : x }
          })
          const groupT = t.map(t => {
            const bin = config.bins.find(bin => bin.column.name === t)
            return { name: bin ? bin.alias : t }
          })
          columns = [...groupX, ...groupT]
        }

        aggregations = y.map(y => ({
          column: y.name,
          aggregation: y.aggregation,
          alias: `${y.name}_${y.aggregation}_${y.id}`
        }))
      }
      return { columns, aggregations }
    },
    render(dataSources) {
      const mergeDataSource = this.mergeDataQueries(dataSources)
      this.chartConfig = this.mergeConfigs(dataSources, mergeDataSource)
    },
    mergeDataQueries(dataSources) {
      return dataSources
        .reverse()
        .reduce((newDs, ds, i) => {
          newDs.cols = [...newDs.cols, ...ds.cols]
          newDs.rows = ds.rows.map((row, j) => {
            return i === 0
              ? [...row]
              : [...newDs.rows[j], ...row]
          })
          return newDs
        }, { cols: [], rows: [] })
    },
    mergeConfigs(dataSources, mergeDataSource) {
      const baseConfig = cloneDeep(this.basicChartConfig)
      let xColumn = null

      const crosstabSeries = flatten(
        dataSources
          .filter(ds => ds.tValues)
          .map(ds => {
            const { cols, tValues } = ds
            const { type: seriesType, axis } = this.crosstabChartConfig.charts[0].series[0]
            const type = seriesType.split('crosstab-')[1]
            // assign x column
            xColumn = cols[0].name
            // build new config
            return tValues.map((tValue, i) => ({
              name: tValue + '',
              axis,
              type,
              data: {
                x: xColumn,
                y: cols[i + 1].name
              }
            }))
          })
      )

      const baseSeries = flatten(
        dataSources
          .filter(ds => !ds.tValues)
          .map((ds, i) => {
            const { name, axis, type, data, id } = this.basicChartConfig.charts[0].series[i]
            const column = ds.cols.find(col => col.name.includes(data.y) && col.name.includes(id))
            // build new config
            return {
              name,
              axis,
              type,
              data: {
                x: xColumn,
                y: column.name
              }
            }
          })
      )

      baseConfig.charts[0].series = [
        ...baseSeries,
        ...crosstabSeries
      ]

      // reset all query
      baseConfig.bins = []
      baseConfig.filter = []
      baseConfig.grouping = { columns: [], aggregations: [] }
      baseConfig.sorting = []

      baseConfig.columns = mergeDataSource.cols.map((col, i) => {
        const baseCol = cloneDeep(this.config.columns.find(column => column.name === col.baseName))
        return {...baseCol, ...{name: col.name}}
      })

      // make it work with local datasource
      const time = new Date().getTime()
      baseConfig.dataSource = `${time}`
      window[time] = mergeDataSource

      return baseConfig
    },
    checkAutoHeightConfig() {
      if (this.config.autoHeight) {
        this.$emit('autoHeightEvent', this.config.id)
      }
    },
    checkHeaderWidget(data) {
      this.$emit('checkHeaderWidget', data)
    },
    changeColor() {
      const changeColorFn = get(this.$refs, '["chart-element"].changeColor')
      if (isFunction(changeColorFn)) changeColorFn()
    },
    resizeChart() {
      const resizeFn = get(this.$refs, '["chart-element"].resizeChart')
      if (isFunction(resizeFn)) resizeFn()
    },
    calculateElementHeight() {
      let numberOfPadding = 1
      let sizeOfPadding = 8
      const chartElement = get(this.$refs, '["chart-element"]') || {}
      return ($(this.$el).height() || 0) + (($(chartElement.$el).height() || 0)) + numberOfPadding * sizeOfPadding
    }
  },
  created() {
    if (!isEmpty(this.filterObj)) {
      this.config.filter = this.filterObj
    }
  },
  mounted() {
    CBPO.$bus.$on(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA, () => {
      this.fetchAndRender()
    })
  },
  destroyed() {
    CBPO.$bus.$off(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA)
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.id))
  },
  watch: {
    filterObj: {
      deep: true,
      handler(val) {
        if (this.cancelToken) this.cancelToken.cancel('Cancel token is applied')
        this.createCancelToken()
        this.config.filter = val
        this.fetchAndRender()
      }
    },
    colorStyle: {
      deep: true,
      handler() {
        this.changeColor()
      }
    }
  }
}
</script>
