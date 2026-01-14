<template>
  <div class="cbpo-s form-group cbpo-filter-control-select">
    <label v-if="control.config.label && control.config.label.text">{{ control.config.label.text }}: </label>
    <div class="select-section">
      <v-select
       v-if="control.config && control.config.infiniteScroll && control.config.infiniteScroll.enabled"
        class="cbpo-custom-select"
        label="label"
        :value="control.config.common.value"
        :reduce="option => option.value"
        :options="paginated"
        :clearable="false"
        :placeholder="control.config.selection.empty.enabled ? control.config.selection.empty.label : 'Please select a value...'"
        :filterable="false"
        @input="selectChange"
        @open="onOpen"
        @close="onClose"
        @search="debouncedSearchHandler"
      >
        <template #open-indicator="{ attributes }">
          <i class="fa fa-angle-down" v-bind="attributes"></i>
        </template>
        <template #list-footer>
          <li v-show="hasNextPage" ref="load" class="loader">
            <i class="fa fa-spinner fa-spin fa-fw"></i> Loading more options...
          </li>
        </template>
      </v-select>
      <v-select
        v-else
        class="cbpo-custom-select"
        label="label"
        :value="control.config.common.value"
        :reduce="option => option.value"
        :options="control.config.selection.options"
        :clearable="false"
        :placeholder="control.config.selection.empty.enabled ? control.config.selection.empty.label : 'Please select a value...'"
        @input="selectChange"
      >
        <template #open-indicator="{ attributes }">
          <i class="fa fa-angle-down" v-bind="attributes"></i>
        </template>
      </v-select>
      <i v-if="!control.config.selection.empty.isEmptySelected && control.config.selection.empty.enabled"
         @click="clearValue" class="fa fa-times" role="clearBtn"></i>
    </div>
  </div>
</template>
<script>
import CBPO from '@/services/CBPO'
import QueryBuilder from '@/services/ds/query/QueryBuilder'
import { makeDefaultSelectControlConfig } from './FilterControlConfig'
import dsFormatManager, {
  FORMAT_DATA_TYPES,
  getDefaultFormatConfigBaseOnFormatType
} from '@/services/dataFormatManager'
import { defaultFormatConfig } from '@/components/widgets/elements/table/TableConfig'
import { BUS_EVENT } from '@/services/eventBusType'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import isEmpty from 'lodash/isEmpty'
import isEqual from 'lodash/isEqual'
import isObject from 'lodash/isObject'
import cloneDeep from 'lodash/cloneDeep'
import orderBy from 'lodash/orderBy'
import uniqWith from 'lodash/uniqWith'
import get from 'lodash/get'
import debounce from 'lodash/debounce'

export default {
  name: 'FilterControlSelect',
  data: () => ({
    observer: null,
    total: 0,
    current: 1,
    listOption: [],
    search: ''
  }),
  methods: {
    widgetConfig(config) {
      this.control.config = Object.assign({}, makeDefaultSelectControlConfig(config))
    },
    buildOptionDataFromRowsData(data, dataIndex, formatFactory) {
      const ignoreValues = this.control.config.selection.ignoreValues || []
      console.log(ignoreValues)
      return cloneDeep(data)
        .map(dataRow => dataRow[dataIndex])
        .map(data => ({ label: formatFactory ? formatFactory(data) : (data || 'Empty'), value: data }))
        .filter(option => ignoreValues.length ? !ignoreValues.includes(option.value) : true)
    },
    getFormatDateFactory(column, format = {}) {
      if (!DataTypeUtil.isTemporal(column.type)) return null
      let formatTemporal = getDefaultFormatConfigBaseOnFormatType(FORMAT_DATA_TYPES.TEMPORAL)
      let formatConfig = Object.assign(
        {},
        cloneDeep(defaultFormatConfig),
        { config: { ...formatTemporal, ...formatTemporal.date } },
        format,
        { type: FORMAT_DATA_TYPES.TEMPORAL }
      )
      return formatConfig ? dsFormatManager.create(formatConfig, false) : null
    },
    async _getDefaultOptions() {
      if (this.control.config.dataSource) {
        let { common: { column }, selection: { format, sort }, filter } = this.control.config
        let formatFactory = this.getFormatDateFactory(column, format)
        let hasEmptyOption = get(this.control.config.selection, 'empty.enabled', false)
        let q = new QueryBuilder()
        q.addOrder(column.name, sort || 'asc')

        // TODO: Need to fix on DS service before using
        // q.setPaging({ limit: this.control.config.infiniteScroll.enabled ? this.control.config.infiniteScroll.limit : 99999, current: this.current })

        q.setPaging({ limit: this.control.config.infiniteScroll.enabled ? this.control.config.infiniteScroll.limit * this.current : 99999, current: 1 })
        q.setGroup([column], [])
        try {
          // set filter
          if (!isEmpty(filter)) {
            q.setFilter(filter)
          }
          if (this.search.length > 0 && isEmpty(filter)) {
            q.setFilter({
              type: 'AND',
              conditions: [{
                column: column.name,
                operator: 'contains',
                value: this.search
              }]
            })
          }
          if (this.search.length > 0 && !isEmpty(filter) && !isEmpty(filter.conditions)) {
            let filterSearch = cloneDeep(filter)
            filterSearch.conditions.push({
              column: column.name,
              operator: 'contains',
              value: this.search
            })
            q.setFilter(filterSearch)
          }
          // get data
          let { rows, cols } = await CBPO.dsManager().getDataSource(this.control.config.dataSource).query(q.params)
          this.listOption = this.search.length > 0 ? [...rows] : [...this.listOption, ...rows]
          if (this.isAllowGetTotal) this.total = await CBPO.dsManager().getDataSource(this.control.config.dataSource).total(q.params)
          // find index and build options
          let indexColumn = cols.findIndex(col => col.name === column.name)
          let options = this.buildOptionDataFromRowsData(this.listOption, indexColumn, formatFactory)
          // order options
          this.control.config.selection.options = orderBy(uniqWith([...options], isEqual), 'value', sort || 'asc')
          // default value when turn off empty option and emit that value to parent component
          if (!hasEmptyOption && !isEmpty(this.control.config.selection.options)) {
            this.control.config.common.value = this.control.config.selection.options[0].value
            this.change(this.control.config.common.value, false)
            return
          }
        } catch (e) {
          console.error(e)
        }
        const findValue = get(this.control.config.common, 'value.value', this.control.config.common.value)
        this.control.config.common.value = this.control.config.selection.options
          .find(option => option.value === findValue) || undefined
        this.change(
          isObject(this.control.config.common.value)
            ? this.control.config.common.value.value
            : this.control.config.common.value,
          findValue === undefined
        )
      }
    },
    clearValue() {
      this.change(null, true)
    },
    // function fired when select is change
    selectChange(value) {
      this.change(value, false)
    },
    async change(value, isClear) {
      this.control.config.selection.empty.isEmptySelected = isClear
      this.control.config.common.value = isClear ? undefined : value
      this.$emit('input', this.control)
    },
    async onOpen() {
      if (this.hasNextPage) {
        await this.$nextTick()
        this.observer.observe(this.$refs.load)
      }
    },
    debouncedSearchHandler: debounce(async function(search) {
      await this.onSearch(search)
    }, 500),
    async onSearch(search) {
      this.search = search
      await this._getDefaultOptions()
      await this.$nextTick()
      return this.paginated
    },
    onClose() {
      this.observer.disconnect()
    },
    async infiniteScroll([{ isIntersecting, target }]) {
      if (isIntersecting) {
        const ul = target.offsetParent
        const scrollTop = target.offsetParent.scrollTop
        this.current++
        await this._getDefaultOptions()
        await this.$nextTick()
        ul.scrollTop = scrollTop
      }
    }
  },
  props: {
    control: Object
  },
  computed: {
    paginated() {
      return this.control.config.selection.options
    },
    hasNextPage() {
      return this.paginated.length < this.total
    },
    isAllowGetTotal() {
      return (this.current === 1 && this.control.config.infiniteScroll.enabled) || !isEmpty(this.search)
    }
  },
  mounted() {
    this.observer = new IntersectionObserver(this.infiniteScroll)
    CBPO.$bus.$on(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA, () => {
      this._getDefaultOptions()
    })
  },
  async created() {
    this.widgetConfig(this.control.config)
    await this._getDefaultOptions()
  },
  destroyed() {
    CBPO.$bus.$off(BUS_EVENT.FORCE_ELEMENT_REFRESH_DATA)
  }
}
</script>
<style lang="scss" scoped>
@import './FilterControlSelect.scss';
</style>
