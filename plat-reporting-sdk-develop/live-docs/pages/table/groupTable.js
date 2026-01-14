const sdkGroupTablePage = Vue.component('sdkGroupTablePage', {
  template: `
    <div class="group-table-demo">
      <h5>Example: </h5>
      <div id="group-table-demo">
      </div>
      <sdk-export-code :templates="getTemplate" />
    </div>
  `,
  data() {
    return {
      template: '<cbpo-element-table class="p-0" config-ref="config"></cbpo-element-table>',
      config: {
        dataSource: 'dataSource',
        widget: {
          title: {
            enabled: true,
            text: 'Demo Table'
          }
        },
        globalControlOptions: {
          aggregation: {
            enabled: true
          },
          grouping: {
            enabled: true
          },
          editColumn: {
            enabled: true
          },
          editColumnLabel: {
            enabled: true
          },
          editColumnFormat: {
            enabled: true
          }
        },
        pagination: {
          limit: 10
        },
        grouping: {
          columns: [
            {name: 'seller_name'}
          ],
          aggregations: [
            {column: 'sku', alias: 'sku', aggregation: 'count'},
            {column: 'upc/ean', alias: 'upc/ean', aggregation: 'count'},
            {column: 'asin', alias: 'asin', aggregation: 'count'},
            {column: 'title', alias: 'title', aggregation: 'concat'},
            {column: 'seller_price', alias: 'seller_price', aggregation: 'sum'},
            {column: 'map_price', alias: 'map_price', aggregation: 'sum'},
            {column: 'diff', alias: 'diff', aggregation: 'sum'},
            {column: 'diff_percent', alias: 'diff_percent', aggregation: 'avg'},
            {column: 'link', alias: 'link', aggregation: 'count'},
            {column: 'screenshot', alias: 'screenshot', aggregation: 'count'},
            {column: 'captured_at', alias: 'captured_at', aggregation: 'count'},
            {column: 'fba', alias: 'fba', aggregation: 'count'},
            {column: 'prime', alias: 'prime', aggregation: 'count'},
            {column: 'condition', alias: 'condition', aggregation: 'count'},
            {column: 'rating', alias: 'rating', aggregation: 'count'},
            {column: 'growth_value', alias: 'growth_value', aggregation: 'count'},
            {column: 'override', alias: 'override', aggregation: 'count'}
          ]
        }
      }
    }
  },
  mixins: [configMixins, renderMixins],
  mounted() {
    this.render('#group-table-demo', this.template)
  },
  computed: {
    getTemplate() {
      return [
        {
          name: 'Group Table',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  created() {
    this.config.columns = _.cloneDeep(this.configColumns)
    window.dataSource = _.cloneDeep(this.dataSource)
    window.config = this.config
  }
})
