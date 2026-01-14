const sdkDashboardGlobalFilterPage = Vue.component('sdkDashboardGlobalFilterPage', {
  template: `
    <div class="dashboard-global-filter">
      <h5>Example: </h5>
      <label>Builder Mode</label>
      <input type="checkbox" v-model="isBuilder" @change="triggerBuilderMode()"/>
      <div id="dashboard-global-filter"></div>
      <sdk-export-code :templates="getTemplate"/>
    </div>
  `,
  components: {
    'sdk-export-code': sdkExportCodeComponent
  },
  mixins: [configMixins, renderMixins],
  data() {
    return {
      template: '<cbpo-widget :builder="true" class="p-0" config-ref="config"></cbpo-widget>',
      widgetConfig: {
        widget: {
          title: {
            text: 'All Repeat Offenders', // or null
            enabled: true // true / false
          }
        },
        elements: [{
          type: 'cbpo-element-table',
          config: {
            widget: {
              title: {
                enabled: false
              }
            },
            dataSource: 'idreportingsdk',
            columns: [],
            pagination: {
              limit: 30
            }
          }
        }]
      },
      config: {
        "menu": {
          "config": {
            "selection": {
              "options": [
                {
                  "label": "Widget Settings",
                  "icon": "fa fa-cog",
                  "value": "widget-settings",
                  "type": "item"
                },
                {
                  "label": "Element Settings",
                  "icon": "fa fa-cog",
                  "value": "element-settings",
                  "type": "item"
                },
                {
                  "label": "Remove",
                  "icon": "fa fa-times",
                  "value": "remove",
                  "type": "item"
                },
                {
                  "type": "divider"
                },
                {
                  "label": "Download CSV",
                  "icon": "fa fa-download",
                  "value": "csv",
                  "type": "item"
                },
                {
                  "label": "Data Source",
                  "icon": "fa fa-database",
                  "value": "#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/87525685-3ea0-4fed-acb4-da0d024c7dfd",
                  "link": true,
                  "type": "item"
                }
              ],
              "dsUrl": "#/ra/11153189-c451-43db-84aa-8de6dcef3484/datasources/manage/managed/:client_id"
            },
            "label": {
              "text": ""
            },
            "icons": {
              "css": "fa fa-ellipsis-h"
            },
            "dataSource": null
          },
          "enabled": true
        },
        "grid": {
          "x": 0,
          "y": 0,
          "w": 12,
          "h": 50,
          "i": 0,
          "id": "id-dabf38c0-0914-410f-bc96-909f54d7a817",
          "moved": false
        },
        "autoHeight": false,
        "widget": {
          "title": {
            "text": "Daily Sales",
            "enabled": true,
            "edited": true
          },
          "style": {
            "background_color": null,
            "foreground_color": null,
            "header_background_color": null,
            "header_foreground_color": null,
            "border_width": null,
            "border_radius": null
          },
          "id": "id-df07a05b-3ec4-4c49-bd07-7ca797211876",
          "class": ""
        },
        "action": {
          "elements": []
        },
        "elements": [
          {
            "type": "cbpo-element-table",
            "config": {
              "dataSource": "87525685-3ea0-4fed-acb4-da0d024c7dfd",
              "header": {
                "resizeMinWidth": null,
                "multiline": false,
                "draggable": false
              },
              "drillDown": {
                "enabled": false
              },
              "columns": [
                {
                  "displayName": "Amazon Order ID",
                  "name": "amazon_order_id",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "string",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "ASIN",
                  "name": "asin",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "string",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "SKU",
                  "name": "sku",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "string",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "Title",
                  "name": "title",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "string",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "Quantity",
                  "name": "quantity",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "number",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "Item Sale Charged",
                  "name": "item_sale_charged",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "number",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "Item Sale Status",
                  "name": "item_sale_status",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "string",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "Fulfillment Type",
                  "name": "fulfillment_type",
                  "visible": true,
                  "cell": {
                    "format": null,
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "string",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                },
                {
                  "displayName": "Date",
                  "name": "date",
                  "visible": false,
                  "cell": {
                    "format": {
                      "config": {
                        "format": "L LT",
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
                      },
                      "type": "temporal",
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
                      }
                    },
                    "aggrFormats": null,
                    "binFormats": null
                  },
                  "header": {
                    "format": null
                  },
                  "sort": {
                    "enabled": true,
                    "direction": null
                  },
                  "type": "date",
                  "sortable": {
                    "enabled": true
                  },
                  "detailColIndex": 0,
                  "isUniqueKey": false
                }
              ],
              "sorting": [],
              "widget": {
                "title": {
                  "text": "Table of [Amazon Order ID, ASIN, SKU, Title, Quantity, Item Sale Charged, Item Sale Status, Fulfillment Type, Date]",
                  "enabled": false,
                  "edited": false
                },
                "style": {
                  "background_color": null,
                  "foreground_color": null,
                  "header_background_color": null,
                  "header_foreground_color": null,
                  "border_width": null,
                  "border_radius": null
                }
              },
              "sizeSettings": {
                "defaultMinSize": 250,
                "warningText": "The area is too small for this visualization."
              },
              "globalControlOptions": {
                "aggregation": {
                  "enabled": false
                },
                "globalGrouping": {
                  "enabled": false,
                  "config": {
                    "value": false
                  },
                  "position": "top"
                },
                "grouping": {
                  "enabled": false
                },
                "editColumn": {
                  "enabled": false
                },
                "editColumnLabel": {
                  "enabled": false
                },
                "editColumnFormat": {
                  "enabled": false
                },
                "editBin": {
                  "enabled": false
                },
                "id": "id-866e3763-b026-461b-8b3a-5f83284065d3"
              },
              "grouping": {
                "columns": [],
                "aggregations": []
              },
              "bins": [],
              "pagination": {
                "limit": 50,
                "current": 1,
                "total": 1,
                "type": "auto",
                "buttons": {
                  "first": {
                    "visibility": true,
                    "label": "First"
                  },
                  "last": {
                    "visibility": true,
                    "label": "Last"
                  },
                  "prev": {
                    "visibility": true,
                    "label": "Previous"
                  },
                  "next": {
                    "visibility": true,
                    "label": "Next"
                  }
                },
                "numbers": {
                  "beforeCurrent": 2,
                  "afterCurrent": 2
                },
                "default": "auto",
                "id": "id-7c8424a6-aebe-4e7f-be4b-37720ca29bad",
                "widget": {
                  "title": {
                    "enabled": true,
                    "text": ""
                  },
                  "class": ""
                }
              },
              "messages": {
                "no_data_at_all": "No data",
                "no_data_found": "No data found"
              },
              "timezone": {
                "enabled": true,
                "utc": "America/Danmarkshavn",
                "visible": false
              },
              "compactMode": {
                "enabled": false,
                "mode": "normal"
              },
              "rowActions": {
                "enabled": false,
                "inline": 1,
                "display": "always",
                "position": "left",
                "colWidth": 150,
                "controls": []
              },
              "bulkActions": {
                "enabled": false,
                "enableInlineAction": true,
                "mode": "checkbox",
                "filterMode": false,
                "total": 3,
                "labels": {
                  "actionColumn": "Actions",
                  "selectAll": "Select all $total items",
                  "allSelected": "All $total items selected"
                },
                "controls": []
              },
              "detailView": {
                "enabled": true,
                "mode": "inline",
                "action": {
                  "breakpoint": 768,
                  "props": {
                    "size": "sm",
                    "variant": "primary"
                  },
                  "icons": {
                    "closed": "fa-arrow-circle-o-down",
                    "opened": "fa-arrow-circle-o-right"
                  },
                  "label": "View"
                },
                "breakpoints": {
                  "320": 1,
                  "768": 2,
                  "1024": 3
                }
              },
              "globalSummary": {
                "enabled": true,
                "summaries": [
                  {
                    "label": "Quantity",
                    "position": "right",
                    "format": {
                      "config": {
                        "comma": true,
                        "precision": 0,
                        "siPrefix": false
                      },
                      "type": "numeric",
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
                      }
                    },
                    "expr": "SUM(@quantity, '87525685-3ea0-4fed-acb4-da0d024c7dfd') as z1",
                    "id": "c9c2dea9-84e3-48bc-87d1-dca32d65bba3",
                    "prefix": "",
                    "suffix": "",
                    "noDataMessage": "No data"
                  },
                  {
                    "label": "Sales",
                    "position": "right",
                    "format": {
                      "config": {
                        "currency": {
                          "symbol": "$",
                          "symbolPrefix": true,
                          "inCents": false
                        },
                        "numeric": {
                          "comma": true,
                          "precision": 2,
                          "siPrefix": false
                        }
                      },
                      "type": "currency",
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
                      }
                    },
                    "expr": "SUM(@item_sale_charged, '87525685-3ea0-4fed-acb4-da0d024c7dfd') as z2",
                    "id": "2014add7-13d5-4a7c-977f-3f41a579ee48",
                    "prefix": "",
                    "suffix": "",
                    "noDataMessage": "No data"
                  }
                ]
              },
              "tableSummary": {
                "enabled": false,
                "position": "footer",
                "labelActionColumn": "Summary",
                "summaries": []
              },
              "id": "2751d4bf-a18a-4284-b5da-70fee8f00cba"
            }
          }
        ],
        "filter": {
          "form": {
            "config": {
              "controls": [
                {
                  "type": "cbpo-filter-control-select",
                  "config": {
                    "common": {
                      "column": {
                        "name": "date",
                        "type": "date",
                        "label": "Date",
                        "displayName": "Date"
                      },
                      "operator": "$eq",
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
                      },
                      "options": {
                        "format": {
                          "start": "YYYY-MM-DDT00:00:00Z",
                          "end": "YYYY-MM-DDT23:59:59Z"
                        }
                      },
                      "value": "2020-12-06T00:00:00.000Z"
                    },
                    "label": {
                      "text": "Date"
                    },
                    "dataSource": "87525685-3ea0-4fed-acb4-da0d024c7dfd",
                    "selection": {
                      "empty": {
                        "label": "Please select",
                        "enabled": false,
                        "isEmptySelected": true
                      },
                      "format": {
                        "config": {
                          "format": "L",
                          "timezone": "America/Danmarkshavn",
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
                        },
                        "type": "temporal"
                      },
                      "sort": "desc",
                      "options": [
                        {
                          "label": "12/06/2020",
                          "value": "2020-12-06T00:00:00.000Z"
                        },
                        {
                          "label": "12/05/2020",
                          "value": "2020-12-05T00:00:00.000Z"
                        },
                        {
                          "label": "12/04/2020",
                          "value": "2020-12-04T00:00:00.000Z"
                        },
                        {
                          "label": "12/03/2020",
                          "value": "2020-12-03T00:00:00.000Z"
                        },
                        {
                          "label": "12/02/2020",
                          "value": "2020-12-02T00:00:00.000Z"
                        },
                        {
                          "label": "12/01/2020",
                          "value": "2020-12-01T00:00:00.000Z"
                        },
                        {
                          "label": "11/30/2020",
                          "value": "2020-11-30T00:00:00.000Z"
                        },
                        {
                          "label": "11/29/2020",
                          "value": "2020-11-29T00:00:00.000Z"
                        },
                        {
                          "label": "11/28/2020",
                          "value": "2020-11-28T00:00:00.000Z"
                        },
                        {
                          "label": "11/25/2020",
                          "value": "2020-11-25T00:00:00.000Z"
                        },
                        {
                          "label": "11/24/2020",
                          "value": "2020-11-24T00:00:00.000Z"
                        },
                        {
                          "label": "11/20/2020",
                          "value": "2020-11-20T00:00:00.000Z"
                        },
                        {
                          "label": "11/10/2020",
                          "value": "2020-11-10T00:00:00.000Z"
                        }
                      ]
                    },
                    "id": "id-8c2541b1-2865-4f24-a2d7-ef4dec81b6e4"
                  },
                  "id": "id-95a11727-5e37-4f90-9850-8b745dcc570c"
                },
                {
                  "type": "cbpo-filter-control-select",
                  "config": {
                    "common": {
                      "column": {
                        "name": "fulfillment_type",
                        "type": "string",
                        "label": "Fulfillment Type",
                        "displayName": "Fulfillment Type"
                      },
                      "operator": "$eq",
                      "sort": "asc",
                      "format": null,
                      "options": {
                        "format": {
                          "start": "YYYY-MM-DDT00:00:00Z",
                          "end": "YYYY-MM-DDT23:59:59Z"
                        }
                      }
                    },
                    "label": {
                      "text": "Fulfillment Type"
                    },
                    "dataSource": "87525685-3ea0-4fed-acb4-da0d024c7dfd",
                    "selection": {
                      "empty": {
                        "label": "Please select",
                        "enabled": true,
                        "isEmptySelected": true
                      },
                      "format": null,
                      "sort": "asc",
                      "options": [
                        {
                          "label": "FBA",
                          "value": "FBA"
                        },
                        {
                          "label": "MFN",
                          "value": "MFN"
                        }
                      ]
                    },
                    "id": "id-2bdf7113-1a2b-4280-b773-eb3fc95d03c1"
                  },
                  "id": "id-06ac3048-70c8-4704-aa27-4d29d0658def"
                }
              ]
            }
          },
          "builder": {
            "enabled": false,
            "readable": {
              "enabled": false
            },
            "config": {
              "trigger": {
                "label": "Setting Filter"
              },
              "modal": {
                "title": "Query Builder"
              },
              "format": {
                "temporal": {
                  "date": "YYYY-MM-DD",
                  "datetime": "YYYY-MM-DD hh:mm"
                }
              },
              "threshold": {
                "maxLevel": 5
              },
              "ignore": {
                "global": {
                  "visible": false,
                  "value": false
                },
                "base": {
                  "visible": false,
                  "value": false
                }
              },
              "query": {
                "id": null,
                "level": 0,
                "type": "AND",
                "conditions": []
              },
              "form": {
                "columns": []
              }
            }
          },
          "globalFilter": {
            "enabled": false
          },
          "alignment": "center",
          "base": {
            "config": {
              "query": {
                "id": "id-bc6d5036-fa3f-49b9-a4ee-567759ba0b70",
                "level": 0,
                "type": "AND",
                "conditions": [
                  {
                    "id": "id-a9cb73c0-6381-4494-ae75-916b1f48498c",
                    "level": 1,
                    "type": "OR",
                    "conditions": [
                      {
                        "id": "id-198312f1-a5cd-4e2f-b5aa-17fb97c16820",
                        "level": 2,
                        "column": "title",
                        "value": "The North Face",
                        "operator": "contains",
                        "parentId": "id-a9cb73c0-6381-4494-ae75-916b1f48498c"
                      }
                    ]
                  }
                ],
                "parentId": null
              }
            }
          }
        },
        "columnManager": {
          "enabled": false,
          "config": {
            "trigger": {
              "label": "Manage Columns"
            },
            "modal": {
              "title": "Manage Columns"
            },
            "hiddenColumns": [],
            "managedColumns": []
          }
        },
        "calculatedColumn": {
          "enabled": false
        },
        "waitingForGlobalFilter": false,
        "id": "f4900be8-62f6-45aa-aa6e-4bb5ac7543af",
        "editMode": true
      },
      // config object
      global: {
        type: 'cbpo-widget',
        config: {
          grid: {
            x: 0, y: 0, w: 12, h: 10, i: 0
          },
          autoHeight: true,
          filter: {
            form: {
              config: {
                controls: [
                  {
                    type: 'cbpo-filter-control-select',
                    config: {
                      dataSource: 'idreportingsdk',
                      loadedDataSource: true,
                      common: {
                        column: {
                          name: 'Country',
                          type: 'string'
                        },
                        operator: '=='
                      },
                      label: {
                        text: 'Country'
                      },
                      selection: {
                        empty: {
                          label: 'Select All',
                          enabled: true
                        }
                      }
                    }
                  },
                  {
                    type: 'cbpo-filter-control-input',
                    config: {
                      common: {
                        column: {
                          name: 'Order Date',
                          type: 'datetime'
                        },
                        operator: '=='
                      },
                      label: {
                        text: 'Order Date'
                      },
                      input: {
                        format: {
                          config: {
                            format: 'MM-DD-YYYY'
                          }
                        }
                      }
                    }
                  }
                ]
              }
            },
            globalFilter: {
              enabled: true
            }
          },
          elements: [
            {
              type: 'cbpo-global-filter',
              config: {}
            }
          ]
        }
      },
      table: {
        type: 'cbpo-widget',
        config: {
          autoHeight: true,
          grid: {
            x: 0, y: 40, w: 12, h: 40, i: 1
          },
          elements: [
            {
              type: 'cbpo-element-table',
              config: {
                dataSource: 'idreportingsdk',
                pagination: {
                  limit: 5
                },
                columns: [
                  {
                    name: 'Country'
                  },
                  {
                    name: 'Total Cost'
                  }
                ]
              }
            }
          ]
        }
      },
      chart: {
        type: 'cbpo-widget',
        config: {
          grid: {
            x: 0, y: 40, w: 12, h: 40, i: 1
          },
          filter: {
            form: {
              config: {
                controls: [
                  {
                    type: 'cbpo-filter-control-select',
                    config: {
                      common: {
                        column: {
                          name: 'Country',
                          type: 'string'
                        },
                        operator: '=='
                      },
                      dataSource: 'idreportingsdk',
                      loadedDataSource: true,
                      label: {
                        text: 'Country'
                      },
                      selection: {
                        empty: {
                          label: 'Select All',
                          enabled: true
                        }
                      }
                    }
                  },
                  {
                    type: 'cbpo-filter-control-input',
                    config: {
                      common: {
                        column: {
                          name: 'Order Date',
                          type: 'datetime'
                        },
                        operator: '=='
                      },
                      label: {
                        text: 'Order Date'
                      },
                      input: {
                        format: {
                          config: {
                            format: 'MM-DD-YYYY'
                          }
                        }
                      }
                    }
                  }
                ]
              }
            }
          },
          elements: [
            {
              type: 'cbpo-element-chart',
              config: {
                dataSource: 'idreportingsdk',
                columns: [
                  {
                    name: 'Country'
                  },
                  {
                    name: 'Total Cost'
                  }
                ],
                grouping: {
                  columns: [ {name: 'Country'} ],
                  aggregations: [ {column: 'Total Cost', aggregation: 'sum', alias: 'Total Cost'} ]
                },
                charts: [
                  {
                    series: [
                      {
                        type: 'pie',
                        data: {
                          x: 'Country',
                          y: 'Total Cost'
                        }
                      }
                    ]
                  }
                ]
              }
            }
          ]
        }
      },
      crosstab: {
        type: 'cbpo-widget',
        config: {
          grid: {
            x: 0, y: 80, w: 12, h: 40, i: 2
          },
          autoHeight: true,
          elements: [
            {
              type: 'cbpo-element-crosstab-table',
              config: {
                dataSource: 'idreportingsdk',
                sizeSettings: {
                  defaultMinSize: 250,
                  warningText: 'The area is too small for this visualization.'
                },
                widget: {
                  title: {
                    text: 'Quantitation of [Ship Date] over [Ship Date, Order Priority]',
                    enabled: true,
                    edited: false
                  },
                  style: {
                    background_color: null,
                    foreground_color: null,
                    header_background_color: null,
                    header_foreground_color: null,
                    border_width: null,
                    border_radius: null
                  }
                },
                messages: {
                  no_data_at_all: 'No data',
                  no_data_found: 'No data found'
                },
                globalControlOptions: {
                  aggregation: {
                    enabled: false
                  },
                  globalGrouping: {
                    enabled: false,
                    config: {
                      value: false
                    }
                  },
                  grouping: {
                    enabled: false
                  },
                  editColumn: {
                    enabled: false
                  },
                  editColumnLabel: {
                    enabled: false
                  },
                  editColumnFormat: {
                    enabled: false
                  },
                  editBin: {
                    enabled: false
                  }
                },
                bins: [],
                formats: {
                  aggrs: {}
                },
                sorting: [],
                xColumns: [
                  {
                    name: 'Country',
                    displayName: 'Country',
                    type: 'string',
                    format: null,
                    sortable: {
                      enabled: true
                    }
                  }
                ],
                tColumns: [
                  {
                    name: 'Order Date',
                    displayName: 'Order Date',
                    type: 'date',
                    format: {
                      type: 'temporal',
                      config: {
                        format: 'MM-DD-YYYY'
                      }
                    },
                    sortable: {
                      enabled: true
                    }
                  }
                ],
                yColumns: [
                  {
                    name: 'Total Cost',
                    displayName: 'Total Cost',
                    type: 'int',
                    format: null,
                    sortable: {
                      enabled: true
                    },
                    aggregation: {
                      aggregation: 'sum',
                      alias: 'Total Cost'
                    }
                  }
                ],
                pagination: {
                  limit: 10,
                  current: 1,
                  total: null,
                  type: 'auto',
                  buttons: {
                    first: {
                      visibility: true,
                      label: 'First',
                      style: {}
                    },
                    last: {
                      visibility: true,
                      label: 'Last',
                      style: {}
                    },
                    prev: {
                      visibility: true,
                      label: 'Previous',
                      style: {}
                    },
                    next: {
                      visibility: true,
                      label: 'Next',
                      style: {}
                    }
                  },
                  numbers: {
                    beforeCurrent: 2,
                    afterCurrent: 2
                  },
                  default: 'auto'
                }
              }
            }
          ]
        }
      },
      isBuilder: false
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
    this.render(
      '#dashboard-global-filter',
      this.template,
      'http://ds-api.qa.channelprecision.com/v1/',
      this.VUE_DEMO_TOKEN,
      ''
    )
  },
  methods: {
    createWidgetLayoutConfig() {
      this.config.widgetLayout.widgets = [
        this.global,
        this.table,
        this.crosstab
      ]
    },
    triggerBuilderMode() {
      window.CBPO.$bus.$emit('CBPO_TOGGLE_BUILDER_MODE', this.isBuilder)
    }
  },
  created() {
    // this.createWidgetLayoutConfig()
    // console.log(_.cloneDeep(this.config))
    window.config = _.cloneDeep(this.config)
    // window.dataSource = _.cloneDeep(this.dataSource)
  }
})
