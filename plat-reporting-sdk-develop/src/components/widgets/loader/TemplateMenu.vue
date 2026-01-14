<template>
  <div class="cbpo-widget-menu p-1 template-title cbpo-template-widget-title">
    Widget Toolbar
    <template-menu-control-select
      :builder="builder"
      :configObj="config.menu.config"
      :widgetInfo="widgetInfo"
      @click="onClickMenu($event)"
      class="template-menu"
    />
    <!--TEMPLATE SETTINGS MODAL-->
    <b-modal dialog-class="cbpo-custom-modal" size="lg" :ref="modalId('template_settings')" :id="modalId('template_settings')" title="Template Settings">
      <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.templateSetting>Switch Visualization</span>
        </b-card-header>
        <b-collapse id="templateSetting" visible>
          <b-card-body>
            <b-form-group label="Widget ID">
              <b-form-input v-model="widgetInfo.id" placeholder="Enter widget ID"></b-form-input>
            </b-form-group>
          </b-card-body>
        </b-collapse>
      </b-card>
      <template v-slot:modal-footer>
        <div class="control-box switch-widget-footer-modal">
          <button class="cbpo-btn btn-primary mr-1 pull-right" @click="onClickMenu('change_widget_id')">
            Apply
          </button>
          <button @click="modalTrigger({type: 'template_settings', isShow: false})" class="cbpo-btn">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>

    <b-modal dialog-class="cbpo-custom-modal" title="Please confirm" centered :ref="modalId('template_remove')" :id="modalId('template_remove')">
      {{ 'Remove this visualization from the dashboard?' }}
      <template v-slot:modal-footer>
        <button class="cbpo-btn btn-warning" @click="onClickMenu('apply_template_remove')">
          <i class="fa fa-check mr-1"></i> Yes
        </button>
        <button class="cbpo-btn" @click="modalTrigger({type: 'template_remove', isShow: false})">
          <i class="fa fa-times mr-1"></i> No
        </button>
      </template>
    </b-modal>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import TemplateMenuControlSelect from '@/components/widgets/loader/TemplateMenuControlSelect'

export default {
  name: 'TemplateMenu',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins
  ],
  data() {
    return {
      widgetID: null,
      widgetName: null
    }
  },
  props: {
    configObj: Object,
    builder: {
      type: Boolean,
      default: false
    },
    widgetInfo: {
      type: Object
    }
  },
  components: {
    'template-menu-control-select': TemplateMenuControlSelect
  },
  computed: {
    modalId() {
      return type => `${this.configObj.id || ''}_modal_${type}`
    },
    widgetSettingComponentRef() {
      return type => `${this.configObj.id || ''}_modal_content_template_settings`
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
      console.log('type', type)
      switch (type) {
        case 'template_settings':
          this.modalTrigger({type: 'template_settings', isShow: true})
          break
        case 'change_widget_id':
          this.modalTrigger({type: 'template_settings', isShow: false})
          this.$emit('input', {type: 'change_widget_id', widgetID: this.widgetInfo.id})
          break
        case 'save_widget':
          this.$emit('input', {type: 'save_action'})
          break
        case 'save_as_widget':
          this.$emit('input', {type: 'save_as_action'})
          break
        case 'remove_template':
          this.modalTrigger({type: 'template_remove', isShow: true})
          break
        case 'apply_template_remove':
          this.modalTrigger({type: 'template_remove', isShow: false})
          this.$emit('input', {type: 'template_remove_action'})
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
  .template-title {
    width: 100%;
    height: 50px;
    font-size: 12px;
    font-weight: 400;
    display: flex;
    align-items: center;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
    border: 1px dashed #777;
  }
  .template-menu {
    position: absolute;
    right: 0;
  }
  .switch-widget-footer-modal {
    width: 100%;
  }
</style>
