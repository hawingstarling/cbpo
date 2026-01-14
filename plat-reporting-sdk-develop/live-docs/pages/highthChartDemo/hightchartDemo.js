const sdkHighChartDemoPage = Vue.component('sdkChartjsDemoPage', {
  template: `
    <div>
      <h5>Example: </h5>
      <div style="height: 400px; width: 80vw; margin: auto" id="chart-demo">
      </div>
    </div>
  `,
  mixins: [renderMixins],
  props: {
    chartType: null
  },
  watch: {
    '$route.path': function() {
      this.changeConfig()
    }
  },
  methods: {
    async changeConfig() {
      let type = this.$route.path.split('hc-')[1]
      let config = _.cloneDeep(this.config1)
      let template = this.template1
      switch (type) {
        case 'bubble':
          config = _.cloneDeep(this.config2)
          break
        case 'scatter':
          config = _.cloneDeep(this.config3)
          break

        case 'pareto':
          type = 'bar'
          config = _.cloneDeep(this.config4)
          break
        case 'donut':
          type = 'pie'
          config.charts[0].options.pie.type = 'doughnut'
          break
        case 'solid':
          template = this.template2
          type = 'solidgauge'
          config = _.cloneDeep(this.config5)
          break
        case 'bullet':
          template = this.template2
          type = 'bulletgauge'
          config = _.cloneDeep(this.config5)
          break
        case 'heat-map':
          template = this.templateHeatMap
          window.configFull = _.cloneDeep(this.configHeatFull)
          window.configStateOnly = _.cloneDeep(this.configHeatStateOnly)
          await this.randomDataHeatMapFull()
          await this.randomDataHeatMapState()
          break
        default:
          break
      }

      console.log(config);
      if (type !== 'heat-map') {
        config.charts[0].series[0].type = type
        config.dataSource = this.dataSource
        window.config = config
      }
      this.render(
        '#chart-demo',
        template,
        'http://ds-api.qa.channelprecision.com/v1/',
        this.VUE_DEMO_TOKEN,
        ''
      )
    },
    async randomDataHeatMapFull() {
      try {
        const { data } = await axios.get(
          'live-docs/assets/json/us-all-state.json'
        )
        const rows = data.map((d) => [d.name, Math.random() * 101])
        window.heatfull = {
          cols: [
            { name: 'County', type: 'string' },
            { name: 'Unit Sold', type: 'int' }
          ],
          rows
        }
      } catch {
        throw new Error('Cannot fetch data')
      }
    },
    async randomDataHeatMapState() {
      try {
        const { data } = await axios.get(
          'live-docs/assets/json/us-all-state.json'
        )
        const { data: states } = await axios.get(
          'live-docs/assets/json/us-state.json'
        )
        const rows = data.map((d) => {
          const codes = d.properties['hc-key'].split('-')
          const stateCode = `${codes[0]}-${codes[1]}`
          const state = states.find(
            (state) => state.properties['hc-key'] === stateCode
          )
          return [state.name, d.name, Math.random() * 101, Math.random() * 101]
        })
        window.heatstateonly = {
          cols: [
            { name: 'State', type: 'string' },
            { name: 'County', type: 'string' },
            { name: 'Unit Sold', type: 'int' }
          ],
          rows
        }
      } catch {
        throw new Error('Cannot fetch data')
      }
    }
  },
  mounted() {
    this.changeConfig()
  },
  data() {
    return {
      dataSource: 'idreportingsdk',
      template1: `<cbpo-element-chart ref="elements" class="p-0" config-ref="config"></cbpo-element-chart>`,
      template2: `<cbpo-element-gauge ref="elements" class="p-0" config-ref="config"></cbpo-element-gauge>`,
      templateHeatMap: `
              <h5 >All County</h5><cbpo-element-heat-map ref="elements" class="p-0" config-ref="configFull"></cbpo-element-heat-map>
              <h5 >States</h5><cbpo-element-heat-map ref="elements" class="p-0" config-ref="configStateOnly"></cbpo-element-heat-map>`,
      config1: {
        dataSource: 'idreportingsdk',
        widget: {
          title: {
            text: 'Widget Title',
            enabled: false
          }
        },
        drillDown: {
          enabled: true,
          config: {
            path: {
              enabled: true,
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
        library: 'highcharts',
        columns: [
          {
            name: 'Region',
            displayName: 'Region',
            type: 'string',
            format: null,
            aggrFormats: null
          },
          {
            name: 'Total Cost',
            displayName: 'Total Cost',
            type: 'int',
            format: null,
            aggrFormats: null
          }
        ],
        sizeSettings: {
          defaultMinSize: 250,
          warningText: 'The area is too small for this visualization.'
        },
        charts: [
          {
            margin: {},
            axis: {
              x: [
                {
                  id: 'x_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce',
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
                  id: 'y_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce',
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
            options: {
              legend: {
                enabled: true,
                position: 'right'
              },
              pie: {
                type: 'pie'
              },
              borderWidth: 0,
              // pointPadding: -0.3

            },
        
            series: [
              {
                type: 'pie',
                name: 'Region (Sum)',
                axis: {
                  x: 'x_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce',
                  y: 'y_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce'
                },
                options: {
               
                },

                data: {
                  x: 'Region',
                  y: 'Total Cost'
                },
                id: 'id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce'
              }
            ]
          }
        ],
        sorting: [],
        grouping: {
          aggregations: [
            {
              column: 'Total Cost',
              aggregation: 'sum',
              alias: 'Total Cost_sum_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce'
            }
          ],
          columns: [
            {
              name: 'Region'
            }
          ]
        },
        bins: [],
        pagination: {
          limit: 1000,
          current: 1,
          type: 'buttons'
        },
        color_scheme: 'Google',
        formats: {
          aggrs: {}
        },
        messages: {
          no_data_at_all: 'No data',
          no_data_found: 'No data found'
        },
        id: 'id-fc41b741-f7c4-43b5-8b8c-194c15083129'
      },
      config2: {
        dataSource: 'idreportingsdk',
        widget: {
          title: {
            text: '',
            enabled: false
          }
        },
        library: 'highcharts',
        columns: [
          {
            name: 'Units Sold',
            displayName: 'Units Sold',
            type: 'int',
            format: null,
            aggrFormats: null
          },
          {
            name: 'Unit Cost',
            displayName: 'Unit Cost',
            type: 'double',
            format: null,
            aggrFormats: null
          },
          {
            name: 'Country',
            displayName: 'Country',
            type: 'string',
            format: null,
            aggrFormats: null
          }
        ],
        sizeSettings: {
          defaultMinSize: 250,
          warningText: 'The area is too small for this visualization.'
        },
        charts: [
          {
            margin: {},
            axis: {
              x: [
                {
                  id: 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
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
                  id: 'y_id-57441788-faad-4618-9ab5-98755c4444c7',
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
            options: {
              legend: {
                enabled: true,
                position: 'bottom'
              },
              radius: {
                scale: 24
              }
            },
            series: [
              {
                type: 'bubble',
                name: 'Unit Cost (Count)',
                axis: {
                  x: 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
                  y: 'y_id-57441788-faad-4618-9ab5-98755c4444c7'
                },
                options: {},
                data: {
                  x: 'Units Sold',
                  y: 'Unit Cost',
                  z: 'Country'
                },
                id: 'id-57441788-faad-4618-9ab5-98755c4444c7'
              }
            ]
          }
        ],
        sorting: [],
        grouping: {
          columns: [
            {
              name: 'Units Sold'
            },
            {
              name: 'Unit Cost'
            }
          ],
          aggregations: [
            {
              column: 'Country',
              aggregation: 'count',
              alias: 'Country_count_id-57441788-faad-4618-9ab5-98755c4444c7'
            }
          ]
        },
        bins: [],
        pagination: {
          limit: 1000,
          current: 1,
          type: 'buttons'
        },
        color_scheme: 'Google',
        formats: {
          aggrs: {}
        },
        messages: {
          no_data_at_all: 'No data',
          no_data_found: 'No data found'
        },
        id: 'id-3a71f383-9765-4f9a-a146-d5080a3643dd'
      },
      config3: {
        dataSource: 'idreportingsdk',
        widget: {
          title: {
            text: '',
            enabled: false
          }
        },
        library: 'highcharts',
        columns: [
          {
            name: 'Unit Price',
            displayName: 'Unit Price',
            type: 'double',
            format: null,
            aggrFormats: null
          },
          {
            name: 'Units Sold',
            displayName: 'Units Sold',
            type: 'int',
            format: null,
            aggrFormats: null
          }
        ],
        sizeSettings: {
          defaultMinSize: 250,
          warningText: 'The area is too small for this visualization.'
        },
        charts: [
          {
            margin: {},
            axis: {
              x: [
                {
                  id: 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
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
                  id: 'y_id-57441788-faad-4618-9ab5-98755c4444c7',
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
            options: {
              legend: {
                enabled: true,
                position: 'bottom'
              }
            },
            series: [
              {
                type: 'scatter',
                name: 'Units Sold (Sum)',
                axis: {
                  x: 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
                  y: 'y_id-57441788-faad-4618-9ab5-98755c4444c7',
                  z: null
                },
                options: {},
                data: {
                  x: 'Unit Price',
                  y: 'Units Sold'
                },
                id: 'id-57441788-faad-4618-9ab5-98755c4444c7'
              }
            ]
          }
        ],
        sorting: [],
        grouping: {
          columns: [],
          aggregations: []
        },
        bins: [],
        pagination: {
          limit: 1000,
          current: 1,
          type: 'buttons'
        },
        color_scheme: 'Google',
        formats: {
          aggrs: {}
        },
        messages: {
          no_data_at_all: 'No data',
          no_data_found: 'No data found'
        },
        id: 'id-36feebf7-c46c-45a6-b1af-0dd05274c82f'
      },
      config4: {
        dataSource: 'idreportingsdk',
        widget: {
          title: {
            text: '',
            enabled: false
          }
        },
        library: 'highcharts',
        columns: [
          {
            name: 'Units Sold',
            displayName: 'Units Sold',
            type: 'int',
            format: null,
            aggrFormats: null
          },
          {
            name: 'Unit Cost',
            displayName: 'Unit Cost',
            type: 'double',
            format: null,
            aggrFormats: null
          },
          {
            name: 'Country',
            displayName: 'Country',
            type: 'string',
            format: null,
            aggrFormats: null
          },
          {
            name: 'Unit Price',
            displayName: 'Unit Price',
            type: 'double',
            format: null,
            aggrFormats: null
          }
        ],
        sizeSettings: {
          defaultMinSize: 250,
          warningText: 'The area is too small for this visualization.'
        },
        charts: [
          {
            margin: {},
            axis: {
              x: [
                {
                  id: 'x_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
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
                  id: 'y_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
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
                },
                {
                  id: 'y_id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc',
                  type: 'linear',
                  format: null,
                  position: 'right',
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
            options: {
              legend: {
                enabled: true,
                position: 'bottom'
              },
              stacking: '',
              isHorizontal: false
            },
            series: [
              {
                type: 'bar',
                name: 'Unit Cost (Sum)',
                axis: {
                  x: 'x_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
                  y: 'y_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640'
                },
                options: {
                    
                },
                data: {
                  x: 'Country',
                  y: 'Unit Cost'
                },
                id: 'id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640'
              },
              {
                type: 'line',
                name: 'Unit Price (Sum)',
                axis: {
                  x: 'x_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
                  y: 'y_id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc'
                },
                options: {
                  stacking: '',
                  isHorizontal: false
                },
                data: {
                  x: 'Country',
                  y: 'Unit Price'
                },
                id: 'id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc'
              }
            ]
          }
        ],
        sorting: [],
        grouping: {
          aggregations: [
            {
              column: 'Unit Cost',
              aggregation: 'sum',
              alias: 'Unit Cost_sum_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640'
            },
            {
              column: 'Unit Price',
              aggregation: 'sum',
              alias: 'Unit Price_sum_id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc'
            }
          ],
          columns: [
            {
              name: 'Country'
            }
          ]
        },
        bins: [],
        pagination: {
          limit: 1000,
          current: 1,
          type: 'buttons'
        },
        color_scheme: 'Google',
        formats: {
          aggrs: {}
        },
        messages: {
          no_data_at_all: 'No data',
          no_data_found: 'No data found'
        },
        id: 'id-77ce8b7e-3839-48c5-bbf3-abad2fc1c719'
      },
      config5: {
        dataSource: 'idreportingsdk',
        widget: {
          title: {
            enabled: false,
            text: 'Widget Title'
          }
        },
        library: 'highcharts',
        columns: [
          {
            name: 'Units Sold',
            displayName: 'Units Sold',
            type: 'int',
            format: null,
            aggrFormats: null
          }
        ],
        sizeSettings: {
          defaultMinSize: 250,
          warningText: 'The area is too small for this visualization.'
        },
        charts: [
          {
            margin: {},
            axis: {
              x: [],
              y: [
                {
                  id: 'y_id-a247d092-f3ab-44b8-a7fa-f8a3d3cf6feb',
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
                  },
                  plotBands: [
                    {
                      from: 0,
                      to: 251306.79,
                      color: '#666'
                    },
                    {
                      from: 251306.79,
                      to: 466712.61,
                      color: '#999'
                    },
                    {
                      from: 466712.61,
                      to: 718019.4,
                      color: '#bbb'
                    }
                  ]
                }
              ]
            },
            options: {
              legend: {
                enabled: true,
                position: 'bottom',
                width_percent: 40
              }
            },
            series: [
              {
                type: 'bulletgauge',
                name: 'Units Sold (Sum)',
                axis: {
                  y: 'y_id-a247d092-f3ab-44b8-a7fa-f8a3d3cf6feb'
                },
                options: {
                  title: 'Units Sold (sum)'
                },
                data: {
                  x: null,
                  y: 'Units Sold'
                },
                id: 'id-a247d092-f3ab-44b8-a7fa-f8a3d3cf6feb'
              }
            ]
          }
        ],
        sorting: [],
        grouping: {
          aggregations: [
            {
              column: 'Units Sold',
              aggregation: 'sum',
              alias: 'Units Sold_sum_id-a247d092-f3ab-44b8-a7fa-f8a3d3cf6feb'
            }
          ],
          columns: []
        },
        bins: [],
        pagination: {
          limit: 1000,
          current: 1,
          type: 'buttons'
        },
        color_scheme: 'Google',
        formats: {
          aggrs: {}
        },
        messages: {
          no_data_at_all: 'No data',
          no_data_found: 'No data found'
        },
        id: 'id-9d23cc5b-cd4f-4a38-bff4-01a5ce4e4d22'
      },
      configHeatFull: {
        dataSource: 'heatfull',
        columns: [
          { name: 'County', displayName: 'County' },
          {
            name: 'Unit Sold',
            displayName: 'Unit Sold',
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
        charts: [
          {
            axis: {
              y: [
                {
                  id: 'y0',
                  ticks: {
                    maxTicksLimit: 5
                  }
                }
              ]
            },
            options: {
              mapNavigation: {
                enabled: false
              }
            },
            series: [
              {
                id: '123',
                type: 'heat-map',
                axis: {
                  x: 'x0',
                  y: 'y0'
                },
                data: {
                  x: 'County',
                  y: 'Unit Sold',
                  // reference link: https://code.highcharts.com/mapdata/
                  country: {
                    geo: 'us',
                    geoDetail: 'us-all'
                  }
                }
              }
            ]
          }
        ]
      },
      configHeatStateOnly: {
        dataSource: 'pf:d3878348-3834-4165-a772-cc91275bdc84:sale_items',
        columns: [
          { name: 'state_key', displayName: 'State' },
          {
            name: 'quantity',
            displayName: 'Quantity',
            format: { type: 'numeric', config: { precision: 0 } }
          }
        ],
        drillDown: {
          enabled: true,
          path: {
            settings: [
              {
                column: 'county_key',
                displayName: 'County'
              }
            ]
          }
        },
        grouping: {
          columns: [{ name: 'state_key' }],
          aggregations: [
            {
              column: 'quantity',
              alias: 'quantity_sum_123',
              aggregation: 'sum'
            }
          ]
        },
        charts: [
          {
            axis: {
              y: [
                {
                  id: 'y0',
                  ticks: {
                    maxTicksLimit: 5
                  }
                }
              ]
            },
            series: [
              {
                id: '123',
                type: 'heat-map',
                axis: {
                  x: 'x0',
                  y: 'y0'
                },
                data: {
                  x: 'state_key',
                  y: 'quantity',
                  // reference link: https://code.highcharts.com/mapdata/
                  country: {
                    geo: 'us',
                    geoDetail: 'us'
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
})
