const sdkChartjsDemoPage = Vue.component('sdkChartjsDemoPage', {
  template: `
    <div>
      <h5>Example: </h5>
      <div style="height: 40em" id="chart-demo">
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
    changeConfig() {
      let type = this.$route.path.split('-')[1]
      let config = _.cloneDeep(this.config1)
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
        default:
          break
      }
      config.charts[0].series[0].type = type
      config.dataSource = this.dataSource
      window.config = config
      this.render('#chart-demo', this.template, 'http://ds-api.qa.channelprecision.com/v1/', this.VUE_DEMO_TOKEN, '')
    }
  },
  mounted() {
    this.changeConfig()
  },
  data() {
    return {
      dataSource: 'idreportingsdk',
      template: `<cbpo-element-chart ref="elements" class="p-0" config-ref="config"></cbpo-element-chart>`,
      config1: {
        'dataSource': 'idreportingsdk',
        'widget': {
          'title': {
            'text': 'Widget Title',
            'enabled': false
          }
        },
        'library': 'chartjs',
        'columns': [
          {
            'name': 'Country',
            'displayName': 'Country',
            'type': 'string',
            'format': null,
            'aggrFormats': null
          },
          {
            'name': 'Item Type',
            'displayName': 'Item Type',
            'type': 'string',
            'format': null,
            'aggrFormats': null
          }
        ],
        'sizeSettings': {
          'defaultMinSize': 250,
          'warningText': 'The area is too small for this visualization.'
        },
        'charts': [
          {
            'margin': {},
            'axis': {
              'x': [
                {
                  'id': 'x_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce',
                  'type': 'category',
                  'display': true,
                  'format': null,
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  },
                  'ticks': {
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  }
                }
              ],
              'y': [
                {
                  'id': 'y_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce',
                  'type': 'linear',
                  'format': null,
                  'position': 'left',
                  'stack': false,
                  'ticks': {
                    'beginAtZero': true,
                    'stepSize': '',
                    'maxTicksLimit': 5,
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  },
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  }
                }
              ]
            },
            'options': {
              'legend': {
                'enabled': true,
                'position': 'right'
              },
              'pie': {
                'type': 'pie'
              },
              'borderWidth': 0
            },
            'series': [
              {
                'type': 'pie',
                'name': 'Item Type (Count)',
                'axis': {
                  'x': 'x_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce',
                  'y': 'y_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce'
                },
                'options': {},
                'data': {
                  'x': 'Country',
                  'y': 'Item Type'
                },
                'id': 'id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce'
              }
            ]
          }
        ],
        'sorting': [],
        'grouping': {
          'aggregations': [
            {
              'column': 'Item Type',
              'aggregation': 'count',
              'alias': 'Item Type_count_id-8d7b2b9d-d87c-43f6-801a-e4616cfc26ce'
            }
          ],
          'columns': [
            {
              'name': 'Country'
            }
          ]
        },
        'bins': [],
        'pagination': {
          'limit': 1000,
          'current': 1,
          'type': 'buttons'
        },
        'color_scheme': 'Google',
        'formats': {
          'aggrs': {}
        },
        'messages': {
          'no_data_at_all': 'No data',
          'no_data_found': 'No data found'
        },
        'id': 'id-fc41b741-f7c4-43b5-8b8c-194c15083129'
      },
      config2: {
        'dataSource': 'idreportingsdk',
        'widget': {
          'title': {
            'text': '',
            'enabled': false
          }
        },
        'library': 'chartjs',
        'columns': [
          {
            'name': 'Units Sold',
            'displayName': 'Units Sold',
            'type': 'int',
            'format': null,
            'aggrFormats': null
          },
          {
            'name': 'Unit Cost',
            'displayName': 'Unit Cost',
            'type': 'double',
            'format': null,
            'aggrFormats': null
          },
          {
            'name': 'Country',
            'displayName': 'Country',
            'type': 'string',
            'format': null,
            'aggrFormats': null
          }
        ],
        'sizeSettings': {
          'defaultMinSize': 250,
          'warningText': 'The area is too small for this visualization.'
        },
        'charts': [
          {
            'margin': {},
            'axis': {
              'x': [
                {
                  'id': 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
                  'type': 'category',
                  'display': true,
                  'format': null,
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  },
                  'ticks': {
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  }
                }
              ],
              'y': [
                {
                  'id': 'y_id-57441788-faad-4618-9ab5-98755c4444c7',
                  'type': 'linear',
                  'format': null,
                  'position': 'left',
                  'stack': false,
                  'ticks': {
                    'beginAtZero': true,
                    'stepSize': '',
                    'maxTicksLimit': 5,
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  },
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  }
                }
              ]
            },
            'options': {
              'legend': {
                'enabled': true,
                'position': 'bottom'
              },
              'radius': {
                'scale': 24
              }
            },
            'series': [
              {
                'type': 'bubble',
                'name': 'Unit Cost (Count)',
                'axis': {
                  'x': 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
                  'y': 'y_id-57441788-faad-4618-9ab5-98755c4444c7'
                },
                'options': {},
                'data': {
                  'x': 'Units Sold',
                  'y': 'Unit Cost',
                  'z': 'Country'
                },
                'id': 'id-57441788-faad-4618-9ab5-98755c4444c7'
              }
            ]
          }
        ],
        'sorting': [],
        'grouping': {
          'columns': [
            {
              'name': 'Units Sold'
            },
            {
              'name': 'Unit Cost'
            }
          ],
          'aggregations': [
            {
              'column': 'Country',
              'aggregation': 'count',
              'alias': 'Country_count_id-57441788-faad-4618-9ab5-98755c4444c7'
            }
          ]
        },
        'bins': [],
        'pagination': {
          'limit': 1000,
          'current': 1,
          'type': 'buttons'
        },
        'color_scheme': 'Google',
        'formats': {
          'aggrs': {}
        },
        'messages': {
          'no_data_at_all': 'No data',
          'no_data_found': 'No data found'
        },
        'id': 'id-3a71f383-9765-4f9a-a146-d5080a3643dd'
      },
      config3: {
        'dataSource': 'idreportingsdk',
        'widget': {
          'title': {
            'text': '',
            'enabled': false
          }
        },
        'library': 'chartjs',
        'columns': [
          {
            'name': 'Unit Price',
            'displayName': 'Unit Price',
            'type': 'double',
            'format': null,
            'aggrFormats': null
          },
          {
            'name': 'Units Sold',
            'displayName': 'Units Sold',
            'type': 'int',
            'format': null,
            'aggrFormats': null
          }
        ],
        'sizeSettings': {
          'defaultMinSize': 250,
          'warningText': 'The area is too small for this visualization.'
        },
        'charts': [
          {
            'margin': {},
            'axis': {
              'x': [
                {
                  'id': 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
                  'type': 'category',
                  'display': true,
                  'format': null,
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  },
                  'ticks': {
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  }
                }
              ],
              'y': [
                {
                  'id': 'y_id-57441788-faad-4618-9ab5-98755c4444c7',
                  'type': 'linear',
                  'format': null,
                  'position': 'left',
                  'stack': false,
                  'ticks': {
                    'beginAtZero': true,
                    'stepSize': '',
                    'maxTicksLimit': 5,
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  },
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  }
                }
              ]
            },
            'options': {
              'legend': {
                'enabled': true,
                'position': 'bottom'
              }
            },
            'series': [
              {
                'type': 'scatter',
                'name': 'Units Sold (Sum)',
                'axis': {
                  'x': 'x_id-57441788-faad-4618-9ab5-98755c4444c7',
                  'y': 'y_id-57441788-faad-4618-9ab5-98755c4444c7',
                  'z': null
                },
                'options': {},
                'data': {
                  'x': 'Unit Price',
                  'y': 'Units Sold'
                },
                'id': 'id-57441788-faad-4618-9ab5-98755c4444c7'
              }
            ]
          }
        ],
        'sorting': [],
        'grouping': {
          'columns': [],
          'aggregations': []
        },
        'bins': [],
        'pagination': {
          'limit': 1000,
          'current': 1,
          'type': 'buttons'
        },
        'color_scheme': 'Google',
        'formats': {
          'aggrs': {}
        },
        'messages': {
          'no_data_at_all': 'No data',
          'no_data_found': 'No data found'
        },
        'id': 'id-36feebf7-c46c-45a6-b1af-0dd05274c82f'
      },
      config4: {
        'dataSource': 'idreportingsdk',
        'widget': {
          'title': {
            'text': '',
            'enabled': false
          }
        },
        'library': 'chartjs',
        'columns': [
          {
            'name': 'Units Sold',
            'displayName': 'Units Sold',
            'type': 'int',
            'format': null,
            'aggrFormats': null
          },
          {
            'name': 'Unit Cost',
            'displayName': 'Unit Cost',
            'type': 'double',
            'format': null,
            'aggrFormats': null
          },
          {
            'name': 'Country',
            'displayName': 'Country',
            'type': 'string',
            'format': null,
            'aggrFormats': null
          },
          {
            'name': 'Unit Price',
            'displayName': 'Unit Price',
            'type': 'double',
            'format': null,
            'aggrFormats': null
          }
        ],
        'sizeSettings': {
          'defaultMinSize': 250,
          'warningText': 'The area is too small for this visualization.'
        },
        'charts': [
          {
            'margin': {},
            'axis': {
              'x': [
                {
                  'id': 'x_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
                  'type': 'category',
                  'display': true,
                  'format': null,
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  },
                  'ticks': {
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  }
                }
              ],
              'y': [
                {
                  'id': 'y_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
                  'type': 'linear',
                  'format': null,
                  'position': 'left',
                  'stack': false,
                  'ticks': {
                    'beginAtZero': true,
                    'stepSize': '',
                    'maxTicksLimit': 5,
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  },
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  }
                },
                {
                  'id': 'y_id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc',
                  'type': 'linear',
                  'format': null,
                  'position': 'right',
                  'stack': false,
                  'ticks': {
                    'beginAtZero': true,
                    'stepSize': '',
                    'maxTicksLimit': 5,
                    'fontColor': '#666',
                    'fontSize': 11,
                    'fontStyle': 'bold'
                  },
                  'scaleLabel': {
                    'display': false,
                    'labelString': ''
                  }
                }
              ]
            },
            'options': {
              'legend': {
                'enabled': true,
                'position': 'bottom'
              },
              'stacking': '',
              'isHorizontal': false
            },
            'series': [
              {
                'type': 'bar',
                'name': 'Unit Cost (Sum)',
                'axis': {
                  'x': 'x_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
                  'y': 'y_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640'
                },
                'options': {},
                'data': {
                  'x': 'Country',
                  'y': 'Unit Cost'
                },
                'id': 'id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640'
              },
              {
                'type': 'line',
                'name': 'Unit Price (Sum)',
                'axis': {
                  'x': 'x_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640',
                  'y': 'y_id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc'
                },
                'options': {
                  'stacking': '',
                  'isHorizontal': false
                },
                'data': {
                  'x': 'Country',
                  'y': 'Unit Price'
                },
                'id': 'id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc'
              }
            ]
          }
        ],
        'sorting': [],
        'grouping': {
          'aggregations': [
            {
              'column': 'Unit Cost',
              'aggregation': 'sum',
              'alias': 'Unit Cost_sum_id-0e5e5fe3-cdde-49ae-b144-67e9da7fe640'
            },
            {
              'column': 'Unit Price',
              'aggregation': 'sum',
              'alias': 'Unit Price_sum_id-1c5c462f-1197-4ab1-99f1-db7d2001e2dc'
            }
          ],
          'columns': [
            {
              'name': 'Country'
            }
          ]
        },
        'bins': [],
        'pagination': {
          'limit': 1000,
          'current': 1,
          'type': 'buttons'
        },
        'color_scheme': 'Google',
        'formats': {
          'aggrs': {}
        },
        'messages': {
          'no_data_at_all': 'No data',
          'no_data_found': 'No data found'
        },
        'id': 'id-77ce8b7e-3839-48c5-bbf3-abad2fc1c719'
      }
    }
  }
})
