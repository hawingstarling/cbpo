<template>
  <div class="w-100">
    <b-form-group label="Enable">
      <div class="row">
        <div class="col-4">
          <b-form-checkbox switch v-model="configData.widget.title.enabled">Title</b-form-checkbox>
        </div>
        <div class="col-4">
          <b-form-checkbox switch v-model="configData.menu.enabled">Menu</b-form-checkbox>
        </div>
        <div class="col-4">
          <b-form-checkbox v-if="isShowQueryBuilder" switch v-model="configData.filter.builder.enabled">Query Builder
          </b-form-checkbox>
        </div>
        <div class="col-4" v-if="isShowColumnManager">
          <b-form-checkbox switch v-model="configData.columnManager.enabled">Column Manager
          </b-form-checkbox>
        </div>
        <div class="col-4">
          <b-form-checkbox switch v-model="configData.autoHeight">Auto Height</b-form-checkbox>
        </div>
      </div>
    </b-form-group>

    <!--Widget Setting-->
    <b-card v-if="configData.widget.title.enabled" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.widgetTitleCollapse>Widget Title</span>
      </b-card-header>
      <b-collapse id="widgetTitleCollapse">
        <b-card-body>
          <b-form-group
            id="widgetTitle"
            label="Title"
            label-for="widgetTitle">
            <b-form-input type="text" v-model="configData.widget.title.text"
                          @input="changeTitle($event)"></b-form-input>
          </b-form-group>
        </b-card-body>
      </b-collapse>
    </b-card>

    <!--Widget Styles-->
    <WidgetStyles :configData="configData.widget.style" />
    <!--end Widget Styles-->

    <!--Filter Setting-->
    <b-card no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.widgetBasicFilterCollapse>Basic Filter</span>
      </b-card-header>
      <b-collapse id="widgetBasicFilterCollapse">
        <b-card-body>
          <div :key="controlIndex" class="mb-1"
               v-for="(control, controlIndex) of configData.filter.form.config.controls">
            <b-card no-body class="mb-1">
              <b-card-header header-tag="header" class="p-1" role="tab">
                <div class="d-flex ml-0 control-box justify-content-center">
                  <span v-b-toggle="`control_${controlIndex}`">{{ getFilterElementTitle(control, controlIndex) }}</span>
                  <button
                    @click="modalTrigger({type: `modal_filter_element_${controlIndex}`, isShow: true})"
                    class="cbpo-btn btn-danger btn-icon circle width-height-18">
                    <i class="fa fa-times text-white"></i>
                  </button>
                  <!--filter element remove modal-->
                  <b-modal dialog-class="cbpo-custom-modal" title="Please confirm"
                           centered
                           :ref="`modal_filter_element_${controlIndex}`"
                           :id="`modal_filter_element_${controlIndex}`">
                    Remove this filter element from the basic filter?
                    <template v-slot:modal-footer>
                      <button class="cbpo-btn btn-warning" @click="deleteFilter(controlIndex)">
                        <i class="fa fa-check mr-1"></i> Yes
                      </button>
                      <button class="cbpo-btn"
                              @click="modalTrigger({type: `modal_filter_element_${controlIndex}`, isShow: false})">
                        <i class="fa fa-times mr-1"></i> No
                      </button>
                    </template>
                  </b-modal>
                </div>
              </b-card-header>
              <b-collapse :id="`control_${controlIndex}`">
                <b-card-body>
                  <div class="row">
                    <div class="col-8">
                      <b-form-group>
                        <DynamicNodeFilter :format="configData.filter.builder.config.format"
                                           :fields="fields"
                                           :basicMode="true"
                                           :basicType="control.type"
                                           :node="control.config.common"
                                           :operators="operators" />
                      </b-form-group>
                    </div>
                    <div class="col-4 margin-top-15">
                      <b-form-group label="Label">
                        <b-form-input :placeholder="getPlaceholderLabel(control)" type="text"
                                      v-model="control.config.label.text"></b-form-input>
                      </b-form-group>
                    </div>
                  </div>
                  <div class="row">
                    <div class="col-4">
                      <b-form-group label="Input type">
                        <b-form-select
                          size="sm"
                          class="mb-2"
                          v-model="control.type"
                          :options="getOptionsBasicFilterType(control.config.common)"
                          @change="changeFilterType(controlIndex)"
                        >
                        </b-form-select>
                      </b-form-group>
                    </div>
                    <div class="col-4">
                      <b-form-group label="Data Source ID"
                                    v-if="isBasicFilterType([CONTROL_TYPE.SELECT], control.type)">
                        <b-form-input type="text" v-model="control.config.dataSource"></b-form-input>
                      </b-form-group>
                    </div>
                  </div>
                  <b-card no-body class="mb-1" v-if="isBasicFilterType([CONTROL_TYPE.SELECT], control.type)">
                    <b-card-header header-tag="header" class="p-1" role="tab">
                      <span v-b-toggle="`control_${controlIndex}_options`">Options</span>
                    </b-card-header>
                    <b-collapse :id="`control_${controlIndex}_options`">
                      <b-card-body v-if="control.config.selection">
                        <div class="row">
                          <div class="col-6 margin-auto">
                            <b-form-group>
                              <b-form-checkbox
                                @change="changeValueSelection($event, controlIndex)"
                                switch
                                v-model="control.config.selection.empty.enabled">
                                Allow empty selection
                              </b-form-checkbox>
                            </b-form-group>
                          </div>
                          <div class="col-6">
                            <b-form-group v-if="control.config.selection.empty.enabled" label="Empty selection label">
                              <b-form-input type="text" v-model="control.config.selection.empty.label"></b-form-input>
                            </b-form-group>
                          </div>
                        </div>
                        <template v-if="!control.config.loadedDataSource">
                          <hr />
                          <b-form-group>
                            <div class="d-flex">
                              <b-form-input ref="selectionLabel" placeholder="Label" class="w-100"
                                            type="text"></b-form-input>
                              <b-form-input ref="selectionValue" placeholder="Value" class="w-100 ml-1"
                                            type="text"></b-form-input>
                              <button @click="addOption(controlIndex)"
                                      class="cbpo-btn btn-success btn-icon circle text-white ml-1 width-height-18">
                                <i class="fa fa-plus"></i>
                              </button>
                            </div>
                          </b-form-group>
                          <!--Only available for select type-->
                          <div v-if="control.config.selection && control.config.selection.options.length" class="row">
                            <div class="col-12">
                              <table class="tb-table table table-bordered bv-docs-tablehead-default">
                                <thead class="thead-default">
                                <tr>
                                  <th>Label</th>
                                  <th>Value</th>
                                  <th style="width: 50px"></th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr :key="`${item.value}_${optionIndex}`"
                                    v-for="(item, optionIndex) of control.config.selection.options">
                                  <td>{{ item.label }}</td>
                                  <td>{{ item.value }}</td>
                                  <td>
                                    <button @click="deleteOption(controlIndex, optionIndex)"
                                            class="ml-auto cbpo-btn btn-icon circle btn-danger icon-only width-height-18">
                                      <i class="fa fa-trash"></i>
                                    </button>
                                  </td>
                                </tr>
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </template>
                      </b-card-body>
                    </b-collapse>
                  </b-card>
                  <b-card no-body class="mb-1" v-if="isBasicFilterType([CONTROL_TYPE.DATE_RANGE, CONTROL_TYPE.RANGE], control.type)">
                    <b-card-header header-tag="header" class="p-1" role="tab">
                      <span v-b-toggle="`control_${controlIndex}_options`">Options</span>
                    </b-card-header>
                    <b-collapse :id="`control_${controlIndex}_options`">
                      <b-card-body>
                        <div class="row">
                          <div class="col-6 margin-auto" v-if="isBasicFilterType([CONTROL_TYPE.DATE_RANGE], control.type)">
                            <b-form-group v-if="control.config.selection">
                              <b-form-checkbox
                                @change="changeDefaultSelection($event, controlIndex)"
                                switch
                                v-model="control.config.selection.empty.isDefaultOption">
                                Using default options
                              </b-form-checkbox>
                              <b-form-checkbox
                                switch
                                v-model="control.config.range.visible">
                                Range Visible
                              </b-form-checkbox>
                            </b-form-group>
                          </div>
                          <div class="col-6">
                            <b-form-group label="Empty selection label">
                              <b-form-input type="text" v-model="control.config.label.text"></b-form-input>
                            </b-form-group>
                          </div>
                        </div>
                        <div class="row" v-if="control.config.range">
                          <div class="col-12">
                            <b-form-group label="Format type">
                              <b-form-select v-model="control.config.range.type" @change="changeFormatTypeInDateRangeSelected(control)">
                                <option v-if="isDisabledOptionDateTime(control, 'time_range')" value="time">Time</option>
                                <option v-if="isDisabledOptionDateTime(control, 'in_range')" value="date">Date</option>
                                <option v-if="isDisabledOptionDateTime(control, 'in_range')" value="datetime">Date time</option>
                              </b-form-select>
                            </b-form-group>
                          </div>
                          <div class="col-6">
                            <b-form-group label="Format label">
                              <b-form-input type="text" v-model="control.config.range.formatLabel"></b-form-input>
                            </b-form-group>
                          </div>
                          <div class="col-6">
                            <b-form-group label="Format value">
                              <b-form-input type="text" v-model="control.config.range.formatValue"></b-form-input>
                            </b-form-group>
                          </div>
                        </div>
                        <template v-if="!control.config.loadedDataSource && isBasicFilterType([CONTROL_TYPE.DATE_RANGE], control.type)">
                          <hr />
                          <b-form-group>
                            <div class="d-flex">
                              <b-form-input ref="selectionLabel" placeholder="Label" class="w-100"
                                            type="text"></b-form-input>
                              <b-form-input ref="selectionFrom" placeholder="From" class="w-100 ml-1"
                                            type="text"></b-form-input>
                              <b-form-input ref="selectionTo" placeholder="To" class="w-100 ml-1"
                                            type="text"></b-form-input>
                              <button @click="addOptionDateRange(controlIndex)"
                                      class="cbpo-btn btn-success btn-icon circle text-white ml-1 width-height-18">
                                <i class="fa fa-plus"></i>
                              </button>
                            </div>
                            <div v-if="isInvalidFromAndToDate" class="text-error pl-2">Please fill in the fields to create the options.</div>
                          </b-form-group>
                          <!--Only available for select type-->
                          <div v-if="control.config.selection && control.config.selection.options.length" class="w-100">
                            <div class="w-100" style="overflow: scroll">
                              <table class="tb-table table table-bordered bv-docs-tablehead-default">
                                <thead class="thead-default">
                                <tr>
                                  <th>Label</th>
                                  <th>From</th>
                                  <th>To</th>
                                  <th style="width: 25px">Is default</th>
                                  <th style="width: 50px"></th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr :key="`${item.value}_${optionIndex}`"
                                    v-for="(item, optionIndex) of control.config.selection.options">
                                  <td>{{ item.label }}</td>
                                  <td>{{ item.value[0] }}</td>
                                  <td>{{ item.value[1] }}</td>
                                  <td class="text-center">
                                    <input type="radio" :name="`default_${controlIndex}_select`"
                                           :checked="item.isDefault" @click="defaultChange(controlIndex, optionIndex)">
                                  </td>
                                  <td>
                                    <button @click="deleteOptionDateRange(controlIndex, optionIndex)"
                                            class="ml-auto cbpo-btn btn-icon circle btn-danger icon-only width-height-18">
                                      <i class="fa fa-trash"></i>
                                    </button>
                                  </td>
                                </tr>
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </template>
                      </b-card-body>
                    </b-collapse>
                  </b-card>
                  <b-card no-body class="mb-1" v-if="isBasicFilterType([CONTROL_TYPE.SELECT], control.type)">
                    <b-card-header header-tag="header" class="p-1" role="tab">
                      <span v-b-toggle="`control_${controlIndex}_format`">Format</span>
                    </b-card-header>
                    <b-collapse :id="`control_${controlIndex}_format`">
                      <b-card-body v-if="control.config.selection">
                        <format-config-builder :key="control.config.common.column.name"
                                               :format-config.sync="control.config.selection.format" />
                      </b-card-body>
                    </b-collapse>
                  </b-card>
                  <b-card no-body class="mb-1" v-if="isBasicFilterType([CONTROL_TYPE.SELECT], control.type)">
                    <b-card-header header-tag="header" class="p-1" role="tab">
                      <span v-b-toggle="`control_${controlIndex}_sorting`">Sorting</span>
                    </b-card-header>
                    <b-collapse :id="`control_${controlIndex}_sorting`">
                      <b-card-body v-if="control.config.selection">
                        <b-form-group label="Sort">
                          <b-form-select size="sm" class="mb-6" v-model="control.config.selection.sort">
                            <option value="asc">Asc</option>
                            <option value="desc">Desc</option>
                          </b-form-select>
                        </b-form-group>
                      </b-card-body>
                    </b-collapse>
                  </b-card>
                </b-card-body>
              </b-collapse>
            </b-card>
          </div>
          <div class="control-box mb-2 d-flex justify-content-end">
            <button
              @click="createNewFilter()"
              class="cbpo-btn btn-success">
              <i class="fa fa-plus"></i> Add
            </button>
          </div>
        </b-card-body>
      </b-collapse>
    </b-card>

  </div>
</template>
<script>
import cloneDeep from 'lodash/cloneDeep'
import uniqBy from 'lodash/uniqBy'
import find from 'lodash/find'
import isEmpty from 'lodash/isEmpty'
import startCase from 'lodash/startCase'
import toLower from 'lodash/toLower'
import pick from 'lodash/pick'
import includes from 'lodash/includes'
import get from 'lodash/get'
import DynamicNodeFilter from '@/components/widgets/builder/DynamicNodeFilter'
import { SUPPORT_OPERATORS, OPTION_DEFAULT_SELECT_RANGE } from '@/services/ds/filter/FilterDefinitions'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import {
  CONTROL_TYPE,
  defaultInputControlConfig,
  makeDefaultInputControlConfig,
  makeDefaultInRangeControlConfig,
  makeDefaultSelectControlConfig,
  makeDefaultInRangeSelectControlConfig
} from '@/components/widgets/form/FilterControlConfig'
import { generateIdIfNotExist } from '@/utils/configUtil'
import CBPO from '@/services/CBPO'
import FormatConfigBuilder from '@/components/formatBuilder/FormatConfigBuilder'
import WidgetStyles from '@/components/widgets/setting/WidgetStyles'
import { StaticExpression } from 'plat-sdk'

export default {
  name: 'WidgetSettings',
  components: {
    DynamicNodeFilter,
    FormatConfigBuilder,
    WidgetStyles
  },
  data() {
    return {
      resetKey: 0,
      configData: null,
      operators: [],
      fields: [],
      CONTROL_TYPE,
      isInvalidFromAndToDate: false
    }
  },
  methods: {
    setDefaultValueInputTypeRange() {
      this.configData.filter.form.config.controls[0].type = CONTROL_TYPE.RANGE
    },
    getConfig() {
      // mapping grouping columns before apply
      if (this.configData.filter.form.config.controls.length) {
        this.configData.filter.form.config.controls = this.configData.filter.form.config.controls.filter(c => {
          let { config: { common } } = c
          return !isEmpty(common) && !isEmpty(common.column) && !isEmpty(common.operator)
        })
      }
      return cloneDeep(this.configData)
    },
    createNewFilter() {
      let defaultConfig = {
        type: CONTROL_TYPE.AUTO,
        config: { ...pick(cloneDeep(defaultInputControlConfig), ['common', 'label']) }
      }
      generateIdIfNotExist(defaultConfig)
      this.configData.filter.form.config.controls.push(defaultConfig)
    },
    deleteFilter(index) {
      this.configData.filter.form.config.controls.splice(index, 1)
      this.modalTrigger({type: `modal_filter_element_${index}`, isShow: false})
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
      this.configData.elements
        .forEach(el => {
          if (el.type === ELEMENT.CROSSTAB_TABLE) {
            configColumns.push(uniqBy([...el.config.xColumns, ...el.config.yColumns, ...el.config.tColumns], 'name'))
          } else {
            configColumns.push(el.config.columns)
          }
          dataSources.push(new Promise((resolve) => resolve(this.getColumns(el.config.dataSource))))
        })
      let columns = await this.getAllColumns(dataSources)
      if (this.configData.elements[0].type === ELEMENT.GLOBAL_FILTER) {
        configColumns = cloneDeep(columns)
      }
      configColumns = configColumns.map((cols, i) => {
        return cols && cols.map(column => {
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
      // update columns from channelManager (base filter)
      this.updatedColumnsState.forEach(col => this.updateColumn(col))
    },
    buildOperators() {
      this.operators = uniqBy(Object.keys(SUPPORT_OPERATORS).map(key => SUPPORT_OPERATORS[key]), 'label')
    },
    defaultChange(controlIndex, optionIndex) {
      const currentValue = this.configData.filter.form.config.controls[controlIndex].config.selection.options[optionIndex].isDefault
      this.configData.filter.form.config.controls[controlIndex].config.selection.options.forEach(option => {
        option.isDefault = false
      })
      this.configData.filter.form.config.controls[controlIndex].config.selection.options[optionIndex].isDefault = !currentValue
    },
    addOption(controlIndex) {
      let value = this.$refs.selectionValue[controlIndex].$refs.input.value
      let label = this.$refs.selectionLabel[controlIndex].$refs.input.value
      if (value && label) {
        // this local won't be clear when stack with datasource
        this.configData.filter.form.config.controls[controlIndex].config.selection.options.push({
          label,
          value,
          local: true
        })
        this.$refs.selectionValue[controlIndex].$refs.input.value = ''
        this.$refs.selectionLabel[controlIndex].$refs.input.value = ''
      }
    },
    addOptionDateRange(controlIndex) {
      let from = this.$refs.selectionFrom[controlIndex].$refs.input.value
      let to = this.$refs.selectionTo[controlIndex].$refs.input.value
      let label = this.$refs.selectionLabel[controlIndex].$refs.input.value
      if (StaticExpression.isValid(from) && StaticExpression.isValid(to) && label) {
        // this local won't be clear when stack with datasource
        this.isInvalidFromAndToDate = false
        let value = [from, to]
        this.configData.filter.form.config.controls[controlIndex].config.selection.options.push({
          label,
          isDefault: false,
          value,
          local: true
        })
        this.$refs.selectionFrom[controlIndex].$refs.input.value = ''
        this.$refs.selectionTo[controlIndex].$refs.input.value = ''
        this.$refs.selectionLabel[controlIndex].$refs.input.value = ''
        this.configData.filter.form.config.controls[controlIndex].config.selection.empty.isDefaultOption = false
      } else {
        this.isInvalidFromAndToDate = true
      }
    },
    deleteOption(controlIndex, optionIndex) {
      this.configData.filter.form.config.controls[controlIndex].config.selection.options.splice(optionIndex, 1)
    },
    deleteOptionDateRange(controlIndex, optionIndex) {
      this.configData.filter.form.config.controls[controlIndex].config.selection.empty.isDefaultOption = false
      this.configData.filter.form.config.controls[controlIndex].config.selection.options.splice(optionIndex, 1)
    },
    changeTitle(data) {
      if (data) this.configData.widget.title.edited = true
    },
    modalTrigger({ type, isShow }) {
      if (isShow) {
        // show modal
        this.$bvModal.show(type)
      } else {
        // hide modal
        this.$bvModal.hide(type)
      }
    },
    changeValueSelection(val, controlIndex) {
      let { options } = this.configData.filter.form.config.controls[controlIndex].config.selection
      this.configData.filter.form.config.controls[controlIndex].config.common.value = val ? '' : (options[0] && options[0].value)
    },
    changeDefaultSelection(val, controlIndex) {
      this.configData.filter.form.config.controls[controlIndex].config.selection.options = val ? OPTION_DEFAULT_SELECT_RANGE : []
    },
    changeFilterType(index) {
      let control = this.configData.filter.form.config.controls[index]
      switch (control.type) {
        case CONTROL_TYPE.INPUT: {
          control.config = makeDefaultInputControlConfig(control.config)
          break
        }
        case CONTROL_TYPE.SELECT: {
          control.config = makeDefaultSelectControlConfig(control.config)
          control.config.dataSource = this.configData.elements[0].config.dataSource
          break
        }
        case CONTROL_TYPE.RANGE: {
          control.config = makeDefaultInRangeControlConfig(control.config)
          break
        }
        case CONTROL_TYPE.DATE_RANGE: {
          console.log(control)
          control.config = makeDefaultInRangeSelectControlConfig(control.config)
          break
        }
        default: {
          control.config = { ...pick(makeDefaultInputControlConfig(control.config), ['common', 'label']) }
        }
      }
    },
    changeFormatTypeInDateRangeSelected(control) {
      switch (control.config.range.type) {
        case 'time':
          control.config.common.value = []
          control.config.range = {
            type: 'time',
            formatLabel: 'hh:mm A',
            formatValue: 'HH:mm'
          }
          break
        case 'datetime':
          control.config.range.formatLabel = 'MM/DD/YYYY hh:mm A'
          control.config.range.formatValue = 'YYYY-MM-DDTHH:mm:ss'
          break
        case 'date':
          control.config.range.formatLabel = 'MM/DD/YYYY'
          control.config.range.formatValue = 'YYYY-MM-DD'
          break
      }
    },
    // update column from channelManager
    updateColumn(data) {
      if (data) {
        const findedCol = this.fields.find(col => col.name === data.name)
        if (findedCol) findedCol.displayName = data.displayName || findedCol.displayName
      }
    }
  },
  props: {
    config: Object
  },
  created() {
    this.buildOperators()
    this.buildFields()
  },
  computed: {
    isShowQueryBuilder() {
      switch (this.configData.elements[0].type) {
        case ELEMENT.GLOBAL_FILTER:
          return false
        default:
          return true
      }
    },
    isShowColumnManager() {
      switch (this.configData.elements[0].type) {
        case ELEMENT.TABLE:
          return true
        default:
          return false
      }
    },
    isBasicFilterType() {
      return (types, controlType) => {
        return types.includes(controlType)
      }
    },
    getOptionsBasicFilterType() {
      return (common) => {
        let { operator } = common
        let filterType
        switch (operator) {
          case SUPPORT_OPERATORS.in.value:
            filterType = Object.keys(CONTROL_TYPE).filter(e => !includes(['SELECT', 'RANGE'], e))
            break
          case SUPPORT_OPERATORS.time_range.value:
            filterType = Object.keys(CONTROL_TYPE).filter(e => !includes(['SELECT', 'DATE_RANGE', 'AUTO', 'INPUT'], e))
            this.setDefaultValueInputTypeRange()
            break
          default:
            filterType = Object.keys(CONTROL_TYPE)
            break
        }
        return filterType.map(name => ({ text: startCase(toLower(name)), value: CONTROL_TYPE[name] }))
      }
    },
    getPlaceholderLabel() {
      return (control) => {
        return (control.config.common && control.config.common.column) ? control.config.common.column.displayName || control.config.common.column.name : ''
      }
    },
    getFilterElementTitle() {
      return (control, i) => {
        return get(control, 'config.common.column.name', null) ? `${control.config.label.text || control.config.common.column.displayName || control.config.common.column.name} ${SUPPORT_OPERATORS[control.config.common.operator] ? SUPPORT_OPERATORS[control.config.common.operator].label : control.config.common.operator}` : `Filter Element ${i + 1}`
      }
    },
    updatedColumnsState() {
      return CBPO.channelManager().getChannel().getColumnSvc().getColumns()
    },
    isDisabledOptionDateTime() {
      return (control, typeDate) => {
        return control.config.common.operator === typeDate
      }
    }
  },
  watch: {
    config: {
      deep: true,
      immediate: true,
      handler(val) {
        this.configData = cloneDeep(val)
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
.cbpo-list {
  margin-top: 10px;
  max-height: 200px;
  overflow: auto;
  padding: 0.5rem 0;
}

.card-padding {
  padding: 0.5rem;
}

.option-label {
  line-height: 30px;
}

.card-header span {
  margin: auto;
}

.justify-content-end {
  justify-content: flex-end;
}

.margin-top-15 {
  margin-top: 15px;
}

.margin-auto {
  margin: auto;
}

.cbpo-btn.btn-icon.circle.width-height-18 {
  width: 18px;
  min-width: 18px;
  height: 18px;
}
</style>
