<template>
  <div class="cbpo-drilldown-path-builder">
    <!-- add button -->
    <template v-if="columns.length > 0">
      <button v-if="limit === -1 || (limit !== -1 && settingsState.length < limit)" @click="addNewItem" class="cbpo-btn btn-success">
        <i class="fa fa-plus"></i>
        Add path
      </button>
      <!-- end add button -->

      <!-- list settings -->
      <div class="cbpo-list-settings mt-3">
        <template v-for="(item, index) of settingsState">
          <b-card :key="index" class="cbpo-setting-item" :class="{'mb-0': index === settingsState.length - 1, 'mb-3': index !== settingsState.length - 1}" >
            <!-- select column -->
            <div class="d-flex mb-3 align-items-center justify-content-between">
              <label class="mb-0">Select a column</label>
              <button @click="clearItem(index)" class="cbpo-btn --small btn-danger btn-icon">
                <i class="fa fa-trash"></i>
              </button>
            </div>
            <v-select
              class="cbpo-custom-select w-100"
              v-model="item.column"
              label="displayName"
              :reduce="column => column.name"
              :options="columns"
              :clearable="false"
              :placeholder="'Please select a column...'"
            >
              <template #open-indicator="{ attributes }">
                <i class="fa fa-angle-down" v-bind="attributes"></i>
              </template>
            </v-select>
            <!-- select column -->

            <!-- bin config -->
            <template v-if="isBinningApplicable(item)">
              <cbpo-binning-options
                :config.sync="item.binConfig"
                :columnType="getColumnType(item)"
              ></cbpo-binning-options>
            </template>
            <!-- end bin config -->
          </b-card>
        </template>
      </div>
    </template>
    <!-- end list settings -->
  </div>
</template>
<script>
import { DEFAULT_STATE_BIN } from '@/components/widgets/elements/table/grouping/ColumnSettingsConfig'
import cloneDeep from 'lodash/cloneDeep'
import startCase from 'lodash/startCase'
import BinningConfig from '@/components/widgets/elements/table/grouping/BinningConfig'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import { FORMAT_DATA_TYPES } from '@/services/dataFormatManager'
import CBPO from '@/services/CBPO'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'

export default {
  data() {
    return {
      columns: [],
      settingsState: []
    }
  },
  mixins: [WidgetLoaderMixins],
  components: {
    'cbpo-binning-options': BinningConfig
  },
  props: {
    settings: {
      type: Array,
      default: () => []
    },
    limit: {
      type: Number,
      default: -1
    },
    dsId: String,
    existedColumns: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    // check if column is temporal or numeric
    isBinningApplicable() {
      return item => {
        if (!item) return false
        let column = this.columns.find(column => column.name === item.column)
        if (!column) return false
        return DataTypeUtil.isTemporal(column.type) || DataTypeUtil.isNumeric(column.type)
      }
    },
    getColumnType() {
      return item => {
        return DataTypeUtil.isTemporal(item.type) ? FORMAT_DATA_TYPES.TEMPORAL : FORMAT_DATA_TYPES.NUMERIC
      }
    },
    updatedColumnsState() {
      return CBPO.channelManager().getChannel().getColumnSvc().getColumns()
    }
  },
  methods: {
    // fetch column
    async fetchColumns(dsId) {
      try {
        this.showLoading()
        let columns = await CBPO.dsManager()
          .getDataSource(dsId)
          .columns()
        this.columns = this.mappingColumns([...columns], this.existedColumns)
        // update columns from channelManager
        this.updatedColumnsState.forEach(col => this.updateColumn(col))
      } catch (e) {
        console.error(e)
      } finally {
        this.hideLoading()
      }
    },
    // add path
    addNewItem() {
      let newPath = {
        column: null,
        binConfig: cloneDeep(DEFAULT_STATE_BIN['null'])
      }
      this.settingsState.push(newPath)
    },
    clearItem(index) {
      this.settingsState.splice(index, 1)
    },
    mappingColumns(columns, existedColumns) {
      return columns.filter(column => !existedColumns.includes(column.name)).map(column => {
        if (!column.displayName) {
          column.displayName = column.label || startCase([column.name])
        }
        return column
      })
    },
    // update column from channelManager
    updateColumn (data) {
      if (data) {
        const findedCol = this.columns.find(col => col.name === data.name)
        if (findedCol) findedCol.displayName = data.displayName || findedCol.displayName
      }
    }
  },
  async created() {
    if (!this.dsId) throw new Error('DataSource is required')
    await this.fetchColumns(this.dsId)
    this.settingsState = cloneDeep(this.settings)
  },
  watch: {
    settingsState: {
      deep: true,
      handler(settings) {
        const existedColumns = settings.map(column => column.column)
        this.columns = this.mappingColumns([...this.columns], existedColumns)
        this.$emit('update:settings', settings.filter(path => path.column !== null))
      }
    },
    updatedColumnsState: {
      deep: true,
      handler: function(newVal, oldVal) {
        if (newVal && newVal.length) {
          newVal.forEach(col => this.updateColumn(col))
          // path
        }
      }
    }
  }
}
</script>

<style lang="scss">
  .cbpo-list-settings {
    height: 300px;
    overflow-y: auto;
    /deep/ .vs__dropdown-menu {
      max-height: 150px;
    }
  }
  .cbpo-custom-select .vs__dropdown-toggle {
    border-radius:2.25px !important;
  }
</style>
