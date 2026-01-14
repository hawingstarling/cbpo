<template>
  <div class="w-100">
    <b-form-group v-if="shouldShow([ELEMENT.CHART])" label="Chart Type">
      <b-form-select  size="sm"
                      class="mb-2"
                      :options="getOptionsBaseOnSelectedElement"
                      v-model="seriesItem.type">
      </b-form-select>
    </b-form-group>
    <b-form-group v-if="!shouldShow([ELEMENT.HEAT_MAP])" disabled label="Type">
      <b-form-select :options="typeOptions" switch size="sm" class="mb-2" v-model="axis.item.type"/>
    </b-form-group>
    <b-form-group label="Label" v-if="!shouldShow([ELEMENT.HEAT_MAP])">
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
    <!-- Ticks options -->
    <b-form-group label="Ticks">
      <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.formatTypeCollapse>Options</span>
        </b-card-header>
        <!--Format Type Config-->
        <b-collapse id="formatTypeCollapse">
          <b-card-body class="bold-title cbpo-form-control">
<!--            <b-form-group label="Stacked" v-if="!shouldShow([ELEMENT.HEAT_MAP])">-->
<!--              <b-form-checkbox switch size="sm" class="mb-2" v-model="axis.item.stack"/>-->
<!--            </b-form-group>-->
            <b-form-group label="Begin At Zero" v-if="!shouldShow([ELEMENT.HEAT_MAP])">
              <b-form-checkbox switch size="sm" class="mb-2" v-model="axis.item.ticks.beginAtZero"/>
            </b-form-group>
            <b-form-group label="Position" v-if="!shouldShow([ELEMENT.HEAT_MAP])">
              <b-form-select :options="positionOptions" switch size="sm" class="mb-2" v-model="axis.item.position"/>
            </b-form-group>
            <b-form-group label="Step Size" v-if="!shouldShow([ELEMENT.HEAT_MAP])">
              <b-form-input switch size="sm" class="mb-2" v-model="axis.item.ticks.stepSize"/>
            </b-form-group>
            <b-form-group label="Max Ticks" v-if="!shouldShow([ELEMENT.HEAT_MAP])">
              <b-form-input switch size="sm" class="mb-2" v-model="axis.item.ticks.maxTicksLimit"/>
            </b-form-group>
            <b-form-group v-if="shouldShow([ELEMENT.HEAT_MAP])" label="Color of min value">
              <color-picker :color="axis.item.ticks.minColor" v-model="axis.item.ticks.minColor" />
            </b-form-group>
            <b-form-group v-if="shouldShow([ELEMENT.HEAT_MAP])" label="Color of max value">
              <color-picker :color="axis.item.ticks.maxColor" v-model="axis.item.ticks.maxColor" />
            </b-form-group>
            <b-form-group v-if="shouldShow([ELEMENT.HEAT_MAP])" label="Color of border axis">
              <color-picker :color="axis.item.axisGridColor" v-model="axis.item.axisGridColor" />
            </b-form-group>
            <b-form-group v-if="shouldShow([ELEMENT.HEAT_MAP])" label="Color of label axis">
              <color-picker :color="axis.item.axisLabelColor" v-model="axis.item.axisLabelColor" />
            </b-form-group>
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
import ColorPicker from '@/components/colorPicker/ColorPicker'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import AxisSettingsMixins from '@/components/visualizationBuilder/AxisSettingsMixins'
import startCase from 'lodash/startCase'

export default {
  name: 'YAxisSettings',
  mixins: [AxisSettingsMixins],
  components: {
    ColorPicker: ColorPicker
  },
  data() {
    return {
      ELEMENT: ELEMENT,
      TYPES: TYPES,
      typeOptions: [
        { value: 'linear', text: 'Linear' }
      ],
      positionOptions: [
        { value: 'left', text: 'Left' },
        { value: 'right', text: 'Right' }
      ],
      chartTypes: Object.values(TYPES).map(type => {
        return {value: type, text: startCase(type)}
      })
    }
  },
  computed: {
    /*
    * Check current selected element is included in array
    * @param {String Array} elements - Array elements
    * */
    shouldShow() {
      return elements => {
        if (!this.element || !this.element.type) {
          return false
        }
        return elements.includes(this.element.type)
      }
    },
    getOptionsBaseOnSelectedElement() {
      switch (this.selectedElement.chartType) {
        case TYPES.PARETO: {
          return this.chartTypes.filter(type => type.value === TYPES.BAR || type.value === TYPES.LINE)
        }
        default: {
          return this.chartTypes.filter(type => type.value === this.selectedElement.chartType)
        }
      }
    }
  }
}
</script>

<style scoped lang="scss">
.bold-title ::v-deep legend {
  font-weight: bold!important;
}

::v-deep .input-group.color-picker {
  .input-group-addon.color-picker-container {
    width: 32px;
    height: 32px;
    display: flex;
    justify-content: center;
    align-items: center;
    .current-color {
      height: 24px;
      width: 24px;
    }
  }
}
</style>
