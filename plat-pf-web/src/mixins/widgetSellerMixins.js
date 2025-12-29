import { BRAND_OPTION, SKU_OPTION, FULFILLMENT_ALL_OPTION, WIDGET_NAME, BRAND_ALL_OPTION, SKU_ALL_OPTION } from '@/shared/constants'
import { mapGetters, mapActions } from 'vuex'
import cloneDeep from 'lodash/cloneDeep'

export default {
  data() {
    return {
      sdkKey: null,
      currentGrouping: null,
      groupBy: {
        options: [
          BRAND_OPTION,
          SKU_OPTION
        ],
        selected: BRAND_OPTION
      },
      filterSelected: BRAND_ALL_OPTION,
      fulfillmentSelected: FULFILLMENT_ALL_OPTION,
      saveAsDefault: false,
      isSDKReady: false,
      groupSettings: cloneDeep(this.$props.sdkConfig.config.elements[0].config.grouping)
    }
  },
  props: {
    sdkConfig: Object
  },
  computed: {
    ...mapGetters({
      isLoading: `pf/saleWidget/isLoading`,
      fulfillmentOptions: `pf/saleWidget/fulfillmentOptions`,
      skuAllSellerOptions: `pf/saleWidget/skuAllSellerOptions`,
      skuSalesBy$AmountOptions: `pf/saleWidget/skuSalesBy$AmountOptions`,
      brandOptions: `pf/saleWidget/brandOptions`
    }),
    getDropdownList() {
      return this.groupBy.selected.value === 'brand'
        ? this.brandOptions
        : this.widget === WIDGET_NAME.dollar
          ? this.skuSalesBy$AmountOptions
          : this.skuAllSellerOptions
    }
  },
  methods: {
    ...mapActions({
      getAllBrandsAndFulfillment: 'pf/saleWidget/getAllBrandsAndFulfillment',
      updateUserTrack: 'pf/saleWidget/updateUserTrack'
    }),
    buildSDKFilterQuery() {
      const conditions = []
      this.filterSelected.value && conditions.push({
        column: this.groupBy.selected.value,
        operator: '$eq',
        value: this.filterSelected.value
      })
      this.fulfillmentSelected.value && conditions.push({
        column: 'fulfillment_type',
        operator: '$eq',
        value: this.fulfillmentSelected.value
      })
      this.sdkConfig.config.filter.base.config.query = {
        type: 'AND',
        conditions: conditions
      }
    },
    buildSDKGroupByColumn() {
      // build column and grouping column
      const configHandler = {
        sku: (column) => {
          column.name = 'brand'
          column.displayName = 'Brand'
          this.sdkConfig.config.elements[0].config.grouping.columns[0].name = 'brand'
        },
        brand: (column) => {
          column.name = 'sku'
          column.displayName = 'SKU'
          this.sdkConfig.config.elements[0].config.grouping.columns[0].name = 'sku'
        }
      }
      this.sdkConfig.config.elements[0].config.columns.forEach(col => [BRAND_OPTION.value, SKU_OPTION.value].includes(col.name) && configHandler[col.name](col))
    },
    buildSDKKey() {
      this.sdkKey = `saleWidget_${this.groupBy.selected.value}_${this.filterSelected.value}_${this.fulfillmentSelected.value}`
    },
    refresh() {
      this.buildSDKFilterQuery()
      if (this.sdkConfig.config.elements[0].config.columns.every(col => col.name !== this.groupBy.selected.value)) {
        this.buildSDKGroupByColumn()
      }
      this.buildSDKKey()
    },
    async selectSaveAsDefault(checked) {
      this.saveAsDefault = checked
      try {
        await this.updateUserTrack({
          clientId: this.$route.params.client_id,
          data: {
            widget: {
              [`sale_by_${this.widget}`]: {
                save_as_default: checked,
                group_by_default: checked ? this.groupBy.selected.value : SKU_OPTION.value
              }
            }
          }
        })
      } catch (err) {
        console.error('Cannot update data user track.')
      }
    }
  },
  mounted() {
    window.addEventListener('resize', this.setContainerHeight)
  },
  watch: {
    'groupBy.selected'(option) {
      this.filterSelected = option.value === 'brand'
        ? BRAND_ALL_OPTION
        : SKU_ALL_OPTION
      if (this.saveAsDefault) {
        this.selectSaveAsDefault(true)
      }
      if (this.currentGrouping) {
        this.sdkConfig.config.elements[0].config.grouping = this.currentGrouping
      }
    },
    'filterSelected'() {
      this.refresh(this.sdkConfig)
    },
    'fulfillmentSelected'(fulfillment) {
      this.currentGrouping = cloneDeep(this.sdkConfig.config.elements[0].config.grouping)
      this.sdkConfig.config.elements[0].config.grouping = fulfillment
        ? { columns: [], aggregations: [] }
        : this.groupSettings
      this.buildSDKFilterQuery()
      this.buildSDKKey()
    }
  }
}
