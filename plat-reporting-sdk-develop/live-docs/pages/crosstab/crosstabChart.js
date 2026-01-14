const sdkCrosstabChartPage = Vue.component('sdkCrosstabChartPage', {
  template: `
    <div class='crosstab-chart-demo'>
    <h5>Example:</h5>
    <div class='description pb-2'>
        <span class='d-block'>
          <b class='p-1'>X Axis Column:</b> Sale Date (binning auto with 5 bins)
        </span>
      <span class='d-block'>
          <b class='p-1'>T Axis Column:</b> Fulfillment type
        </span>
      <span class='d-block'>
          <b class='p-1'>Y Axis Column:</b> Item total cost
      </span>
      <span class='d-block'>
          <b class='p-1'>Filter: </b> <b class="text-danger">Sale Date</b> not full, <b class="text-danger">Fulfillment</b> type not null, <b class="text-danger">Item Sale Status</b> in Return Reversed
      </span>
    </div>
    <div id='crosstab-table-demo'>
    </div>
    <sdk-export-code :templates='getTemplate' />
    </div>
  `,
  data() {
    return {
      template: '<cbpo-element-crosstab-chart config-ref="config"></cbpo-element-crosstab-chart>',
      config: {
        dataSource: 'pf:1dd0bded-e981-4d2f-9bef-2874016661e7:sale_items',
        widget: {
          title: {
            text: 'Demo Crosstab Chart',
            enabled: true
          }
        },
        bins: [
          {
            column: {
              name: 'sale_date',
              type: 'datetime'
            },
            alias: 'sale_date_bin',
            options: {
              alg: 'auto',
              numOfBins: 5
            }
          }
        ],
        sorting: [
          {
            column: 'sale_date',
            direction: 'asc'
          }
        ],
        grouping: {
          columns: [{name: 'sale_date_bin'}],
          aggregations: [
            {
              column: 'item_total_cost',
              aggregation: 'sum',
              alias: 'item_total_cost_sum_id-1b890091-824f-4c95-8196-ade013fc6473'
            }
          ]
        },
        columns: [
          {
            name: 'sale_date',
            format: {
              type: 'temporal',
              config: {}
            }
          },
          {
            name: 'fulfillment_type'
          },
          {
            name: 'item_total_cost',
            format: {
              type: 'numeric',
              common: {
                prefix: '$'
              },
              config: {
                precision: 0
              }
            }
          }
        ],
        filter: {
          conditions: [
            {
              type: 'AND',
              conditions: [
                {
                  column: 'fulfillment_type',
                  operator: 'not_null',
                  value: ''
                }
              ]
            },
            {
              column: 'sale_date',
              operator: 'not_null',
              value: ''
            },
            {
              column: 'item_sale_status',
              operator: 'in',
              value: ['Return Reversed']
            }
          ],
          type: 'AND'
        },
        charts: [
          {
            axis: {
              x: [
                { id: 'abc' }
              ],
              y: [
                { id: 'abc' }
              ]
            },
            series: [
              {
                id: 'id-1b890091-824f-4c95-8196-ade013fc6473',
                type: 'bar',
                axis: {
                  x: 'abc', y: 'abc'
                },
                name: 'Total',
                data: {
                  x: 'sale_date',
                  y: 'item_total_cost'
                }
              },
              {
                id: 'id-d782a55b-fc8b-4eb8-971f-95113f83ca22',
                type: 'crosstab-line',
                axis: {
                  x: 'abc', y: 'abc'
                },
                data: {
                  x: 'sale_date',
                  t: 'fulfillment_type',
                  y: {
                    name: 'item_total_cost',
                    aggregation: 'sum'
                  }
                }
              }
            ]
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
  },
  created() {
    window.config = this.config
  }
})
