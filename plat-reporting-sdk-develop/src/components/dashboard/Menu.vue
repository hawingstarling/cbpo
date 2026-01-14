<template>
  <div class="cbpo-widget-menu p-1">
    <menu-control-select
      :allow-custom-options="false"
      :builder="builder"
      :configObj="config.menu.config"
      @click="onClickMenu($event)">
    </menu-control-select>

    <!--WIDGET SETTINGS MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="lg" :ref="modalId('widget_settings')" :id="modalId('widget_settings')" title="Widget Settings">
      <!--Widget Styles-->
      <WidgetStyles :configData="config.style" />
      <!--end Widget Styles-->
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
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import MenuControlSelect from '@/components/widgets/menu/MenuControlSelect'
import WidgetStyles from '@/components/widgets/setting/WidgetStyles'

export default {
  name: 'DashboardMenu',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins
  ],
  props: {
    configObj: Object,
    builder: {
      type: Boolean,
      default: false
    }
  },
  components: {
    WidgetStyles,
    'menu-control-select': MenuControlSelect
  },
  computed: {
    modalId() {
      return type => `${this.configObj.id || ''}_modal_${type}`
    },
    widgetSettingComponentRef() {
      return type => `${this.configObj.id || ''}_modal_content_widget_settings`
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
      switch (type) {
        case 'widget-settings':
          this.modalTrigger({type: 'widget_settings', isShow: true})
          break
        case 'apply_widget_settings':
          this.modalTrigger({type: 'widget_settings', isShow: false})
          this.$emit('input', {type: 'changeWidgetConfig', config: this.configObj})
          break
        default:
          break
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  @import '@/components/widgets/menu/Menu.scss';
</style>
