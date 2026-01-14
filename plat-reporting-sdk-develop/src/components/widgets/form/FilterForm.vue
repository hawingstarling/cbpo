<template>
  <div class="cbpo-s cbpo-wrapper-form">
    <form @submit.prevent="() => false" class="cbpo-form cbpo-filter-form">
      <div class="cbpo-control-item d-flex" v-for="(control, idx) in controls" :key="idx">
        <template  v-if="control.type === CONTROL_TYPE.AUTO">
          <cbpo-filter-control-range
            v-if="control.config.common.operator === SUPPORT_OPERATORS.in_range.value"
            :control="control"
            @input="controlChange"
          />
          <cbpo-filter-control-textarea
            v-else-if="control.config.common.operator === SUPPORT_OPERATORS.in.value"
            :control="control"
            @input="controlChange"
          />
          <cbpo-filter-control-input
            v-else
            :control="control"
            @input="controlChange"
          />
        </template>
        <template  v-else-if="control.type === CONTROL_TYPE.DATE_RANGE">
          <cbpo-filter-control-range-select
            v-if="control.config.common.operator === SUPPORT_OPERATORS.in_range.value"
            :control="control"
            @input="controlChange"
          />
        </template>
        <template v-else>
          <cbpo-filter-control-select
            v-if="control.type === CONTROL_TYPE.SELECT"
            :control="control"
            @input="controlChange"
          />
          <cbpo-filter-control-input
            v-if="control.type === CONTROL_TYPE.INPUT"
            :control="control"
            @input="controlChange"
          />
          <cbpo-filter-control-range
            v-if="control.type === CONTROL_TYPE.RANGE"
            :control="control"
            @input="controlChange"
          />
        </template>
      </div>
    </form>
  </div>
</template>
<script>
import FilterControlSelect from './FilterControlSelect'
import FilterControlInput from './FilterControlInput'
import FilterControlRange from './FilterControlRange'
import FilterControlRangeSelect from './FilterControlRangeSelect'
import FilterControlTextarea from './FilterControlTextarea'
import { SUPPORT_OPERATORS } from '@/services/ds/filter/FilterDefinitions'
import { generateIdIfNotExist } from '@/utils/configUtil'
import { SUPPORT_LOGIC } from '@/utils/filterUtils'
import { CONTROL_TYPE } from '@/components/widgets/form/FilterControlConfig'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import get from 'lodash/get'
import findIndex from 'lodash/findIndex'
import cloneDeep from 'lodash/cloneDeep'
import isArray from 'lodash/isArray'
import CBPO from '@/services/CBPO'

export default {
  name: 'FilterForm',
  props: {
    globalFilter: Boolean,
    waitingForGlobalFilter: Boolean,
    controls: {
      type: Array,
      default: () => []
    }
  },
  components: {
    'cbpo-filter-control-select': FilterControlSelect,
    'cbpo-filter-control-input': FilterControlInput,
    'cbpo-filter-control-range': FilterControlRange,
    'cbpo-filter-control-textarea': FilterControlTextarea,
    'cbpo-filter-control-range-select': FilterControlRangeSelect
  },
  data () {
    return {
      fetchCount: 0,
      numOfControlLoadData: 0,
      CONTROL_TYPE,
      SUPPORT_OPERATORS
    }
  },
  methods: {
    countControl() {
      this.numOfControlLoadData = this.controls
        .filter(control => control.type === CONTROL_TYPE.SELECT && control.config.dataSource)
        .length
    },
    createIndexForEachControl() {
      this.controls.forEach(control => generateIdIfNotExist(control.config))
    },
    controlChange(control) {
      this.fetchCount++
      let index = findIndex(this.controls, ctrl => control.config.id === ctrl.config.id)
      index !== -1 && (this.$set(this.controls, index, control))
      this.buildFilterFromControls(this.controls)
      // change config for save config feature
      this.$emit('update:controls', this.controls)
      if (this.fetchCount === this.numOfControlLoadData) {
        // TODO: find a better way. Current issue: Duplicate calling api
        // global filter need to be call after other controls is ready
        setTimeout(() => CBPO.channelManager().getChannel().getFilterSvc().setGlobalFilterReady(true), 200)
      }
    },
    buildFilterFromControls(controls) {
      let filter = {
        type: SUPPORT_LOGIC.AND,
        conditions: []
      }
      filter.conditions = cloneDeep(controls)
        // Do not select all select with empty selected
        .filter(control => {
          // undefined is unset
          switch (control.type) {
            case CONTROL_TYPE.SELECT: {
              return !get(control, 'config.selection.empty.isEmptySelected', true)
            }
            case CONTROL_TYPE.INPUT: {
              return get(control, 'config.common.value', undefined)
            }
            case CONTROL_TYPE.DATE_RANGE:
            case CONTROL_TYPE.RANGE: {
              return get(control, 'config.common.value', [undefined, undefined]).every(value => value !== undefined)
            }
            default: {
              return get(control, 'config.common.value', undefined) !== undefined
            }
          }
        })
        // Build filter query from available selected
        .map(control => {
          // get common value as filter query
          const common = control.config.common

          // convert value to other type base on operator
          if (common.operator === SUPPORT_OPERATORS.in.value) {
            common.value = common.value.split(',').map(value => value.trim())
          }

          // parse value to iso string if column type is temporal
          if (DataTypeUtil.isNumeric(common.column.type) && common.value !== null) {
            common.value = isArray(common.value) ? common.value.map(value => Number(value)) : Number(common.value)
          }

          // force common change to null operator when control type is SELECT and current option value is null.
          // Required changed by DS.
          if ((common.value === null || common.value === 'null') && control.type === CONTROL_TYPE.SELECT) {
            common.operator = SUPPORT_OPERATORS.null.value
            common.value = ''
          }

          // parse common to query type (column must be a string)
          common.column = common.column.name
          return common
        })
      this.$emit('filterChange',
        this.globalFilter
          ? { global: filter.conditions.length ? filter : {} }
          : { form: filter.conditions.length ? filter : {} }
      )
    }
  },
  created() {
    this.countControl()
    this.createIndexForEachControl()
    if (this.globalFilter) {
      CBPO.channelManager().getChannel().getFilterSvc().setGlobalFilterReady(this.numOfControlLoadData === 0)
    }
  }
}
</script>
<style lang="scss" scoped>
  @import './FilterForm.scss';
</style>
