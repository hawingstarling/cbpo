<template>
  <div class="cbpo-widget-menu">
    <menu-control-select
      :allow-custom-options="false"
      :configObj="config.menu.config"
      :builder="builder"
      :isVisualize="isVisualize"
      @click="onClickMenu($event)">
    </menu-control-select>
    <!--WIDGET SETTINGS MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="lg" :ref="modalId('widget_settings')" :id="modalId('widget_settings')" title="Widget Settings">
      <cbpo-widget-settings
        :ref="widgetSettingComponentRef"
        :config="config">
      </cbpo-widget-settings>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button class="cbpo-btn btn-primary mr-1" @click="onClickMenu('apply_widget_settings')">
            Save
          </button>
          <button @click="modalTrigger({type: 'widget_settings', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--ELEMENT MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="lg" no-enforce-focus :ref="modalId('element_settings')" :id="modalId('element_settings')" title="Element Settings">
      <cbpo-element-settings
        :ref="elementSettingComponentRef"
        :selectedElement="getSelected"
        :element="config.elements[0]"
        :filterAlignment="config.filter.alignment"/>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button class="cbpo-btn btn-primary mr-1" @click="onClickMenu('apply_element_settings')">
            Save
          </button>
          <button @click="modalTrigger({type: 'element_settings', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <!--WIDGET REMOVE MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" title="Please confirm" centered :ref="modalId('widget_remove')" :id="modalId('widget_remove')">
      {{ getMethodReset ? 'Reset the visualization builder state. Are you sure?' : 'Remove this visualization from the dashboard?' }}
      <template v-slot:modal-footer>
        <button class="cbpo-btn btn-warning" @click="onClickMenu('apply_widget_remove')">
          <i class="fa fa-check mr-1"></i> Yes
        </button>
        <button class="cbpo-btn" @click="modalTrigger({type: 'widget_remove', isShow: false})">
          <i class="fa fa-times mr-1"></i> No
        </button>
      </template>
    </b-modal>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import WidgetSettings from '@/components/widgets/setting/WidgetSettings'
import ElementSettings from '@/components/widgets/setting/ElementSettings'
import MenuControlSelect from '@/components/widgets/menu/MenuControlSelect'
import get from 'lodash/get'
import cloneDeep from 'lodash/cloneDeep'
import isEmpty from 'lodash/isEmpty'
import isObject from 'lodash/isObject'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import { BUS_EVENT } from '@/services/eventBusType'
import CBPO from '@/services/CBPO'

export default {
  name: 'Menu',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins
  ],
  props: {
    builder: {
      type: Boolean,
      default: false
    },
    // Event methods which was passed from Visualization
    visualizationProps: Object
  },
  components: {
    'cbpo-widget-settings': WidgetSettings,
    'cbpo-element-settings': ElementSettings,
    'menu-control-select': MenuControlSelect
  },
  computed: {
    getMethodReset() {
      return get(this.visualizationProps, 'resetAllConfig', null)
    },
    isVisualize() {
      return isEmpty(this.visualizationProps)
    },
    modalId() {
      return type => `${this.config.id}_modal_${type}`
    },
    widgetSettingComponentRef() {
      return type => `${this.config.id}_modal_content_widget_settings`
    },
    elementSettingComponentRef() {
      return type => `${this.config.id}_modal_content_element_settings`
    },
    getSelected() {
      if (!this.config.elements[0]) return null
      let chartType = null
      let config = this.config.elements[0].config
      let type = this.config.elements[0].type
      if (type === ELEMENT.CHART) {
        let series = config.charts[0].series
        if (series.every(e => e.type === TYPES.PIE)) {
          chartType = TYPES.PIE
        } else if (series.every(e => e.type === TYPES.BAR)) {
          chartType = TYPES.BAR
        } else if (series.every(e => e.type === TYPES.LINE)) {
          chartType = TYPES.LINE
        } else if (series.every(e => e.type === TYPES.BUBBLE)) {
          chartType = TYPES.BUBBLE
        } else if (series.every(e => e.type === TYPES.SCATTER)) {
          chartType = TYPES.SCATTER
        } else if (series.every(e => e.type === TYPES.AREA)) {
          chartType = TYPES.AREA
        } else if (series.some(e => e.type === TYPES.BAR) && series.some(e => e.type === TYPES.LINE)) {
          chartType = TYPES.PARETO
        }
      }
      if (type === ELEMENT.GAUGE) {
        let series = config.charts[0].series
        if (series.every(e => e.type === TYPES.BULLETGAUGE)) {
          chartType = TYPES.BULLETGAUGE
        } else if (series.every(e => e.type === TYPES.SOLIDGAUGE)) {
          chartType = TYPES.SOLIDGAUGE
        }
      }
      return {
        elementType: type,
        chartType
      }
    }
  },
  methods: {
    modalTrigger({type, isShow}) {
      if (isShow) {
        // show modal
        this.$bvModal.show(this.modalId(type))
      } else {
        // hide modal
        this.$bvModal.hide(this.modalId(type))
      }
    },
    onClickMenu(type) {
      if (isObject(type) && type.type === 'template-csv') this.$emit('input', {type: 'widgetTemplateExport', config: 'template-csv', templateName: type.templateName})

      switch (type) {
        case 'widget-settings':
          this.modalTrigger({type: 'widget_settings', isShow: true})
          break
        case 'element-settings':
          this.modalTrigger({type: 'element_settings', isShow: true})
          break
        case 'remove':
          this.modalTrigger({type: 'widget_remove', isShow: true})
          break
        case 'csv':
          this.$emit('input', {type: 'widgetExport', config: 'csv'})
          break
        case 'custom-csv':
          this.$emit('input', {type: 'widgetCustomExport', config: 'custom-csv'})
          break
        case 'apply_widget_remove':
          this.modalTrigger({type: 'widget_remove', isShow: false})
          if (get(this.visualizationProps, 'resetAllConfig', null)) {
            this.visualizationProps.resetAllConfig()
          } else {
            this.$emit('input', {type: 'removeWidget'})
          }
          break
        case 'apply_widget_settings':
          this.modalTrigger({type: 'widget_settings', isShow: false})
          let widgetConfig = this.$refs[this.widgetSettingComponentRef].getConfig()
          console.log(widgetConfig)
          // update widget styles for element
          if (get(widgetConfig, 'elements[0].config.widget')) {
            widgetConfig.elements[0].config.widget.style = {...widgetConfig.widget.style}
          }
          this.$emit('input', {type: 'changeWidgetConfig', config: widgetConfig})
          if (get(this.visualizationProps, 'widgetSettingMethod', null)) this.visualizationProps.widgetSettingMethod(cloneDeep(widgetConfig))
          break
        case 'apply_element_settings':
          this.modalTrigger({type: 'element_settings', isShow: false})
          let elementConfig = this.$refs[this.elementSettingComponentRef].getConfig()
          switch (elementConfig.type) {
            case ELEMENT.GLOBAL_FILTER:
              let filterAlignment = this.$refs[this.elementSettingComponentRef].getFilterAlignment()
              let widgetGlobalFilterConfig = cloneDeep(this.config)
              widgetGlobalFilterConfig.filter.alignment = filterAlignment
              this.$emit('input', {type: 'changeWidgetConfig', config: widgetGlobalFilterConfig})
              if (get(this.visualizationProps, 'widgetSettingMethod', null)) this.visualizationProps.widgetSettingMethod(cloneDeep(widgetGlobalFilterConfig))
              break
            default:
              let type = get(this.config, 'elements[0].type', '')
              if (type === ELEMENT.CHART) {
                elementConfig.config.charts[0].options.legend.widthPercent = parseInt(elementConfig.config.charts[0].options.legend.widthPercent)
              }
              this.$emit('input', {type: 'changeElementConfig', config: elementConfig})
              if (get(this.visualizationProps, 'elementSettingMethod', null)) {
                this.visualizationProps.elementSettingMethod(cloneDeep(elementConfig))
              } else {
                CBPO.$bus.$emit(BUS_EVENT.ELEMENT_CONFIG_CHANGE(elementConfig.config.id), elementConfig.config)
              }
              break
          }
          break
        default:
          break
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  @import './Menu.scss';
</style>
