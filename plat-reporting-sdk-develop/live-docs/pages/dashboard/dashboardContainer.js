const sdkDashboardContainerPage = Vue.component('sdkDashboardContainerPage', {
  template: `
    <div class="dashboard-container-demo">
    <h5>Example: </h5>
    <label>Builder Mode</label>
    <input type="checkbox" v-model="isBuilder" @change="triggerBuilderMode()" />
    <div id="dashboard-container-demo">
    </div>
    <sdk-export-code :templates="getTemplate" />
    </div>
  `,
  components: {
    'sdk-export-code': sdkExportCodeComponent
  },
  mixins: [configMixins, renderMixins],
  data() {
    return {
      template: '<cbpo-dashboard class="p-0" config-ref="config"></cbpo-dashboard>',
      config: {
        'widget': {
          'enabled': false,
          'title': null,
          'class': ''
        },
        'style': {
          'background_color': null,
          'foreground_color': null,
          'header_background_color': null,
          'header_foreground_color': null,
          'border_width': null,
          'border_radius': null
        },
        'widgetLayout': {
          'gridConfig': {
            'colNum': 12,
            'rowHeight': 1,
            'margin': [
              8,
              8
            ],
            'defaultHeight': 50,
            'responsive': {
              'enabled': true,
              'breakpoints': {
                'lg': 1200,
                'md': 996,
                'sm': 768,
                'xs': 480,
                'xxs': 0
              },
              'cols': {
                'lg': 12,
                'md': 12,
                'sm': 12,
                'xs': 6,
                'xxs': 6
              }
            },
            'minHeight': 10
          },
          'widgets': [
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 191,
                  'w': 6,
                  'h': 39,
                  'i': 2,
                  'moved': false
                },
                'autoHeight': false,
                'widget': {
                  'title': {
                    'text': 'Seller Buy-box Percentage (Updated Weekly)',
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
                  'id': 'id-8a8d9657-4871-4ab4-b9ae-7d4815d28374',
                  'class': ''
                },
                'action': {
                  'elements': []
                },
                'elements': [
                  {
                    'type': 'cbpo-element-chart',
                    'config': {
                      'dataSource': '21c876b1-c58b-4dd2-89ae-fbfdee171b41',
                      'widget': {
                        'title': {
                          'enabled': false,
                          'text': 'Quantitation of [bb_winner] over [bb_winner]',
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
                          'name': 'bb_winner',
                          'displayName': 'Count BB Winner',
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
                                'id': 'x_id-e1a033a1-564a-4796-b1ad-acb62492a988',
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
                                'id': 'y_id-e1a033a1-564a-4796-b1ad-acb62492a988',
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
                              'position': 'right',
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
                              'name': 'Count BB Winner (Count)',
                              'axis': {
                                'x': 'x_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                                'y': 'y_id-e1a033a1-564a-4796-b1ad-acb62492a988'
                              },
                              'data': {
                                'x': 'bb_winner',
                                'y': 'bb_winner'
                              },
                              'id': 'id-e1a033a1-564a-4796-b1ad-acb62492a988'
                            }
                          ]
                        }
                      ],
                      'sorting': [
                        {
                          'column': 'bb_winner_count_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                          'direction': 'desc'
                        }
                      ],
                      'grouping': {
                        'aggregations': [
                          {
                            'column': 'bb_winner',
                            'aggregation': 'count',
                            'alias': 'bb_winner_count_id-e1a033a1-564a-4796-b1ad-acb62492a988'
                          }
                        ],
                        'columns': [
                          {
                            'name': 'bb_winner'
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
                      'timezone': {
                        'enabled': true,
                        'utc': 'America/Danmarkshavn',
                        'visible': false
                      },
                      'id': '03f4ee81-fa40-48a2-9645-7ca5b939e962'
                    }
                  }
                ],
                'filter': {
                  'form': {
                    'config': {
                      'controls': []
                    }
                  },
                  'base': {
                    'config': {
                      'query': {
                        'id': 'id-e825ec80-0b65-47b7-bfc3-da2db5eaa234',
                        'level': 0,
                        'type': 'AND',
                        'conditions': [
                          {
                            'id': 'id-07f9af28-ea48-49ca-aa5e-cc65912c62fc',
                            'level': 1,
                            'column': 'bb_winner',
                            'value': 'null',
                            'operator': 'not_null',
                            'parentId': 'id-e825ec80-0b65-47b7-bfc3-da2db5eaa234'
                          }
                        ],
                        'parentId': null
                      }
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
                    'id': 'id-8bb95fb4-612a-4ad5-9015-52bb26bb76d0',
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
                'id': 'id-4c49ee5c-3e80-40ba-ba90-3852f078ada1'
              },
              'id': 'id-cbe25537-7408-457b-b938-d649815fd1c5'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 260,
                  'w': 12,
                  'h': 46,
                  'i': 1,
                  'id': 'id-a296c628-c5b5-4ed7-aba7-a246338205be',
                  'moved': false
                },
                'widgetId': '20dc5e7e-055f-4818-870e-3d14e559f5f4',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-c33f1633-6c4a-43e5-b333-6594c812657f',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-0afca882-e376-44be-bb79-2e1a061f9fc5',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '13de907c-add5-4b46-9a19-eacca41fb700',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-3740e472-a74d-452b-b5f5-92ff9a6fba89'
            },
            // done
            {
              'type': 'cbpo-widget',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 221,
                  'w': 6,
                  'h': 39,
                  'i': 2,
                  'id': 'id-a8aa2178-215d-45a6-b1fd-f61bcd49bbce',
                  'moved': false
                },
                'autoHeight': false,
                'widget': {
                  'title': {
                    'text': 'Seller Buy-box Percentage (Updated Weekly)',
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
                  'id': 'id-8a8d9657-4871-4ab4-b9ae-7d4815d28374',
                  'class': ''
                },
                'action': {
                  'elements': []
                },
                'elements': [
                  {
                    'type': 'cbpo-element-chart',
                    'config': {
                      'dataSource': '21c876b1-c58b-4dd2-89ae-fbfdee171b41',
                      'widget': {
                        'title': {
                          'enabled': false,
                          'text': 'Quantitation of [bb_winner] over [bb_winner]',
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
                          'name': 'bb_winner',
                          'displayName': 'Count BB Winner',
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
                                'id': 'x_id-e1a033a1-564a-4796-b1ad-acb62492a988',
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
                                'id': 'y_id-e1a033a1-564a-4796-b1ad-acb62492a988',
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
                              'position': 'right',
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
                              'name': 'Count BB Winner (Count)',
                              'axis': {
                                'x': 'x_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                                'y': 'y_id-e1a033a1-564a-4796-b1ad-acb62492a988'
                              },
                              'data': {
                                'x': 'bb_winner',
                                'y': 'bb_winner'
                              },
                              'id': 'id-e1a033a1-564a-4796-b1ad-acb62492a988'
                            }
                          ]
                        }
                      ],
                      'sorting': [
                        {
                          'column': 'bb_winner_count_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                          'direction': 'desc'
                        }
                      ],
                      'grouping': {
                        'aggregations': [
                          {
                            'column': 'bb_winner',
                            'aggregation': 'count',
                            'alias': 'bb_winner_count_id-e1a033a1-564a-4796-b1ad-acb62492a988'
                          }
                        ],
                        'columns': [
                          {
                            'name': 'bb_winner'
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
                      'timezone': {
                        'enabled': true,
                        'utc': 'America/Danmarkshavn',
                        'visible': false
                      },
                      // config to check table export config - uncomment to turn it on
                      "exportConfig": {
                        "query": {
                          "orders": [
                            {
                              "column": "date",
                              "direction": "desc"
                            }
                          ],
                          "timezone": "America/Los_Angeles",
                          "group": {
                            "columns": [
                              {
                                "name": "bb_winner",
                                "displayName": "Buybox Winner",
                                "type": "string",
                                "format": null,
                                "aggrFormats": null
                              },
                              {
                                "name": "product_id",
                                "displayName": "Product ID",
                                "type": "string",
                                "format": null,
                                "aggrFormats": null
                              },
                              {
                                "name": "asin",
                                "displayName": "ASIN",
                                "type": "string",
                                "format": null,
                                "aggrFormats": null
                              },
                              {
                                "name": "title",
                                "displayName": "Title",
                                "type": "string",
                                "format": null,
                                "aggrFormats": null
                              },
                              {
                                "name": "date",
                                "displayName": "Date",
                                "type": "date",
                                "format": null,
                                "aggrFormats": null
                              },
                            ],
                            "aggregations": []
                          },
                          "fields": [
                            {
                              "name": "bb_winner",
                              "alias": "BB Winner"
                            },
                            {
                              "name": "product_id",
                              "alias": "Product ID"
                            },
                            {
                              "name": "asin",
                              "alias": "ASIN"
                            },
                            {
                              "name": "title",
                              "alias": "Title"
                            },
                            {
                              "name": "date",
                              "alias": "Date"
                            }
                          ],
                          'paging': {
                            'limit': 999999,
                            'current': 1,
                          },
                          "filter": {
                            "type": "AND",
                            "conditions": [
                              {
                                "id": "id-07f9af28-ea48-49ca-aa5e-cc65912c62fc",
                                "level": 1,
                                "column": "bb_winner",
                                "value": "null",
                                "operator": "not_null",
                                "parentId": "id-e825ec80-0b65-47b7-bfc3-da2db5eaa234"
                              },
                              {
                                "type": "AND",
                                "conditions": [
                                  {
                                    "column": "date",
                                    "operator": "in_range",
                                    "value": [
                                      "DATE_LAST(2,'days')",
                                      "TODAY()"
                                    ],
                                    "sort": "desc",
                                    "format": {
                                      "common": {
                                        "plain": {
                                          "nil": "NULL",
                                          "empty": "EMPTY",
                                          "na": "N/A"
                                        },
                                        "html": {
                                          "nil": "<span class=\"d-sdk-nil\">null</span>",
                                          "empty": "<span class=\"d-sdk-empty\">empty</span>",
                                          "na": "<span class=\"d-sdk-na\">N/A</span>"
                                        },
                                        "prefix": null,
                                        "suffix": null
                                      },
                                      "type": "temporal",
                                      "config": {
                                        "format": "L",
                                        "date": {
                                          "format": "L"
                                        },
                                        "time": {
                                          "format": "LT"
                                        },
                                        "options": {
                                          "year": "YYYY",
                                          "quarter": "YYYY [Q]Q",
                                          "month": "YYYY MMM",
                                          "week": "YYYY [w]w",
                                          "day": "YYYY-MM-DD",
                                          "hour": "YYYY-MM-DD kk",
                                          "minute": "YYYY-MM-DD kk:mm",
                                          "second": "YYYY-MM-DD kk:mm:ss"
                                        }
                                      }
                                    }
                                  }
                                ]
                              }
                            ]
                          },
                          "dataSource" : "da21e905-41d6-4c96-bc03-fcae1024f16e"
                        }
                      },
                      'id': '03f4ee81-fa40-48a2-9645-7ca5b939e962'
                    }
                  }
                ],
                'filter': {
                  'form': {
                    'config': {
                      'controls': [
                        {
                          "type": "cbpo-filter-control-range-select",
                          "config": {
                            "common": {
                              "column": {
                                "name": "date",
                                "type": "date",
                                "label": "Date",
                                "displayName": "Date"
                              },
                              "operator": "in_range",
                              "value": [
                                null,
                                null
                              ],
                              "sort": "desc",
                              "format": {
                                "common": {
                                  "plain": {
                                    "nil": "NULL",
                                    "empty": "EMPTY",
                                    "na": "N/A"
                                  },
                                  "html": {
                                    "nil": "<span class=\"d-sdk-nil\">null</span>",
                                    "empty": "<span class=\"d-sdk-empty\">empty</span>",
                                    "na": "<span class=\"d-sdk-na\">N/A</span>"
                                  },
                                  "prefix": null,
                                  "suffix": null
                                },
                                "type": "temporal",
                                "config": {
                                  "format": "L",
                                  "date": {
                                    "format": "L"
                                  },
                                  "time": {
                                    "format": "LT"
                                  },
                                  "options": {
                                    "year": "YYYY",
                                    "quarter": "YYYY [Q]Q",
                                    "month": "YYYY MMM",
                                    "week": "YYYY [w]w",
                                    "day": "YYYY-MM-DD",
                                    "hour": "YYYY-MM-DD kk",
                                    "minute": "YYYY-MM-DD kk:mm",
                                    "second": "YYYY-MM-DD kk:mm:ss"
                                  }
                                }
                              }
                            },
                            "label": {
                              "text": "Date"
                            },
                            "range": {
                              "type": "date",
                              "formatLabel": "MM/DD/YYYY",
                              "formatValue": "YYYY-MM-DD",
                              "visible": false
                            },
                            "selection": {
                              "empty": {
                                "label": "Select Date Range",
                                "enabled": true,
                                "isEmptySelected": true,
                                "isDefaultOption": false
                              },
                              "sort": "asc",
                              "options": [
                                {
                                  "label": "Yesterday",
                                  "isDefault": false,
                                  "value": [
                                    "DATE_START_OF(DATE_LAST(1,'days'), 'days')",
                                    "DATE_END_OF(DATE_LAST(1,'days'), 'days')"
                                  ],
                                  "local": true
                                },
                                {
                                  "label": "Last 7 days",
                                  "value": [
                                    "DATE_LAST(7,'days')",
                                    "TODAY()"
                                  ],
                                  "isDefault": true,
                                  "dateFormatForSort": "2021-01-17T17:00:00.000Z"
                                },
                                {
                                  "label": "Last 15 days",
                                  "isDefault": false,
                                  "value": [
                                    "DATE_LAST(15,'days')",
                                    "TODAY()"
                                  ],
                                  "local": true,
                                  "dateFormatForSort": "2021-01-09T17:00:00.000Z"
                                },
                                {
                                  "label": "Last 30 days",
                                  "value": [
                                    "DATE_LAST(30,'days')",
                                    "TODAY()"
                                  ],
                                  "isDefault": false,
                                  "dateFormatForSort": "2020-12-25T17:00:00.000Z"
                                }
                              ]
                            },
                            "id": "id-1a93a586-d4e3-4d55-b570-88dcf49c1a47"
                          },
                          "id": "id-ebf29fa1-dae4-4df2-ab09-0f61318d8c0a"
                        }
                      ]
                    }
                  },
                  'base': {
                    'config': {
                      'query': {
                        'id': 'id-e825ec80-0b65-47b7-bfc3-da2db5eaa234',
                        'level': 0,
                        'type': 'AND',
                        'conditions': [
                          {
                            'id': 'id-07f9af28-ea48-49ca-aa5e-cc65912c62fc',
                            'level': 1,
                            'column': 'bb_winner',
                            'value': 'null',
                            'operator': 'not_null',
                            'parentId': 'id-e825ec80-0b65-47b7-bfc3-da2db5eaa234'
                          }
                        ],
                        'parentId': null
                      }
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
                    'id': 'id-8bb95fb4-612a-4ad5-9015-52bb26bb76d0',
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
                'id': 'id-4c49ee5c-3e80-40ba-ba90-3852f078ada1'
              },
              'id': 'id-b4042cfd-10c2-4322-8c70-cfe5db0db53b'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 6,
                  'y': 342,
                  'w': 6,
                  'h': 38,
                  'i': 3,
                  'id': 'id-01f13e02-3138-4c86-9a43-42092ac67861',
                  'moved': false
                },
                'widgetId': '40ace0ef-c70e-4e41-b1e3-355a14d869ae',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-38017bde-2e46-47ee-ada7-14a38907a161',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-52b6613e-2978-4db5-b196-fee549a7ebb2',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': 'id-d3d911e4-ccbb-4629-ad43-6647eb220915',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-7cd702a5-0563-418f-a350-e94e864bf0ff'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 342,
                  'w': 6,
                  'h': 38,
                  'i': 4,
                  'id': 'id-da848f2a-62be-4748-9f1f-e78ff8439e42',
                  'moved': false
                },
                'widgetId': '0600c032-144b-4dfc-ac91-7f87c76bfb8f',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-b8dbb449-d78b-438c-9454-3c4140b6ef7a',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-d151942a-0938-4482-90aa-f9cdd36de836',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '0c9f5749-01c7-43ae-b0dd-83aec55052e7',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-d1dfc109-6668-4127-b5f6-3c6b231b55cd'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 6,
                  'y': 221,
                  'w': 6,
                  'h': 39,
                  'i': 5,
                  'id': 'id-735dd3f9-6f96-4b73-8dfb-d766cabfbcee',
                  'moved': false
                },
                'widgetId': '5ea5d1aa-f0ef-450e-b374-8157b2552508',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-86c20a85-1822-4826-a6a7-47af67ddc15b',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-67f46dc6-ac9b-4db2-964c-54a77d3cf52b',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '3af415da-b11b-4135-9560-1149a642dc70',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-f9af4747-6bcd-4cab-9d1b-8972e1c86fbc'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 306,
                  'w': 6,
                  'h': 36,
                  'i': 6,
                  'id': 'id-d323cc3b-bf8c-4882-a655-9294f2ee94ad',
                  'moved': false
                },
                'widgetId': 'cbf2e576-a810-45e9-91a0-16c1c6f1fada',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-2702d5a0-2d4a-4915-b0c8-5a1f12a6ec5f',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-7ecc66bf-a582-4bfe-bdab-8af098225267',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '536a6f60-595b-41e2-935f-0108bb8b5157',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-9a5159cb-dfb6-4ad2-bfbb-265f08d312b5'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 6,
                  'y': 306,
                  'w': 6,
                  'h': 36,
                  'i': 7,
                  'id': 'id-cbcc39c2-e11c-4f55-acbc-0e085be75ea3',
                  'moved': false
                },
                'widgetId': 'e2174616-c2ba-4351-83b4-7318c79bc1ad',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-81909890-8326-48a7-93d5-6e9f7cb50c14',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-a903c6eb-85c9-4230-b952-c8fa99333a60',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '9dae4d74-f020-48c9-9d29-44b6d7a3b37b',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-6e65e919-0a6a-465e-b450-d16e22a70771'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 52,
                  'w': 12,
                  'h': 73,
                  'i': 8,
                  'id': 'id-239e0787-b1e0-47bf-9816-2273e30102b5',
                  'moved': false
                },
                'widgetId': '5eab5815-7051-4d3f-b158-9b2d0b8af443',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-cf212841-e490-4427-8d48-4bfc59235f9f',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-b6d2a0b2-9b36-489d-99ea-1cf8e60cae97',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '56cad9ba-ce54-4887-827e-aff8b53fbdb8',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-54eda008-cb6e-4f90-9b1d-562f63b651b8'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 125,
                  'w': 12,
                  'h': 59,
                  'i': 9,
                  'id': 'id-818eaec6-c7a1-435f-bb4f-7e4cf416fd0f',
                  'moved': false
                },
                'widgetId': '73951368-24f6-4e85-be97-1a2944fbdb0c',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-3f26c2cb-b392-4b96-839b-764cafad9001',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-39dedc0e-81dc-45bd-9724-236bd8dc540d',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '12773170-d687-4ea1-9326-fa51a5f4bcc6',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-c1044eb3-0d18-47dc-887c-ca1c39d9c8e3'
            },
            {
              'type': 'cbpo-widget-loader',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 184,
                  'w': 12,
                  'h': 37,
                  'i': 10,
                  'id': 'id-41808acb-a6ad-4865-be13-e7ebe6267bd2',
                  'moved': false
                },
                'widgetId': 'ed422907-ecdf-4c0a-86f6-7969c4667463',
                'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id',
                'id': 'id-af534514-0db3-499a-b96b-f3c30a9b02e0',
                'dataSource': null,
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
                          'label': 'Template Settings',
                          'icon': 'fa fa-cog',
                          'value': 'template_settings',
                          'type': 'item',
                          'variant': 'secondary'
                        },
                        {
                          'label': 'Save',
                          'icon': 'fa fa-floppy-o',
                          'value': 'save_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Save As',
                          'icon': 'fa fa-clone',
                          'value': 'save_as_widget',
                          'type': 'item',
                          'variant': 'primary'
                        },
                        {
                          'label': 'Remove',
                          'icon': 'fa fa-times',
                          'value': 'remove_template',
                          'type': 'item',
                          'variant': 'danger'
                        }
                      ]
                    },
                    'id': 'id-6a22f059-264f-460d-8b49-4181395ab5aa',
                    'widget': {
                      'title': {
                        'enabled': true,
                        'text': ''
                      },
                      'class': ''
                    }
                  }
                },
                'elementId': '3ba520bc-cd6e-411b-8fa1-2e444c328c37',
                'widget': {
                  'title': {
                    'enabled': true,
                    'text': ''
                  },
                  'class': ''
                }
              },
              'id': 'id-f98fe147-242a-45fc-b94e-cb2f99972e6d'
            },
            {
              'type': 'cbpo-widget',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 380,
                  'w': 12,
                  'h': 50,
                  'i': 11,
                  'id': 'id-73f6d312-716b-42a7-b57c-f4944da3f6fe',
                  'moved': false
                },
                'autoHeight': false,
                'widget': {
                  'title': {
                    'text': 'Listings w/ A+ Content',
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
                  'id': 'id-9592c6bb-67e3-4d6b-a584-5cb2c577975f',
                  'class': ''
                },
                'action': {
                  'elements': []
                },
                'elements': [
                  {
                    'type': 'cbpo-element-table',
                    'config': {
                      'dataSource': '6ca8622d-c851-423f-be32-616d559ced44',
                      'header': {
                        'draggable': false,
                        'resizeMinWidth': null,
                        'multiline': false
                      },
                      'columns': [
                        {
                          'name': 'style',
                          'type': 'string',
                          'label': 'Style',
                          'header': {
                            'format': null
                          },
                          'cell': {
                            'width': 316.75,
                            'format': null,
                            'aggrFormats': null,
                            'binFormats': null
                          },
                          'sortable': {
                            'enabled': true
                          },
                          'visible': true,
                          'detailColIndex': 0,
                          'isUniqueKey': false,
                          'displayName': 'Style'
                        },
                        {
                          'name': 'asin',
                          'type': 'string',
                          'label': 'ASIN',
                          'header': {
                            'format': null
                          },
                          'cell': {
                            'format': null,
                            'aggrFormats': null,
                            'binFormats': null,
                            'width': 316.75
                          },
                          'sortable': {
                            'enabled': true
                          },
                          'visible': true,
                          'detailColIndex': 0,
                          'isUniqueKey': false,
                          'displayName': 'ASIN'
                        },
                        {
                          'name': 'title',
                          'type': 'string',
                          'label': 'Title',
                          'header': {
                            'format': null
                          },
                          'cell': {
                            'format': null,
                            'aggrFormats': null,
                            'binFormats': null,
                            'width': 316.75
                          },
                          'sortable': {
                            'enabled': true
                          },
                          'visible': true,
                          'detailColIndex': 0,
                          'isUniqueKey': false,
                          'displayName': 'Title'
                        },
                        {
                          'name': 'amazon_link',
                          'type': 'string',
                          'label': 'Amazon Link',
                          'header': {
                            'format': null
                          },
                          'cell': {
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
                              'type': 'link',
                              'config': {
                                'target': '_blank',
                                'text': 'amazon.com'
                              }
                            },
                            'aggrFormats': null,
                            'binFormats': null,
                            'width': 316.75
                          },
                          'sortable': {
                            'enabled': true
                          },
                          'visible': true,
                          'detailColIndex': 0,
                          'isUniqueKey': false,
                          'displayName': 'Amazon Link'
                        }
                      ],
                      'sorting': [],
                      'widget': {
                        'title': {
                          'text': 'Listings w/ A+ Content',
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
                          },
                          'position': 'top'
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
                        },
                        'id': 'id-09f9f916-7088-4868-8a12-139d1a46e12b'
                      },
                      'grouping': {
                        'columns': [],
                        'aggregations': []
                      },
                      'bins': [],
                      'pagination': {
                        'limit': 50,
                        'current': 1,
                        'total': 1,
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
                        'id': 'id-2867ff7e-1fb3-45e2-8583-ab79ad25a8a2',
                        'widget': {
                          'title': {
                            'enabled': true,
                            'text': ''
                          },
                          'class': ''
                        }
                      },
                      'messages': {
                        'no_data_at_all': 'No data',
                        'no_data_found': 'No data found'
                      },
                      'timezone': {
                        'enabled': true,
                        'utc': 'America/Danmarkshavn',
                        'visible': false
                      },
                      'rowActions': {
                        'enabled': false,
                        'inline': 1,
                        'display': 'always',
                        'position': 'left',
                        'colWidth': 150,
                        'controls': []
                      },
                      'bulkActions': {
                        'enabled': false,
                        'enableInlineAction': true,
                        'mode': 'checkbox',
                        'filterMode': false,
                        'total': 35,
                        'labels': {
                          'actionColumn': 'Actions',
                          'selectAll': 'Select all $total items',
                          'allSelected': 'All $total items selected'
                        },
                        'controls': []
                      },
                      'detailView': {
                        'enabled': true,
                        'mode': 'inline',
                        'action': {
                          'breakpoint': 768,
                          'props': {
                            'size': 'sm',
                            'variant': 'primary'
                          },
                          'icons': {
                            'closed': 'fa-arrow-circle-o-down',
                            'opened': 'fa-arrow-circle-o-right'
                          },
                          'label': 'View'
                        },
                        'breakpoints': {
                          '320': 1,
                          '768': 2,
                          '1024': 3
                        }
                      },
                      'id': '919612e7-e325-4b3b-8c48-5923df647825',
                      'filter': {
                        'type': 'AND',
                        'conditions': [
                          {
                            'id': 'id-a9e1e5bc-b1e2-4b51-9fac-d6055421555f',
                            'level': 1,
                            'column': 'ebc_uploaded',
                            'value': 'Y',
                            'operator': '$eq',
                            'parentId': 'id-369ace5c-6b27-45f9-bd02-614ad1a533a4'
                          },
                          {
                            'id': 'id-d0883e69-ef96-45d8-ae76-9f14eca6034d',
                            'level': 1,
                            'type': 'OR',
                            'conditions': [
                              {
                                'id': 'id-d874a03b-17f8-4d83-a74c-086bdec7247e',
                                'level': 2,
                                'column': 'map_status',
                                'value': 'Y',
                                'operator': '$eq',
                                'parentId': 'id-d0883e69-ef96-45d8-ae76-9f14eca6034d'
                              },
                              {
                                'id': 'id-553ee496-d7c2-4f1e-bc83-431a5a2ffe68',
                                'level': 2,
                                'column': 'map_status',
                                'value': 'MAP',
                                'operator': '$eq',
                                'parentId': 'id-d0883e69-ef96-45d8-ae76-9f14eca6034d'
                              }
                            ],
                            'parentId': 'id-369ace5c-6b27-45f9-bd02-614ad1a533a4'
                          }
                        ]
                      },
                      'drillDown': {
                        'enabled': false
                      },
                      'compactMode': {
                        'enabled': false,
                        'mode': 'normal'
                      },
                      'globalSummary': {
                        'enabled': false,
                        'summaries': []
                      },
                      'tableSummary': {
                        'enabled': false,
                        'position': 'footer',
                        'labelActionColumn': 'Summary',
                        'summaries': []
                      },
                      // config to check table export config - uncomment to turn it on
                      // "exportConfig": {
                      //   "query": {
                      //     "orders": [
                      //       {
                      //         "column": "asin",
                      //         "direction": "desc"
                      //       }
                      //     ],
                      //     "timezone": "America/Los_Angeles",
                      //     "group": {
                      //       "columns": [
                      //         {
                      //           'name': 'asin',
                      //           'type': 'string',
                      //           'label': 'ASIN',
                      //           'header': {
                      //             'format': null
                      //           },
                      //           'cell': {
                      //             'format': null,
                      //             'aggrFormats': null,
                      //             'binFormats': null,
                      //             'width': 316.75
                      //           },
                      //           'sortable': {
                      //             'enabled': true
                      //           },
                      //           'visible': true,
                      //           'detailColIndex': 0,
                      //           'isUniqueKey': false,
                      //           'displayName': 'ASIN'
                      //         },
                      //       ],
                      //       "aggregations": []
                      //     },
                      //     "fields": [
                      //       {
                      //         "name": "title",
                      //         "alias": "Title"
                      //       },
                      //       {
                      //         "name": "asin",
                      //         "alias": "ASIN"
                      //       }
                      //     ]
                      //   }
                      // }
                    }
                  }
                ],
                'filter': {
                  'form': {
                    'config': {
                      'controls': []
                    }
                  },
                  'base': {
                    'config': {
                      'query': {
                        'id': 'id-369ace5c-6b27-45f9-bd02-614ad1a533a4',
                        'level': 0,
                        'type': 'AND',
                        'conditions': [
                          {
                            'id': 'id-a9e1e5bc-b1e2-4b51-9fac-d6055421555f',
                            'level': 1,
                            'column': 'ebc_uploaded',
                            'value': 'Y',
                            'operator': '$eq',
                            'parentId': 'id-369ace5c-6b27-45f9-bd02-614ad1a533a4'
                          },
                          {
                            'id': 'id-d0883e69-ef96-45d8-ae76-9f14eca6034d',
                            'level': 1,
                            'type': 'OR',
                            'conditions': [
                              {
                                'id': 'id-d874a03b-17f8-4d83-a74c-086bdec7247e',
                                'level': 2,
                                'column': 'map_status',
                                'value': 'Y',
                                'operator': '$eq',
                                'parentId': 'id-d0883e69-ef96-45d8-ae76-9f14eca6034d'
                              },
                              {
                                'id': 'id-553ee496-d7c2-4f1e-bc83-431a5a2ffe68',
                                'level': 2,
                                'column': 'map_status',
                                'value': 'MAP',
                                'operator': '$eq',
                                'parentId': 'id-d0883e69-ef96-45d8-ae76-9f14eca6034d'
                              }
                            ],
                            'parentId': 'id-369ace5c-6b27-45f9-bd02-614ad1a533a4'
                          }
                        ],
                        'parentId': null
                      }
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
                      },
                      'ignore': {
                        'global': {
                          'visible': false,
                          'value': false
                        },
                        'base': {
                          'visible': false,
                          'value': false
                        }
                      },
                      'form': {
                        'columns': []
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
                    'managedColumns': [],
                    'hiddenColumns': []
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
                        },
                        {
                          'label': 'Data Source',
                          'icon': 'fa fa-database',
                          'value': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/6ca8622d-c851-423f-be32-616d559ced44',
                          'link': true,
                          'type': 'item'
                        }
                      ],
                      'dsUrl': '#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id'
                    },
                    'id': 'id-bcc2ea06-4d1c-4faa-b0ee-350d2991482b',
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
                'id': 'c5301338-530c-4f6d-98a7-305c30efa6be'
              },
              'visualizationId': 'fd57c72b-6e91-46d2-88ad-1c19d4bbbe40'
            }
          ],
          'layout': [
            {
              'x': 0,
              'y': 0,
              'w': 12,
              'h': 49,
              'i': 0,
              'moved': false
            },
            {
              'x': 0,
              'y': 230,
              'w': 12,
              'h': 46,
              'i': 1,
              'moved': false
            },
            {
              'x': 0,
              'y': 191,
              'w': 6,
              'h': 39,
              'i': 2,
              'moved': false
            },
            {
              'x': 6,
              'y': 312,
              'w': 6,
              'h': 38,
              'i': 3,
              'moved': false
            },
            {
              'x': 0,
              'y': 312,
              'w': 6,
              'h': 38,
              'i': 4,
              'moved': false
            },
            {
              'x': 6,
              'y': 191,
              'w': 6,
              'h': 39,
              'i': 5,
              'moved': false
            },
            {
              'x': 0,
              'y': 276,
              'w': 6,
              'h': 36,
              'i': 6,
              'moved': false
            },
            {
              'x': 6,
              'y': 276,
              'w': 6,
              'h': 36,
              'i': 7,
              'moved': false
            },
            {
              'x': 0,
              'y': 49,
              'w': 12,
              'h': 58,
              'i': 8,
              'moved': false
            },
            {
              'x': 0,
              'y': 107,
              'w': 12,
              'h': 47,
              'i': 9,
              'moved': false
            },
            {
              'x': 0,
              'y': 154,
              'w': 12,
              'h': 37,
              'i': 10,
              'moved': false
            }
          ],
          'id': 'id-ad56e646-f673-4890-81bd-abae324732f3'
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
                  'label': 'Dashboard Settings',
                  'icon': 'fa fa-cog',
                  'value': 'widget-settings',
                  'type': 'item'
                }
              ]
            },
            'id': 'id-6412f2c8-55bc-4152-a125-a10adbde3327',
            'widget': {
              'title': {
                'enabled': true,
                'text': ''
              },
              'class': ''
            }
          }
        },
        'id': 'id-6cae5aee-fbb1-4ab8-85da-c7173087daa5'
      },
      isBuilder: false,
      token: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiY2UwYmU1ODEtNDlkZi00Mjg4LThiNzItZTk2MWRkMzBhMTA1IiwidXNlcm5hbWUiOiJjYnBvX3FhQG1haWxpbmF0b3IuY29tIiwiZXhwIjoxNTk4NzUyNjQwLCJlbWFpbCI6ImNicG9fcWFAbWFpbGluYXRvci5jb20iLCJvcmlnX2lhdCI6MTU5ODU3OTg0MCwiYXBwIjoibWF0cml4IiwiZm5hbWUiOiJDQlBPIiwibG5hbWUiOiJRQSJ9.Pe6gb1KjAimOiUbimvRkwyLHAog3qcYemGbMXR1X6MWCErJbe3hhNHMtB21saROTe2nOfq0Gk8FOcgo87m08GP3OBGPuKMvBKjCWCSWf8HqDLbu3gPgBI4lKxKy239xHZf-0WYHK5CxZem7HS6Rwsr7tBhFLkw5AwZizh7AC8m1YGlOrjOMSkuzEjWDr9eTVHO02QSKFhXfXvwrzbeKhcsfhJ6b7fnFFDxoOz3NpIHVxK4XRBbyK9yB__P_LPLgYkcqgKXNCMkhotRnfWkoNu1NhS8eTQQg5kZ1V1P_psyb-Wjsk0ykSHWlaBBpwOninZ3zhJSnlwFnxPYprsYcXcA',
      raAxios: null
    }
  },
  computed: {
    getTemplate() {
      return [
        {
          name: 'Dashboard Container',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  mounted() {
    this.render('#dashboard-container-demo', this.template, 'http://ds-api.qa.channelprecision.com/v1/', '652cce4a-7190-475f-8e4d-d73b02173ab5')
  },
  methods: {
    createWidgetLayoutConfig() {
      let widgets = _.range(0, 9).map((e) => {
        let widgetConfig = {
          type: 'cbpo-widget',
          config: _.cloneDeep(this.widgetConfig)
        }
        let filterConfig = {
          form: {
            config: {
              controls: [
                {
                  type: 'cbpo-filter-control-select',
                  config: {
                    label: {
                      text: 'Seller Name'
                    },
                    dataSource: 'dataSource',
                    common: {
                      column: {
                        name: 'seller_name',
                        type: 'string'
                      },
                      operator: '==',
                      value: null
                    },
                    selection: {
                      empty: {
                        label: 'Select All',
                        value: null
                      },
                      options: []
                    }
                  }
                },
                {
                  type: 'cbpo-filter-control-select',
                  config: {
                    label: {
                      text: 'Date'
                    },
                    dataSource: 'dataSource',
                    common: {
                      column: {
                        name: 'captured_at',
                        type: 'date'
                      },
                      operator: '==',
                      value: null
                    },
                    selection: {
                      empty: {
                        label: 'Select All',
                        value: null
                      },
                      options: []
                    }
                  }
                },
                {
                  type: 'cbpo-filter-control-input',
                  config: {
                    label: {
                      text: 'asin'
                    },
                    dataSource: 'dataSource',
                    common: {
                      column: {
                        name: 'asin',
                        type: 'string'
                      },
                      operator: 'contains',
                      value: null
                    },
                    selection: {
                      empty: {
                        label: 'Select All',
                        value: null
                      },
                      options: []
                    }
                  }
                },
                {
                  type: 'cbpo-filter-control-range',
                  config: {
                    label: {
                      text: 'Seller Price'
                    },
                    dataSource: 'dataSource',
                    common: {
                      column: {
                        name: 'seller_price',
                        type: 'number'
                      },
                      operator: 'in_range',
                      value: []
                    },
                    selection: {
                      empty: {
                        label: 'Select All',
                        value: null
                      },
                      options: []
                    }
                  }
                },
                {
                  type: 'cbpo-filter-control-range',
                  config: {
                    label: {
                      text: 'Captured At'
                    },
                    dataSource: 'dataSource',
                    common: {
                      column: {
                        name: 'captured_at',
                        type: 'date'
                      },
                      operator: 'in_range',
                      value: []
                    },
                    selection: {
                      empty: {
                        label: 'Select All',
                        value: null
                      },
                      options: []
                    }
                  }
                }
              ]
            }
          }
        }
        let groupingConfig = {
          columns: [
            { name: 'sku' }
          ],
          aggregations: [
            { column: 'seller_name', alias: 'seller_name', aggregation: 'count' },
            { column: 'upc/ean', alias: 'upc/ean', aggregation: 'count' },
            { column: 'asin', alias: 'asin', aggregation: 'count' },
            { column: 'title', alias: 'title', aggregation: 'concat' },
            { column: 'seller_price', alias: 'seller_price', aggregation: 'sum' },
            { column: 'map_price', alias: 'map_price', aggregation: 'sum' },
            { column: 'diff', alias: 'diff', aggregation: 'sum' },
            { column: 'diff_percent', alias: 'diff_percent', aggregation: 'avg' },
            { column: 'link', alias: 'link', aggregation: 'count' },
            { column: 'screenshot', alias: 'screenshot', aggregation: 'count' },
            { column: 'captured_at', alias: 'captured_at', aggregation: 'count' },
            { column: 'fba', alias: 'fba', aggregation: 'count' },
            { column: 'prime', alias: 'prime', aggregation: 'count' },
            { column: 'condition', alias: 'condition', aggregation: 'count' },
            { column: 'rating', alias: 'rating', aggregation: 'count' },
            { column: 'growth_value', alias: 'growth_value', aggregation: 'count' }
          ]
        }
        widgetConfig.config.widget.title.text = 'Widget ' + (e + 1)
        widgetConfig.config.elements[0].config.columns = _.cloneDeep(this.configColumns)
        switch (e) {
          case 0:
            widgetConfig.config.grid = {
              x: 0,
              y: 0,
              w: 12,
              h: 40,
              i: 0
            }
            widgetConfig.config.filter = _.cloneDeep(filterConfig)
            break
          case 1:
            widgetConfig.config.filter = _.cloneDeep(filterConfig)
            widgetConfig.config.elements[0].config.grouping = _.cloneDeep(groupingConfig)
            widgetConfig.config.grid = {
              x: 0,
              y: 40,
              w: 6,
              h: 80,
              i: 1
            }
            break
          case 2:
            widgetConfig.config = _.cloneDeep(this.widgetChartConfig)
            widgetConfig.config.grid = {
              x: 6,
              y: 40,
              w: 6,
              h: 40,
              i: 2
            }
            break
          case 3:
            widgetConfig.config.grid = {
              x: 6,
              y: 80,
              w: 6,
              h: 40,
              i: 3
            }
            break
          case 4:
            widgetConfig.config.grid = {
              x: 0,
              y: 120,
              w: 12,
              h: 40,
              i: 4
            }
            widgetConfig.config.elements[0].config.pagination.limit = 5
            widgetConfig.config.autoHeight = true
            break
          case 5:
            widgetConfig.config.grid = {
              x: 0,
              y: 160,
              w: 12,
              h: 40,
              i: 5
            }
            widgetConfig.config.elements[0].config.pagination.limit = 5
            widgetConfig.config.autoHeight = true
            break
          case 6:
            widgetConfig.config.filter = _.cloneDeep(filterConfig)
            widgetConfig.config.grid = {
              x: 0,
              y: 200,
              w: 8,
              h: 40,
              i: 6
            }
            break
          case 7:
            widgetConfig.config.grid = {
              x: 8,
              y: 200,
              w: 4,
              h: 40,
              i: 7
            }
            break
          case 8:
            widgetConfig.config = _.cloneDeep(this.widgetHtmlConfig)
            widgetConfig.config.grid = {
              x: 0,
              y: 240,
              w: 12,
              h: 40,
              i: 8
            }
            break
        }
        return widgetConfig
      })
      this.config.widgetLayout.widgets = widgets
    },
    triggerBuilderMode() {
      window.CBPO.$bus.$emit('CBPO_TOGGLE_BUILDER_MODE', this.isBuilder)
    }
  },
  async created() {
    this.raAxios = axios.create({
      baseURL: 'http://ra-api.qa.channelprecision.com',
      timeout: 60000
    })
    this.raAxios.interceptors.request.use(config => {
      // config.headers['ra-api-token'] = `87f6e425-4810-4897-a81d-1581a43fc829`
      let apiToken = JSON.parse(localStorage.getItem('auth')).ps.userModule.userToken
      if (apiToken) {
        config.headers.Authorization = `Bearer ${apiToken}`
      } else {
        config.headers.Authorization = `Bearer ${this.token}`
      }
      return config
    }, (err) => {
      return Promise.reject(err)
    })
    this.raAxios.interceptors.response.use((response) => {
      return response
    }, (error) => {
      if (error.response && error.response.data) {
        let handler = `handle`
        if (!handler) {
          console.log('No remove API error handler.')
        } else {
          handler(error.response.data.statusCode)
        }
        return Promise.reject(error.response.data)
      }
      return Promise.reject(error.message)
    })
    this.config.widgetLayout.widgets.forEach(widget => {
      widget.config.load = async (promise, widgetId, dataSource) => {
        const clientId = '11153189-c451-43db-84aa-8de6dcef3484'
        // call RA service here, after that promise.resolve(config) to pass config to sdk
        let response = await this.raAxios.get(`/v1/clients/${clientId}/visualizations/${widgetId || widget.config.widgetId}`)
        // console.log(promise, widgetId, dataSource)
        promise.resolve(
          response.data
        )
      }
      widget.config.save = async (promise, widgetInfo, saveAs) => {
        let payload = {
          ds_id: widgetInfo.ds_id,
          cf_object: widgetInfo.cf_object,
          name: `${widgetInfo.name}`
        }
        if (saveAs || widgetInfo.is_programmed) {
          let response = await this.raAxios.post(`/v1/clients/${widgetInfo.client_id}/visualizations`, payload)
          promise.resolve(
            response.data
          )
        } else {
          let response = await this.raAxios.put(`/v1/clients/${widgetInfo.client_id}/visualizations/${widgetInfo.id}`, payload)
          promise.resolve(
            response.data
          )
        }
      }
    })
    window.config = _.cloneDeep(this.config)
    window.dataSource = _.cloneDeep(this.dataSource)
  }
})
