<template>
  <div v-if="configReady" class="cbpo-builder-wrapper">
    <slot :openModal="openModal" :isFieldsReady="isFieldsReady" name="button">
      <button @click="openModal()" class="cbpo-btn btn-primary">
        <span>
          {{config.trigger.label}}
        </span>
      </button>
    </slot>
    <!--Modal dynamic filter-->
    <b-modal dialog-class="cbpo-custom-modal modal-build-filter" :id="'query-builder-modal-' + config.id" size="custom" no-close-on-backdrop>
        <template v-slot:modal-title>
          {{config.modal.title}}
        </template>
        <!--TODO Use vuelidate later-->
        <ValidationObserver ref="dynamicForm"  v-slot="{ invalid, passes }">
          <form @submit.prevent="passes(apply)" :id="`connector-${config.id}`" v-on:keyup.enter="apply()">
            <cbpo-filter-wrapper
              ref="wrapper"
              :scope="config.id"
              :fields="fields"
              :operators="operators"
              :format="config.format"
              :filter="config.query"
              :maxlevel="config.threshold.maxLevel"
              :form-columns="config.form.columns"
              @updateItems="updateItems($event)"
              :updateItemsObj="updateItemsObj"
            >
            </cbpo-filter-wrapper>
          </form>
        </ValidationObserver>
        <template v-slot:modal-footer="{ ok, cancel }">
          <button @click="clear" class="cbpo-btn btn-warning mr-2 modal-build-filter__btn-clear">
            <span>Clear</span>
          </button>
          <button @click="reset" class="cbpo-btn btn-warning mr-auto modal-build-filter__btn-reset">
            <span>Reset</span>
          </button>
          <!-- Emulate built in modal footer ok and cancel button actions -->
          <b-form-checkbox v-if="config.ignore.base.visible" class="cbpo-custom-checkbox" v-model="config.ignore.base.value">Ignore base filter</b-form-checkbox>
          <b-form-checkbox v-if="config.ignore.global.visible" class="cbpo-custom-checkbox" v-model="config.ignore.global.value">Ignore global filter</b-form-checkbox>

          <button @click="apply()" class="cbpo-btn btn-primary mr-2">
            <span>Apply</span>
          </button>
          <button class="cbpo-btn" @click="cancel()">
            <span>Cancel</span>
          </button>
        </template>
    </b-modal>
  </div>
</template>

<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import { makeFilterControlDefaultConfig } from './DynamicFilterConfig'
import FilterWrapper from './FilterWrapper'
import { generateIdIfNotExist } from '@/utils/configUtil.js'
import { convertColumnNameToColumnObject } from '@/utils/filterUtils'
import { ValidationObserver } from 'vee-validate'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import { SUPPORT_OPERATORS } from '@/services/ds/filter/FilterDefinitions'
// import moment from 'moment/moment'
import CBPO from '@/services/CBPO'
import { BUS_EVENT } from '@/services/eventBusType'
// import { StaticExpression } from 'plat-sdk'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import get from 'lodash/get'
import isEmpty from 'lodash/isEmpty'
import uniqBy from 'lodash/uniqBy'
import map from 'lodash/map'
import cloneDeep from 'lodash/cloneDeep'
import startCase from 'lodash/startCase'
import find from 'lodash/find'
import sortBy from 'lodash/sortBy'
import isArray from 'lodash/isArray'
import isString from 'lodash/isString'
import isNumber from 'lodash/isNumber'
import flatten from 'lodash/flatten'
import uuidv4 from 'uuid'

export default {
  name: 'QueryBuilder',
  props: {
    elements: Array,
    updateItemsObj: Object
  },
  components: {
    'cbpo-filter-wrapper': FilterWrapper,
    ValidationObserver
  },
  data() {
    return {
      root: {},
      fields: [],
      operators: [],
      defaultState: null,
      defaultIgnoreState: null,
      isFieldsReady: false
    }
  },
  extends: WidgetBase,
  mixins: [WidgetBaseMixins],
  methods: {
    widgetConfig(config) {
      config.id = uuidv4()
      makeFilterControlDefaultConfig(config)
      this.buildFilterState(this.config.query, 0)
      this.buildFields()
      this.buildOperators()
      this.defaultState = this.cloneObject(this.config.query)
      this.defaultIgnoreState = this.cloneObject(this.config.ignore)
    },
    openModal() {
      this.$bvModal.show('query-builder-modal-' + this.config.id)
      this.config.query = this.cloneObject(this.defaultState)
      this.config.ignore = this.cloneObject(this.defaultIgnoreState)
    },
    cloneObject(object = {}) {
      return cloneDeep(object)
    },
    buildFilterObject(filter) {
      const supportOperator = [SUPPORT_OPERATORS.not_in.value, SUPPORT_OPERATORS.in.value]
      if (!filter.conditions) {
        // let format
        if (isArray(filter.value)) {
          filter.value = flatten(map(filter.value, (value) => this.buildFilterObject({...filter, value}).value))
          filter.column = filter.column.name
          return filter
        // } else if (filter.column.type === SUPPORT_COLUMN_TYPES.DATE) {
        //   format = this.config.format.temporal.date
        //   filter.value = StaticExpression.isValid(filter.value) ? filter.value : moment(filter.value).format(format.formatValue)
        // } else if (filter.column.type === SUPPORT_COLUMN_TYPES.DATE_TIME) {
        //   format = this.config.format.temporal.datetime
        //   filter.value = moment(filter.value, format).format(format.formatValue)
        } else if (DataTypeUtil.isNumeric(filter.column.type) && !supportOperator.includes(filter.operator)) {
          filter.value = isNumber(filter.value) ? Number(filter.value) : filter.value
        } else if (supportOperator.includes(filter.operator)) {
          if (isString(filter.value)) {
            filter.value = map(filter.value.split(','), value => {
              if (DataTypeUtil.isNumeric(filter.column.type)) {
                return parseFloat(value, 10)
              } else {
                return value.trim()
              }
            })
          } else {
            filter.value = [filter.value]
          }
        } else if (isString(filter.value)) {
          filter.value = filter.value.trim()
        }
        filter.column = filter.column.name
        return filter
      } else {
        filter.conditions = filter.conditions.map(ft => this.buildFilterObject(ft))
        return filter
      }
    },
    cancel() {
      this.$bvModal.hide(`query-builder-modal-${this.config.id}`)
      this.config.query = this.cloneObject(this.defaultState)
      this.config.ignore = this.cloneObject(this.defaultIgnoreState)
    },
    async apply() {
      try {
        let isValid = await this.$refs.dynamicForm.validate()
        if (isValid) {
          let filter = this.cloneObject(this.config.query)
          this.defaultState = filter
          this.defaultIgnoreState = this.cloneObject(this.config.ignore)
          this.emitFilters(filter.conditions.length > 0 ? this.buildFilterObject(this.cloneObject(filter)) : {}, this.config.ignore)
        }
      } catch (e) {
        console.error('Form is invalid', e)
      }
    },
    reset() {
      this.config.query = this.cloneObject(this.defaultState)
      this.config.ignore = this.cloneObject(this.defaultIgnoreState)
      // show toast message
      this.$bvToast.toast('The filter has been reset', {
        solid: true,
        variant: 'success',
        headerClass: 'd-none'
      })
      this.$refs.dynamicForm.reset()
    },
    clear() {
      // clear all current node and add new node
      this.config.query.conditions = []
    },
    emitFilters(filter, ignoreState) {
      this.$emit('filterChange', {builder: filter, ignore: ignoreState})
      this.$bvModal.hide(`query-builder-modal-${this.config.id}`)
    },
    getColumns(dataSource) {
      return CBPO
        .dsManager()
        .getDataSource(dataSource)
        .columns()
    },
    getAllColumns(dataSources) {
      try {
        return Promise.all(dataSources)
      } catch (e) {
        return []
      }
    },
    async buildFields() {
      let configColumns = []
      let dataSources = []
      this.elements
        .forEach(el => {
          let type = el.type
          if (type === ELEMENT.CROSSTAB_TABLE) {
            configColumns.push(uniqBy([...el.config.xColumns, ...el.config.yColumns, ...el.config.tColumns], 'name'))
          } else {
            configColumns.push(el.config.columns)
          }
          dataSources.push(new Promise((resolve) => resolve(this.getColumns(el.config.dataSource))))
        })
      let columns = await this.getAllColumns(dataSources)
      CBPO.$bus.$emit(BUS_EVENT.BUILDER_FILTER_COLUMNS_READY)
      configColumns = configColumns.map((cols, i) => {
        return cols.map(column => {
          let singleColumn = find(columns[i], (o) => o.name === column.name)
          if (singleColumn) {
            singleColumn.displayName = column.displayName || singleColumn.label || startCase(singleColumn.name)
            return singleColumn
          }
        })
      })
      this.fields = [].concat.apply([], columns).filter(c => {
        return !isEmpty(c) && !isEmpty(c.displayName)
      })
      // update columns from channelManager (builder filter)
      this.updatedColumnsState.forEach(col => this.updateColumn(col))
      this.fields = sortBy(this.fields, f => f.displayName)
        .filter(f => !get(this.config, 'hiddenColumns', []).find(col => col.name === f.name))
    },
    buildOperators() {
      this.operators = uniqBy(Object.keys(SUPPORT_OPERATORS).map(key => SUPPORT_OPERATORS[key]), 'label')
    },
    buildFilterState(filter, level, parentId = null) {
      if (!filter.id) {
        generateIdIfNotExist(filter)
      }
      if (!filter.level) {
        filter.level = level
      }
      filter.parentId = parentId
      if (filter.conditions && filter.conditions.length > 0) {
        filter.conditions.forEach(f => {
          this.buildFilterState(f, level + 1, filter.id)
        })
      }
    },
    // update column from channelManager
    updateColumn (data) {
      if (data) {
        const foundCol = this.fields.find(col => col.name === data.name)
        if (foundCol) foundCol.displayName = data.displayName || foundCol.displayName
      }
    },
    updateItems(data) {
      this.$emit('updateItems', data)
    }
  },
  computed: {
    updatedColumnsState () {
      return CBPO.channelManager().getChannel().getColumnSvc().getColumns()
    }
  },
  watch: {
    'config.query': {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal !== oldVal) {
          this.root = newVal
          if (this.fields && this.fields.length) {
            this.config.query = convertColumnNameToColumnObject(this.config.query, this.fields)
          }
        }
      }
    },
    elements: {
      deep: true,
      handler: function() {
        this.buildFields()
      }
    },
    fields: {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal && newVal.length) {
          this.isFieldsReady = true
        }
      }
    },
    updatedColumnsState: {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal && newVal.length) {
          newVal.forEach(col => this.updateColumn(col))
        }
      }
    }
  }
}
</script>
<style scoped lang="scss">
  @import "BuilderFilter";
</style>
