<template>
  <div class="cbpo-widget-loader-container"
    v-if="configReady">
    <cbpo-template-menus
      v-if="config.menu && config.menu.enabled && builder && !checkNoShowMenu"
      @input="onClickMenuWidget($event)"
      :builder="builder"
      :configObj="config"
      :widgetInfo="widgetInfo"
      class="mb-1"
    />
    <cbpo-widget
      v-if="isConfigReady"
      :configObj.sync="widgetInfo.cf_object.config.widgetConfig"
      :builder="builder"
      :class="{
        'overflow-hidden': isNotGlobalElement
      }"
      ref="widgetElement"
      @removeWidget="removeTemplateWidget()"
      @autoHeightEvent="autoHeightEvent($event)"
      @checkHeaderWidget="checkHeaderWidget"
    >
    </cbpo-widget>
  </div>
</template>
<script>

import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import cloneDeep from 'lodash/cloneDeep'
import isFunction from 'lodash/isFunction'
import get from 'lodash/get'
import { makeWidgetLoaderDefaultConfig } from '@/components/widgets/loader/WidgetLoaderConfig'
import Widget from '@/components/widgets/Widget'
import TemplateMenu from './TemplateMenu'
import toastMixin from '@/components/mixin/toastMixin'
import $ from 'jquery'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
export default {
  name: 'WidgetLoader',
  extends: WidgetBase,
  props: {
    builder: Boolean,
    visualizationProps: Object
  },
  components: {
    'cbpo-widget': Widget,
    'cbpo-template-menus': TemplateMenu
  },
  mixins: [WidgetBaseMixins, toastMixin],
  data() {
    return {
      isConfigReady: false,
      newWidgetInfo: null,
      widgetInfo: null,
      reRender: 0,
      checkNoShowMenu: false
    }
  },
  computed: {
    isNotGlobalElement() {
      return get(this.widgetInfo, 'cf_object.config.widgetConfig.elements[0].type') !== ELEMENT.GLOBAL_FILTER
    }
  },
  methods: {
    widgetConfig (config) {
      this.config = Object.assign({}, cloneDeep(makeWidgetLoaderDefaultConfig(config)))
    },
    widgetInit() {
      this.fetchWidget()
    },
    // fetch widget config
    async fetchWidget() {
      if (!this.config.load || !isFunction(this.config.load)) throw new Error('Please override load method in sdk config')
      try {
        // handle success
        this.widgetInfo = await this.promiseLoadWidgetCallback()
        const menuConfig = get(this.widgetInfo, 'cf_object.config.widgetConfig.menu.config.selection')
        menuConfig.dsUrl = get(this.config, 'dsUrl', '')
        this.config.elementId = get(this.widgetInfo, 'cf_object.config.widgetConfig.elements[0].config.id', '')
        this.updateConfig()
        this.isConfigReady = true
        this.reRender++
      } catch (e) {
        this.vueToast('Fail to get visualizaion data', 'error')
        // handle error
      }
    },
    // callback get widget config
    async promiseLoadWidgetCallback() {
      return new Promise((resolve, reject) => {
        this.config.load({resolve, reject}, this.config.widgetId, this.config.dataSource)
      })
    },
    // callback save widget config
    async promiseSaveWidgetCallback() {
      return new Promise((resolve, reject) => {
        this.config.save({resolve, reject}, this.widgetInfo)
      })
    },
    async promiseBeforeSaveWidgetCallback(saveAs) {
      return new Promise((resolve, reject) => {
        this.config.beforeSave({resolve, reject}, this.widgetInfo, this.handleSaveWidget, saveAs)
      })
    },
    async handleSaveWidget() {
      if (!this.config.save || !isFunction(this.config.save)) throw new Error('Please override save method in sdk config')
      try {
        // get newWidgetInfo to replace back into config loader
        this.newWidgetInfo = await this.promiseSaveWidgetCallback()
        this.widgetInfo = this.newWidgetInfo
        this.config.widgetId = this.newWidgetInfo.id
        // console.log('this.config', this.config)
      } catch (e) {
        throw new Error('Can not save config to RA api')
      }
    },
    async handleBeforeSaveWidget(saveAs) {
      if (!this.config.beforeSave || !isFunction(this.config.beforeSave)) throw new Error('Please override beforeSave method in sdk config')
      try {
        await this.promiseBeforeSaveWidgetCallback(saveAs)
      } catch (e) {
        throw new Error(e)
      }
    },
    removeTemplateWidget() {
      this.$emit('removeWidget', this.config.id)
    },
    onClickMenuWidget(eventInfo) {
      switch (eventInfo.type) {
        case 'change_widget_id':
          this.config.widgetId = eventInfo.widgetID
          // this.widgetInit()
          // this.updateConfig()
          break
        case 'save_action':
          this.handleBeforeSaveWidget(false)
          // this.updateConfig()
          break
        case 'save_as_action':
          this.handleBeforeSaveWidget(true)
          // this.updateConfig()
          break
        case 'template_remove_action':
          this.removeTemplateWidget()
          break
        default:
          break
      }
    },
    updateConfig() {
      this.$emit('update:configObj', this.config)
    },
    autoHeightEvent(id) {
      this.$emit('autoHeightEvent', this.config.id)
    },
    getTotalHeight() {
      let $title = $(this.$el).find('.cbpo-template-widget-title')
      let $widget = this.$refs.widgetElement.getTotalHeight()
      let margin = 4
      return ($title.length ? $title.height() + 2 : 0) + margin + $widget
    },
    checkHeaderWidget(data) {
      this.checkNoShowMenu = data
    }
  },
  watch: {
    async 'config.widgetId' (newVal, oldVal) {
      if (newVal && newVal !== oldVal) {
        await this.fetchWidget()
      }
    },
    'config.widget.style' (value) {
      if (this.widgetInfo) {
        this.widgetInfo.cf_object.config.widgetConfig.widget.style = value
      }
    }
  }
}
</script>
<style scoped lang="scss">
  @import './WidgetLoader.scss';
</style>
