<template>
  <div class="cbpo-format-builder cbpo-form-control">
    <!--Select format datatype-->
    <b-form-group class="--bold" label="Format Type">
      <b-form-select
        text-field="label"
        value-field="value"
        size="sm"
        v-model="type"
        :options="formatTypes">
      </b-form-select>
    </b-form-group>

    <!--Format common config-->
    <template v-if="type">
      <b-form-group class="--bold" label="Plain">
        <div class="form-inline">
          <label>Nil</label>
          <b-form-input v-model="cloneFormat.common.plain.nil"/>
        </div>
        <div class="form-inline">
          <label>Empty</label>
          <b-form-input v-model="cloneFormat.common.plain.empty"/>
        </div>
        <div class="form-inline">
          <label>N/A</label>
          <b-form-input v-model="cloneFormat.common.plain.na"/>
        </div>
      </b-form-group>
      <b-form-group class="--bold" label="Html">
        <div class="form-inline">
          <label>Nil</label>
          <b-form-input v-model="cloneFormat.common.html.nil"/>
        </div>
        <div class="form-inline">
          <label>Empty</label>
          <b-form-input v-model="cloneFormat.common.html.empty"/>
        </div>
        <div class="form-inline">
          <label>N/A</label>
          <b-form-input v-model="cloneFormat.common.html.na"/>
        </div>
      </b-form-group>
      <b-form-group class="--bold" label="Prefix">
        <b-form-input v-model="cloneFormat.common.prefix"/>
      </b-form-group>
      <b-form-group class="--bold" label="Suffix">
        <b-form-input v-model="cloneFormat.common.suffix"/>
      </b-form-group>
    </template>

    <!-- Format text config -->
    <template v-if="type && type === FORMAT_DATA_TYPES.TEXT">
      <b-form-group class="--bold" label="Transform type">
        <div class="form-inline">
          <b-form-select
            class="w-100"
            text-field="label"
            value-field="value"
            size="sm"
            v-model="cloneFormat.config.transform"
            :options="textTransformTypes">
          </b-form-select>
        </div>
      </b-form-group>
    </template>

    <!--Format Link config-->
    <template v-if="type && type === FORMAT_DATA_TYPES.LINK">
      <b-form-group class="--bold" label="Format Link Config">
        <div class="form-inline">
          <label>Target</label>
          <b-form-select text-field="label"
                         value-field="value"
                         size="sm"
                         class="w-100"
                         v-model="cloneFormat.config.target"
                         :options="targetTypes"/>
        </div>
        <div class="form-inline">
          <label>Text</label>
          <b-form-input v-model="cloneFormat.config.text"/>
        </div>
      </b-form-group>
    </template>

    <!--Format Boolean config-->
    <template v-if="type && type === FORMAT_DATA_TYPES.BOOLEAN">
      <b-form-group class="--bold" label="Format Boolean Config">
        <b-form-group class="--bold" label="Positive">
          <div class="form-inline">
            <label>Text</label>
            <b-form-input v-model="cloneFormat.config.positive.text"/>
          </div>
          <div class="form-inline">
            <label>HTML</label>
            <b-form-input v-model="cloneFormat.config.positive.html"/>
          </div>
        </b-form-group>
        <b-form-group class="--bold" label="Negative">
          <div class="form-inline">
            <label>Text</label>
            <b-form-input v-model="cloneFormat.config.negative.text"/>
          </div>
          <div class="form-inline">
            <label>HTML</label>
            <b-form-input v-model="cloneFormat.config.negative.html"/>
          </div>
        </b-form-group>
      </b-form-group>
    </template>

    <!--Format Temporal config-->
    <template v-if="type && type === FORMAT_DATA_TYPES.TEMPORAL">
      <b-form-group class="--bold" label="Format Temporal Config">
        <div class="form-inline">
          <label>Format</label>
          <b-form-input v-model="cloneFormat.config.format"/>
        </div>
        <div class="form-inline">
          <label>Timezone</label>
          <b-form-input v-model="cloneFormat.config.timezone"/>
        </div>
        <div class="form-inline">
          <label>Date Format</label>
          <b-form-input v-model="cloneFormat.config.date.format"/>
        </div>
        <div class="form-inline">
          <label>Time Format</label>
          <b-form-input v-model="cloneFormat.config.time.format"/>
        </div>
        <b-form-group class="--bold" label="Bin Format">
          <div class="form-inline">
            <label>Year</label>
            <b-form-input v-model="cloneFormat.config.options.year"/>
          </div>
          <div class="form-inline">
            <label>Quarter</label>
            <b-form-input v-model="cloneFormat.config.options.quarter"/>
          </div>
          <div class="form-inline">
            <label>Month</label>
            <b-form-input v-model="cloneFormat.config.options.month"/>
          </div>
          <div class="form-inline">
            <label>Week</label>
            <b-form-input v-model="cloneFormat.config.options.week"/>
          </div>
          <div class="form-inline">
            <label>Day</label>
            <b-form-input v-model="cloneFormat.config.options.day"/>
          </div>
          <div class="form-inline">
            <label>Hour</label>
            <b-form-input v-model="cloneFormat.config.options.hour"/>
          </div>
          <div class="form-inline">
            <label>Minute</label>
            <b-form-input v-model="cloneFormat.config.options.minute"/>
          </div>
          <div class="form-inline">
            <label>Second</label>
            <b-form-input v-model="cloneFormat.config.options.second"/>
          </div>
        </b-form-group>
      </b-form-group>
    </template>

    <!--Format Progress config-->
    <template v-if="type && type === FORMAT_DATA_TYPES.PROGRESS">
      <b-form-group class="--bold" label="Format Progress Config">
        <div class="form-inline">
          <label>Visualization</label>
          <b-form-select text-field="label"
                         value-field="value"
                         size="sm"
                         class="w-100"
                         v-model="cloneFormat.config.visualization"
                         :options="progressTypes"/>
        </div>
        <div class="form-inline">
          <label>Base</label>
          <b-form-input v-model="cloneFormat.config.base"/>
        </div>
        <div class="form-inline">
          <label>Label</label>
          <b-form-input v-model="cloneFormat.config.label"></b-form-input>
        </div>
        <div class="form-inline format-color-picker">
          <label>Color</label>
          <ColorPicker :color="cloneFormat.config.color" v-model="cloneFormat.config.color" defaultColor="#337ab7" />
        </div>
      </b-form-group>
    </template>

    <!--Format Stars config-->
    <template v-if="type && type === FORMAT_DATA_TYPES.STARS">
      <b-form-group class="--bold" label="Format Stars Config">
        <div class="form-inline">
          <label>Maximum</label>
          <b-form-input type="number" v-model.number="cloneFormat.config.maximum" @input="updateMaximum"/>
        </div>
        <b-form-group class="--bold" label="Stars Value">
          <div class="form-inline">
            <label>Display</label>
            <b-form-select
              text-field="label"
              value-field="value"
              size="sm"
              v-model="cloneFormat.config.value.display"
              :options="displayStarsFormatTypes">
            </b-form-select>
          </div>
          <div class="form-inline">
            <label>Format Value</label>
            <b-form-select
              text-field="label"
              value-field="value"
              size="sm"
              v-model="cloneFormat.config.value.format.type"
              :options="formatStarsFormatTypes">
            </b-form-select>
          </div>
          <div class="form-inline">
            <label>Half Style</label>
            <b-form-checkbox v-model="cloneFormat.config.style.half"/>
          </div>
        </b-form-group>
      </b-form-group>
    </template>

    <!--Format Segments config-->
    <template v-if="type && type === FORMAT_DATA_TYPES.SEGMENTS">
      <b-form-group class="--bold" label="Format Segments Config">
        <div class="form-inline">
          <label>Type</label>
          <b-form-select
            text-field="label"
            value-field="value"
            size="sm"
            v-model="cloneFormat.config.segmentType"
            :options="displaySegmentFormatTypes">
          </b-form-select>
        </div>
        <div class="form-inline">
          <label>Format Value</label>
          <b-form-select
            text-field="label"
            value-field="value"
            size="sm"
            v-model="cloneFormat.config.value.format.type"
            :options="formatSegmentsFormatTypes">
          </b-form-select>
        </div>
      </b-form-group>
    </template>

    <!--Format Currency config-->
    <template v-if="type && type === FORMAT_DATA_TYPES.CURRENCY">
      <b-form-group class="--bold" label="Format Numeric Config">
        <div class="form-inline">
          <label>Symbol</label>
          <b-form-input v-model.number="cloneFormat.config.currency.symbol"/>
        </div>
        <div class="form-inline">
          <label>Symbol Prefix</label>
          <b-form-checkbox v-model="cloneFormat.config.currency.symbolPrefix"/>
        </div>
        <div class="form-inline">
          <label>In Cents</label>
          <b-form-checkbox v-model="cloneFormat.config.currency.inCents"/>
        </div>
      </b-form-group>
    </template>

    <!--Format Numeric config-->
    <template v-if="shouldShowNumericConfig">
      <b-form-group class="--bold" label="Format Numeric Config">
        <div class="form-inline">
          <label>Comma</label>
          <b-form-checkbox v-model="getNumericConfig(type).comma"/>
        </div>
        <div class="form-inline">
          <label>Precision</label>
          <b-form-input type="number" v-model.number="getNumericConfig(type).precision"/>
        </div>
        <div class="form-inline">
          <label>Si Prefix</label>
          <b-form-checkbox v-model="getNumericConfig(type).siPrefix"/>
        </div>
        <div class="form-inline">
          <label>Absolute</label>
          <b-form-checkbox v-model="getNumericConfig(type).abs"></b-form-checkbox>
        </div>
      </b-form-group>
    </template>

    <template v-if="type && type === FORMAT_DATA_TYPES.OVERRIDE">
      <b-form-group class="--bold" label="Override Value">
        <b-form-input v-model="cloneFormat.config.format.text"/>
      </b-form-group>
    </template>
  </div>
</template>

<script>
import { cloneDeep, isEmpty, defaultsDeep, startCase, get } from 'lodash'
import { FORMAT_DATA_TYPES, getDefaultFormatConfigBaseOnFormatType } from '@/services/dataFormatManager'
import { defaultFormatConfig } from '@/components/widgets/elements/table/TableConfig'
import commonFormatConfig from '@/services/dataFormats/commonFormatConfig'
import { TYPES_TRANSFORM } from '@/services/dataFormats/textFormatConfig'
import ColorPicker from '@/components/colorPicker/ColorPicker'

export default {
  name: 'FormatConfigBuilder',
  props: {
    formatConfig: Object
  },
  components: {
    ColorPicker
  },
  data() {
    const buildTransformTypes = TYPES_TRANSFORM.map(value => {
      const label = value
        ? startCase(value)
        : 'No transform'
      return { label, value }
    })
    return {
      textTransformTypes: buildTransformTypes,
      formatTypes: [
        { label: 'No Format', value: '' },
        { label: 'Text', value: FORMAT_DATA_TYPES.TEXT },
        { label: 'Numeric', value: FORMAT_DATA_TYPES.NUMERIC },
        { label: 'Currency', value: FORMAT_DATA_TYPES.CURRENCY },
        { label: 'Link', value: FORMAT_DATA_TYPES.LINK },
        { label: 'Boolean', value: FORMAT_DATA_TYPES.BOOLEAN },
        { label: 'Temporal', value: FORMAT_DATA_TYPES.TEMPORAL },
        { label: 'Progress', value: FORMAT_DATA_TYPES.PROGRESS },
        { label: 'Segments', value: FORMAT_DATA_TYPES.SEGMENTS },
        { label: 'Stars', value: FORMAT_DATA_TYPES.STARS },
        { label: 'Override', value: FORMAT_DATA_TYPES.OVERRIDE }
      ],
      targetTypes: [
        { label: 'Blank', value: '_blank' },
        { label: 'Self', value: '_self' },
        { label: 'Parent', value: '_parent' },
        { label: 'Top', value: '_top' }
      ],
      progressTypes: [
        { label: 'Bar', value: 'bar' },
        { label: 'Percentage', value: 'percentage' }
      ],
      displayStarsFormatTypes: [
        { label: 'None', value: 'none' },
        { label: 'Left', value: 'left' },
        { label: 'Right', value: 'right' }
      ],
      formatStarsFormatTypes: [
        { label: 'Numeric', value: 'numeric' }
      ],
      formatSegmentsFormatTypes: [
        { label: 'Numeric', value: 'numeric' }
      ],
      displaySegmentFormatTypes: [
        { label: 'Trend', value: 'trend' }
        // { label: 'Custom', value: 'custom' } // No need to support custom for now
      ],
      FORMAT_DATA_TYPES: FORMAT_DATA_TYPES,
      cloneFormat: null,
      type: null,
      firstTime: true
    }
  },
  computed: {
    /**
     * Get config of format base on selection type
     * **/
    getNumericConfig() {
      return type => {
        switch (type) {
          case FORMAT_DATA_TYPES.CURRENCY:
            return this.cloneFormat.config.numeric
          case FORMAT_DATA_TYPES.STARS:
          case FORMAT_DATA_TYPES.SEGMENTS:
            return this.cloneFormat.config.value.format.config
          default: {
            return this.cloneFormat.config
          }
        }
      }
    },
    /**
     * Get config of numeric base on current selected dataType
     * **/
    shouldShowNumericConfig() {
      if (!this.type) {
        return false
      }
      return this.type &&
        (
          this.type === FORMAT_DATA_TYPES.NUMERIC ||
          this.type === FORMAT_DATA_TYPES.CURRENCY ||
          (
            (this.type === FORMAT_DATA_TYPES.SEGMENTS || this.type === FORMAT_DATA_TYPES.STARS) &&
            this.cloneFormat.config.value.format.type === FORMAT_DATA_TYPES.NUMERIC
          )
        )
    }
  },
  methods: {
    updateMaximum () {
      this.cloneFormat.config.maximum = Math.abs(this.cloneFormat.config.maximum)
    }
  },
  created() {
    const type = get(this.formatConfig, 'type', '')
    this.cloneFormat = defaultsDeep(
      (isEmpty(this.formatConfig) ? cloneDeep(defaultFormatConfig) : cloneDeep(this.formatConfig)),
      {config: getDefaultFormatConfigBaseOnFormatType(type), type, common: commonFormatConfig}
    )

    this.type = type
  },
  watch: {
    /**
     * Watch selected "type" and return suitable format config
     * **/
    type(val) {
      // this "if" case for re-open component without create new default format config
      if ((this.firstTime && isEmpty(this.type)) || !this.firstTime) {
        this.cloneFormat = {...this.cloneFormat, ...{config: getDefaultFormatConfigBaseOnFormatType(val), type: val}}
      }
      this.firstTime = false
    },
    /**
     * Watch clone format and update formatConfig.sync
     * **/
    cloneFormat: {
      deep: true,
      handler(val) {
        this.$emit('update:formatConfig', !isEmpty(this.type) ? val : null)
      }
    }
  }
}
</script>
<style lang="scss" scoped>
.cbpo-form-control {
  .--bold {
    legend {
      font-weight: bold;
    }
  }

  .form-inline {
    margin-bottom: 1rem;
    flex-wrap: nowrap;

    label {
      min-width: 100px;
      text-align: left;
      justify-content: left;
    }

    input[type=text].form-control {
      width: 100%;
    }
  }

  ::v-deep.format-color-picker {
    .color-picker {
      width:100%;
    }

    .color-picker-container {
        height: calc(1.5em + 0.75rem + 2px);
        display: flex;
        align-items: center;
    }
  }
}
</style>
