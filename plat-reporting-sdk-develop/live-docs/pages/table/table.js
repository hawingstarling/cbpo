const sdkTablePage = Vue.component('sdkTablePage', {
  template: `
    <div class="table-demo">
      <h5>Example: </h5>
      <div id="table-demo">
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
        drillDown: {
          enabled: true
        },
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
        },
        timezone: {
          enabled: true
        },
        rowActions: {
          enabled: true,
          inline: 1, // number of inline item, max inline items are 2, else -> dropdown
          display: 'always', // always | onhover
          position: 'left',
          colWidth: 200,
          controls: [
            {
              display: true,
              props: { size: "sm", variant: "primary" },
              style: { padding: '0px 5px' },
              icon: 'fa-gear',
              label: 'Edit',
              event: function (dataRow) { console.log('action 1', dataRow) }
            },
            {
              display: true,
              props: { size: "sm", variant: "primary" },
              style: {},
              icon: 'fa-home',
              label: 'Action 2',
              event: function (dataRow) { console.log('action 2', dataRow) }
            },
            {
              display: true,
              props: { size: "sm", variant: "primary" },
              style: {},
              icon: 'fa-home',
              label: 'Action 3',
              event: function (dataRow) { console.log('action 3', dataRow) }
            }
          ]
        },
        bulkActions: {
          enabled: true,
          controls: [
            {
              display: true,
              props: { size: "sm", variant: "primary" },
              style: {},
              icon: 'fa-gear',
              label: 'Action 1',
              event: function (dataRow) { console.log('bulk action 1', dataRow) }
            },
            {
              display: true,
              props: { size: "sm", variant: "primary" },
              style: {},
              icon: 'fa-home',
              label: 'Action 3',
              event: function (dataRow) { console.log('bulk action 3', dataRow) }
            }
          ]
        },
        pagination: {
          limit: 10,
          type: 'buttons'
        },
        columns: [],
        detailView: {
          enabled: true,
          mode: 'inline',
          action: {
            breakpoint: 768,
            props: { size: 'sm', variant: 'primary' },
            icons: {
              closed: 'fa-arrow-circle-o-down',
              opened: 'fa-arrow-circle-o-right'
            },
            label: 'View'
          },
          breakpoints: {
            1024: 3,
            768: 2,
            320: 1
          }
        }
      }
    }
  },
  components: {
    'sdk-export-code': sdkExportCodeComponent
  },
  mixins: [configMixins, renderMixins],
  mounted() {
    this.render('#table-demo', this.template, 'http://ds-api.qa.channelprecision.com/v1', this.VUE_DEMO_TOKEN)
  },
  computed: {
    getTemplate() {
      return [
        {
          name: 'Table',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  created() {
    this.config.columns = _.cloneDeep(this.configColumns)
    this.config.columns[1].isUniqueKey = true
    window.dataSource = _.cloneDeep(this.dataSource)
    window.config = this.config
  }
})
