const sdkVisualizationPage = Vue.component('sdkVisualizationPage', {
  template: `
    <div class="visualization">
      <h5>Example: </h5>
      <sdkliveDataSource :state="state"
                         :need-validation="false"
                         :get-button="true"
                         @get="changeDataSource($event)"/>
      <div id="visualization">
      </div>
      <sdk-export-code :templates="getTemplate"/>
    </div>
  `,
  data() {
    let dataSource = 'idreportingsdk' // 'elasticsearch-demo-5k-records'
    return {
      state: {
        baseURL: 'http://ds-api.qa.channelprecision.com/v1/',
        token: this.VUE_DEMO_TOKEN,
        clientId: '',
        dataSource: dataSource
      },
      template: '<cbpo-visualization class="p-0" config-ref="config"></cbpo-visualization>',
      config: {
        dataSource: dataSource,
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
          },
          editBin: {
            enabled: true
          }
        },
        templates: [
          {
            'config': {
              'grid': { 'x': 0, 'y': 0, 'w': 12, 'h': 4, 'i': 0 },
              'autoHeight': false,
              'widget': { 'title': { 'text': 'Quantitation of [Units Sold] over [Region]', 'enabled': true, 'edited': false }, 'style': { 'background_color': null, 'foreground_color': null, 'header_background_color': null, 'header_foreground_color': null, 'border_width': null, 'border_radius': null } },
              'action': { 'elements': [] },
              'elements': [{ 'type': 'cbpo-element-heat-map', 'config': { 'dataSource': 'idreportingsdk', 'widget': { 'title': { 'enabled': false, 'text': 'Quantitation of [Units Sold] over [Region]', 'edited': false }, 'style': { 'background_color': null, 'foreground_color': null, 'header_background_color': null, 'header_foreground_color': null, 'border_width': null, 'border_radius': null } }, 'columns': [{ 'name': 'Region', 'displayName': 'Region', 'type': 'string', 'format': null, 'aggrFormats': null }, { 'name': 'Units Sold', 'displayName': 'Units Sold', 'type': 'number', 'format': null, 'aggrFormats': null }], 'drillDown': { 'enabled': false, 'path': { 'settings': [] } }, 'sizeSettings': { 'defaultMinSize': 250, 'warningText': 'The area is too small for this visualization.' }, 'charts': [{ 'axis': { 'x': [{ 'id': 'x_bee499ff-7062-4323-8975-349551048494', 'format': null }], 'y': [{ 'id': 'y_bee499ff-7062-4323-8975-349551048494', 'axisLabelColor': null, 'axisGridColor': null, 'ticks': { 'maxTicksLimit': 5, 'minColor': '#F1EEF6', 'maxColor': '#500007', 'format': null } }] }, 'options': { 'mapNavigation': { 'enabled': true }, 'labelDrillUpButton': null, 'gridBorderColor': null, 'dataLabelColor': null, 'legend': { 'enabled': true, 'isHorizontal': true, 'position': 'right' } }, 'series': [{ 'id': 'bee499ff-7062-4323-8975-349551048494', 'type': 'heat-map', 'axis': { 'x': 'x_bee499ff-7062-4323-8975-349551048494', 'y': 'y_bee499ff-7062-4323-8975-349551048494' }, 'data': { 'x': 'Region', 'y': 'Units Sold', 'name': '', 'country': { 'geo': 'us', 'geoDetail': 'us' } }, 'name': 'Units Sold (Sum)' }] }], 'sorting': [], 'grouping': { 'aggregations': [{ 'column': 'Units Sold', 'aggregation': 'sum', 'alias': 'Units Sold_sum_bee499ff-7062-4323-8975-349551048494' }], 'columns': [{ 'name': 'Region' }] }, 'bins': [], 'pagination': { 'limit': 99999, 'current': 1, 'total': null, 'type': 'auto', 'buttons': { 'first': { 'visibility': true, 'label': 'First', 'style': {} }, 'last': { 'visibility': true, 'label': 'Last', 'style': {} }, 'prev': { 'visibility': true, 'label': 'Previous', 'style': {} }, 'next': { 'visibility': true, 'label': 'Next', 'style': {} } }, 'numbers': { 'beforeCurrent': 2, 'afterCurrent': 2 }, 'default': 'auto' }, 'messages': { 'no_data_at_all': 'No data', 'no_data_found': 'No data found' }, 'timezone': { 'enabled': false, 'utc': null, 'visible': true }, 'library': 'highcharts', 'id': 'id-8cc18030-69c1-4ed0-bb15-3304fc40869a' } }],
              'filter': { 'form': { 'config': { 'controls': [], 'query': {} } }, 'base': { 'config': { 'query': {} } }, 'builder': { 'enabled': false, 'readable': { 'enabled': false }, 'config': { 'trigger': { 'label': 'Setting Filter' }, 'modal': { 'title': 'Query Builder' }, 'format': { 'temporal': {} }, 'threshold': { 'maxLevel': 5 }, 'ignore': { 'global': { 'visible': false, 'value': false }, 'base': { 'visible': false, 'value': false } }, 'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] }, 'form': { 'columns': [] } } }, 'globalFilter': { 'enabled': false }, 'alignment': '' },
              'columnManager': { 'enabled': false, 'config': { 'trigger': { 'label': 'Manage Columns' }, 'modal': { 'title': 'Manage Columns' }, 'hiddenColumns': [], 'managedColumns': [] } },
              'calculatedColumn': { 'enabled': false },
              'menu': { 'enabled': true, 'config': {} },
              'waitingForGlobalFilter': false
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-10T10:31:15.037Z'
          },
          {
            'config': {
              'grid': {
                'x': 6,
                'y': 113,
                'w': 6,
                'h': 39,
                'i': 5,
                'moved': false
              },
              'autoHeight': false,
              'widget': {
                'title': {
                  'text': 'Marketing (Monthly)',
                  'enabled': true,
                  'edited': true
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                },
                'id': 'id-3713844b-9435-4cad-8f80-2d2d09f3a65f',
                'class': ''
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-chart',
                  'config': {
                    'dataSource': '08f4603c-5656-4301-b8d5-c5bddaa804de',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Quantitation of [sales, acos] over [date]',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [
                      {
                        'name': 'date',
                        'displayName': 'Date',
                        'type': 'date',
                        'format': {
                          'common': {
                            'plain': {
                              'nil': 'NULL',
                              'empty': 'EMPTY',
                              'na': 'N/A'
                            },
                            'html': {
                              'nil': '<span class="d-sdk-nil">null</span>',
                              'empty': '<span class="d-sdk-empty">empty</span>',
                              'na': '<span class="d-sdk-na">N/A</span>'
                            },
                            'prefix': null,
                            'suffix': null
                          },
                          'type': 'temporal',
                          'config': {
                            'format': 'MMM YY',
                            'date': {
                              'format': 'MMM YY'
                            },
                            'time': {
                              'format': ''
                            },
                            'options': {
                              'year': 'YYYY',
                              'quarter': 'YYYY [Q]Q',
                              'month': 'YYYY MMM',
                              'week': 'YYYY [w]w',
                              'day': 'YYYY-MM-DD',
                              'hour': 'YYYY-MM-DD kk',
                              'minute': 'YYYY-MM-DD kk:mm',
                              'second': 'YYYY-MM-DD kk:mm:ss'
                            }
                          }
                        },
                        'aggrFormats': null
                      },
                      {
                        'name': 'sales',
                        'displayName': 'Sales',
                        'type': 'double',
                        'format': {
                          'common': {
                            'plain': {
                              'nil': 'NULL',
                              'empty': 'EMPTY',
                              'na': 'N/A'
                            },
                            'html': {
                              'nil': '<span class="d-sdk-nil">null</span>',
                              'empty': '<span class="d-sdk-empty">empty</span>',
                              'na': '<span class="d-sdk-na">N/A</span>'
                            },
                            'prefix': '$',
                            'suffix': null
                          },
                          'type': 'numeric',
                          'config': {
                            'comma': true,
                            'precision': 0,
                            'siPrefix': false
                          }
                        },
                        'aggrFormats': null
                      },
                      {
                        'name': 'spend',
                        'displayName': 'Spend',
                        'type': 'double',
                        'format': {
                          'common': {
                            'plain': {
                              'nil': 'NULL',
                              'empty': 'EMPTY',
                              'na': 'N/A'
                            },
                            'html': {
                              'nil': '<span class="d-sdk-nil">null</span>',
                              'empty': '<span class="d-sdk-empty">empty</span>',
                              'na': '<span class="d-sdk-na">N/A</span>'
                            },
                            'prefix': '$',
                            'suffix': null
                          },
                          'type': 'numeric',
                          'config': {
                            'comma': true,
                            'precision': 0,
                            'siPrefix': false
                          }
                        },
                        'aggrFormats': null
                      },
                      {
                        'name': 'acos',
                        'displayName': 'ACoS',
                        'type': 'double',
                        'format': {
                          'common': {
                            'plain': {
                              'nil': 'NULL',
                              'empty': 'EMPTY',
                              'na': 'N/A'
                            },
                            'html': {
                              'nil': '<span class="d-sdk-nil">null</span>',
                              'empty': '<span class="d-sdk-empty">empty</span>',
                              'na': '<span class="d-sdk-na">N/A</span>'
                            },
                            'prefix': null,
                            'suffix': '%'
                          },
                          'type': 'progress',
                          'config': {
                            'visualization': 'percentage',
                            'base': '1'
                          }
                        },
                        'aggrFormats': null
                      }
                    ],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [
                      {
                        'axis': {
                          'x': [
                            {
                              'id': 'x_id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d',
                              'type': 'category',
                              'display': true,
                              'format': null,
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'ticks': {
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              }
                            }
                          ],
                          'y': [
                            {
                              'id': 'y_id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d',
                              'type': 'linear',
                              'format': null,
                              'position': 'left',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              },
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              }
                            },
                            {
                              'id': 'y_id-802d266c-dc24-441a-bcd2-3c230ddf7425',
                              'type': 'linear',
                              'format': null,
                              'position': 'right',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
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
                            'position': 'top',
                            'widthPercent': 40,
                            'isHorizontal': true
                          },
                          'stacking': true,
                          'isHorizontal': false
                        },
                        'series': [
                          {
                            'type': 'bar',
                            'name': 'Spend',
                            'axis': {
                              'x': 'x_id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d',
                              'y': 'y_id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d'
                            },
                            'data': {
                              'x': 'date',
                              'y': 'spend'
                            },
                            'id': 'id-d5a06342-7199-4f58-b2e7-9ad02445510d'
                          },
                          {
                            'type': 'bar',
                            'name': 'Sales',
                            'axis': {
                              'x': 'x_id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d',
                              'y': 'y_id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d'
                            },
                            'data': {
                              'x': 'date',
                              'y': 'sales'
                            },
                            'id': 'id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d'
                          },
                          {
                            'type': 'line',
                            'name': 'ACoS',
                            'axis': {
                              'x': 'x_id-802d266c-dc24-441a-bcd2-3c230ddf7425',
                              'y': 'y_id-802d266c-dc24-441a-bcd2-3c230ddf7425'
                            },
                            'options': {
                              'stacking': '',
                              'isHorizontal': false
                            },
                            'data': {
                              'x': 'date',
                              'y': 'acos'
                            },
                            'id': 'id-802d266c-dc24-441a-bcd2-3c230ddf7425'
                          }
                        ]
                      }
                    ],
                    'sorting': [
                      {
                        'column': 'date',
                        'direction': 'asc'
                      }
                    ],
                    'grouping': {
                      'aggregations': [
                        {
                          'column': 'sales',
                          'aggregation': 'sum',
                          'alias': 'sales_sum_id-11c5630f-aa8b-49ac-bf9b-da2d7550a79d'
                        },
                        {
                          'column': 'spend',
                          'aggregation': 'sum',
                          'alias': 'spend_sum_id-d5a06342-7199-4f58-b2e7-9ad02445510d'
                        },
                        {
                          'column': 'acos',
                          'aggregation': 'avg',
                          'alias': 'acos_sum_id-802d266c-dc24-441a-bcd2-3c230ddf7425'
                        }
                      ],
                      'columns': [
                        {
                          'name': 'date'
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
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'id': '3af415da-b11b-4135-9560-1149a642dc70'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': false,
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  },
                  'readable': {
                    'enabled': false
                  }
                },
                'globalFilter': {
                  'enabled': false
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': false,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  },
                  'id': 'id-c0a7e368-aa06-4bbd-baed-11beb11292a2',
                  'widget': {
                    'title': {
                      'enabled': true,
                      'text': ''
                    },
                    'class': ''
                  }
                }
              },
              'waitingForGlobalFilter': false,
              'id': 'id-01626923-2081-4050-b406-f0d01c506e93',
              'editMode': true,
              'calculatedColumn': {
                'enabled': false
              }
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-10T10:31:15.037Z'
          },
          {
            'config': {
              'grid': {
                'x': 6,
                'y': 57,
                'w': 6,
                'h': 34,
                'i': 4,
                'moved': false
              },
              'autoHeight': false,
              'widget': {
                'title': {
                  'text': 'Arbitrage',
                  'enabled': true,
                  'edited': true
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                },
                'id': 'id-31738494-c98b-4051-970c-15540239f982',
                'class': ''
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-chart',
                  'config': {
                    'dataSource': 'b3d0081e-973c-41d1-9548-070b279402c3',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Quantitation of [total] over [arbitrage_status]',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [
                      {
                        'name': 'arbitrage_status',
                        'displayName': 'Arbitrage Status',
                        'type': 'string',
                        'format': null,
                        'aggrFormats': null
                      },
                      {
                        'name': 'total',
                        'displayName': 'Total',
                        'type': 'int',
                        'format': {
                          'common': {
                            'plain': {
                              'nil': 'NULL',
                              'empty': 'EMPTY',
                              'na': 'N/A'
                            },
                            'html': {
                              'nil': '<span class="d-sdk-nil">null</span>',
                              'empty': '<span class="d-sdk-empty">empty</span>',
                              'na': '<span class="d-sdk-na">N/A</span>'
                            },
                            'prefix': null,
                            'suffix': null
                          },
                          'type': 'numeric',
                          'config': {
                            'comma': true,
                            'precision': 0,
                            'siPrefix': false
                          }
                        },
                        'aggrFormats': null
                      }
                    ],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [
                      {
                        'axis': {
                          'x': [
                            {
                              'id': 'x_id-ff209262-b40d-4c23-a2c5-92c818d0d239',
                              'type': 'category',
                              'display': true,
                              'format': null,
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'ticks': {
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              }
                            }
                          ],
                          'y': [
                            {
                              'id': 'y_id-ff209262-b40d-4c23-a2c5-92c818d0d239',
                              'type': 'linear',
                              'format': null,
                              'position': 'left',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
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
                            'position': 'bottom',
                            'widthPercent': 40,
                            'isHorizontal': false
                          },
                          'pie': {
                            'type': 'pie'
                          },
                          'borderWidth': 0
                        },
                        'series': [
                          {
                            'type': 'pie',
                            'name': 'Total (Sum)',
                            'axis': {
                              'x': 'x_id-ff209262-b40d-4c23-a2c5-92c818d0d239',
                              'y': 'y_id-ff209262-b40d-4c23-a2c5-92c818d0d239'
                            },
                            'data': {
                              'x': 'arbitrage_status',
                              'y': 'total'
                            },
                            'id': 'id-ff209262-b40d-4c23-a2c5-92c818d0d239'
                          }
                        ]
                      }
                    ],
                    'sorting': [
                      {
                        'column': 'arbitrage_status',
                        'direction': 'asc'
                      }
                    ],
                    'grouping': {
                      'aggregations': [
                        {
                          'column': 'total',
                          'aggregation': 'sum',
                          'alias': 'total_sum_id-ff209262-b40d-4c23-a2c5-92c818d0d239'
                        }
                      ],
                      'columns': [
                        {
                          'name': 'arbitrage_status'
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
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'id': 'a22a70a2-9042-4ca8-a269-30a4d277b7ea'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': false,
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  }
                },
                'globalFilter': {
                  'enabled': false
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': false,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  },
                  'id': 'id-f471e471-2b61-40e2-8472-9a45286ba8f3',
                  'widget': {
                    'title': {
                      'enabled': true,
                      'text': ''
                    },
                    'class': ''
                  }
                }
              },
              'waitingForGlobalFilter': false,
              'id': 'id-15679439-0a52-4d6d-95e1-fc1c733edb46',
              'editMode': true
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-10T08:10:30.074Z'
          },
          {
            'config': {
              'grid': {
                'x': 0,
                'y': 93,
                'w': 12,
                'h': 49,
                'i': 5,
                'moved': false
              },
              'autoHeight': false,
              'widget': {
                'title': {
                  'text': 'Seller Status (2 months)',
                  'enabled': true,
                  'edited': true
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                },
                'id': 'id-3803d899-ec6f-437b-a916-2ca2d5b7a8be',
                'class': ''
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-crosstab-table',
                  'config': {
                    'dataSource': 'b3d0081e-973c-41d1-9548-070b279402c3',
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'widget': {
                      'title': {
                        'text': 'Quantitation of [total] over [total, date]',
                        'enabled': false,
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'globalControlOptions': {
                      'aggregation': {
                        'enabled': false
                      },
                      'globalGrouping': {
                        'enabled': false,
                        'config': {
                          'value': false
                        }
                      },
                      'grouping': {
                        'enabled': false
                      },
                      'editColumn': {
                        'enabled': false
                      },
                      'editColumnLabel': {
                        'enabled': false
                      },
                      'editColumnFormat': {
                        'enabled': false
                      },
                      'editBin': {
                        'enabled': false
                      }
                    },
                    'bins': [],
                    'sorting': [],
                    'xColumns': [
                      {
                        'name': 'investigation',
                        'displayName': 'Investigation Status',
                        'type': 'string',
                        'format': null,
                        'sortable': {
                          'enabled': true
                        }
                      }
                    ],
                    'tColumns': [
                      {
                        'name': 'date',
                        'displayName': 'Date',
                        'type': 'date',
                        'format': {
                          'common': {
                            'plain': {
                              'nil': 'NULL',
                              'empty': 'EMPTY',
                              'na': 'N/A'
                            },
                            'html': {
                              'nil': '<span class="d-sdk-nil">null</span>',
                              'empty': '<span class="d-sdk-empty">empty</span>',
                              'na': '<span class="d-sdk-na">N/A</span>'
                            },
                            'prefix': null,
                            'suffix': null
                          },
                          'type': 'temporal',
                          'config': {
                            'format': 'MM/DD/YYYY',
                            'date': {
                              'format': 'L'
                            },
                            'time': {
                              'format': 'LT'
                            },
                            'options': {
                              'year': 'YYYY',
                              'quarter': 'YYYY [Q]Q',
                              'month': 'YYYY MMM',
                              'week': 'YYYY [w]w',
                              'day': 'YYYY-MM-DD',
                              'hour': 'YYYY-MM-DD kk',
                              'minute': 'YYYY-MM-DD kk:mm',
                              'second': 'YYYY-MM-DD kk:mm:ss'
                            }
                          }
                        },
                        'sortable': {
                          'enabled': true
                        }
                      }
                    ],
                    'yColumns': [
                      {
                        'name': 'total',
                        'displayName': 'Total',
                        'type': 'int',
                        'format': null,
                        'sortable': {
                          'enabled': true
                        },
                        'aggregation': {
                          'aggregation': 'sum',
                          'alias': 'total_a89c21c6-7d9f-43b9-85ec-15a698647540'
                        }
                      }
                    ],
                    'pagination': {
                      'limit': 10,
                      'current': 1,
                      'total': 17,
                      'type': 'auto',
                      'buttons': {
                        'first': {
                          'visibility': true,
                          'label': 'First'
                        },
                        'last': {
                          'visibility': true,
                          'label': 'Last'
                        },
                        'prev': {
                          'visibility': true,
                          'label': 'Previous'
                        },
                        'next': {
                          'visibility': true,
                          'label': 'Next'
                        }
                      },
                      'numbers': {
                        'beforeCurrent': 2,
                        'afterCurrent': 2
                      },
                      'default': 'auto',
                      'id': 'id-3561f76c-bc2f-4448-9f8d-f36fb647590a',
                      'widget': {
                        'title': {
                          'enabled': true,
                          'text': ''
                        },
                        'class': ''
                      }
                    },
                    'id': '6fb7fdbd-8aa7-46b1-9d5c-3dbfeba47979'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': [
                      {
                        'type': 'cbpo-filter-control-select',
                        'config': {
                          'label': {
                            'text': 'Status'
                          },
                          'dataSource': '',
                          'common': {
                            'id': 'id-54884e44-107a-4139-9247-9002a52a1b24',
                            'level': 1,
                            'column': {
                              'name': 'short_status',
                              'type': 'string'
                            },
                            'value': '',
                            'operator': 'contains',
                            'sort': 'asc',
                            'format': null
                          },
                          'selection': {
                            'empty': {
                              'label': 'All',
                              'value': '',
                              'enabled': true
                            },
                            'options': [
                              {
                                'label': 'New',
                                'value': 'New'
                              },
                              {
                                'label': 'Rogue',
                                'value': 'Rogue'
                              },
                              {
                                'label': 'Complied',
                                'value': 'Complied'
                              },
                              {
                                'label': 'Relisted',
                                'value': 'Relisted'
                              }
                            ]
                          },
                          'id': 'id-65243e03-ba3c-4784-8d8e-7aec499ebd49'
                        },
                        'id': 'id-feefe7c3-f146-423e-9c6a-399e486fb560'
                      }
                    ],
                    'query': {
                      'type': 'AND',
                      'conditions': [
                        {
                          'id': 'id-54884e44-107a-4139-9247-9002a52a1b24',
                          'level': 1,
                          'column': {
                            'name': 'short_status',
                            'type': 'string'
                          },
                          'value': '',
                          'operator': 'contains',
                          'sort': 'asc',
                          'format': null,
                          'empty': {
                            'label': 'All',
                            'value': '',
                            'enabled': true
                          }
                        }
                      ]
                    },
                    'id': 'id-5f5a917a-0b33-4799-b7ff-63a334de25eb'
                  }
                },
                'builder': {
                  'enabled': false,
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  }
                },
                'globalFilter': {
                  'enabled': false
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': false,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  },
                  'id': 'id-23eaa300-4982-449d-8c6c-94bc1f781f38',
                  'widget': {
                    'title': {
                      'enabled': true,
                      'text': ''
                    },
                    'class': ''
                  }
                }
              },
              'waitingForGlobalFilter': false,
              'id': 'id-6dde66c0-5708-42a8-9af5-fd5e7f460efb',
              'editMode': true
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-10T08:11:00.079Z'
          },
          {
            'config': {
              'grid': {
                'x': 0,
                'y': 0,
                'w': 12,
                'h': 4,
                'i': 0
              },
              'autoHeight': false,
              'widget': {
                'title': {
                  'text': 'Table of [OrderDate, ShipVia, ShipPostalCode, ShipCountry]',
                  'enabled': true,
                  'edited': false
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                }
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-table',
                  'config': {
                    'dataSource': '0cd5f3b9-3857-4edf-a922-d1e579cd3568',
                    'header': {
                      'draggable': false
                    },
                    'columns': [
                      {
                        'name': 'OrderDate',
                        'type': 'date',
                        'label': 'OrderDate',
                        'cell': {
                          'format': {
                            'type': 'temporal',
                            'common': {
                              'plain': {
                                'nil': 'NULL',
                                'empty': 'EMPTY',
                                'na': 'N/A'
                              },
                              'html': {
                                'nil': '<span class="d-sdk-nil">null</span>',
                                'empty': '<span class="d-sdk-empty">empty</span>',
                                'na': '<span class="d-sdk-na">N/A</span>'
                              },
                              'prefix': null,
                              'suffix': null
                            }
                          },
                          'width': 100,
                          'aggrFormats': null,
                          'binFormats': null
                        },
                        'header': {
                          'format': null
                        },
                        'sortable': {
                          'enabled': true
                        },
                        'visible': true,
                        'displayName': 'OrderDate'
                      },
                      {
                        'name': 'ShipVia',
                        'type': 'int',
                        'label': 'ShipVia',
                        'header': {
                          'format': null
                        },
                        'cell': {
                          'width': 100,
                          'format': null,
                          'aggrFormats': null,
                          'binFormats': null
                        },
                        'sortable': {
                          'enabled': true
                        },
                        'visible': true,
                        'displayName': 'ShipVia'
                      },
                      {
                        'name': 'ShipPostalCode',
                        'type': 'int',
                        'label': 'ShipPostalCode',
                        'header': {
                          'format': null
                        },
                        'cell': {
                          'width': 100,
                          'format': null,
                          'aggrFormats': null,
                          'binFormats': null
                        },
                        'sortable': {
                          'enabled': true
                        },
                        'visible': true,
                        'displayName': 'ShipPostalCode'
                      },
                      {
                        'name': 'ShipCountry',
                        'type': 'string',
                        'label': 'ShipCountry',
                        'header': {
                          'format': null
                        },
                        'cell': {
                          'width': 100,
                          'format': null,
                          'aggrFormats': null,
                          'binFormats': null
                        },
                        'sortable': {
                          'enabled': true
                        },
                        'visible': true,
                        'displayName': 'ShipCountry'
                      }
                    ],
                    'sorting': [],
                    'widget': {
                      'title': {
                        'text': 'Table of [OrderDate, ShipVia, ShipPostalCode, ShipCountry]',
                        'enabled': true,
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'globalControlOptions': {
                      'aggregation': {
                        'enabled': false
                      },
                      'globalGrouping': {
                        'enabled': false,
                        'config': {
                          'value': false
                        }
                      },
                      'grouping': {
                        'enabled': false
                      },
                      'editColumn': {
                        'enabled': false
                      },
                      'editColumnLabel': {
                        'enabled': false
                      },
                      'editColumnFormat': {
                        'enabled': false
                      },
                      'editBin': {
                        'enabled': false
                      }
                    },
                    'grouping': {
                      'columns': [
                        {
                          'name': 'OrderDate_bin'
                        }
                      ],
                      'aggregations': [
                        {
                          'column': 'ShipVia',
                          'aggregation': 'sum',
                          'alias': 'ShipVia'
                        },
                        {
                          'column': 'ShipPostalCode',
                          'aggregation': 'sum',
                          'alias': 'ShipPostalCode'
                        },
                        {
                          'column': 'ShipCountry',
                          'aggregation': 'count',
                          'alias': 'ShipCountry'
                        },
                        {
                          'column': 'OrderDate',
                          'aggregation': 'max',
                          'alias': 'OrderDate'
                        }
                      ]
                    },
                    'bins': [
                      {
                        'column': {
                          'name': 'OrderDate',
                          'type': 'date'
                        },
                        'alias': 'OrderDate_bin',
                        'options': {
                          'alg': 'auto',
                          'numOfBins': 5
                        }
                      },
                      {
                        'column': {
                          'name': 'ShipPostalCode',
                          'type': 'int'
                        },
                        'alias': 'ShipPostalCode_bin',
                        'options': {
                          'alg': 'auto',
                          'numOfBins': 5,
                          'nice': true
                        }
                      }
                    ],
                    'pagination': {
                      'limit': 50,
                      'current': 1,
                      'total': null,
                      'type': 'auto',
                      'buttons': {
                        'first': {
                          'visibility': true,
                          'label': 'First'
                        },
                        'last': {
                          'visibility': true,
                          'label': 'Last'
                        },
                        'prev': {
                          'visibility': true,
                          'label': 'Previous'
                        },
                        'next': {
                          'visibility': true,
                          'label': 'Next'
                        }
                      },
                      'numbers': {
                        'beforeCurrent': 2,
                        'afterCurrent': 2
                      },
                      'default': 'auto'
                    },
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'rowActions': {
                      'enabled': false,
                      'inline': 1,
                      'display': 'always',
                      'position': 'left'
                    }
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': false,
                  'readable': {
                    'enabled': false
                  },
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  }
                },
                'globalFilter': {
                  'enabled': false
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': false,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'calculatedColumn': {
                'enabled': false
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  }
                }
              },
              'waitingForGlobalFilter': false
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-11T06:18:13.705Z'
          },
          {
            'config': {
              'grid': {
                'x': 0,
                'y': 0,
                'w': 12,
                'h': 4,
                'i': 0
              },
              'autoHeight': false,
              'widget': {
                'title': {
                  'text': 'Analytics 1',
                  'enabled': true,
                  'edited': true
                },
                'id': 'id-b7305c5c-3449-442f-8518-40b086c05ec7',
                'class': '',
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                }
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-chart',
                  'config': {
                    'dataSource': 'b79646cb-4238-447d-9b0e-4617f9d04786',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Widget Title',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [
                      {
                        'name': 'Date ',
                        'displayName': 'Date ',
                        'type': 'date',
                        'format': null,
                        'aggrFormats': null
                      },
                      {
                        'name': 'Inventory',
                        'displayName': 'Inventory',
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
                        'axis': {
                          'x': [
                            {
                              'id': 'x_id-1dd5971d-6a9f-4732-b317-eb76847fdcfe',
                              'type': 'category',
                              'display': true,
                              'format': null,
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'ticks': {
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              }
                            }
                          ],
                          'y': [
                            {
                              'id': 'y_id-1dd5971d-6a9f-4732-b317-eb76847fdcfe',
                              'type': 'linear',
                              'format': null,
                              'position': 'left',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
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
                            'position': 'bottom',
                            'widthPercent': 40,
                            'isHorizontal': true
                          }
                        },
                        'series': [
                          {
                            'type': 'scatter',
                            'name': 'Inventory',
                            'axis': {
                              'x': 'x_id-1dd5971d-6a9f-4732-b317-eb76847fdcfe',
                              'y': 'y_id-1dd5971d-6a9f-4732-b317-eb76847fdcfe'
                            },
                            'data': {
                              'x': 'Date ',
                              'y': 'Inventory'
                            },
                            'id': 'id-1dd5971d-6a9f-4732-b317-eb76847fdcfe'
                          }
                        ]
                      }
                    ],
                    'sorting': [],
                    'grouping': {
                      'columns': [],
                      'aggregations': []
                    },
                    'bins': [
                      {
                        'column': {
                          'name': 'Inventory',
                          'type': 'int'
                        },
                        'alias': 'Inventory_id-1dd5971d-6a9f-4732-b317-eb76847fdcfe_bin',
                        'options': {
                          'alg': 'auto',
                          'numOfBins': 5,
                          'nice': true
                        }
                      },
                      {
                        'column': {
                          'name': 'Date ',
                          'type': 'date'
                        },
                        'alias': 'Date _bin',
                        'options': {
                          'alg': 'auto',
                          'numOfBins': 5
                        }
                      }
                    ],
                    'pagination': {
                      'limit': 1000,
                      'current': 1,
                      'type': 'buttons'
                    },
                    'color_scheme': 'Google',
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'id': 'id-01f3d5d5-dbd4-437b-93d9-83d43fe7b5dd'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': false,
                  'readable': {
                    'enabled': false
                  },
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  }
                },
                'globalFilter': {
                  'enabled': false
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': false,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  },
                  'id': 'id-361dd030-2327-4a85-a5ea-123c404baee1',
                  'widget': {
                    'title': {
                      'enabled': true,
                      'text': ''
                    },
                    'class': ''
                  }
                }
              },
              'id': 'id-c9701927-ac45-4d15-a9ec-809657037d30',
              'editMode': true,
              'waitingForGlobalFilter': false,
              'calculatedColumn': {
                'enabled': false
              }
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-15T07:09:43.576Z'
          },
          {
            'config': {
              'grid': {
                'x': 0,
                'y': 0,
                'w': 12,
                'h': 4,
                'i': 0
              },
              'autoHeight': false,
              'widget': {
                'title': {
                  'text': 'Quantitation of [impressions, 7_day_advertised_sku_units] over [start_date] per 1 M uniform interval',
                  'enabled': true,
                  'edited': false
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                }
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-chart',
                  'config': {
                    'dataSource': 'bf685620-88d2-4367-9408-9878187c1d0e',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Quantitation of [impressions, 7_day_advertised_sku_units] over [start_date] per 1 M uniform interval',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [
                      {
                        'name': 'match_type',
                        'displayName': 'Match Type',
                        'type': 'string',
                        'format': null,
                        'aggrFormats': null
                      },
                      {
                        'name': 'impressions',
                        'displayName': 'Impressions',
                        'type': 'int',
                        'format': null,
                        'aggrFormats': null
                      },
                      {
                        'name': '7_day_advertised_sku_units',
                        'displayName': '7 Day Advertised SKU Units (#)',
                        'type': 'int',
                        'format': null,
                        'aggrFormats': null
                      },
                      {
                        'name': 'start_date',
                        'displayName': 'Start Date',
                        'type': 'date',
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
                        'axis': {
                          'x': [
                            {
                              'id': 'x_id-2f5ff14b-84ad-4f83-8c03-9609d5626528',
                              'type': 'category',
                              'display': true,
                              'format': null,
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'ticks': {
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              }
                            }
                          ],
                          'y': [
                            {
                              'id': 'y_id-2f5ff14b-84ad-4f83-8c03-9609d5626528',
                              'type': 'linear',
                              'format': null,
                              'position': 'left',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              },
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              }
                            },
                            {
                              'id': 'y_id-08661321-a5f1-49be-bf0a-c58f0c8b26ec',
                              'type': 'linear',
                              'format': null,
                              'position': 'right',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
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
                            'position': 'bottom',
                            'widthPercent': 40,
                            'isHorizontal': true
                          },
                          'stacking': '',
                          'isHorizontal': false
                        },
                        'series': [
                          {
                            'type': 'bar',
                            'name': 'Impressions (Sum)',
                            'axis': {
                              'x': 'x_id-2f5ff14b-84ad-4f83-8c03-9609d5626528',
                              'y': 'y_id-2f5ff14b-84ad-4f83-8c03-9609d5626528'
                            },
                            'data': {
                              'x': 'start_date',
                              'y': 'impressions'
                            },
                            'id': 'id-2f5ff14b-84ad-4f83-8c03-9609d5626528'
                          },
                          {
                            'type': 'bar',
                            'name': '7 Day Advertised SKU Units (#) (Sum)',
                            'axis': {
                              'x': 'x_id-2f5ff14b-84ad-4f83-8c03-9609d5626528',
                              'y': 'y_id-08661321-a5f1-49be-bf0a-c58f0c8b26ec'
                            },
                            'options': {
                              'stacking': '',
                              'isHorizontal': false
                            },
                            'data': {
                              'x': 'start_date',
                              'y': '7_day_advertised_sku_units'
                            },
                            'id': 'id-08661321-a5f1-49be-bf0a-c58f0c8b26ec'
                          }
                        ]
                      }
                    ],
                    'sorting': [],
                    'grouping': {
                      'columns': [
                        {
                          'name': 'start_date_bin'
                        }
                      ],
                      'aggregations': [
                        {
                          'column': 'impressions',
                          'aggregation': 'sum',
                          'alias': 'impressions_sum_id-2f5ff14b-84ad-4f83-8c03-9609d5626528'
                        },
                        {
                          'column': '7_day_advertised_sku_units',
                          'aggregation': 'sum',
                          'alias': '7_day_advertised_sku_units_sum_id-08661321-a5f1-49be-bf0a-c58f0c8b26ec'
                        },
                        {
                          'column': 'start_date',
                          'aggregation': 'max',
                          'alias': 'start_date'
                        }
                      ]
                    },
                    'bins': [
                      {
                        'column': {
                          'name': 'start_date',
                          'type': 'date'
                        },
                        'alias': 'start_date_bin',
                        'options': {
                          'alg': 'uniform',
                          'uniform': {
                            'width': 1,
                            'unit': 'M'
                          }
                        }
                      }
                    ],
                    'pagination': {
                      'limit': 1000,
                      'current': 1,
                      'type': 'buttons'
                    },
                    'color_scheme': 'Google',
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'id': 'id-8bd1d388-334b-4e27-a804-9896ba9a9ff3'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': false,
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  },
                  'readable': {
                    'enabled': false
                  }
                },
                'globalFilter': {
                  'enabled': false
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': false,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  }
                }
              },
              'waitingForGlobalFilter': false,
              'calculatedColumn': {
                'enabled': false
              }
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-11T07:58:13.716Z'
          },
          {
            'config': {
              'grid': {
                'x': 0,
                'y': 0,
                'w': 12,
                'h': 4,
                'i': 0
              },
              'autoHeight': true,
              'widget': {
                'title': {
                  'text': 'Quantitation of [Freight, Fulfillment] ',
                  'enabled': true,
                  'edited': false
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                },
                'id': 'id-0b3867f0-e291-41f9-b6f8-b2e149435402',
                'class': ''
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-gauge',
                  'config': {
                    'dataSource': '0cd5f3b9-3857-4edf-a922-d1e579cd3568',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': 'Quantitation of [Freight, Fulfillment]  update',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [
                      {
                        'name': 'Freight',
                        'displayName': 'Freight',
                        'type': 'double',
                        'format': null,
                        'aggrFormats': null,
                        'visible': false
                      },
                      {
                        'name': 'Fulfillment',
                        'displayName': 'Fulfillment',
                        'type': 'int',
                        'format': null,
                        'aggrFormats': null,
                        'visible': true
                      }
                    ],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [
                      {
                        'axis': {
                          'x': [],
                          'y': [
                            {
                              'id': 'y_id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc',
                              'type': 'linear',
                              'format': null,
                              'position': 'right',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              },
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'max': 10474.77,
                              'stops': [
                                [
                                  3666.17,
                                  '#78F759'
                                ],
                                [
                                  6808.6,
                                  '#F6F80D'
                                ],
                                [
                                  10474.77,
                                  '#DF5353'
                                ]
                              ]
                            },
                            {
                              'id': 'y_id-2370f71f-3c99-402d-b3bf-5f7d44483ca0',
                              'type': 'linear',
                              'format': null,
                              'position': 'left',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              },
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'max': 18.2,
                              'stops': [
                                [
                                  6.37,
                                  '#55BF3B'
                                ],
                                [
                                  11.83,
                                  '#DDDF0D'
                                ],
                                [
                                  18.2,
                                  '#DF5353'
                                ]
                              ]
                            }
                          ]
                        },
                        'options': {
                          'legend': {
                            'enabled': true,
                            'position': 'bottom',
                            'widthPercent': 40,
                            'isHorizontal': false
                          }
                        },
                        'series': [
                          {
                            'type': 'solidgauge',
                            'name': 'Freight (Sum)',
                            'axis': {
                              'y': 'y_id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc'
                            },
                            'options': {
                              'stacking': '',
                              'isHorizontal': false,
                              'subtitle': 'Freight (sum)',
                              'size': 25
                            },
                            'data': {
                              'x': null,
                              'y': 'Freight'
                            },
                            'id': 'id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc'
                          },
                          {
                            'type': 'solidgauge',
                            'name': 'Fulfillment (Sum)',
                            'axis': {
                              'y': 'y_id-2370f71f-3c99-402d-b3bf-5f7d44483ca0'
                            },
                            'options': {
                              'stacking': '',
                              'isHorizontal': false,
                              'subtitle': 'Fulfillment (sum)',
                              'size': 25
                            },
                            'data': {
                              'x': null,
                              'y': 'Fulfillment'
                            },
                            'id': 'id-2370f71f-3c99-402d-b3bf-5f7d44483ca0'
                          }
                        ]
                      }
                    ],
                    'sorting': [],
                    'grouping': {
                      'aggregations': [
                        {
                          'column': 'Freight',
                          'alias': 'Freight_sum_id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc',
                          'aggregation': 'sum'
                        },
                        {
                          'column': 'Fulfillment',
                          'alias': 'Fulfillment_sum_id-2370f71f-3c99-402d-b3bf-5f7d44483ca0',
                          'aggregation': 'sum'
                        }
                      ],
                      'columns': []
                    },
                    'bins': [],
                    'pagination': {
                      'limit': 1000,
                      'current': 1,
                      'type': 'buttons'
                    },
                    'color_scheme': 'Google',
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'id': 'id-47fa36f4-7b21-4d53-a0ca-abf1e75a6f69'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': true,
                  'readable': {
                    'enabled': false
                  },
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  }
                },
                'globalFilter': {
                  'enabled': true
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': true,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'calculatedColumn': {
                'enabled': false
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  },
                  'id': 'id-80f705f1-01f1-4e54-ade5-029d305cebfa',
                  'widget': {
                    'title': {
                      'enabled': true,
                      'text': ''
                    },
                    'class': ''
                  }
                }
              },
              'waitingForGlobalFilter': false,
              'id': 'id-6256bcd8-c8af-49d6-b5a3-8a633bb6a7e2',
              'editMode': true
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-16T02:52:42.425Z'
          },
          {
            'config': {
              'grid': {
                'x': 0,
                'y': 0,
                'w': 12,
                'h': 4,
                'i': 0
              },
              'autoHeight': false,
              'widget': {
                'title': {
                  'text': 'Quantitation of [df] over [dfgdfg]',
                  'enabled': true,
                  'edited': true
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                },
                'id': 'id-666b4e0d-1b01-4be6-b73b-8ee5291076ee',
                'class': ''
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-gauge',
                  'config': {
                    'dataSource': '26d82d7f-0c3e-4d72-ad8a-575ba4c3e054',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Widget Title',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [
                      {
                        'name': 'STT',
                        'displayName': 'STT',
                        'type': 'int',
                        'format': {
                          'common': {
                            'plain': {
                              'nil': 'NULL',
                              'empty': 'EMPTY',
                              'na': 'N/A'
                            },
                            'html': {
                              'nil': '<span class="d-sdk-nil">null</span>',
                              'empty': '<span class="d-sdk-empty">empty</span>',
                              'na': '<span class="d-sdk-na">N/A</span>'
                            },
                            'prefix': null,
                            'suffix': null
                          },
                          'type': 'currency',
                          'config': {
                            'currency': {
                              'symbol': '$',
                              'symbolPrefix': true,
                              'inCents': true
                            },
                            'numeric': {
                              'comma': true,
                              'precision': 3,
                              'siPrefix': false
                            }
                          }
                        },
                        'aggrFormats': null
                      }
                    ],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [
                      {
                        'axis': {
                          'x': [],
                          'y': [
                            {
                              'id': 'y_id-4ea7346e-ac5f-457c-823d-01ccea52325f',
                              'type': 'linear',
                              'format': null,
                              'position': 'left',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              },
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'plotBands': [
                                {
                                  'from': 0,
                                  'to': 51.45,
                                  'color': '#666'
                                },
                                {
                                  'from': 51.45,
                                  'to': 95.55,
                                  'color': '#999'
                                },
                                {
                                  'from': 95.55,
                                  'to': 147,
                                  'color': '#bbb'
                                }
                              ]
                            }
                          ]
                        },
                        'options': {
                          'legend': {
                            'enabled': true,
                            'position': 'bottom',
                            'widthPercent': 40,
                            'isHorizontal': false
                          },
                          'isHorizontal': true
                        },
                        'series': [
                          {
                            'type': 'bulletgauge',
                            'name': 'STT (Sum)',
                            'axis': {
                              'y': 'y_id-4ea7346e-ac5f-457c-823d-01ccea52325f'
                            },
                            'options': {
                              'title': 'STT (sum)'
                            },
                            'data': {
                              'x': null,
                              'y': 'STT'
                            },
                            'id': 'id-4ea7346e-ac5f-457c-823d-01ccea52325f'
                          }
                        ]
                      }
                    ],
                    'sorting': [],
                    'grouping': {
                      'columns': [],
                      'aggregations': [
                        {
                          'column': 'STT',
                          'alias': 'STT_sum_id-4ea7346e-ac5f-457c-823d-01ccea52325f',
                          'aggregation': 'sum'
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
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'id': 'id-eb094563-8866-4f4b-a603-3133cab7d27d'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': false,
                  'readable': {
                    'enabled': false
                  },
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  }
                },
                'globalFilter': {
                  'enabled': false
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': false,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  },
                  'id': 'id-19319c30-b0fc-4070-b65e-821b777507f5',
                  'widget': {
                    'title': {
                      'enabled': true,
                      'text': ''
                    },
                    'class': ''
                  }
                }
              },
              'waitingForGlobalFilter': false,
              'id': 'id-d1e4cab6-83d3-4fd5-9f00-130ce5d66678',
              'editMode': true,
              'calculatedColumn': {
                'enabled': false
              }
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-16T02:50:12.112Z'
          },
          {
            'config': {
              'grid': {
                'x': 0,
                'y': 0,
                'w': 12,
                'h': 4,
                'i': 0
              },
              'autoHeight': true,
              'widget': {
                'title': {
                  'text': 'Quantitation of [Freight, Fulfillment] ',
                  'enabled': true,
                  'edited': false
                },
                'style': {
                  'background_color': null,
                  'foreground_color': null,
                  'header_background_color': null,
                  'header_foreground_color': null,
                  'border_width': null,
                  'border_radius': null
                },
                'id': 'id-0b3867f0-e291-41f9-b6f8-b2e149435402',
                'class': ''
              },
              'action': {
                'elements': []
              },
              'elements': [
                {
                  'type': 'cbpo-element-gauge',
                  'config': {
                    'dataSource': '0cd5f3b9-3857-4edf-a922-d1e579cd3568',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': 'Quantitation of [Freight, Fulfillment]  update',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [
                      {
                        'name': 'Freight',
                        'displayName': 'Freight',
                        'type': 'double',
                        'format': null,
                        'aggrFormats': null,
                        'visible': false
                      },
                      {
                        'name': 'Fulfillment',
                        'displayName': 'Fulfillment',
                        'type': 'int',
                        'format': null,
                        'aggrFormats': null,
                        'visible': true
                      }
                    ],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [
                      {
                        'axis': {
                          'x': [],
                          'y': [
                            {
                              'id': 'y_id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc',
                              'type': 'linear',
                              'format': null,
                              'position': 'right',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              },
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'max': 10474.77,
                              'stops': [
                                [
                                  3666.17,
                                  '#78F759'
                                ],
                                [
                                  6808.6,
                                  '#F6F80D'
                                ],
                                [
                                  10474.77,
                                  '#DF5353'
                                ]
                              ]
                            },
                            {
                              'id': 'y_id-2370f71f-3c99-402d-b3bf-5f7d44483ca0',
                              'type': 'linear',
                              'format': null,
                              'position': 'left',
                              'stack': false,
                              'ticks': {
                                'beginAtZero': true,
                                'stepSize': '',
                                'maxTicksLimit': 5,
                                'fontSize': 11,
                                'fontStyle': 'bold'
                              },
                              'scaleLabel': {
                                'display': false,
                                'labelString': ''
                              },
                              'max': 18.2,
                              'stops': [
                                [
                                  6.37,
                                  '#55BF3B'
                                ],
                                [
                                  11.83,
                                  '#DDDF0D'
                                ],
                                [
                                  18.2,
                                  '#DF5353'
                                ]
                              ]
                            }
                          ]
                        },
                        'options': {
                          'legend': {
                            'enabled': true,
                            'position': 'bottom',
                            'widthPercent': 40,
                            'isHorizontal': false
                          }
                        },
                        'series': [
                          {
                            'type': 'solidgauge',
                            'name': 'Freight (Sum)',
                            'axis': {
                              'y': 'y_id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc'
                            },
                            'options': {
                              'stacking': '',
                              'isHorizontal': false,
                              'subtitle': 'Freight (sum)',
                              'size': 25
                            },
                            'data': {
                              'x': null,
                              'y': 'Freight'
                            },
                            'id': 'id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc'
                          },
                          {
                            'type': 'solidgauge',
                            'name': 'Fulfillment (Sum)',
                            'axis': {
                              'y': 'y_id-2370f71f-3c99-402d-b3bf-5f7d44483ca0'
                            },
                            'options': {
                              'stacking': '',
                              'isHorizontal': false,
                              'subtitle': 'Fulfillment (sum)',
                              'size': 25
                            },
                            'data': {
                              'x': null,
                              'y': 'Fulfillment'
                            },
                            'id': 'id-2370f71f-3c99-402d-b3bf-5f7d44483ca0'
                          }
                        ]
                      }
                    ],
                    'sorting': [],
                    'grouping': {
                      'aggregations': [
                        {
                          'column': 'Freight',
                          'alias': 'Freight_sum_id-46f9c82a-bddb-4860-a8e0-cc3db53ba0fc',
                          'aggregation': 'sum'
                        },
                        {
                          'column': 'Fulfillment',
                          'alias': 'Fulfillment_sum_id-2370f71f-3c99-402d-b3bf-5f7d44483ca0',
                          'aggregation': 'sum'
                        }
                      ],
                      'columns': []
                    },
                    'bins': [],
                    'pagination': {
                      'limit': 1000,
                      'current': 1,
                      'type': 'buttons'
                    },
                    'color_scheme': 'Google',
                    'messages': {
                      'no_data_at_all': 'No data',
                      'no_data_found': 'No data found'
                    },
                    'id': 'id-47fa36f4-7b21-4d53-a0ca-abf1e75a6f69'
                  }
                }
              ],
              'filter': {
                'form': {
                  'config': {
                    'controls': []
                  }
                },
                'builder': {
                  'enabled': true,
                  'readable': {
                    'enabled': false
                  },
                  'config': {
                    'trigger': {
                      'label': 'Setting Filter'
                    },
                    'modal': {
                      'title': 'Query Builder'
                    },
                    'format': {
                      'temporal': {
                        'date': 'YYYY-MM-DD',
                        'datetime': 'YYYY-MM-DD hh:mm'
                      }
                    },
                    'threshold': {
                      'maxLevel': 5
                    },
                    'query': {
                      'id': null,
                      'level': 0,
                      'type': 'AND',
                      'conditions': []
                    }
                  }
                },
                'globalFilter': {
                  'enabled': true
                },
                'alignment': ''
              },
              'columnManager': {
                'enabled': true,
                'config': {
                  'trigger': {
                    'label': 'Manage Columns'
                  },
                  'modal': {
                    'title': 'Manage Columns'
                  },
                  'managedColumns': []
                }
              },
              'calculatedColumn': {
                'enabled': false
              },
              'menu': {
                'enabled': true,
                'config': {
                  'label': {
                    'text': ''
                  },
                  'icons': {
                    'css': 'fa fa-ellipsis-h'
                  },
                  'dataSource': null,
                  'selection': {
                    'options': [
                      {
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      },
                      {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      },
                      {
                        'type': 'divider'
                      },
                      {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }
                    ]
                  },
                  'id': 'id-80f705f1-01f1-4e54-ade5-029d305cebfa',
                  'widget': {
                    'title': {
                      'enabled': true,
                      'text': ''
                    },
                    'class': ''
                  }
                }
              },
              'waitingForGlobalFilter': false,
              'id': 'id-6256bcd8-c8af-49d6-b5a3-8a633bb6a7e2',
              'editMode': true
            },
            'screenshot': 'https://storage.googleapis.com/precise/widget-2020-06-17T03:46:03.071Z'
          }
        ]
      },
      defaultDataSource: 'dataSource'
    }
  },
  components: {
    'sdk-export-code': sdkExportCodeComponent
  },
  mixins: [configMixins, renderMixins],
  mounted() {
    this.render('#visualization', this.template, this.state.baseURL, this.state.token, this.state.clientId)
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
    },
    changeDataSource(state) {
      this.state = state
      let config = _.cloneDeep(this.config)
      if (!_.isEmpty(state.dataSource)) {
        config.dataSource = state.dataSource
      } else {
        config.dataSource = this.defaultDataSource
        window[this.defaultDataSource] = _.cloneDeep(this.mappingDataSource())
      }
      window.config = config
      this.render('#visualization', this.template, this.state.baseURL, this.state.token, this.state.clientId)
    }
  },
  computed: {
    getTemplate() {
      return [
        {
          name: 'Visualization',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  created() {
    window.config = _.cloneDeep(this.config)
  }
})
