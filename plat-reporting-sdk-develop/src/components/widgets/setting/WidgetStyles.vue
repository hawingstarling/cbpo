<template>
  <div>
    <b-card no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.widgetStylesCollapse>Widget Styles</span>
      </b-card-header>
      <b-collapse id="widgetStylesCollapse">
        <b-card-body>
          <b-form-group label="Background color">
            <ColorPicker :color="configData.background_color" v-model="configData.background_color" />
          </b-form-group>
          <b-form-group label="Foreground color">
            <ColorPicker :color="configData.foreground_color" v-model="configData.foreground_color" />
          </b-form-group>
          <b-form-group label="Header background color">
            <ColorPicker :color="configData.header_background_color" v-model="configData.header_background_color" />
          </b-form-group>
          <b-form-group label="Header foreground color">
            <ColorPicker :color="configData.header_foreground_color" v-model="configData.header_foreground_color" />
          </b-form-group>
          <b-form-group label="Border width">
            <custom-numeric-input min="0" type="int" v-model="configData.border_width" />
          </b-form-group>
          <b-form-group label="Border radius">
            <custom-numeric-input min="0" type="int" v-model="configData.border_radius" />
          </b-form-group>
        </b-card-body>
      </b-collapse>
    </b-card>
  </div>
</template>

<script>
import ColorPicker from '@/components/colorPicker/ColorPicker'
import CustomNumericInput from '@/components/share/forms/CustomNumericInput'

export default {
  name: 'WidgetStyles',
  components: {
    ColorPicker,
    'custom-numeric-input': CustomNumericInput
  },
  props: {
    configData: Object
  },
  data () {
    return {
    }
  }
}
</script>
