<template>
  <div class="cbpo-grouping-container">
    <div class="grouping-row">
      <div class="label">
        <span>Binning</span>
      </div>
    </div>
    <b-card
      header="Option"
      header-tag="header"
      header-class="p-1"
    >
      <b-form-group label="Type" label-class="font-weight-bold">
        <b-form-select
          v-model="configObj.binningType"
          @change="typeChange($event)"
          :options="binningTypes"
          :disabled="disabled"
          size="sm">
        </b-form-select>
      </b-form-group>
      <p v-if="disabled">Chartjs doesn't support category axis for this chart</p>
      <div v-if="configObj.binningType">
        <b-form-group v-if="configObj.binningType === 'auto'"
                      label="Expected"
                      label-for="input-sm"
                      label-class="font-weight-bold">
          <custom-numeric-input type="int" min=1 v-model="configObj.expected"></custom-numeric-input>
        </b-form-group>
        <b-form-group v-if="configObj.binningType === 'uniform'"
                      label="Width"
                      label-for="input-sm"
                      label-class="font-weight-bold">
          <custom-numeric-input type="decimal" min=0 v-model="configObj.width"></custom-numeric-input>
        </b-form-group>
        <b-form-group v-if="columnType === FORMAT_DATA_TYPES.TEMPORAL && configObj.binningType === 'uniform'"
                      label="Unit"
                      label-for="unit_select"
                      label-class="font-weight-bold">
          <b-form-select
            id="unit_select"
            v-model="configObj.unit"
            :options="listUnit"
            size="sm">
          </b-form-select>
        </b-form-group>
        <b-form-checkbox v-if="columnType === FORMAT_DATA_TYPES.NUMERIC"
          v-model="configObj.nice"
          value=true
          unchecked-value=false
        >
          Nice
        </b-form-checkbox>
      </div>
    </b-card>
  </div>
</template>
<script>
import CustomNumericInput from '@/components/share/forms/CustomNumericInput'
import { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import {
  LIST_UNIT,
  BINNING_TYPES,
  DEFAULT_STATE_BIN
} from '@/components/widgets/elements/table/grouping/ColumnSettingsConfig'
import cloneDeep from 'lodash/cloneDeep'

export default {
  name: 'BinningConfig',
  components: {
    'custom-numeric-input': CustomNumericInput
  },
  props: {
    columnType: String,
    config: {
      type: Object
    },
    disabled: Boolean
  },
  data () {
    return {
      configObj: null,
      FORMAT_DATA_TYPES: FORMAT_DATA_TYPES,
      binningTypes: BINNING_TYPES,
      listUnit: LIST_UNIT
    }
  },
  methods: {
    typeChange(binningType) {
      this.configObj = cloneDeep(!binningType
        ? cloneDeep(DEFAULT_STATE_BIN['null'])
        : cloneDeep(DEFAULT_STATE_BIN[`${binningType}_${this.columnType}`]))
      this.$emit('update:config', this.configObj)
    }
  },
  created() {
    this.configObj = cloneDeep(this.config)
  },
  watch: {
    configObj: {
      deep: true,
      handler(val) {
        if (val.binningType === this.config.binningType) {
          this.$emit('update:config', this.configObj)
        }
      }
    }
  }
}
</script>
<style scoped lang="scss">
  .grouping-row {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;

    .label {
      width: 100%;
      padding: 0.5rem 0;
    }

    .action {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      width: 120px;
    }
  }
</style>
