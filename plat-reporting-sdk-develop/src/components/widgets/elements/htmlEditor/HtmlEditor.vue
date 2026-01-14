<template>
  <div v-if="configReady" ref="htmlEditor" :id="config.id" :class="config.css" :style="config.style"
    v-cbpo-loading="{ loading: loading }" class="cbpo-s cbpo-container cbpo-container-html-editor">
    <div v-show="!isElementHidden" v-if="config.builder.enabled" class="editor-btn">
      <b-button-group v-if="editMode" size="sm" variant="default">
        <b-button :pressed.sync="editMode" size="sm" @click="cancel()">
          <i class="fa fa-times-circle-o" aria-hidden="true"></i>
          Cancel
        </b-button>
        <b-button :pressed.sync="editMode" size="sm" @click="update()">
          <i class="fa fa-dot-circle-o" aria-hidden="true"></i>
          Update
        </b-button>
      </b-button-group>
      <b-button v-else :pressed.sync="editMode" size="sm">
        <i class="fa fa-pencil-square-o" aria-hidden="true"></i>
        Edit
      </b-button>
    </div>
    <editor v-show="!isElementHidden" v-if="editMode" :api-key="apiKey" :init="{
      height: minHeight,
      menubar: true,
      plugins: config.options.plugins,
      toolbar: config.options.toolbar,
    }" :initial-value="config.content" v-model="config.content" />
    <div class="ql-container" v-show="!isElementHidden"
      :style="{ 'visibility': loadingContent && !editMode ? 'visible' : 'hidden' }"
      :class="{ 'max-height': !parsingContent || parsingContent.length === 0, 'isInvisible': !(loadingContent && !editMode) }">
      <div class="ql-editor" v-cbpo-image-loader="{ callback: emitAutoHeight }" v-html="parsingContent">
      </div>
    </div>
    <div class="warning-size-content" v-show="isElementHidden">
      <span>{{ config.sizeSettings.warningText }}</span>
    </div>
  </div>
</template>

<script>
import Editor from '@tinymce/tinymce-vue'
import WidgetBase from '@/components/WidgetBase'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import CBPO from '@/services/CBPO'
import $ from 'jquery'
import cloneDeep from 'lodash/cloneDeep'
import get from 'lodash/get'
import isEmpty from 'lodash/isEmpty'
import loadingDirective from '@/directives/loadingDirective'
import imageLoaderDirective from '@/directives/imageLoaderDirective'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import { makeDefaultHtmlEditorConfig } from './HtmlEditorConfig'
import { HtmlReplacer } from '@/services/ds/html/HtmlReplacer'
import { BUS_EVENT } from '@/services/eventBusType'
import expressionParser from '@/services/ds/expression/ExpressionParser'
import { getFileName, getPollingSetting, getPollingIntervalSetting } from '@/utils/multiExportUtil'

export default {
  name: 'HtmlEditor',
  extends: WidgetBase,
  mixins: [WidgetBaseMixins, WidgetLoaderMixins],
  props: {
    builder: Boolean,
    filterObj: {
      type: Object,
      default() {
        return {}
      }
    },
    dataSources: {
      type: Array,
      default: () => []
    }
  },
  directives: {
    'cbpo-loading': loadingDirective,
    'cbpo-image-loader': imageLoaderDirective
  },
  components: {
    editor: Editor
  },
  data() {
    return {
      // This data will be assign to apply callback in updated hook
      minHeight: 400,
      apiKey: '',
      currentTimezone: null,
      htmlRs: new HtmlReplacer(),
      expressionParser,
      parsingContent: null,
      editMode: false,
      updateMode: false,
      originalContent: '',
      loadingContent: false,
      isElementHidden: false
    }
  },
  methods: {
    async calcTotalPage() {
      // Do nothing right now
    },
    emitAutoHeight() {
      this.$emit('autoHeightEvent', this.config.id)
    },
    widgetConfig(config) {
      makeDefaultHtmlEditorConfig(config)
      config.builder.enabled = this.builder
      this.currentTimezone = this.config.timezone.utc
      if (config.dataSource) {
        this.fetchAndRender()
      } else {
        // if content is set, show content and hide loading
        if (this.config.content) {
          this.loadingContent = true
          this.parsingContent = this.config.content
          this.hideLoading()
        }
      }
      this.originalContent = this.config.content
      CBPO.$bus.$on(BUS_EVENT.ELEMENT_RESIZE_EVENT(this.config.id), () => {
        // check visible
        this.isElementHidden = this.$refs.htmlEditor.clientWidth < this.config.sizeSettings.defaultMinSize
        this.$emit('checkHeaderWidget', this.isElementHidden)
      })
    },
    calculateElementHeight() {
      const paddingHeight = 16 * 0.5 * 2
      const imgHeight = paddingHeight + $(this.$el).find('.ql-editor img')
        .toArray()
        .reduce((total, imgEl) => { total += imgEl.naturalHeight; return total }, 0)
      const containerHeight = $(this.$el).find('.ql-editor').height()
      // 500 is minHeight which can be accepted
      return this.builder ? this.minHeight : Math.max(imgHeight, containerHeight)
    },
    _buildMainQueryParams() {
      let query = this._buildMainQuery().getParams()
      CBPO.dataQueryManager().setQuery(this.config.dataSource, cloneDeep(query))
      return query
    },
    // Build query
    _buildMainQuery() {
      let q = new QueryBuilder()
      if (!isEmpty(this.config.sorting)) {
        let { column, direction } = this.config.sorting[0]
        let binColumn = this.config.bins.find(bin => bin.column.name === column)
        q.addOrder(binColumn ? binColumn.alias : column, direction)
      }
      let { current, limit } = this.config.pagination
      q.setPaging({ current, limit })
      if (!isEmpty(this.config.grouping.columns)) {
        let { columns, aggregations } = this.config.grouping
        q.setGroup(columns, aggregations)
      }
      if (!isEmpty(this.config.filter)) {
        q.setFilter(this.config.filter)
      }
      if (!isEmpty(this.config.bins)) {
        q.setBins(this.config.bins)
      }
      // add timezone
      if (this.config.timezone.enabled && this.currentTimezone) {
        q.setTimezone(this.currentTimezone)
      }
      return q
    },
    async fetchAndRender() {
      this.loadingContent = false
      this.parsingContent = this.config.content
      this.fetch().then(() => {
        // handle after fetch
      })
    },
    async fetch() {
      this.showLoading()
      try {
        await this.evalExprInContent()
      } catch (e) {
        console.error(e)
      }
      return CBPO
        .dsManager()
        .getDataSource(this.config.dataSource)
        .query(this._buildMainQueryParams(), this.cancelToken)
        .then(data => {
          this.parsingContent = this.htmlRs
            .setDataSource(data)
            .parse(this.config.columns, this.config.bins, this.parsingContent)
          this.loadingContent = true
          this.hideLoading()
          this.$nextTick(() => this.emitAutoHeight())
        }, er => {
          this.loadingContent = true
          this.parsingContent = this.parsingContent.replace(/(?:{{:)(.*?)(?:}})/g, '#Error')
          this.hideLoading()
          this.$nextTick(() => this.emitAutoHeight())
        })
    },
    async evalExprInContent() {
      const decodedContent = this.htmlDecode(this.config.content)
      const expressions = this.expressionParser.getExpressions(decodedContent)
      if (expressions && expressions.length) {
        const dataSources = this.expressionParser.getDataSourceIDs(expressions)
        this.$emit('update:dataSources', [...dataSources])
        const evalData = await this.expressionParser.eval(expressions, this.config)
        const { newEvalData, parsingContent } = this.expressionParser.replaceShortcodeContent(evalData, decodedContent)
        // remove text before Error or No data
        const errRegex = /<span(\s+)?(style\s*=\s*"([^"]*)")?>#Error<\/span>/gi
        const noDataRegex = /<span(\s+)?(style\s*=\s*"([^"]*)")?>#No data<\/span>/gi
        this.parsingContent = parsingContent
          .replace(errRegex, '<span class="text-danger">Error</span>')
          .replace(noDataRegex, 'No data')
        // build chart if current shortCode contains chart
        this.$nextTick(() => this.expressionParser.applyCallback(newEvalData))
      }
    },
    htmlDecode(input) {
      let e = document.createElement('textarea')
      e.innerHTML = input
      return e.childNodes.length === 0 ? '' : e.childNodes[0].nodeValue
    },
    cancel() {
      // reset content
      this.config.content = this.originalContent
      this.editMode = false
    },
    async update() {
      // update content
      this.originalContent = this.config.content
      await this.fetchAndRender()
      this.editMode = false
      this.$emit('updateConfig')
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
    getColumnAliasByName(columns, name) {
      const column = columns.find(col => col.name === name)
      return column ? column.alias : null
    },
    _buildMainQueryParamsExport() {
      const query = cloneDeep(this._buildMainQuery().getParams())
      let { group: { aggregations } } = query
      // add fields query for header title
      let columnVisible = this.config.columns.filter(column => column.visible)
      query.order_export = this.getOrderFields(columnVisible)
      if (!isEmpty(aggregations)) {
        query.group.aggregations = aggregations.map(aggr => {
          aggr.alias = `${aggr.column}(${aggr.aggregation})`
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
    widgetExport(dataSource, fileName, fileType, polling, pollingInterval, isMulti = false) {
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
        .getDataSource(dataSource)
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
        .then(
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
    }
  },
  created() {
    this.showLoading()
    if (!isEmpty(this.filterObj)) {
      this.config.filter = this.filterObj
    }
    this.apiKey = get(window, 'API_KEY_EDITOR') || process.env.VUE_APP_API_KEY_EDITOR
  },
  mounted: function () {
    CBPO.$bus.$on(BUS_EVENT.EXPORT_WIDGET(this.config.id), async (widget, handleResponse) => {
      this.widgetExport(
        widget.dataSource,
        getFileName(this.config),
        widget.fileType,
        getPollingSetting(this.config),
        getPollingIntervalSetting(this.config),
        true
      ).then((res) => {
        handleResponse(res)
      })
    })
  },
  watch: {
    builder(val) {
      this.config.builder.enabled = val
    },
    filterObj: {
      deep: true,
      handler(val) {
        if (this.cancelToken) this.cancelToken.cancel('Cancel token is applied')
        this.createCancelToken()
        this.config.filter = val
        if (this.config.dataSource) {
          this.fetchAndRender()
        }
      }
    }
  },
  destroyed() {
    CBPO.$bus.$off(BUS_EVENT.EXPORT_WIDGET(this.config.id))
  }
}
</script>
<style scoped lang="scss">
@import './HtmlEditor';
</style>
