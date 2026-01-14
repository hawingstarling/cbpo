<template>
  <div
    v-if="configReady"
    :style="config.style"
    :class="{'empty-layout': config.widgets.length === 0}"
    class="cbpo-layout"
    id="cbpo-widget-layout">
    <grid-layout
      class="w-100 cbpo-vue-grid-layout"
      ref="gridLayout"
      :layout="layout"
      :col-num="config.gridConfig.colNum"
      :responsive="config.gridConfig.responsive.enabled"
      :cols="config.gridConfig.responsive.cols"
      :breakpoints="config.gridConfig.responsive.breakpoints"
      :row-height="config.gridConfig.rowHeight"
      :is-draggable="builder"
      :is-resizable="builder"
      :vertical-compact="true"
      :use-css-transforms="true"
      :margin="config.gridConfig.margin"
      @layout-updated="layoutUpdatedEvent">
      <grid-item
        ref="gridItem"
        dragIgnoreFrom=".cbpo-table-container"
        v-for="(item, index) in layout"
        v-cbpo-z-index
        :key="checkIndex(index)"
        :x="item.x"
        :y="item.y"
        :w="item.w"
        :h="item.h"
        :i="item.i"
        :min-h="config.gridConfig.minHeight"
        @move="moveElement"
        @moved="movedElement"
        @resized="resizeEvent, updateGridOfWidget(item, index)"
        @resize="resizeEvent, updateWidthOfWidget(index)"
        @container-resized="containerResizedEvent"
      >
        <template v-if="fullRendering">
          <!-- fake grid item was added by drag event -->
          <template v-if="config.widgets[index]">
          <Widget
            v-if="config.widgets[index].type === 'cbpo-widget'"
            ref="elementInWidgetLayout"
            :builder="builder"
            :configObj.sync="config.widgets[index].config"
            @autoHeightEvent="findAndUpdateHeight($event)"
            @removeWidget="removeWidget($event)"/>
          <WidgetLoader
            v-if="config.widgets[index].type === 'cbpo-widget-loader'"
            ref="elementInWidgetLayout"
            :builder="builder"
            :configObj.sync="config.widgets[index].config"
            @autoHeightEvent="findAndUpdateHeight($event)"
            @removeWidget="removeWidget($event)"
          />
          <Table
            v-if="config.widgets[index].type === 'cbpo-element-table'"
            ref="elementInWidgetLayout"
            :configObj.sync="config.widgets[index].config"
            @autoHeightEvent="findAndUpdateHeight($event)"
          />
          <Chart
            v-if="config.widgets[index].type === 'cbpo-element-chart'"
            ref="elementInWidgetLayout"
            :configObj.sync="config.widgets[index].config"
            @autoHeightEvent="findAndUpdateHeight($event)"
          />
          <BulletGauge
            v-if="config.widgets[index].type === 'cbpo-element-gauge'"
            ref="elementInWidgetLayout"
            :configObj.sync="config.widgets[index].config"
            @autoHeightEvent="findAndUpdateHeight($event)"
          />
          <HtmlEditor
            v-if="config.widgets[index].type === 'cbpo-element-html-editor'"
            ref="elementInWidgetLayout"
            :builder="builder"
            :configObj.sync="config.widgets[index].config"
          />
          </template>
        </template>
      </grid-item>
    </grid-layout>
  </div>
</template>
<script>

import VueGridLayout from 'vue-grid-layout'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import Widget from '@/components/widgets/Widget'
import WidgetLoader from '@/components/widgets/loader/WidgetLoader'
import Table from '@/components/widgets/elements/table/Table'
import Chart from '@/components/widgets/elements/chart/Chart'
import BulletGauge from '@/components/widgets/elements/gauge/Gauge'
import HtmlEditor from '@/components/widgets/elements/htmlEditor/HtmlEditor'
import { makeDefaultLayoutConfig } from '@/components/widgetLayout/WidgetLayoutConfig'
import { get, findIndex, debounce, cloneDeep, forEach } from 'lodash'
import { BUS_EVENT } from '@/services/eventBusType'
import CBPO from '@/services/CBPO'
import zIndexDirective from '@/directives/zIndexDirective'
import { generateIdIfNotExist } from '@/utils/configUtil'
import { defaultGridItemConfig } from '@/components/widgets/WidgetConfig'
import uuidv4 from 'uuid'

export default {
  name: 'Layout',
  extends: WidgetBase,
  props: {
    builder: Boolean,
    scopeConfig: String
  },
  directives: {
    'cbpo-z-index': zIndexDirective
  },
  data() {
    return {
      fullRendering: false,
      layout: [],
      refsChecking: {
        isRendered: false,
        count: 0
      },
      callbackAutoHeight: [],
      optionUpdateWidget: {},
      checkShowWidget: false,
      dataDrag: {},
      isDraggingOverDashboardContainer: false
    }
  },
  components: {
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem,
    Widget,
    WidgetLoader,
    Table,
    Chart,
    HtmlEditor,
    BulletGauge
  },
  mixins: [
    WidgetBaseMixins
  ],
  methods: {
    layoutUpdatedEvent(newLayout) {
      this.layout = newLayout
    },
    moveElement(i) {
      let index = findIndex(this.layout, item => item.i === i)
      this.$refs['gridItem'][index].$el.classList.add('cbpo-vue-dragging-item')
    },
    movedElement(i) {
      let index = findIndex(this.layout, item => item.i === i)
      this.$refs['gridItem'][index].$el.classList.remove('cbpo-vue-dragging-item')
    },
    widgetConfig(config) {
      this.config = Object.assign({}, cloneDeep(makeDefaultLayoutConfig(config)))
      forEach(this.config.widgets, function(widget, key) {
        widget.key = uuidv4()
      })
      this.$emit('update:configObj', this.config)
      this.buildLayoutGrid(config)
      CBPO.$bus.$on(BUS_EVENT.CHECK_IN_AREA_DROP, (data) => {
        this.isDraggingOverDashboardContainer = data.isInArea
      })
      if (this.scopeConfig) {
        CBPO.$bus.$on(`${BUS_EVENT.DRAG_EVENT_DASHBOARD_BUILDER_INTERNAL}_${this.scopeConfig}`,
          (data) => {
            let dataDragWidget = cloneDeep(data)
            if (dataDragWidget && dataDragWidget.data && dataDragWidget.data.ui) {
              let positionDrag = dataDragWidget.data.ui.position
              let mouseXY = {}
              mouseXY.x = positionDrag.left
              mouseXY.y = positionDrag.top
              let defaultHeight = this.config.gridConfig.defaultHeight
              let colNum = this.config.gridConfig.colNum
              let defaultGrid = cloneDeep(defaultGridItemConfig)
              let dragPos = {'x': null, 'y': null, 'w': defaultGrid.w, 'h': defaultHeight, 'i': null}
              let parentRect = this.$parent.$el.getBoundingClientRect()
              let scrollHeight = window.pageYOffset
              if (this.isDraggingOverDashboardContainer === true && (this.layout.findIndex(item => item.i === 'drop')) === -1) {
                this.layout.push({
                  x: colNum,
                  y: this.layout.length + (this.colNum || 12),
                  w: defaultGrid.w,
                  h: defaultHeight,
                  i: 'drop'
                })
              }
              let index = this.layout.findIndex(item => item.i === 'drop')
              if (index !== -1) {
                try {
                  this.$refs.gridLayout.$children[this.layout.length].$refs.item.style.display = 'none'
                } catch {
                }
                let el = this.$refs.gridLayout.$children[index]
                // Calculation widget position dragging on dashboard container
                el.dragging = {'top': mouseXY.y - (scrollHeight + parentRect.y), 'left': mouseXY.x - parentRect.x}
                let newPos = el.calcXY(mouseXY.y - (scrollHeight + parentRect.y), mouseXY.x - parentRect.x)
                this.dataDrag = {
                  x: newPos.x,
                  y: newPos.y,
                  w: defaultGrid.w,
                  h: defaultHeight
                }
                if (this.isDraggingOverDashboardContainer) {
                  this.$refs.gridLayout.dragEvent('dragstart', 'drop', newPos.x, newPos.y, defaultHeight, defaultGrid.w)
                  dragPos.i = String(index)
                  dragPos.x = this.layout[index].x
                  dragPos.y = this.layout[index].y
                  CBPO.$bus.$emit(BUS_EVENT.POSITION_ITEM_ADD, dragPos)
                } else {
                  this.$refs.gridLayout.dragEvent('dragend', 'drop', newPos.x, newPos.y, defaultHeight, defaultGrid.w)
                  this.layout = this.layout.filter(obj => obj.i !== 'drop')
                }
              }
            }
          }
        )
      }
      CBPO.$bus.$on(BUS_EVENT.DROP_EVENT_VISUALIZATION_INTERNAL,
        (data) => {
          if (this.dataDrag) {
            this.$refs.gridLayout.dragEvent('dragend', 'drop', this.dataDrag.x, this.dataDrag.y, this.dataDrag.h, this.dataDrag.w)
            this.layout = this.layout.filter(obj => obj.i !== 'drop')
            this.isDraggingOverDashboardContainer = false
          }
        })
    },
    removeWidget(id) {
      const fwidget = cloneDeep(this.config.widgets).find(w => w.config.id === id)
      let gridId = ''
      if (fwidget) gridId = fwidget.config.grid.id
      this.config.widgets = this.config.widgets.filter(widget => widget.config.id !== id)
      this.layout = this.layout.filter(grid => grid.id !== gridId)
    },
    findAndUpdateHeight(id) {
      let index = findIndex(this.config.widgets, w => {
        return get(w, 'config.id', null) === id
      })
      this.handleAutoHeightGridItem(index)
    },
    buildLayoutGrid() {
      this.layout = this.config.widgets.map((widget, i) => {
        widget.config.grid.i = i
        generateIdIfNotExist(widget.config.grid)
        return widget.config.grid
      })
    },
    resizeEvent(i, h, w, hpx, wpx) {
      let id = ''
      if (i !== 'drop') {
        const widget = get(this.config, `widgets[${i}]`)
        if (widget) {
          if (widget.type === 'cbpo-widget-loader') {
            id = get(widget, 'config.elementId')
          } else {
            id = get(widget, `config.elements[0].config.id`)
          }
          if (id) {
            CBPO.$bus.$emit(BUS_EVENT.ELEMENT_RESIZE_EVENT(id), { h, w, hpx, wpx, colSize: this.$refs.gridLayout.width / this.config.gridConfig.colNum })
          }
        }
      }
    },
    updateWidthOfWidget(index) {
      let id = ''
      const widget = get(this.config, `widgets[${index}]`)
      if (widget) {
        if (widget.type === 'cbpo-widget-loader') {
          id = get(widget, 'config.elementId')
        } else {
          id = get(widget, `config.elements[0].config.id`)
        }
        debounce(() => {
          if (id) {
            CBPO.$bus.$emit(BUS_EVENT.ELEMENT_RESIZE_EVENT(id))
          }
        }, 500)()
      }
    },
    containerResizedEvent (i, h, w, hpx, wpx) {
      if (this.fullRendering) {
        this.resizeEvent(i, h, w, hpx, wpx)
      }
    },
    updateGridOfWidget(grid, index) {
      this.config.widgets[index].config.grid = grid
    },
    handleAutoHeightGridItem(index) {
      this.$nextTick(() => {
        let totalHeight = this.$refs.elementInWidgetLayout[index].getTotalHeight()
        let my = this.config.gridConfig.margin[1]
        let gridHeight = this.config.gridConfig.rowHeight
        let {w, x, y, i} = this.layout[index]
        let row = Math.ceil((totalHeight) / (gridHeight + my))
        // set new height into grid layout
        this
          .$refs
          .gridLayout
          .resizeEvent('resizeend', i, x, y, row, w)
      })
    }
  },
  computed: {
    checkIndex() {
      return index => {
        return get(this.config, `widgets[${index}].key`, index)
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      if (!this.fullRendering) {
        this.fullRendering = true
      }
    })
  },
  watch: {
    'config.widgets.length'() {
      this.buildLayoutGrid()
    },
    builder (val) {
      if (val) {
        this.layout.forEach((grid, index) => {
          let id = ''
          const widget = this.config.widgets[index]
          const colSize = this.$refs.gridLayout.width / this.config.gridConfig.colNum
          if (widget.type === 'cbpo-widget-loader') {
            id = get(widget, 'config.elementId')
          } else {
            id = get(widget, `config.elements[0].config.id`)
          }
          this.$nextTick(() => {
            CBPO.$bus.$emit(BUS_EVENT.ELEMENT_RESIZE_EVENT(id), { h: grid.h, w: grid.w, hpx: grid.h * this.config.gridConfig.rowHeight, wpx: colSize * grid.w, colSize })
          })
        })
      }
    },
    layout() {
      this.layout.forEach(grid => {
        let index = findIndex(this.config.widgets, widget => widget && widget.config.grid.id === grid.id)
        if (index !== -1) this.config.widgets[index].config.grid = grid
      })
    }
  },
  destroyed() {
    CBPO.$bus.$off(`${BUS_EVENT.DRAG_EVENT_DASHBOARD_BUILDER_INTERNAL}_${this.scopeConfig}`)
  }
}
</script>
<style scoped lang="scss">
  @import './WidgetLayout.scss';
</style>
