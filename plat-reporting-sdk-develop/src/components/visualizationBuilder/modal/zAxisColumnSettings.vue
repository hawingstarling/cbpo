<template>
  <div v-if="columnData" class="w-100">
    <div class="row">
      <div v-if="selectedType.elementType === ELEMENT.CROSSTAB_TABLE" class="col-md-6 col-12">
        <b-form-group label="Sortable">
          <b-form-checkbox switch v-model="columnData.sort.enabled"/>
        </b-form-group>
      </div>
      <div class="col-md-6 col-12">
        <b-form-group v-if="elementData && elementData.type === ELEMENT.TABLE" label="Visible">
          <b-form-checkbox switch v-model="columnData.visible"/>
        </b-form-group>
      </div>
      <div v-if="elementData && elementData.type === ELEMENT.TABLE" class="col-md-6 col-12">
        <b-form-group label="Sortable">
          <b-form-checkbox switch v-model="columnData.sort.enabled"/>
        </b-form-group>
      </div>
      <template v-if="selectedType.elementType === ELEMENT.CROSSTAB_TABLE">
        <div v-if="columnData.sort.enabled" class="col-12">
          <b-form-group label="Direction">
            <b-form-select switch :value="sortModel(columnData)" @change="addSorting($event, columnData)">
              <option :value="null">None</option>
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </b-form-select>
          </b-form-group>
        </div>
      </template>
    </div>
    <b-form-group v-if="elementData && elementData.type !== ELEMENT.CROSSTAB_TABLE" label="Grouping">
      <b-form-checkbox switch :checked="isGrouping" @change="groupData($event)"/>
    </b-form-group>
    <b-form-group label="Display Name">
      <b-form-input v-model="columnData.displayName"/>
    </b-form-group>
    <b-form-group>
      <BinningConfig v-if="binningAccept"
                     :config.sync="binObj"
                     :columnType="columnType"
      />
    </b-form-group>
    <b-form-group label="Format">
      <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.formatTypeCollapse>Options</span>
        </b-card-header>
        <!--Format Type Config-->
        <b-collapse id="formatTypeCollapse">
          <b-card-body class="cbpo-form-control">
            <format-config-builder
              v-if="columnData"
              :format-config.sync="getFormatConfig"/>
          </b-card-body>
        </b-collapse>
      </b-card>
    </b-form-group>
  </div>
</template>
<script>
import AxisMixins from '@/components/visualizationBuilder/AxisColumnMixins'
import FormatConfigBuilder from '@/components/formatBuilder/FormatConfigBuilder'
import BinningConfig from '@/components/widgets/elements/table/grouping/BinningConfig'
import isEmpty from 'lodash/isEmpty'
import { ELEMENT } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { GROUPING_TYPE, handleGrouping, handleUngrouping } from '@/utils/visualizationUtil'
import { createBinColumnAlias } from '@/utils/binUtils'

export default {
  name: 'ZAxisColumnSettings',
  props: {
    fields: Array,
    column: Object,
    element: Object
  },
  components: {
    'format-config-builder': FormatConfigBuilder,
    BinningConfig
  },
  data() {
    return {
      isGrouping: false,
      elementData: null,
      ELEMENT: ELEMENT
    }
  },
  computed: {
    sortModel() {
      return column => {
        let isBin = this.binObj && this.binObj.binningType
        let name = createBinColumnAlias(this.column.name, this.setAliasBinnedCol)
        let sortColumn = this.elementData.config.sorting.find(col => (isBin ? name : column.name) === col.column)
        return sortColumn ? sortColumn.direction : null
      }
    }
  },
  methods: {
    addSorting(e, column) {
      let isBin = this.binObj && this.binObj.binningType
      let name = isBin ? createBinColumnAlias(this.column.name, this.setAliasBinnedCol) : column.name
      this.elementData.config.sorting = this.elementData.config.sorting.filter(col => col.column !== name)
      if (e) {
        this.elementData.config.sorting = [...this.elementData.config.sorting, {column: name, direction: e}]
      }
    },
    bindingGrouping() {
      if (this.elementData.type === ELEMENT.CROSSTAB_TABLE) return true
      this.isGrouping = !isEmpty(this.elementData.config.grouping.columns)
    },
    groupData(result) {
      this.isGrouping = result
      let seriesItem = this.selectedType.elementType === ELEMENT.CHART ? this.series : null
      let column = this.columnData
      if (result) {
        handleGrouping(this.elementData, seriesItem, column, GROUPING_TYPE.COLUMNS)
      } else {
        handleUngrouping(this.elementData, seriesItem, column, GROUPING_TYPE.COLUMNS)
      }
    }
  },
  mixins: [AxisMixins],
  created() {
    this.bindingGrouping()
  }
}
</script>
<style scoped lang="scss">
  .text-transform {
    text-transform: capitalize;
    display: inline!important;
  }
</style>
