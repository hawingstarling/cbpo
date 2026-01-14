<template>
  <div v-if="configReady">
    <div class="drop-layout-header">
      <slot name="drop-layout-header">
        <h6>Build Dashboard</h6>
      </slot>
    </div>
    <div
      v-if="!isEmpty(config.scope)"
      class="cbpo-drop-layout"
      v-cbpo-droppable="{ scope: config.scope,
        [EVENT.DROP_EVENT]: dropEvent,
        [EVENT.OVER_EVENT]: overEvent,
        [EVENT.OUT_EVENT]: outEvent }" >
      <Dashboard
        ref="cbpo-dashboard"
        :enableBuilderMode.sync="config.buildDashboard.enabled"
        :configObj.sync="config.dashboardConfig"
        :scope-config="config.scope"
      >
      </Dashboard>
    </div>
  </div>
</template>

<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import Dashboard from '@/components/dashboard/Dashboard'
import { makeDefaultDropLayoutContainerConfig } from '@/components/dropLayoutContainer/DropLayoutContainerConfig'
import { BUS_EVENT } from '@/services/eventBusType'
import { EVENT } from '@/utils/dragAndDropUtil'
import { cloneDeep, isEmpty, get } from 'lodash'
import { defaultGridItemConfig } from '@/components/widgets/WidgetConfig'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import $ from 'jquery'
import dropDirective from '@/directives/dropDirective'
import uuidv4 from 'uuid'
import CBPO from '@/services/CBPO'

export default {
  name: 'DropLayoutContainer',
  data() {
    return {
      isFirstTime: false,
      BUS_EVENT,
      EVENT,
      isEmpty: isEmpty,
      dataDrag: {}
    }
  },
  mixins: [WidgetBaseMixins],
  directives: {
    'cbpo-droppable': dropDirective
  },
  components: {
    Dashboard
  },
  methods: {
    widgetConfig(config) {
      this.config = Object.assign({}, cloneDeep(makeDefaultDropLayoutContainerConfig(config)))
      this.$emit('update:configObj', this.config)
      if (config.scope) {
        CBPO.$bus.$on(
          `${BUS_EVENT.DRAG_EVENT_DASHBOARD_BUILDER_INTERNAL}_${config.scope}`,
          (e) => {
            this[BUS_EVENT.DRAG_DATA_DIRECTIVE] = e
            if (e) {
              $(`#${this.config.scope}_cbpo-drop-layout`).addClass('active')
            } else {
              $(`#${this.config.scope}_cbpo-drop-layout`).removeClass('active')
            }
          }
        )
      }
      CBPO.$bus.$on(BUS_EVENT.POSITION_ITEM_ADD,
        (data) => {
          this.dataDrag = data
        })
    },
    dropEvent(_, el, ui) {
      let { data: { source } } = cloneDeep(this[BUS_EVENT.DRAG_DATA_DIRECTIVE])
      let widgetConfig = cloneDeep(source.widget.cf_object.config.widgetConfig)
      let isGlobalFilter = get(widgetConfig, 'config.filter.globalFilter.enabled', false)
      let isGlobalFilterExisted = this.config.dashboardConfig.widgetLayout.widgets.some(widget => get(widgetConfig, 'config.filter.globalFilter.enabled', false))
      if (isGlobalFilter && isGlobalFilterExisted) {
        this.$bvToast.toast('Only one global filter allowed.', {
          solid: true,
          variant: 'error',
          headerClass: 'd-none'
        })
      }
      let defaultHeight = this.config.dashboardConfig.widgetLayout.gridConfig.defaultHeight
      let defaultGrid = cloneDeep(defaultGridItemConfig)
      widgetConfig.id = uuidv4()
      widgetConfig.elements[0].config.id = uuidv4()
      if (source.widgetType === 'cbpo-widget') {
        let widget = {
          type: ELEMENT.WIDGET,
          key: uuidv4(),
          config: {
            ...widgetConfig,
            ...{
              grid: Object.assign(defaultGrid, {
                i: this.dataDrag.i,
                y: this.dataDrag.y,
                h: defaultHeight
              })
            }
          },
          visualizationId: get(source, 'widget.id', '')
        }
        let checkDiv = false
        CBPO.$bus.$emit('DROP_EVENT_VISUALIZATION_INTERNAL', {checkDiv})
        this.config.dashboardConfig.widgetLayout.widgets = [...this.config.dashboardConfig.widgetLayout.widgets, widget]
      } else if (source.widgetType === 'cbpo-widget-loader') {
        let widgetId = source.widget.id
        let widget = {
          type: ELEMENT.WIDGET_LOADER,
          key: uuidv4(),
          config: {
            grid: Object.assign(defaultGrid, {
              i: this.dataDrag.i,
              y: this.dataDrag.y,
              h: defaultHeight
            }),
            widgetId,
            save: this.config.save,
            load: this.config.load,
            beforeSave: this.config.beforeSave,
            dsUrl: this.config.dsUrl
          },
          id: `id-${uuidv4()}`
        }
        let checkDiv = false
        CBPO.$bus.$emit('DROP_EVENT_VISUALIZATION_INTERNAL', {checkDiv})
        this.config.dashboardConfig.widgetLayout.widgets = [...this.config.dashboardConfig.widgetLayout.widgets, widget]
      }
      $(el.target)
        .find('#cbpo-drop-layout')
        .removeClass('active')
    },
    overEvent(_, el, ui) {
      let isInArea = true
      CBPO.$bus.$emit('CHECK_IN_AREA_DROP', {isInArea})
    },
    outEvent(_, el, ui) {
      let isInArea = false
      CBPO.$bus.$emit('CHECK_IN_AREA_DROP', {isInArea})
    }
  },
  destroyed() {
    CBPO.$bus.$off(
      `${BUS_EVENT.DRAG_EVENT_DASHBOARD_BUILDER_INTERNAL}_${this.config.scope}`
    )
  }
}
</script>

<style scoped lang="scss">
.cbpo-drop-layout {
  min-height: 500px;
  position: relative;
  border: none;
  >.cbpo-dashboard {
    min-height: 500px;
  }
}
.drop-layout {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  left: 0;
  z-index: -999;
  &.active {
    z-index: 950;
  }
  .background {
    display: flex;
    height: 100%;
    width: 100%;
    justify-content: center;
    align-items: center;
  }
}
</style>
