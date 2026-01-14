const sdkDrillDownChart = Vue.component('sdkDrillDownChart', {
  template: `
  <div class="dashboard-container-demo">
    <h5>Example: </h5>
    <label for="chart">Chart Type</label>
    <select v-model="chart" name="chart" id="chart">
      <option value="pie">Pie Chart</option>
      <option value="bar">Bar Chart</option>
    </select>
    <div class="card mb-2">
      <div class="card-body">
        <h6><b>Manual</b></h6>
        <div id="drill-down-demo" style="height: 400px; width: 80vw">
        </div>
      </div>
    </div>
    <div class="card mb-2">
      <div class="card-body">
        <h6><b>Passive</b></h6>
        <div>
          <label>Description</label>
          <div>
            <ul>
              <li>Level 1: Column <b>Order Date</b></li>
              <li>Level 2: Column <b>Country</b></li>
              <li>Level 3: Column <b>Item type</b></li>
            </ul>
          </div>
        </div>
        <div id="drill-down-passive-demo" style="height: 400px; width: 80vw">
        </div>
      </div>
    </div>
    <sdk-export-code :templates="getTemplate"/>
  </div>
  `,
  components: {
    'sdk-export-code': sdkExportCodeComponent
  },
  mixins: [configMixins, renderMixins],
  data() {
    return {
      chart: 'pie',
      template: `<cbpo-element-chart config-ref="config"></cbpo-element-chart>`,
      templatePassive: `<cbpo-element-chart config-ref="configPassive"></cbpo-element-chart>`
    }
  },
  computed: {
    getTemplate() {
      return [
        {
          name: 'Drill Dow for chart',
          tag: this.template,
          config: window.config
        },
        {
          name: 'Drill Dow Passive for chart',
          tag: this.templatePassive,
          config: window.configPassive
        }
      ]
    }
  },
  methods: {
    init() {
      this.render('#drill-down-demo', this.template, 'http://ds-api.qa.channelprecision.com/v1/', '652cce4a-7190-475f-8e4d-d73b02173ab5')
      this.render('#drill-down-passive-demo', this.templatePassive, 'http://ds-api.qa.channelprecision.com/v1/', '652cce4a-7190-475f-8e4d-d73b02173ab5')
    },
    getConfig(id, type, isPassive = false) {
      return {
        dataSource: `idreportingsdk`,
        drillDown: {
          enabled: true,
          config: {
            path: {
              enabled: isPassive,
              settings: [
                // level 1
                {
                  column: 'Order Date',
                  binConfig: {
                    binningType: 'auto',
                    nice: true,
                    expected: 5
                  }
                },
                // level 2
                {
                  column: 'Country',
                  binConfig: null
                },
                // level 3
                {
                  column: 'Item Type',
                  binConfig: null
                }
              ]
            }
          }
        },
        columns: [
          {
            name: 'Region',
            type: 'string'
          },
          {
            name: 'Units Sold',
            type: 'number'
          }
        ],
        grouping: {
          columns: [{ name: 'Region' }],
          aggregations: [{
            column: 'Units Sold',
            aggregation: 'sum',
            alias: 'Units Sold_sum_' + id
          }]
        },
        charts: [
          {
            axis: {
              x: [
                {
                  id: 'x_' + id,
                  type: 'category',
                  display: true,
                  format: null,
                  scaleLabel: {
                    display: false,
                    labelString: ''
                  },
                  ticks: {
                    fontColor: '#666',
                    fontSize: 11,
                    fontStyle: 'bold'
                  }
                }
              ],
              y: [
                {
                  id: 'y_' + id,
                  type: 'linear',
                  format: null,
                  position: 'left',
                  stack: false,
                  ticks: {
                    beginAtZero: true,
                    stepSize: '',
                    maxTicksLimit: 5,
                    fontColor: '#666',
                    fontSize: 11,
                    fontStyle: 'bold'
                  },
                  scaleLabel: {
                    display: false,
                    labelString: ''
                  }
                }
              ]
            },
            series: [
              {
                id: id,
                type: type,
                name: 'Region (Sum)',
                axis: {
                  x: 'x_' + id,
                  y: 'y_' + id
                },
                data: {
                  x: 'Region',
                  y: 'Units Sold'
                }
              }
            ]
          }
        ]
      }
    }
  },
  watch: {
    chart: {
      immediate: true,
      handler(value) {
        window.config = this.getConfig('id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce', value)
        window.configPassive = this.getConfig('id-8d7b2b9d-d87c-43f6-801b-e4616cfc26ce', value, true)
        this.$nextTick(() => {
          this.init()
        })
      }
    }
  }
})
