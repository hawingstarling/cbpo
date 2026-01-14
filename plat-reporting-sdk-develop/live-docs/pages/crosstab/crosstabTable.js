const sdkCrosstabTablePage = Vue.component('sdkCrosstabTablePage', {
  template: `
    <div class="crosstab-table-demo">
      <h5>Example:</h5>
      <div class="description pb-2">
        <span class="d-block">
          <b class="p-1">Header Column:</b> Order Date
        </span>
        <span class="d-block">
          <b class="p-1">Tab Column:</b>Shipped City, Ship Name
        </span>
        <span class="d-block">
          <b class="p-1">Value:</b>Freight
        </span>
      </div>
      <div id="crosstab-table-demo">
      </div>
      <sdk-export-code :templates="getTemplate" />
    </div>
  `,
  data() {
    return {
      template: '<cbpo-element-crosstab-table config-ref="config"></cbpo-element-crosstab-table>',
      config: {
        dataSource: 'idreportingsdk',
        widget: {
          title: {
            text: 'Demo Crosstab Table',
            enabled: true
          }
        },
        xColumns: [
          {
            name: 'Country'
          }
        ],
        yColumns: [
          {
            name: 'Units Sold',
            format: {
              type: 'numeric'
            },
            aggregation: {
              aggregation: 'sum', alias: 'Units Sold'
            }
          }
        ],
        tColumns: [
          {
            name: 'Order Date',
            format: {
              type: 'datetime'
            }
          },
          {
            name: 'Sales Channel'
          }
          // { name: 'prime' }
        ],
        bins: [
          {
            column: {
              name: 'Order Date',
              type: 'datetime'
            },
            alias: 'Order Date_bin',
            options: {
              alg: 'auto',
              numOfBins: 5
            }
          }
        ],
        pagination: {
          limit: 10
        },
        sorting: [
          {
            column: 'Country',
            direction: 'asc'
          },
          {
            column: 'Order Date',
            direction: 'asc'
          }
        ]
      }
    }
  },
  mixins: [configMixins, renderMixins],
  mounted() {
    this.render('#crosstab-table-demo', this.template, 'http://ds-api.qa.channelprecision.com/v1/', '652cce4a-7190-475f-8e4d-d73b02173ab5')
  },
  computed: {
    getTemplate() {
      return [
        {
          name: 'Crosstab Table',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  methods: {
    mappingDataSource() {
      let indexes = []
      let dataSource = _.cloneDeep(this.dataSource)
      dataSource.cols.forEach((col, i) => {
        if (col.type === 'date' || col.type === 'time' || col.type === 'datetime' || col.type === 'temporal') {
          indexes.push(i)
        }
      })
      indexes.forEach(i => {
        dataSource.rows = dataSource.rows.map(r => {
          r[i] = new Date((new Date(2018, 0, 1)).getTime() + Math.random() * (((new Date()).getTime() - (new Date(2018, 0, 1)).getTime())))
          return r
        })
      })
      return dataSource
    }
  },
  created() {
    window.dataSource = this.mappingDataSource()
    window.config = this.config
  }
})
