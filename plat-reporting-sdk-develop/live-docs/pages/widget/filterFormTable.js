const sdkFilterFormTablePage = Vue.component('sdkFilterFormTablePage', {
  template: `
    <div>
      <h5>Demo Widget Table: </h5>
      <div id="widgetTableSDK"></div>
    </div>
  `,
  data() {
    let dataSource = 'idreportingsdk'
    return {
      dataSource: dataSource,
      template: `<cbpo-widget config-ref="config"></cbpo-widget>`,
      baseURL: 'http://ds-api.qa.channelprecision.com/v1/',
      config: {
        widget: {
          title: {
            text: 'Filter Form Table'
          }
        },
        filter: {
          form: {
            config: {
              controls: [
                {
                  type: 'cbpo-filter-control-auto',
                  config: {
                    common: {
                      column: { name: 'Item Type', type: 'string' },
                      operator: 'in'
                    },
                    label: {
                      text: 'Item Type'
                    }
                  }
                },
                {
                  type: 'cbpo-filter-control-range',
                  config: {
                    common: {
                      column: { name: 'Order Date', type: 'datetime' },
                      operator: 'in_range'
                    },
                    label: {
                      text: 'Select date range'
                    },
                    range: {
                      format: {
                        config: {
                          format: 'MM/DD/YYYY'
                        }
                      }
                    }
                  }
                },
                {
                  type: 'cbpo-filter-control-range',
                  config: {
                    common: {
                      column: { name: 'Ship Date', type: 'datetime' },
                      operator: 'time_range'
                    },
                    label: {
                      text: 'Time'
                    },
                    range: {
                      type: 'time',
                      formatLabel: 'hh:mm a',
                      formatValue: 'HH:mm'
                    }
                  }
                },
                {
                  type: 'cbpo-filter-control-select',
                  config: {
                    infiniteScroll: {
                      enabled: true,
                      limit: 15
                    },
                    dataSource: dataSource,
                    loadedDataSource: true,
                    common: {
                      column: { name: 'Country', type: 'string' },
                      operator: '$eq',
                      value: undefined
                    },
                    label: {
                      text: 'Country'
                    }
                  }
                }
              ]
            }
          }
        },
        elements: [
          {
            type: 'cbpo-element-table',
            config: {
              dataSource: dataSource,
              columns: [],
              pagination: {
                limit: 10
              }
            }
          }
        ]
      }
    }
  },
  mixins: [configMixins, renderMixins],
  methods: {
    async initSDK() {
      let { columns } = await columnService.getColumns(this.baseURL, this.VUE_DEMO_TOKEN, '', { dataSource: this.dataSource })
      this.config.elements[0].config.columns = columns
      console.log(this.config)
      window.config = this.config
      this.render('#widgetTableSDK', this.template, this.baseURL, this.VUE_DEMO_TOKEN, '')
    }
  },
  computed: {
    getTemplate() {
      return [
        {
          name: 'Filter Form Table',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  mounted() {
    this.initSDK()
  }
})
