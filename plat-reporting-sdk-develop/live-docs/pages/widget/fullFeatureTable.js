const sdkFeatureTablePage = Vue.component('sdkFeatureTablePage', {
  template: `
    <div class="full-feature-table-demo">
    <h5>Example: </h5>
    <div style="height: 600px" id="full-feature-table-demo">
    </div>
    <div class="mt-2">
      <sdk-export-code :templates="getTemplate"/>
    </div>
    </div>
  `,
  data() {
    let dataSource = 'idreportingsdk'
    return {
      dataSource: dataSource,
      baseURL: 'http://ds-api.qa.channelprecision.com/v1/',
      template: '<cbpo-widget class="p-0" config-ref="config"></cbpo-widget>',
      config: {
        widget: {
          title: {
            text: `Last year is [[format expression="DATE_END_OF(DATE_LAST(1,'year'), 'year')" type="temporal" format="YYYY"][/format]] and current is [2020]`,
            enabled: false
          }
        },
        columnManager: {
          enabled: true
        },
        filter: {
          builder: {
            enabled: true,
            readable: {
              enabled: true
            },
            config: {
              form: {
                columns: [
                  {
                    name: 'Ship Date',
                    type: 'input',
                    operator: '$ne',
                    value: '1996-05-14T00:00:00',
                    options: {
                      isExpression: false
                    }
                  },
                  {
                    name: 'Country',
                    type: 'select',
                    options: [
                      { text: 'Amani', value: 'Amani' },
                      { text: 'Nike', value: 'Nike' },
                      { text: 'Nani', value: 'Nani' },
                      { text: 'Nini', value: 'Nini' },
                      { text: 'Luni', value: 'Luni' },
                      { text: 'Apheni', value: 'Apheni' },
                      { text: 'Bani', value: 'Bani' },
                      { text: 'Ninu', value: 'Ninu' }
                    ]
                  }
                ]
              }
            }
          }
        },
        elements: [
          {
            type: 'cbpo-element-table',
            config: {
              dataSource: dataSource,
              header: {
                resizeMinWidth: 5,
                multiline: true
              },
              widget: {
                title: {
                  enabled: false
                }
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
              compactMode: {
                enabled: true
              },
              rowActions: {
                enabled: true,
                inline: 1, // number of inline item, max inline items are 2, else -> dropdown
                display: 'always', // always | onhover
                position: 'left',
                colWidth: 150,
                eventHandler: function(eventName, item) {
                  console.log(eventName, item)
                },
                controls: [
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-gear',
                    label: 'Action 1',
                    event: function(dataRow) {
                      console.log('action 1', dataRow)
                    }
                  },
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-home',
                    label: 'Action 2',
                    event: function(dataRow) {
                      console.log('action 2', dataRow)
                    }
                  },
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-home',
                    label: 'Action 3',
                    event: function(dataRow) {
                      console.log('action 3', dataRow)
                    }
                  }
                ]
              },
              bulkActions: {
                enabled: true,
                mode: 'both',
                controls: [
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-gear',
                    label: 'Action 1',
                    event: function(dataRow) {
                      console.log('bulk action 1', dataRow)
                    }
                  },
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-home',
                    label: 'Action 3',
                    event: function(dataRow) {
                      console.log('bulk action 3', dataRow)
                    }
                  }
                ]
              },
              pagination: {
                type: 'lazy',
                limit: 20
              },
              globalSummary: {
                enabled: true,
                summaries: [{
                  label: "Count 'H'",
                  position: 'left',
                  format: {},
                  expr: `COUNTIF(@'Order Priority'=='H', 'idreportingsdk') as a1`
                }, {
                  label: 'Europe average of Units Sold',
                  position: 'left',
                  format: {
                    type: 'numeric'
                  },
                  expr: `AVGIF(@'Units Sold', @'Region' contains 'Europe', 'idreportingsdk') as avg`
                }, {
                  label: 'Total Sales',
                  position: 'right',
                  format: {
                    type: 'numeric',
                    common: {
                      plain: {
                        nil: 'NULL', // default NULL
                        empty: 'EMPTY', // default EMPTY
                        na: 'N/A'
                      },
                      html: {
                        nil: '<span class="d-null">null</span>',
                        empty: '<span class="empty">empty</span>',
                        na: '<span class="d-na">n/a</span>'
                      },
                      prefix: '$',
                      suffix: null
                    },
                    config: {
                      comma: true,
                      precision: 2,
                      siPrefix: true
                    }
                  },
                  expr: `SUMIF(@'Total Revenue', 'idreportingsdk') as a3`
                }]
              },
              tableSummary: {
                enabled: true,
                position: 'both',
                labelColumnSummary: 'Summary',
                summaries: [
                  {
                    label: '',
                    column: 'Region',
                    format: {
                      type: 'numeric',
                      common: {
                        plain: {
                          nil: 'NULL', // default NULL
                          empty: 'EMPTY', // default EMPTY
                          na: 'N/A'
                        },
                        html: {
                          nil: '<span class="d-null">null</span>',
                          empty: '<span class="empty">empty</span>',
                          na: '<span class="d-na">n/a</span>'
                        },
                        prefix: null,
                        suffix: ' (count)'
                      },
                      config: {
                        comma: true,
                        precision: 4,
                        siPrefix: false
                      }
                    },
                    expr: `COUNTIF(@'Region' contains 'Europe', 'idreportingsdk') as region`
                  },
                  {
                    label: '',
                    column: 'Units Sold',
                    format: {
                      type: 'numeric',
                      common: {
                        plain: {
                          nil: 'NULL', // default NULL
                          empty: 'EMPTY', // default EMPTY
                          na: 'N/A'
                        },
                        html: {
                          nil: '<span class="d-null">null</span>',
                          empty: '<span class="empty">empty</span>',
                          na: '<span class="d-na">n/a</span>'
                        },
                        prefix: null,
                        suffix: ' (sum)'
                      },
                      config: {
                        comma: true,
                        precision: 2,
                        siPrefix: true
                      }
                    },
                    expr: `SUMIF(@'Units Sold', @'Region' contains 'Europe', 'idreportingsdk') as region`
                  }
                ]
              }
            }
          }
        ],
        calculatedColumn: {
          enabled: true
        }
      }
    }
  },
  mixins: [configMixins, renderMixins],
  computed: {
    getTemplate() {
      return [
        {
          name: 'Full Features Table',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  methods: {
    async initSDK() {
      let columns = await columnService.getColumns(this.baseURL, this.VUE_DEMO_TOKEN, '', { dataSource: this.dataSource })
      this.config.elements[0].config.columns = _.cloneDeep(columns.columns.map(col => {
        col.cell = {}
        if (col.type === 'date' || col.type === 'datetime') {
          col.cell = {
            format: {
              type: 'temporal'
            }
          }
        }
        if (col.type === 'float') {
          col.cell = {
            format: {
              type: 'numeric'
            }
          }
        }
        col.cell.width = 150
        return col
      }))
      window.config = this.config
      this.render('#full-feature-table-demo', this.template, this.baseURL, this.VUE_DEMO_TOKEN,'')
    }
  },
  mounted() {
    this.initSDK()
  }
  // created() {
  //   this.config.elements[0].config.columns = _.cloneDeep(this.configColumns)
  //   this.config.elements[0].config.columns[1].isUniqueKey = true
  //   window.dataSource = _.cloneDeep(this.dataSource)
  //   window.config = this.config
  // }
})
