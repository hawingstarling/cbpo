<script>
import { mapActions } from 'vuex'

export default {
  name: 'variationsMixins',
  data() {
    return {
      selectOption: {
        size_variant: [],
        style_variant: [],
        brand: [],
        sale_status: [],
        profit_status: [],
        fulfillment_type: []
      },
      paramOption: {
        brand: {
          // BE param: { label: "FE label", value: default value }
          is_obsolete: {
            label: 'Hide Obsolete Brands',
            value: 0,
            checkedValue: 0,
            uncheckedValue: null
          }
        }
      },
      variationMapping: {
        size: { hasVariation: true, type: 'size_variant' },
        style: { hasVariation: true, type: 'style_variant' },
        brands: { hasVariation: false, type: 'brand' },
        'sale-status': { hasVariation: false, type: 'sale_status' },
        'profit-status': { hasVariation: false, type: 'profit_status' },
        'fulfillment-types': { hasVariation: false, type: 'fulfillment_type' }
      }
    }
  },
  methods: {
    ...mapActions({
      getSaleItemVariation: `pf/analysis/getSaleItemVariation`
    }),
    initialVariations() {
      for (const [key, value] of Object.entries(this.variationMapping)) {
        if (!this.selectOption[value.type].length) {
          this.getVariation(
            value.hasVariation,
            key,
            '',
            this.paramOption[value.type]
          )
        }
      }
    },
    getVariation(hasVariation, type, keyword, params) {
      let payload = {
        clientId: this.clientID,
        hasVariation: hasVariation,
        type,
        keyword
      }
      if (params) {
        const filterParams = Object.entries(params).reduce(
          (acc, [key, value]) => ({
            ...acc,
            ...(value.value !== null ? { [key]: value.value } : {})
          }),
          {}
        )
        payload.queries = filterParams
      }
      this.getSaleItemVariation(payload).then(response => {
        if (response.data) {
          const results = response.data.results.map(item => item.name)
          this.selectOption[this.variationMapping[type].type] = results
        }
      })
    },
    handleGetVariations(payload) {
      for (const [key, value] of Object.entries(this.variationMapping)) {
        if (value.type === payload.type) {
          this.getVariation(
            value.hasVariation,
            key,
            payload.value,
            this.paramOption[value.type]
          )
        }
      }
    },
    handleChangeParams(payload) {
      for (const [key, value] of Object.entries(this.variationMapping)) {
        if (value.type === payload.type) {
          this.getVariation(
            value.hasVariation,
            key,
            payload.value,
            payload.params
          )
        }
      }
    }
  },
  watch: {
    dataRow() {
      this.initialVariations()
    }
  }
}
</script>
