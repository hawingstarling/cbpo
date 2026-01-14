<template>
  <div v-if="configReady"
    class="cbpo-s cbpo-widget cbpo-widget-control cbpo-feature-container"
    ref="widget"
    :style="globalStyles"
  >
    <cbpo-widget-title
      class="cbpo-widget-title"
      v-if="config.widget.title.enabled"
      :configObj="config.widget"
      :configStyles="headerStyle"
    />
    <div class="cbpo-control-features cbpo-p-cs"
        :style="colorStyle"
        :class="{
                  'p-1': !config.filter.builder.enabled && !config.columnManager.enabled && !(config.menu.enabled && builder) && !config.action.elements.length && !config.filter.form.config.controls.length,
                  'menu-position': canShow(config, 'widget.title.enabled', false)
                }">
      <div class="w-100 d-flex">
        <!--dynamic filter-->
        <slot name="queryBuilder">
          <cbpo-element-builder-filter
            v-if="config.filter.builder.enabled"
            ref="queryBuilder"
            :elements="config.elements || []"
            :configObj.sync="config.filter.builder.config"
            @filterChange="updateFilter($event)">
          </cbpo-element-builder-filter>
        </slot>

        <!--Manage Column-->
        <slot name="columnManager">
          <cbpo-column-manager
            v-if="isShowColumnManager([ELEMENT.TABLE])"
            :class="{'ml-2': config.filter.builder.enabled}"
            :columns="columnsOfElements"
            :configObj.sync="config.columnManager.config"
            @input="columnChange($event)">
          </cbpo-column-manager>
        </slot>

        <!--Calculated columns-->
        <cbpo-calculated-column
          v-if="config.calculatedColumn.enabled"
          :columns.sync="columnsOfElements"
          @input="addCalculatedColumn($event)"
        >
        </cbpo-calculated-column>
        <!--Widget Export-->
        <!--! TODO: Remove condition with element = 3 after support download csv for html -->
        <cbpo-widget-menus
          v-if="builder || (config.menu && config.menu.enabled)"
          @input="onClickMenuWidget($event)"
          :builder="builder"
          :visualizationProps="visualizationProps"
          :configObj="config"
          :id="`${config.id}_id`"
        />
      </div>
      <div class="w-100 pt-2" v-if="config.filter.builder.readable.enabled && dataReadableFilter">
        <cbpo-readable-filter :dataFilter="dataReadableFilter" :dataColumns="config.elements[0].config.columns" class="cbpo-readable-filter"></cbpo-readable-filter>
      </div>
      <div class="w-100 d-flex"
        :class="{
          'filter-center' : config.filter.alignment === 'center',
          'filter-right' : config.filter.alignment === 'right'
        }">
        <!--Basic filter-->
        <cbpo-filter-form
          ref="filterForm"
          :class="{
            'filter-center': config.filter.alignment === 'center',
            'filter-right' : config.filter.alignment === 'right'
          }"
          v-show="isShowFilterForm"
          v-if="!config.filter.builder.enabled && config.filter.form.config.controls.length"
          :controls.sync="config.filter.form.config.controls"
          :globalFilter="config.filter.globalFilter.enabled"
          :waitingForGlobalFilter="config.waitingForGlobalFilter"
          @filterChange="updateFilter($event)"
        />

        <!--Action-->
        <div class="cbpo-wrapper-action">
          <div
            class="cbpo-action-item"
            v-for="(element, index) in config.action.elements"
            :key="index"
          >
            <cbpo-element-button
              v-if="element.type === 'cbpo-element-button'"
              :configObj="element.config"
            />
          </div>
        </div>
      </div>
    </div>
    <!--There is 3 status, please check in @/services/globalService.js to see more-->
    <template v-if="getGlobalStatus !== false">
      <template v-for="(element, index) in config.elements">
        <cbpo-element-table ref="elements"
                            v-if="element.type === 'cbpo-element-table'"
                            :key="`${index}_${config.id}`"
                            :configObj.sync="element.config"
                            :filterObj="query"
                            :style="colorStyle"
                            :colorStyle="colorStyle"
                            :builder="builder"
                            :auto-height="config.autoHeight"
                            :configWidget="config"
                            @autoHeightEvent="checkAutoHeightConfig()"
                            @onClickMenuTable="onClickMenuWidget($event)"
                            @checkHeaderWidget="checkHeaderWidget"
                            @getLastUpdated="getLastUpdated"/>
        <cbpo-element-comparable-table ref="elements"
                            v-if="element.type === 'cbpo-element-comparable-table'"
                            :key="`${index}_${config.id}`"
                            :configObj.sync="element.config"
                            :filterObj="query"
                            :colorStyle="colorStyle"
                            :configWidget="config"/>
        <cbpo-element-crosstab-table ref="elements"
                                     v-if="element.type === 'cbpo-element-crosstab-table'"
                                     :key="`${index}_${config.id}`"
                                     :configObj.sync="element.config"
                                     :filterObj="query"
                                     :style="colorStyle"
                                     :colorStyle="colorStyle"
                                     @autoHeightEvent="checkAutoHeightConfig()"
                                     @checkHeaderWidget="checkHeaderWidget"/>
        <cbpo-element-chart ref="elements"
                            v-if="element.type === 'cbpo-element-chart'"
                            :key="`${index}_${config.id}`"
                            :configObj.sync="element.config"
                            :filterObj="query"
                            :class="{'--cbpo-no-border': !canShow(element, 'config.widget.title.enabled')}"
                            :style="colorStyle"
                            :colorStyle="colorStyle"
                            @autoHeightEvent="checkAutoHeightConfig()"
                            @checkHeaderWidget="checkHeaderWidget"
                            @getLastUpdated="getLastUpdated"/>
        <cbpo-element-gauge ref="elements"
                            v-if="element.type === 'cbpo-element-gauge'"
                            :key="`${index}_${config.id}`"
                            :configObj.sync="element.config"
                            :filterObj="query"
                            :class="{'--cbpo-no-border': !canShow(element, 'config.widget.title.enabled')}"
                            :style="colorStyle"
                            :colorStyle="colorStyle"
                            @autoHeightEvent="checkAutoHeightConfig()"/>
        <cbpo-element-heat-map ref="elements"
                            v-if="element.type === 'cbpo-element-heat-map'"
                            :key="`${index}_${config.id}`"
                            :configObj.sync="element.config"
                            :filterObj="query"
                            :class="{'--cbpo-no-border': !canShow(element, 'config.widget.title.enabled')}"
                            :style="colorStyle"
                            :colorStyle="colorStyle"
                            @autoHeightEvent="checkAutoHeightConfig()"
                            @checkHeaderWidget="checkHeaderWidget"/>
        <cbpo-element-html-editor ref="elements"
                                  v-if="element.type === 'cbpo-element-html-editor'"
                                  :key="`${index}_${config.id}`"
                                  :configObj.sync="element.config"
                                  :filterObj="query"
                                  :builder="builder"
                                  :style="colorStyle"
                                  @updateConfig="updateElementConfig()"
                                  @autoHeightEvent="checkAutoHeightConfig()"
                                  @checkHeaderWidget="checkHeaderWidget"
                                  :dataSources.sync="dataSources"
                                />
      </template>
    </template>
    <template v-else-if="!config.filter.globalFilter.enabled">
      <div class="d-block text-center p-2">
        <i class="fa fa-circle-o-notch fa-spin"></i> Waiting for the filter to get data...
      </div>
    </template>
  </div>
</template>
<script>

import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import HeatMap from '@/components/widgets/elements/heat-map/HeatMap'
import Title from '@/components/widgets/title/Title'
import FilterForm from '@/components/widgets/form/FilterForm'
import Table from '@/components/widgets/elements/table/Table'
import ComparableTable from '@/components/widgets/elements/comparable-table/ComparableTable'
import Chart from '@/components/widgets/elements/chart/Chart'
import HtmlEditor from '@/components/widgets/elements/htmlEditor/HtmlEditor'
import BulletGauge from '@/components/widgets/elements/gauge/Gauge'
import Button from '@/components/widgets/actions/Button'
import Menu from '@/components/widgets/menu/Menu'
import QueryBuilder from '@/components/widgets/builder/BuilderFilter'
import ColumnManager from '@/components/widgets/columns/ManageColumns'
import ReadableFilter from '@/components/widgets/builder/ReadableFilter'
import CrosstabTable from '@/components/widgets/elements/crosstab-table/CrosstabTable'
import { makeWidgetDefaultConfig } from './WidgetConfig'
import { generateIdIfNotExist } from '@/utils/configUtil.js'
import { convertColumnObjectToColumnName, parseOperators, SUPPORT_LOGIC } from '@/utils/filterUtils'
import { BUS_EVENT } from '@/services/eventBusType'
import { CONTROL_TYPE } from '@/components/widgets/form/FilterControlConfig'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import get from 'lodash/get'
import findIndex from 'lodash/findIndex'
import forEach from 'lodash/forEach'
import cloneDeep from 'lodash/cloneDeep'
import sortBy from 'lodash/sortBy'
import isEmpty from 'lodash/isEmpty'
import isEqual from 'lodash/isEqual'
import $ from 'jquery'
import CBPO from '@/services/CBPO'
import CalculatedColumn from '@/components/widgets/calculated/Column'
import _ from 'lodash'
import { getFileName, getPollingSetting, getPollingIntervalSetting } from '@/utils/multiExportUtil'

export default {
  name: 'Widget',
  extends: WidgetBase,
  props: {
    builder: Boolean,
    visualizationProps: Object,
    configObj: Object
  },
  components: {
    'cbpo-widget-title': Title,
    'cbpo-widget-menus': Menu,
    'cbpo-filter-form': FilterForm,
    'cbpo-element-table': Table,
    'cbpo-element-comparable-table': ComparableTable,
    'cbpo-element-chart': Chart,
    'cbpo-element-html-editor': HtmlEditor,
    'cbpo-element-button': Button,
    'cbpo-element-builder-filter': QueryBuilder,
    'cbpo-column-manager': ColumnManager,
    'cbpo-element-gauge': BulletGauge,
    'cbpo-element-heat-map': HeatMap,
    'cbpo-element-crosstab-table': CrosstabTable,
    'cbpo-calculated-column': CalculatedColumn,
    'cbpo-readable-filter': ReadableFilter
  },
  mixins: [WidgetBaseMixins],
  data() {
    return {
      ELEMENT,
      key: null,
      cachedGlobalFilter: null,
      columnsOfElements: [],
      filter: {},
      query: {},
      dataReadableFilter: {},
      dataSources: [],
      isShowFilterForm: true
    }
  },
  computed: {
    // get state of filter. Used by watch hook
    getGlobalFilterState() {
      return CBPO.channelManager().getChannel().getFilterSvc().getGlobalFilter()
    },
    getGlobalStatus() {
      return CBPO.channelManager().getChannel().getFilterSvc().getGlobalFilterReady()
    },
    canShow() {
      return (object, path, defaultValue = null) => get(object, path, defaultValue)
    },
    globalStyles () {
      let style = get(this.config, 'widget.style', {})
      if (isEmpty(style)) return ''
      let result = {}
      for (let st in style) {
        if (style[st] !== null) {
          switch (st) {
            case 'background_color':
              result['background-color'] = style[st]
              break
            case 'border_width':
              result['border-style'] = 'solid'
              result['border-width'] = style[st] ? `${style[st]}px` : `1px`
              break
            case 'border_radius':
              result['border-radius'] = style[st] ? `${style[st]}px` : `1px`
              break
          }
        }
      }
      return result
    },
    headerStyle () {
      // const self = this
      let style = get(this.config, 'widget.style', {})
      if (isEmpty(style)) return ''
      let headerStyle = {}
      let borderWidth = 0
      // let menuStyle = {}
      for (let st in style) {
        if (style[st] !== null) {
          switch (st) {
            case 'header_background_color':
              headerStyle['background-color'] = style[st]
              break
            case 'header_foreground_color':
              headerStyle['color'] = style[st]
              break
            case 'border_width':
              borderWidth = parseInt(style[st])
              // menuStyle['top'] = `${borderWidth + 5}px`
              // menuStyle['right'] = `${borderWidth + 5}px`
              break
            case 'border_radius':
              const radius = borderWidth < style[st] ? style[st] - borderWidth : 0
              headerStyle['border-top-left-radius'] = `${radius}px`
              headerStyle['border-top-right-radius'] = `${radius}px`
              // if (!borderWidth) menuStyle['top'] = '5px'
              // menuStyle['right'] = `${((radius / 2) + borderWidth) + 5}px`
              break
          }
        }
      }
      // $(document).ready(function () {
      //   $(`#${self.config.id}_id`).css(menuStyle)
      // })
      return headerStyle
    },
    colorStyle () {
      let style = get(this.config, 'widget.style.foreground_color', null)
      if (!style) return {}
      return {color: style}
    },
    isShowColumnManager () {
      return array => this.config.columnManager.enabled && array.includes(this.config.elements[0].type)
    }
  },
  methods: {
    applyNewConfigColumnsForSummaries() {
      if (this.$refs.elements && this.$refs.elements.length > 0 && this.$refs.elements[0].updateConfigAndSummaries) {
        this.$refs.elements[0].updateConfigAndSummaries()
      }
    },
    updateFilter(filter) {
      if (filter.global) {
        // global need to be run after other controls
        setTimeout(() => {
          CBPO.channelManager()
            .getChannel()
            .getFilterSvc()
            .setGlobalFilter(filter.global)
          CBPO
            .channelManager()
            .getChannel()
            .getFilterSvc()
            .setControls(this.config.filter.form.config.controls)
        }, 0)
      } else {
        // do not build query if status is not ready)
        if (filter.builder) {
          this.dataReadableFilter = filter.builder
        }
        // this.buildFilterObject(filter)
        if (get(this.visualizationProps, 'widgetSettingMethod', null) && filter.builder) {
          this.visualizationProps.widgetSettingMethod(cloneDeep(this.config))
        } else {
          this.buildFilterObject(filter)
        }
      }
    },
    mapControlFromGlobalFilter() {
      let globalControls = cloneDeep(CBPO
        .channelManager()
        .getChannel()
        .getFilterSvc()
        .getControls())
      let controls = get(this.config, 'filter.form.config.controls', [])
      if (!isEmpty(globalControls) && !isEmpty(controls)) {
        globalControls.forEach(gloCtrl => {
          let index = findIndex(controls, ctrl => gloCtrl.config.common.column.name === ctrl.config.common.column.name && gloCtrl.config.common.operator === ctrl.config.common.operator)
          if (index !== -1) {
            // remove old filter
            this.removeOldFilterFromControl(this.filter.form, gloCtrl.config)
            // map empty selected
            if (gloCtrl.type === CONTROL_TYPE.SELECT) {
              controls[index].config.selection.empty.isEmptySelected = gloCtrl.config.selection.empty.isEmptySelected
            }
            // map new value
            controls[index].config.common.value = gloCtrl.config.common.value
          }
        })
      }
    },
    removeOldFilterFromControl(filter, control) {
      if (!filter) return
      if (!filter.conditions) {
        if (filter.operator === control.common.operator && filter.column === control.common.column.name) {
          filter.value = control.common.value
        }
      } else {
        filter.conditions.forEach(f => {
          this.removeOldFilterFromControl(f, control)
        })
        filter.conditions = filter.conditions.filter(f => f.value !== undefined)
      }
    },
    buildFilterObject(filter, isMergeGlobalFilter = false) {
      // query of widget
      this.query = {}
      // state of query
      this.filter = {...this.filter, ...filter}
      // merge global filter into builder or form filter
      let builderMode = this.config.filter.builder.enabled
      let isCurrentGlobalFilter = _.get(this.config, 'filter.globalFilter.enabled', false)
      let queryFilter = builderMode ? this.filter.builder : this.filter.form
      let isIgnoreGlobal = builderMode && this.config.filter.builder.config.ignore.global.value
      let isIgnoreBase = builderMode && this.config.filter.builder.config.ignore.base.value
      if ((isMergeGlobalFilter || !isCurrentGlobalFilter) && !isIgnoreGlobal) {
        let global = cloneDeep(CBPO.channelManager().getChannel().getFilterSvc().getGlobalFilter())
        if (!isEmpty(global)) {
          if (isEmpty(queryFilter)) queryFilter = { type: SUPPORT_LOGIC.AND, conditions: [] }
          global.conditions = global.conditions.filter(condition => _.isArray(condition.value) ? !_.every(condition.value, _.isNull) : !_.isEmpty(condition.value))
          !_.isEmpty(global.conditions) && queryFilter.conditions.push(global)
        }
      }
      if (!isEmpty(this.filter.base) && !isIgnoreBase) {
        this.query = {
          type: this.filter.base.type || SUPPORT_LOGIC.AND,
          conditions: [...this.filter.base.conditions]
        }
        if (!isEmpty(queryFilter) && !isEmpty(queryFilter.conditions)) {
          this.query.conditions = [...this.query.conditions, queryFilter]
        }
      } else {
        if (!isEmpty(queryFilter) && !isEmpty(queryFilter.conditions)) {
          this.query = {...queryFilter}
        }
      }
      if (this.query.conditions) {
        this.query.conditions = this.query.conditions.filter(cond => !isEmpty(cond))
        this.query = this.query.conditions.length ? this.query : {}
      } else {
        this.query = {}
      }
      this.query = parseOperators(this.query)
    },
    /**
     * @override
     */
    widgetConfig (config) {
      this.config = makeWidgetDefaultConfig(config)
      // update widget styles for element
      if (get(this.config, 'elements[0].config.widget.style')) {
        this.config.elements[0].config.widget.style = {...this.config.widget.style}
      }
      this.initWidgetData(this.config)
      // mapping menuConfig
      this.mappingMenuConfig()
      if (get(this.config, 'elements[0].type') === ELEMENT.HTML_EDITOR) {
        this.config.menu.config.selection.options = this.config.menu.config.selection.options.filter(item => (item.value !== 'csv' && item.type === 'item'))
      }
      const element = get(this.config, 'elements[0]')
      if (element) {
        CBPO.$bus.$on(BUS_EVENT.ELEMENT_RESIZE_EVENT(element.config.id), () => {
          const diffWidgetAndFilterFormWidth = 6
          if (this.$refs.filterForm && this.isShowFilterForm) {
            this.isShowFilterForm = this.$refs.widget.clientWidth + diffWidgetAndFilterFormWidth >= this.$refs.filterForm.$el.clientWidth
          }
          if (this.$refs.filterForm && !this.isShowFilterForm) {
            this.isShowFilterForm = true
            this.$nextTick(() => {
              this.isShowFilterForm = this.$refs.widget.clientWidth + diffWidgetAndFilterFormWidth >= this.$refs.filterForm.$el.clientWidth
            })
          }
        })
      }
    },
    mappingMenuConfig () {
      const selectionConfig = get(this.config, 'menu.config.selection', {})
      const options = cloneDeep(selectionConfig).options
      if (options && options.length) {
        selectionConfig.options = options.map(option => {
          if (option.link && !option.value) {
            const dsId = get(this.config, 'elements[0].config.dataSource', '')
            const dsUrlTmpl = selectionConfig.dsUrl || ''
            if (dsId && dsUrlTmpl) {
              option.value = dsUrlTmpl.replace(':client_id', dsId)
            }
          }
          return option
        })
      }
    },
    initWidgetData(config) {
      this.createQueryBuilder()
      if (config.columnManager.enabled) {
        this.mappingColumns()
      }
    },
    checkAutoHeightConfig() {
      if (this.config.autoHeight) {
        this.$emit('autoHeightEvent', this.config.id)
      }
    },
    checkHeaderWidget(data) {
      this.$emit('checkHeaderWidget', data)
    },
    /**
     * Create query after init config
     * Will be call inside widgetConfig method
     * **/
    createQueryBuilder() {
      // filter include base, builder, form and global
      // global will be added in buildFilterObject
      let filter = {
        base: convertColumnObjectToColumnName(cloneDeep(get(this.config, 'filter.base.config.query'))),
        builder: convertColumnObjectToColumnName(cloneDeep(get(this.config, 'filter.builder.config.query'))),
        form: convertColumnObjectToColumnName(cloneDeep(
          this.$refs.filterForm
            ? this.$refs.filterForm.buildFilterFromControls(get(this.config, 'filter.form.config.controls'))
            : {}
        ))
      }
      this.buildFilterObject(filter)
    },
    calculateElementHeight() {
      // TODO: change way to get all these settings
      let $title = $(this.$el).find('.cbpo-widget-title')
      let $controlFeature = $(this.$el).find('.cbpo-control.__advance-feature')
      let $controlBasicFeature = $(this.$el).find('.cbpo-control.__basic-filter.__btn-action')
      let numberOfPadding = 4
      let sizeOfPadding = 8
      return ($title.length ? $title.height() + 11.2 * 2 : 0) +
        ($controlFeature.height() || 0) +
        ($controlBasicFeature.height() || 0) +
        (numberOfPadding * sizeOfPadding) +
        (get(this.config, 'filter.globalFilter.enabled') ? 50 : 0)
    },
    getTotalHeight() {
      return get(this.config, 'filter.globalFilter.enabled')
        ? this.calculateElementHeight() + (this.builder ? 50 : 0)
        : this.$refs.elements[0].calculateElementHeight() + this.calculateElementHeight()
    },
    /**
     * @override
     */
    widgetExport ($event) {
      this.$refs.elements[0].widgetExport(
        $event, getFileName(this.config), getPollingSetting(this.config), getPollingIntervalSetting(this.config)
      )
    },
    removeWidget() {
      this.$emit('removeWidget', this.config.id)
    },
    customExport(config) {
      this.$emit('customExport', config)
    },
    widgetTemplateExport(config, templateName) {
      this.$emit('widgetTemplateExport', {config, templateName})
    },
    onClickMenuWidget({type, config, templateName = null}) {
      switch (type) {
        case 'removeWidget':
          this.removeWidget()
          break
        case 'widgetExport':
          this.widgetExport(config)
          break
        case 'widgetCustomExport':
          this.customExport(config)
          break
        case 'widgetTemplateExport':
          this.widgetTemplateExport(config, templateName)
          break
        case 'changeWidgetConfig':
          this.changeWidgetConfig(config)
          break
        case 'changeElementConfig':
          this.changeElementConfig(config)
          break
        default:
          break
      }
    },
    changeWidgetConfig(config) {
      this.config = config
      // this.initWidgetData(config)
      this.$nextTick(() => {
        this.config.elements[0].type === ELEMENT.CHART && this.$refs.elements[0].resizeChart()
      })
      this.$emit('update:configObj', config)
    },
    changeElementConfig(config) {
      this.$set(this.config.elements[0], 'config', config.config)
      this.$emit('update:configObj', this.config)
      // CBPO.$bus.$emit(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.elements[0].config.id), config.config)
    },
    updateElementConfig() {
      if (get(this.visualizationProps, 'elementSettingMethod', null)) {
        this.visualizationProps.elementSettingMethod(cloneDeep(this.config.elements[0]))
      } else {
        CBPO.$bus.$emit(BUS_EVENT.ELEMENT_CONFIG_CHANGE(this.config.elements[0].config.id), this.config.elements[0].config)
      }
    },
    columnChange(columnsInElement) {
      forEach(this.config.elements, (element, index) => {
        let columns = element.config.columns.map(col => {
          let colIndex = findIndex(columnsInElement[index].columns, c => c.alias ? c.alias === col.alias : c.name === col.name)
          col.index = colIndex
          col.visible = columnsInElement[index].columns[colIndex].visible
          return col
        })
        columns = sortBy(columns, c => c.index)
        columns = columns.map(col => { delete col.index; return col })
        this.$refs.elements[index].changeIndexColumn(columns)
        if (this.$refs.elements[index].resizableColumns) {
          this.$refs.elements[0].resizableColumns()
        }
      })
    },
    mappingColumns() {
      this.columnsOfElements = this.config.elements.map(e => {
        let columns = e.config.columns ? e.config.columns.map((c, i) => {
          let {name, displayName, visible} = c
          return {name, displayName: displayName, visible: visible !== undefined ? visible : true}
        }) : []
        let table = { columns }
        generateIdIfNotExist(table)
        return table
      })
    },
    addCalculatedColumn(column) {
      // add to element
      forEach(this.config.elements, (element, index) => {
        element.config.columns.push(column)
        this.$refs.elements[index].addCalculatedColumn()
      })
      // add to managed column
      const columns = get(this.config, 'columnManager.config.managedColumns[0].columns')
      const {name, expr, visible} = column
      columns.push({name, expr, visible: visible !== undefined ? visible : true})
    },
    buildMenuOptions(dataSources) {
      const dsId = get(this.config, 'elements[0].config.dataSource', '')
      const selectionConfig = get(this.config, 'menu.config.selection', {})
      let options = cloneDeep(selectionConfig).options || []
      options = options.filter(option => !option.optional)
      const filteredDS = dataSources.filter(ds => ds !== dsId)
      const dsLength = filteredDS.length
      if (dsLength) {
        // update the first datasource name
        const linkOption = options.find(option => option.link)
        let dsQty = 0
        if (linkOption) {
          linkOption.label = 'Data Source 1'
          dsQty = 1
        }
        const dsUrlTmpl = selectionConfig.dsUrl
        for (let i = 0; i < dsLength; i++) {
          options.push({
            label: `Data Source ${dsLength > 1 || linkOption ? dsQty + i + 1 : ''}`,
            icon: 'fa fa-database',
            value: dsUrlTmpl ? dsUrlTmpl.replace(':client_id', filteredDS[i]) : '',
            link: true,
            optional: true,
            type: 'item'
          })
        }
        selectionConfig.options = [...options]
      }
    },
    getLastUpdated(lastUpdated) {
      this.$emit('getLastUpdated', lastUpdated || null)
    }
  },
  mounted() {
    if (get(this.config, 'filter.globalFilter.enabled')) {
      // global filter doesn't have element inside. It will auto trigger autoHeight event
      this.$nextTick(() => this.checkAutoHeightConfig())
    }
  },
  watch: {
    // watch a computed get state
    'getGlobalFilterState'(val) {
      if (!isEqual(this.cachedGlobalFilter, val)) {
        if (!get(this.config, 'filter.globalFilter.enabled')) {
          this.mapControlFromGlobalFilter()
          this.buildFilterObject({}, true)
        }
      }
      this.cachedGlobalFilter = val
    },
    dataSources: {
      deep: true,
      handler (val) {
        if (val) this.buildMenuOptions(val)
      }
    },
    'configObj.id' (val) {
      this.widgetConfig(this.configObj)
    }
  },
  destroyed() {
    const element = get(this.config, 'elements[0]')
    if (element) {
      CBPO.$bus.$off(BUS_EVENT.ELEMENT_RESIZE_EVENT(element.config.id))
    }
  }
}
</script>
<style scoped lang="scss">
  @import './Widget.scss';
</style>
