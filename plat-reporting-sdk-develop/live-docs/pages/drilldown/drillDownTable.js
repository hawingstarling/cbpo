const sdkDrillDownTablePage = Vue.component('sdkDrillDownTablePage', {
  template: `
    <div class="dashboard-container-demo">
    <h5>Example: </h5>
    <div class="card mb-2">
      <div class="card-body">
        <h6><b>Manual</b></h6>
        <div id="drill-down-demo" style="height: 600px; width: 100%">
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
        <div id="drill-down-passive-demo" style="height: 600px; width: 100%">
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
      template: `<cbpo-element-table config-ref="config"></cbpo-element-table>`,
      templatePassive: `<cbpo-element-table config-ref="configPassive"></cbpo-element-table>`
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
  mounted() {
    window.config = this.getConfig()
    window.configPassive = this.getConfig(true)
    this.render('#drill-down-demo', this.template, 'http://ds-api.qa.channelprecision.com/v1/', '652cce4a-7190-475f-8e4d-d73b02173ab5')
    this.render('#drill-down-passive-demo', this.templatePassive, 'http://ds-api.qa.channelprecision.com/v1/', '652cce4a-7190-475f-8e4d-d73b02173ab5')
  },
  methods: {
    getConfig(isPassive = false) {
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
          { 'name': 'Region', 'type': 'string', 'label': 'Region' },
          {
            'name': 'Country',
            'type': 'string',
            'label': 'Country'
          },
          { 'name': 'Item Type', 'type': 'string', 'label': 'Item Type' },
          {
            'name': 'Sales Channel',
            'type': 'string',
            'label': 'Sales Channel'
          },
          { 'name': 'Order Priority', 'type': 'string', 'label': 'Order Priority' },
          {
            'name': 'Order Date',
            'type': 'date',
            'label': 'Order Date'
          },
          { 'name': 'Order ID', 'type': 'number', 'label': 'Order ID' },
          {
            'name': 'Ship Date',
            'type': 'date',
            'label': 'Ship Date'
          },
          { 'name': 'Units Sold', 'type': 'number', 'label': 'Units Sold' },
          {
            'name': 'Unit Price',
            'type': 'number',
            'label': 'Unit Price'
          },
          { 'name': 'Unit Cost', 'type': 'number', 'label': 'Unit Cost' },
          {
            'name': 'Total Revenue',
            'type': 'number',
            'label': 'Total Revenue'
          },
          { 'name': 'Total Cost', 'type': 'number', 'label': 'Total Cost' },
          {
            'name': 'Total Profit',
            'type': 'number',
            'label': 'Total Profit'
          }
        ],
        globalControlOptions: {
          aggregation: {
            enabled: true
          },
          globalGrouping: {
            enabled: true,
            config: {
              value: false
            }
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
          },
          editBin: {
            enabled: true
          }
        }
      }
    }
  }
})
