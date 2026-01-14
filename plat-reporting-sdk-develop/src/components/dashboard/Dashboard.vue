<template>
  <div v-if="configReady" :id="config.id + '_cbpo_dashboard'" class="cbpo-dashboard">
    <div class="cbpo-dashboard-container">
      <cbpo-widget-title
        class="border-bottom-0"
        v-if="config.widget.enabled"
        :configObj="config.widget"
      />
      <div class="cbpo-dashboard-header" :class="{ 'cbpo-dashboard-border-bottom': isBuilderState }">
        <cbpo-dashboard-menus
          v-if="config.menu.enabled && isBuilderState"
          @input="onClickMenuWidget($event)"
          :builder="isBuilderState"
          :configObj="config"
        />
      </div>
      <cbpo-layout
          ref="cbpo_layout"
          :builder="isBuilderState"
          :configObj.sync="config.widgetLayout"
          :scope-config="scopeConfig"
        />
    </div>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import Layout from '@/components/widgetLayout/WidgetLayout'
import Title from '@/components/widgets/title/Title'
import { makeWidgetDefaultConfig } from './DashboardConfig'
import {
  isEmpty,
  get,
  cloneDeep,
  map
} from 'lodash'
import CBPO from '@/services/CBPO'
import { BUS_EVENT } from '@/services/eventBusType'
import Menu from './Menu'

export default {
  name: 'Dashboard',
  extends: WidgetBase,
  props: {
    enableBuilderMode: {
      type: Boolean,
      default: false
    },
    scopeConfig: {
      type: String
    }
  },
  data() {
    return {
      isBuilderState: null
    }
  },
  components: {
    'cbpo-layout': Layout,
    'cbpo-widget-title': Title,
    'cbpo-dashboard-menus': Menu
  },
  mixins: [WidgetBaseMixins],
  methods: {
    widgetConfig(config) {
      this.config = Object.assign({}, cloneDeep(makeWidgetDefaultConfig(config)))
      this.$emit('update:configObj', this.config)
    },
    changeState(e) {
      this.isBuilderState = e
      this.$emit('update:isBuilderState', e)
    },
    onClickMenuWidget({ type, config }) {
      if (type === 'changeWidgetConfig') {
        this.config = config
        // update widget settings
        this.updateWidgetStyles()
      }
    },
    updateWidgetStyles() {
      let widgetLayout = get(this.config, 'widgetLayout', {})
      let dashboardStyles = get(this.config, 'style', {})
      if (!isEmpty(widgetLayout.widgets)) {
        map(widgetLayout.widgets, (layout, index) => {
          layout.config.widget.style = cloneDeep(dashboardStyles)
        })
      }
      this.$set(this.config, 'widgetLayout', cloneDeep(widgetLayout))
    }
  },
  created() {
    this.isBuilderState = this.enableBuilderMode
    CBPO.$bus.$on(BUS_EVENT.CBPO_TOGGLE_BUILDER_MODE, (e) => {
      this.changeState(e)
    })
    CBPO.$bus.$on(BUS_EVENT.DRAG_EVENT_DASHBOARD_BUILDER_INTERNAL, (e) => {
      this[BUS_EVENT.DRAG_DATA_DIRECTIVE] = e
    })
  },
  watch: {
    enableBuilderMode(val) {
      this.changeState(val)
    }
  },
  destroyed() {
    CBPO.$bus.$off(BUS_EVENT.CBPO_TOGGLE_BUILDER_MODE)
    CBPO.$bus.$off(BUS_EVENT.DRAG_EVENT_DASHBOARD_BUILDER_INTERNAL)
  }
}
</script>
<style scoped lang="scss">
@import './Dashboard.scss';
</style>
