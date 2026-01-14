<template>
  <div class="w-100">
    <b-form-group label="Label">
      <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.axisSettingsOptions>Options</span>
        </b-card-header>
        <b-collapse v-if="axis.item" id="axisSettingsOptions">
          <b-card-body class="cbpo-form-control">
            <b-form-group label="Title Enabled">
              <b-form-checkbox switch size="sm" class="mb-2" v-model="axis.item.scaleLabel.display"/>
            </b-form-group>
            <b-form-group label="Title Text" v-if="axis.item.scaleLabel.display">
              <b-form-input switch size="sm" class="mb-2" v-model="axis.item.scaleLabel.labelString"/>
            </b-form-group>
          </b-card-body>
        </b-collapse>
      </b-card>
    </b-form-group>
    <b-form-group label="Ticks">
      <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.formatTypeCollapse>Options</span>
        </b-card-header>
        <!--Format Type Config-->
        <b-collapse id="formatTypeCollapse">
          <b-card-body class="cbpo-form-control">
            <format-config-builder
              v-if="axis.item"
              :format-config.sync="axis.item.format"/>
          </b-card-body>
        </b-collapse>
      </b-card>
    </b-form-group>
  </div>
</template>

<script>
import AxisSettingsMixins from '@/components/visualizationBuilder/AxisSettingsMixins'

export default {
  name: 'XAxisSettings',
  mixins: [AxisSettingsMixins]
}
</script>
