<template>
  <div class="tree-form-group" :class="{'end-node': nodeConfig.index === nodeConfig.childNodes - 1, 'basic-mode': basicMode}">
    <!-- Drop zone -->
    <div v-if="!basicMode && nodeConfig.index === 0"
         v-cbpo-droppable="{
            scope: scope,
            level: nodeData.level,
            node: nodeData,
            index: nodeConfig.index
         }"
         :key="`dropZone_${nodeData.id}_before`"
         :data-level="nodeData.level"
         :data-index="nodeConfig.index"
         class="first-node tree-node-droppable ">
      <i class="fa fa-arrow-circle-o-right"/>
    </div>

    <!-- Drag point -->
    <i v-if="!basicMode"
       v-cbpo-draggable="{
        scope: scope,
        level: nodeData.level,
        node: nodeData,
        index: nodeConfig.index,
        [EVENT.START_EVENT]: startEvent,
        [EVENT.STOP_EVENT]: stopEvent
       }"
       v-cbpo-connector="{
        position: {
          start: 'center',
          end: 'center'
        },
        scopeId: `connector-${scope}`
       }"
       :key="`dragNode_${nodeData.id}`"
       class="tree-node-draggable fa fa-arrows"/>

    <!-- Drop zone -->
    <div v-if="!basicMode"
         v-cbpo-droppable="{
          scope: scope,
          level: nodeData.level,
          node: nodeData,
          index: nodeConfig.index + 1
        }"
         :key="`dropZone_${nodeData.id}_after`"
         :data-level="nodeData.level"
         :data-index="nodeConfig.index + 1"
         :class="{'last-node': nodeConfig.index === nodeConfig.childNodes - 1 }"
         class="tree-node-droppable">
      <i data-n="after" class="fa fa-arrow-circle-o-right"/>
    </div>
    <!--Dynamic form-->
    <ValidationObserver class="cbpo-s cbpo-wrapper-form auto-fit" ref="dynamicForm" v-slot="{ invalid }">
      <!--Select column-->
      <div class="cbpo-filter-form">
        <ValidationProvider name="nodeData.type" rules="required" class="d-block w-100">
          <div slot-scope="{ errors }">
            <div :class="{'invalid-form': errors[0]}" class="cbpo-s form-group pl-0 cbpo-filter-control-select">
              <legend v-if="basicMode" class="col-form-label">Field</legend>
              <!-- <select
                class="form-control cbpo-custom-select"
                v-model="nodeData.column"
                @change="setDefaultValue($event)">
                <option value="">Select a field</option>
                <option v-for="f in fields" :value="f" :key="`${f.value}_${f.name}`">{{f.displayName || f.name}}</option>
              </select> -->

              <v-select @input="setDefaultValue" class="cbpo-custom-select select w-100 p-0" :options="fields" v-model="nodeData.column" label="displayName" :placeholder="'Select a field'"
                :clearable="false">
                <template #open-indicator="{ attributes }">
                  <i class="fa fa-angle-down" v-bind="attributes"></i>
                </template>
              </v-select>
              <span class="text-error">{{ errors[0] ? 'Please select a column' : '' }}</span>
            </div>
          </div>
        </ValidationProvider>
      </div>
      <!--Select condition-->
      <div class="cbpo-filter-form">
        <ValidationProvider name="nodeData.operator" rules="required" class="d-block w-100">
          <div slot-scope="{ errors }">
            <div :class="{'invalid-form': !!errors[0]}" class="cbpo-s form-group cbpo-filter-control-select">
              <legend v-if="basicMode" class="col-form-label">Operator</legend>
              <v-select @change="changeCondition($event)" :disabled="!nodeData.column" class="cbpo-custom-select select w-100 p-0" :options="getCondition(nodeData.column)" v-model="nodeData.operator" label="label" :reduce="option => option.value" :placeholder="'Select condition'" :clearable="false">
                <template #open-indicator="{ attributes }">
                  <i class="fa fa-angle-down" v-bind="attributes"></i>
                </template>
              </v-select>
              <span class="text-error">{{ errors[0] ? 'Please select an operator' : '' }}</span>
            </div>
          </div>
        </ValidationProvider>
      </div>
      <div class="cbpo-filter-form" style="display: flex; flex-direction: column;">
        <!--Enter Value-->
        <div v-if="getConditionValueInput && !basicMode && !isSelectionType" class="cbpo-filter-form">
          <template v-if="nodeData.column">
            <!--Selected column format is Date | Datetime-->
            <template v-if="format.temporal[nodeData.column.type]">
              <ValidationProvider name="nodeData.value[0]" rules="required" class="d-block w-100">
                <div slot-scope="{ errors }">
                  <div :class="{'invalid-form': !!errors[0]}" class="cbpo-s form-group cbpo-filter-control-input">
                    <template v-if="isOperatorInRange">
                      <cbpo-datetime-picker :key="`_${nodeData.operator}`" class="w-100" :value="dataRange[0]" v-model="dataRange[0]" :config="getDateType"></cbpo-datetime-picker>
                    </template>
                    <template v-else>
                      <cbpo-datetime-picker :key="`_${nodeData.operator}`" class="w-100" :value="nodeData.value" v-model="nodeData.value" :config="getDateType"></cbpo-datetime-picker>
                    </template>
                    <span class="text-error">{{ errors[0] ? isOperatorTimeRange ? 'Please select a time' : 'Please select a date' : '' }}</span>
                  </div>
                </div>
              </ValidationProvider>
            </template>
            <!--Selected column format is Other type-->
            <template v-else>
              <ValidationProvider name="nodeData.value" rules="required" class="d-block w-100">
                <div slot-scope="{ errors }">
                  <div :class="{'invalid-form': errors[0]}" class="cbpo-s form-group cbpo-filter-control-input">
                    <textarea-autosize :min-height="24" rows="1" v-if="isInOperator" class="w-100 cbpo-custom-input input-height" :disabled="!nodeData.column" v-model="parseValue" :important="false"></textarea-autosize>
                    <input v-else-if="isOperatorInRange" placeholder="Input a value" class="form-control cbpo-custom-input" :type="getInputType(nodeData.column ? nodeData.column.type: '')" :disabled="!nodeData.column" name="nodeValue[]" v-model="dataRange[0]">
                    <input v-else placeholder="Input a value" class="form-control cbpo-custom-input" :type="getInputType(nodeData.column ? nodeData.column.type: '')" :disabled="!nodeData.column" name="nodeValue[]" v-model.trim="nodeData.value">
                    <span class="text-error">{{ errors[0] ? 'Please input a value' : '' }}</span>
                  </div>
                </div>
              </ValidationProvider>
            </template>
          </template>
          <template v-else>
            <ValidationProvider name="nodeData.value" rules="required" class="d-block w-100">
              <div slot-scope="{ errors }">
                <div :class="{'invalid-form': errors[0]}" class="cbpo-s form-group cbpo-filter-control-input">
                  <input placeholder="Input a value" class="form-control cbpo-custom-input"  :type="getInputType(nodeData.column ? nodeData.column.type: '')" :disabled="!nodeData.column" v-model.trim="parseValue">
                  <span class="text-error">{{ errors[0] ? 'Please input a value' : '' }}</span>
                </div>
              </div>
            </ValidationProvider>
          </template>
        </div>
        <!-- Selected condition In_Range -->
        <div v-if="isOperatorInRange && !basicMode && !isSelectionType" class="cbpo-filter-form">
          <template v-if="nodeData.column">
            <!--Selected column format is Date | Datetime-->
            <template v-if="format.temporal[nodeData.column.type]">
              <ValidationProvider name="nodeData.value[1]" rules="required" class="d-block w-100">
                <div slot-scope="{ errors }">
                  <div :class="{'invalid-form': !!errors[0]}" class="cbpo-s form-group cbpo-filter-control-input">
                      <cbpo-datetime-picker
                       :key="`_${nodeData.operator}`"
                       :value="dataRange[1]" class="w-100"
                        v-model="dataRange[1]"
                        :config="getDateType"
                      ></cbpo-datetime-picker>
                    <span class="text-error">{{ errors[0] ? isOperatorTimeRange ? 'Please select a time' : 'Please select a date' : '' }}</span>
                  </div>
                </div>
              </ValidationProvider>
            </template>
            <!--Selected column format is Other type-->
            <template v-else>
              <ValidationProvider name="nodeData.value" rules="required" class="d-block w-100">
                <div slot-scope="{ errors }">
                  <div :class="{'invalid-form': errors[0]}" class="cbpo-s form-group cbpo-filter-control-input">
                    <input placeholder="Input a value" class="form-control cbpo-custom-input" :type="getInputType(nodeData.column ? nodeData.column.type: '')" :disabled="!nodeData.column" v-model="dataRange[1]">
                    <span class="text-error">{{ errors[0] ? 'Please input a value' : '' }}</span>
                  </div>
                </div>
              </ValidationProvider>
            </template>
          </template>
          <template v-else>
            <ValidationProvider name="nodeData.value" rules="required" class="d-block w-100">
              <div slot-scope="{ errors }">
                <div :class="{'invalid-form': errors[0]}" class="cbpo-s form-group cbpo-filter-control-input">
                  <input placeholder="Input a value" class="form-control cbpo-custom-input"  :type="getInputType(nodeData.column ? nodeData.column.type: '')" :disabled="!nodeData.column" v-model.trim="parseValue">
                  <span class="text-error">{{ errors[0] ? 'Please input a value' : '' }}</span>
                </div>
              </div>
            </ValidationProvider>
          </template>
        </div>
        <!-- Select options for selection-type field -->
        <div class="cbpo-filter-form" v-if="getConditionValueInput && isSelectionType">
          <!-- for multi dropdown do not use key -->
          <template v-if="isMultiDropDownSelect && isInOperator">
            <ValidationProvider name="nodeData.value" rules="required" class="d-block w-100">
              <div slot-scope="{ errors }">
                <div :class="{'invalid-form': !!errors[0]}" class="cbpo-s form-group cbpo-filter-control-select">
                  <!-- Multi select -->
                  <multi-select-dropdown
                    v-if="isMultiDropDownSelect"
                    v-model="nodeData.value"
                    :lazy="true"
                    :lazyLoading="isLazyLoading"
                    :limit="limit"
                    :header-text="getHeaderText(nodeData.column ? nodeData.column.name : '')"
                    :options="getOptions(nodeData.column ? nodeData.column.name : '')"
                    :colName="nodeData.column ? nodeData.column.name : ''"
                    @updateItems="updateItems($event)"
                    :updateItemsObj="updateItemsObj"
                  />
                  <span class="text-error">{{ errors[0] ? 'Please select a value' : '' }}</span>
                </div>
              </div>
            </ValidationProvider>
          </template>
          <!-- for multi select -->
          <template v-else>
            <ValidationProvider :key="JSON.stringify(nodeData.value)" name="nodeData.value" rules="required" class="d-block w-100">
              <div slot-scope="{ errors }">
                <div :class="{'invalid-form': !!errors[0]}" class="cbpo-s form-group cbpo-filter-control-select">
                  <v-select
                    v-if="isInOperator || isNotInOperator"
                    class="cbpo-custom-select select w-100 p-0"
                    v-model="nodeData.value"
                    label="text"
                    :reduce="option => option.value"
                    :options="isLazyLoading && currentOptions.length ? currentOptions : getOptions(nodeData.column ? nodeData.column.name : '')"
                    @close="onClose"
                    @open="onOpen"
                    @search="(query) => {
                      search = query
                    }"
                    multiple
                    placeholder="Select options"
                  >
                    <template #open-indicator="{ attributes }">
                      <i class="fa fa-angle-down" v-bind="attributes"></i>
                    </template>
                    <template #list-footer>
                      <div v-if="isLazyLoading && (count === null || currentOptions.length < count)" ref="loadMore"></div>
                    </template>
                    <span slot="no-options">
                    {{ nodeData.column.displayName || nodeData.column.name }} does not exist.
                  </span>
                  </v-select>

                  <v-select
                    v-else
                    class="cbpo-custom-select select w-100 p-0"
                    v-model="nodeData.value"
                    label="text"
                    @close="onClose"
                    @open="onOpen"
                    @search="(query) => (search = query)"
                    :reduce="option => option.value"
                    :options="isLazyLoading && currentOptions.length ? currentOptions : getOptions(nodeData.column ? nodeData.column.name : '')"
                    placeholder="Select options"
                  >
                    <template #open-indicator="{ attributes }">
                      <i class="fa fa-angle-down" v-bind="attributes"></i>
                    </template>
                    <template #list-footer>
                      <div ref="loadMore"></div>
                    </template>
                    <span slot="no-options">
                    {{ nodeData.column.displayName || nodeData.column.name }} does not exist.
                  </span>
                  </v-select>
                  <span class="text-error">{{ errors[0] ? 'Please select a value' : '' }}</span>
                </div>
              </div>
            </ValidationProvider>
          </template>
        </div>
      </div>
      <!--Delete Button-->
      <button v-if="!basicMode" @click="deleteNote" class="cbpo-btn btn-danger btn-icon --outline" type="button">
        <i class="fa fa-times"></i>
      </button>
    </ValidationObserver>
  </div>
</template>
<script>

import { SUPPORT_LOGIC } from '@/utils/filterUtils'
import { SUPPORT_COLUMN_TYPES, DataTypeUtil } from '@/services/ds/data/DataTypes'
import { SUPPORT_OPERATORS, logicWithoutValue, getConditionBaseOnDataType, EXPRESSION_SYNTAX } from '@/services/ds/filter/FilterDefinitions'
import { StaticExpression } from 'plat-sdk'
import { ValidationProvider, ValidationObserver } from 'vee-validate'
import { EVENT } from '@/utils/dragAndDropUtil'
import { BUS_EVENT } from '@/services/eventBusType'
import { cloneDeep, isArray, includes, get, isString } from 'lodash'
import debounce from 'lodash/debounce'
import connectorDirective from '@/directives/connectorDirective'
import dropDirective from '@/directives/dropDirective'
import dragDirective from '@/directives/dragDirective'
import CBPO from '@/services/CBPO'
import $ from 'jquery'
import { FORMAT_DATA_TYPES, getDefaultFormatConfigBaseOnFormatType } from '@/services/dataFormatManager'
import { defaultFormatConfig } from '@/components/widgets/elements/table/TableConfig'
import { CONTROL_TYPE } from '@/components/widgets/form/FilterControlConfig'
import datetimePicker from '@/components/datetimePicker/DatetimePicker'
import Vue from 'vue'
import moment from 'moment'
import TextareaAutosize from 'vue-textarea-autosize'
import MultiSelectDropdown from '@/components/share/forms/MultiSelectDropdown'
Vue.use(TextareaAutosize)

export default {
  name: 'DynamicNodeFilter',
  components: {
    'cbpo-datetime-picker': datetimePicker,
    MultiSelectDropdown,
    ValidationProvider,
    ValidationObserver
  },
  props: {
    fields: {
      type: Array,
      default: function() {
        return []
      }
    },
    scope: String,
    basicType: String,
    basicMode: {
      type: Boolean,
      default: false
    },
    operators: {
      type: Array,
      default: function() {
        return []
      }
    },
    nodeConfig: {
      type: Object,
      default: function () {
        return {
          childNodes: 0,
          index: 0
        }
      }
    },
    format: Object,
    node: Object,
    formColumns: {
      type: Array,
      default: () => []
    },
    updateItemsObj: Object
  },
  directives: {
    'cbpo-draggable': dragDirective,
    'cbpo-droppable': dropDirective,
    'cbpo-connector': connectorDirective
  },
  data() {
    return {
      SUPPORT_LOGIC,
      SUPPORT_OPERATORS,
      SUPPORT_COLUMN_TYPES,
      EXPRESSION_SYNTAX,
      EVENT,
      child: {},
      nodeData: this.mappingNodeData(this.node),
      renderComponent: true,
      isShowInputExpression: true,
      dataRange: [],
      CONTROL_TYPE,
      observer: null,
      page: 1,
      search: '',
      currentOptions: [],
      count: null,
      isJustSearched: false
    }
  },
  computed: {
    parseValue: {
      get () {
        return this.nodeData.value
      },
      set (value) {
        if (this.nodeData.value === value) return
        if (value.length > 0 && !isNaN(value)) {
          value = parseFloat(value)
        }
        this.nodeData.value = value
      }
    },
    isOperatorInRange() {
      return this.nodeData.operator === SUPPORT_OPERATORS.in_range.value || this.nodeData.operator === SUPPORT_OPERATORS.time_range.value
    },
    isInOperator() {
      return this.nodeData.operator === SUPPORT_OPERATORS.in.value
    },
    isNotInOperator() {
      return this.nodeData.operator === SUPPORT_OPERATORS.not_in.value
    },
    isOperatorTimeRange() {
      return this.nodeData.operator === SUPPORT_OPERATORS.time_range.value
    },
    isSelectionType() {
      return this.formColumns
        .findIndex(option =>
          option.name === get(this.nodeData, 'column.name', '') &&
          option.type === 'select'
        ) !== -1
    },
    isMultipleSelect() {
      return this.formColumns
        .findIndex(option =>
          option.name === get(this.nodeData, 'column.name') &&
          option.type === 'dropdown-select'
        ) !== -1
    },
    isLazyLoading() {
      return this.formColumns
        .findIndex(option =>
          option.name === get(this.nodeData, 'column.name') &&
          get(option, 'config.lazyLoading', false)
        ) !== -1
    },
    limit() {
      const result = this.formColumns
        .find(option =>
          option.name === get(this.nodeData, 'column.name'))
      return get(result, 'config.limit', 20)
    },
    isMultiDropDownSelect() {
      return this.formColumns
        .findIndex(option =>
          option.name === get(this.nodeData, 'column.name') &&
          option.typeForMultipleOperator === 'dropdown-select'
        ) !== -1
    },
    getNode() {
      return cloneDeep(this.node)
    },
    getCondition: function() {
      return column => {
        const dataType = column ? column.type : ''
        let condition = getConditionBaseOnDataType(dataType)
        if (this.basicMode) {
          condition = condition.filter(e => (!includes(logicWithoutValue, e.value)))
          if (this.basicType === CONTROL_TYPE.SELECT) {
            condition = condition.filter(e => (!includes([SUPPORT_OPERATORS.in_range.value], e.value)))
          }
        }
        return condition
      }
    },
    getOptions() {
      return (columnName) => {
        if (this.formColumns.length) {
          const column = this.formColumns.find((option) => option.name === columnName && option.type === 'select')
          return column ? column.options : []
        }
      }
    },
    getHeaderText() {
      return (columnName) => {
        if (this.formColumns.length) {
          const column = this.formColumns.find((option) => option.name === columnName && option.type === 'select')
          return get(column, 'config.headerText', 'Dropdown Selection')
        }
      }
    },
    getInputType: function() {
      return dataType => {
        switch (dataType) {
          case SUPPORT_COLUMN_TYPES.NUM:
          case SUPPORT_COLUMN_TYPES.NUMBER:
          case SUPPORT_COLUMN_TYPES.FLOAT:
          case SUPPORT_COLUMN_TYPES.LONG:
          case SUPPORT_COLUMN_TYPES.DOUBLE:
          case SUPPORT_COLUMN_TYPES.INT: {
            return 'number'
          }
          default: {
            return 'text'
          }
        }
      }
    },
    getDateType() {
      let formatConfig = this.format.temporal.date
      if (this.nodeData.column && this.format.temporal[this.nodeData.column.type]) {
        formatConfig = this.format.temporal[this.nodeData.column.type]
      }
      if (this.nodeData.operator === SUPPORT_OPERATORS.time_range.value) {
        return {
          formatLabel: 'hh:mm A',
          formatValue: 'HH:mm',
          type: 'time'
        }
      }
      if (isString(formatConfig) && this.nodeData.column.type === 'date') {
        return {
          formatLabel: 'MM/DD/YYYY',
          formatValue: 'YYYY-MM-DD',
          type: 'date'
        }
      }
      if (isString(formatConfig) && this.nodeData.column.type === 'datetime') {
        return {
          formatLabel: 'MM/DD/YYYY hh:mm:ss A',
          formatValue: 'YYYY-MM-DDTHH:mm:ss',
          type: 'datetime'
        }
      }
      return formatConfig
    },
    getConditionValueInput() {
      return !logicWithoutValue.includes(this.nodeData.operator)
    }
  },
  methods: {
    searchOptions(options, search) {
      let regex = new RegExp(`^${search}`, 'i')
      return options.filter(option => {
        let label = option.text
        if (typeof label === 'number') {
          label = label.toString()
        }
        return label.match(regex)
      })
    },
    startEvent(data, el) {
      $(el.target).closest('.tree-group').find()
      let $body = $(el.target).closest('.modal-body')
      let nodesSameLevel = $(el.target).closest('.tree-group').find(`.tree-node-droppable[data-level=${data.level}]`)
      $body
        .find('.tree-node-draggable, .tree-group-draggable')
        .not('.cbpo-btn, .cbpo-filter-form')
        .addClass('hide')
      $body
        .find('.tree-node-droppable, .tree-group-droppable')
        .not('.cbpo-btn, .cbpo-filter-form')
        .addClass('show')
      $body
        .find(`.tree-group-droppable[data-level=${data.index}][data-index=${data.level}]`)
        .not('.cbpo-btn, .cbpo-filter-form')
        .removeClass('show')

      if (!data.index) {
        $(nodesSameLevel.get(0)).removeClass('show')
        $(nodesSameLevel.get(1)).removeClass('show')
      } else {
        $(nodesSameLevel.get(data.index)).removeClass('show')
        $(nodesSameLevel.get(data.index + 1)).removeClass('show')
      }

      CBPO.$bus.$emit(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_CHILD_INTERNAL}`, cloneDeep(this[BUS_EVENT.DRAG_DATA_DIRECTIVE]))
    },
    stopEvent(data, el) {
      let $body = $(el.target).closest('.modal-body')
      $body.find('.tree-node-draggable, .tree-group-draggable').removeClass('hide')
      $body.find('.tree-node-droppable, .tree-group-droppable').removeClass('show')

      // Emit empty data to parent
      CBPO.$bus.$emit(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_CHILD_INTERNAL}`, null)
    },
    mappingNodeData(node) {
      if (node.operator === '==' || node.operator === 'eq') {
        node.operator = '$eq'
      }
      if (node.operator === '!=' || node.operator === 'ne') {
        node.operator = '$ne'
      }
      if (node.operator === '<' || node.operator === 'lt') {
        node.operator = '$lt'
      }
      if (node.operator === '<=' || node.operator === 'lte') {
        node.operator = '$lte'
      }
      if (node.operator === '>' || node.operator === 'gt') {
        node.operator = '$gt'
      }
      if (node.operator === '>=' || node.operator === 'gte') {
        node.operator = '$gte'
      }
      return node
    },
    deleteNote() {
      this.$emit('delete:node', this.node)
    },
    setDefaultValue() {
      this.$refs.dynamicForm.reset()
      const isExisted = false
      const node = this.formColumns.find(column =>
        (column.name === get(this.nodeData, 'column.name', ''))
      )
      if (node) {
        const { type } = this.nodeData.column
        this.nodeData.value = node.value
        this.nodeData.operator = node.operator ? node.operator : '$eq'
        if (['datetime', 'date', 'temporal'].includes(type)) {
          const date = moment(new Date(node.value))
          let value = ''
          if (date.isValid()) {
            value = date.format(this.format.temporal[type])
          } else if (StaticExpression.isValid(node.value)) {
            value = node.value
          }
          this.nodeData.value = value
        }
      } else {
        const operatorList = this.getCondition(this.nodeData.column)
        const hasEqualValue = operatorList.findIndex(op => op.value === '$eq') !== -1
        this.nodeData.value = ''
        this.nodeData.operator = this.nodeData.column && hasEqualValue ? '$eq' : ''
      }
      if (this.isOperatorInRange) {
        this.dataRange = []
      }
      if (this.basicMode) {
        this.nodeData.sort = 'asc'
        this.nodeData.format = null
        if (!isExisted) {
          if (DataTypeUtil.isTemporal(this.nodeData.column.type)) {
            let formatTemporal = getDefaultFormatConfigBaseOnFormatType(FORMAT_DATA_TYPES.TEMPORAL)
            this.nodeData.format = {...defaultFormatConfig, config: {...formatTemporal, ...formatTemporal.date}, type: FORMAT_DATA_TYPES.TEMPORAL}
            this.nodeData.sort = 'desc'
          }
          if (this.basicType === CONTROL_TYPE.RANGE) {
            this.nodeData.operator = SUPPORT_OPERATORS.in_range.value
            this.nodeData.value = []
          }
          if (this.basicType === CONTROL_TYPE.AUTO && includes([SUPPORT_OPERATORS.in_range.value, SUPPORT_OPERATORS.in.value], this.nodeData.operator)) {
            this.nodeData.value = []
          }
        }
      }
    },
    changeCondition(e) {
      this.$refs.dynamicForm.reset()
      let isNotArray = false
      if (this.basicMode && this.basicType === CONTROL_TYPE.AUTO && includes([SUPPORT_OPERATORS.in_range.value, SUPPORT_OPERATORS.in.value], this.nodeData.operator)) {
        this.nodeData.value = []
        isNotArray = true
      }
      if (this.basicMode && this.basicType === CONTROL_TYPE.DATE_RANGE && SUPPORT_OPERATORS.in_range.value === this.nodeData.operator) {
        this.nodeData.value = []
        isNotArray = true
      }
      if (!isNotArray) {
        this.nodeData.value = ''
      }
      if (this.isSelectionType) {
        if (includes(SUPPORT_OPERATORS.in.value, this.nodeData.operator)) {
          this.nodeData.value = this.nodeData.value ? [this.nodeData.value] : []
        } else {
          if (isArray(this.nodeData.value)) {
            this.nodeData.value = this.nodeData.value.length ? this.nodeData.value[0] : ''
          }
        }
      }
    },
    setValueNodeData(data) {
      this.isShowInputExpression = false
      this.renderComponent = false
      if (this.isOperatorInRange) {
        this.dataRange[data.index] = data.value
        this.nodeData.value = this.dataRange
      } else {
        this.nodeData.value = data.value
      }
      this.$nextTick(() => {
        this.isShowInputExpression = true
        this.renderComponent = true
      })
    },
    showDropdown(nameDropdown) {
      nameDropdown === 'dropdownExpFirst' ? this.$refs.dropdownExpFirst.showDropdown() : this.$refs.dropdownExpSecond.showDropdown()
    },
    buildNodeData() {
      if (this.isSelectionType || this.isMultiDropDownSelect) {
        this.nodeData.value = this.nodeData.value.filter(val => val !== null)
      } else if (isArray(this.nodeData.value)) {
        this.nodeData.value = this.nodeData.value.join(',')
      }
    },
    updateItems(data) {
      this.$emit('updateItems', data)
    },
    async infiniteScroll([{ isIntersecting, target }]) {
      if (isIntersecting) {
        const ul = target.offsetParent
        const scrollTop = target.offsetParent.scrollTop
        debounce(() => {
          if (!this.isJustSearched && (this.currentOptions.length < this.count || this.count === null)) {
            this.page++
            this.updateItems({search: this.search, columnName: this.nodeData.column ? this.nodeData.column.name : '', page: this.page, limit: this.limit})
          }
        }, 500)()
        await this.$nextTick()
        ul.scrollTop = scrollTop
      }
    },
    onClose() {
      if (this.isLazyLoading) this.observer.disconnect()
    },
    async onOpen() {
      if (this.isLazyLoading) {
        await this.$nextTick()
        this.searchChange()
        this.observer.observe(this.$refs.loadMore)
      }
    },
    async searchChange() {
      this.isJustSearched = true
      this.page = 1
      await debounce(() => {
        if (!this.isLazyLoading) return
        this.updateItems({search: this.search, columnName: this.nodeData.column ? this.nodeData.column.name : '', page: 1, limit: this.limit})
      }, 300)()
      this.isJustSearched = false
    },
    handleUpdateItems (data) {
      this.page = data[this.nodeData.column.name].page
      this.count = data[this.nodeData.column.name].count
      if (data[this.nodeData.column.name].page !== 1) {
        this.currentOptions[data[this.nodeData.column.name]] = this.currentOptions.push(...data[this.nodeData.column.name].items)
      } else this.currentOptions = cloneDeep(data[this.nodeData.column.name].items)
    }
  },
  created() {
    CBPO.$bus.$on(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_CHILD_INTERNAL}`, (dragData) => {
      this[BUS_EVENT.DRAG_DATA_DIRECTIVE] = dragData
    })
    if (isArray(this.nodeData.value) && this.isOperatorInRange) {
      this.dataRange = this.nodeData.value
    }
    if (this.isInOperator) {
      this.buildNodeData()
    }
  },
  mounted() {
    this.observer = new IntersectionObserver(this.infiniteScroll)
  },
  watch: {
    nodeData(val, oldVal) {
      this.$emit('update:node', val)
    },
    node(val) {
      this.nodeData = val
      if (this.isInOperator) {
        this.buildNodeData()
      }
    },
    dataRange(val) {
      this.nodeData.value = val
    },
    updateItemsObj: {
      deep: true,
      immediate: true,
      handler(val) {
        if (val && Object.keys(val).length && this.nodeData.column && this.nodeData.column.name) this.handleUpdateItems(val)
      }
    },
    search: {
      deep: true,
      immediate: true,
      handler(val) {
        this.searchChange(val)
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "DynamicNodeFilter";
</style>
