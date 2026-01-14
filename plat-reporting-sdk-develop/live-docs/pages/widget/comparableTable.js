const sdkComparableTablePage = Vue.component('sdkComparableTablePage', {
  template: `
      <div class="comparable-table-demo">
      <h5>Example: </h5>
      <div style="height: 600px" id="comparable-table-demo">
      </div>
      <div class="mt-2">
        <sdk-export-code :templates="getTemplate"/>
      </div>
      </div>
    `,
  data() {
    let dataSource = 'es:8b9f6796-0432-495e-b5fb-0a3720b0cefa:sale_items'
    return {
      dataSource: dataSource,
      baseURL: 'http://ds-api.qa.channelprecision.com/v1/',
      template: '<cbpo-widget class="p-0" config-ref="config"></cbpo-widget>',
      config: {
        widget: {
          title: {
            text: `View Data Comparison Builder`,
            enabled: false
          }
        },
        columnManager: {
          enabled: true
        },
        filter: {
          base: {
            config: {
              query: {
                conditions: [
                  // {
                  //   value: "DATE_START_OF(TODAY(), 'day')",
                  //   column: 'sale_date',
                  //   operator: '$gte'
                  // },
                  // {
                  //   value: "DATE_END_OF(TODAY(), 'day')",
                  //   column: 'sale_date',
                  //   operator: '$lte'
                  // },
                  // {
                  //   value: 'amazon.com',
                  //   column: 'channel_name',
                  //   operator: '$eq'
                  // }
                ],
                type: 'AND'
              }
            }
          }
        },
        elements: [
          {
            type: 'cbpo-element-comparable-table',
            config: {
              messages: {
                no_data_at_all: 'No data',
                no_data_found: 'No data found'
              },
              dataSource: dataSource,
              header: {
                resizeMinWidth: 5,
                multiline: true,
                draggable: false
              },
              widget: {
                title: {
                  enabled: false
                }
              },
              timezone: {
                enabled: true,
                utc: 'America/Los_Angeles',
                visible: true
              },
              grouping: {
                columns: [],
                aggregations: [
                  {
                    column: 'item_sale_charged',
                    alias: 'item_sale_charged_sum',
                    aggregation: 'sum'
                  },
                  { column: 'cogs', alias: 'cogs_sum', aggregation: 'sum' },
                  {
                    column: 'item_shipping_cost',
                    alias: 'item_shipping_cost_sum',
                    aggregation: 'sum'
                  },
                  {
                    column: 'refund_admin_fee',
                    alias: 'refund_admin_fee_sum',
                    aggregation: 'sum'
                  },
                  {
                    column: 'item_profit',
                    alias: 'item_profit_sum',
                    aggregation: 'sum'
                  },
                  {
                    column: 'item_sale_charged',
                    alias: 'item_sale_charged_avg',
                    aggregation: 'avg'
                  },
                  { column: 'cogs', alias: 'cogs_avg', aggregation: 'avg' },
                  {
                    column: 'item_shipping_cost',
                    alias: 'item_shipping_cost_avg',
                    aggregation: 'avg'
                  },
                  {
                    column: 'refund_admin_fee',
                    alias: 'refund_admin_fee_avg',
                    aggregation: 'avg'
                  },
                  {
                    column: 'item_profit',
                    alias: 'item_profit_avg',
                    aggregation: 'avg'
                  }
                  // {
                  //   column: 'item_margin',
                  //   alias: 'item_margin',
                  //   aggregation: 'sum'
                  // }
                ]
              },
              rows: [
                {
                  data: {
                    name: 'view 1',
                    alias: 'view_1'
                  },
                  filter: {
                    type: 'AND',
                    conditions: [
                      {
                        value: "DATE_START_OF(DATE_LAST(30,'day'), 'day')",
                        column: 'sale_date',
                        operator: '$gte'
                      },
                      {
                        value: "DATE_END_OF(TODAY(), 'day')",
                        column: 'sale_date',
                        operator: '$lte'
                      },
                      {
                        value: 'amazon.com',
                        column: 'channel_name',
                        operator: '$eq'
                      }
                    ]
                  }
                },
                {
                  data: {
                    name: 'view 2',
                    alias: 'view_2'
                  },
                  filter: {
                    type: 'AND',
                    conditions: [
                      {
                        value: "DATE_START_OF(YESTERDAY(), 'day')",
                        column: 'sale_date',
                        operator: '$gte'
                      },
                      {
                        value: "DATE_END_OF(YESTERDAY(), 'day')",
                        column: 'sale_date',
                        operator: '$lte'
                      },
                      {
                        value: 'amazon.com',
                        column: 'channel_name',
                        operator: '$eq'
                      },
                      {
                        id: 'id-6fb652df-f5d3-4480-a9e9-0efa413a7280',
                        type: 'AND',
                        level: 0,
                        config: {
                          query: {},
                          ignore: {
                            base: {
                              value: false,
                              visible: true
                            },
                            global: {
                              value: false,
                              visible: false
                            }
                          }
                        },
                        enabled: true,
                        parentId: null,
                        conditions: [
                          {
                            id: 'id-2b9d3d1e-c823-446d-a5ea-9fc7a13007a1',
                            level: 1,
                            value: ['Completed', 'Pending'],
                            column: 'item_sale_status',
                            operator: 'in',
                            parentId: 'id-6fb652df-f5d3-4480-a9e9-0efa413a7280'
                          }
                        ]
                      }
                    ]
                  }
                },
                {
                  data: {
                    name: 'view 3',
                    alias: 'view_3'
                  },
                  filter: {
                    type: 'AND',
                    conditions: [
                      {
                        value: "DATE_START_OF(DATE_LAST(30,'day'), 'day')",
                        column: 'sale_date',
                        operator: '$gte'
                      },
                      {
                        value: "DATE_END_OF(TODAY(), 'day')",
                        column: 'sale_date',
                        operator: '$lte'
                      },
                      {
                        value: 'amazon.com',
                        column: 'channel_name',
                        operator: '$eq'
                      },
                      {
                        id: 'id-174df815-cb53-4c55-b542-c1dacf938b28',
                        type: 'OR',
                        level: 0,
                        config: {
                          query: {},
                          ignore: {
                            base: {
                              value: false,
                              visible: true
                            },
                            global: {
                              value: false,
                              visible: false
                            }
                          }
                        },
                        enabled: true,
                        parentId: null,
                        conditions: [
                          {
                            id: 'id-d9724426-c66e-4bcb-9179-8a4f8c3aad15',
                            level: 1,
                            value: '50',
                            column: 'item_sale_charged',
                            operator: '$gt',
                            parentId: 'id-174df815-cb53-4c55-b542-c1dacf938b28'
                          },
                          {
                            id: 'id-936aa71b-f489-4cf6-8efb-dd5ae663a431',
                            level: 1,
                            value: ['Pending'],
                            column: 'item_sale_status',
                            operator: 'in',
                            parentId: 'id-174df815-cb53-4c55-b542-c1dacf938b28'
                          }
                        ]
                      }
                    ]
                  }
                },
                {
                  data: {
                    name: 'view 4',
                    alias: 'view_4'
                  },
                  filter: {
                    type: 'AND',
                    conditions: [
                      {
                        value: "DATE_START_OF(YESTERDAY(), 'day')",
                        column: 'sale_date',
                        operator: '$gte'
                      },
                      {
                        value: "DATE_END_OF(YESTERDAY(), 'day')",
                        column: 'sale_date',
                        operator: '$lte'
                      },
                      {
                        value: 'amazon.com',
                        column: 'channel_name',
                        operator: '$eq'
                      },
                      {
                        id: 'id-6fb652df-f5d3-4480-a9e9-0efa413a7280',
                        type: 'AND',
                        level: 0,
                        config: {
                          query: {},
                          ignore: {
                            base: {
                              value: false,
                              visible: true
                            },
                            global: {
                              value: false,
                              visible: false
                            }
                          }
                        },
                        enabled: true,
                        parentId: null,
                        conditions: [
                          {
                            id: 'id-2b9d3d1e-c823-446d-a5ea-9fc7a13007a1',
                            level: 1,
                            value: ['Completed', 'Pending'],
                            column: 'item_sale_status',
                            operator: 'in',
                            parentId: 'id-6fb652df-f5d3-4480-a9e9-0efa413a7280'
                          }
                        ]
                      }
                    ]
                  }
                }
              ],
              columns: [
                {
                  name: 'view_title',
                  displayName: 'View Title',
                  alias: 'view_title',
                  sortable: {
                    enabled: true
                  },
                  cell: {
                    width: 150,
                    computeClass: (value) => {},
                    format: {
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
                      type: 'string'
                    }
                  },
                  visible: true,
                  type: 'text'
                },
                {
                  name: 'item_sale_charged',
                  displayName: 'Sales Charged SUM',
                  alias: 'item_sale_charged_sum',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    computeClass: (value) => {},
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'cogs',
                  alias: 'cogs_sum',
                  displayName: 'COGS SUM',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    computeClass: (value) => {},
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'item_shipping_cost',
                  displayName: 'Shipping Cost SUM',
                  alias: 'item_shipping_cost_sum',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'refund_admin_fee',
                  displayName: 'RefundAdmin Fee SUM',
                  alias: 'refund_admin_fee_sum',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    computeClass: (value) => {},
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'item_profit',
                  displayName: 'Profit SUM',
                  alias: 'item_profit_sum',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'item_sale_charged',
                  alias: 'item_sale_charged_avg',
                  displayName: 'Sales Charged AVG',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    computeClass: (value) => {},
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'cogs',
                  displayName: 'COGS AVG',
                  alias: 'cogs_avg',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    computeClass: (value) => {},
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'item_shipping_cost',
                  displayName: 'Shipping Cost AVG',
                  alias: 'item_shipping_cost_avg',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'refund_admin_fee',
                  displayName: 'RefundAdmin Fee AVG',
                  alias: 'refund_admin_fee_avg',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    computeClass: (value) => {},
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'item_profit',
                  displayName: 'Profit AVG',
                  alias: 'item_profit_avg',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
                  visible: true,
                  type: 'float'
                },
                {
                  name: 'item_margin',
                  displayName: 'Margin',
                  alias: 'margin',
                  sortable: {
                    enabled: false
                  },
                  cell: {
                    width: 150,
                    format: {
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
                      type: 'numeric'
                    },
                    aggrFormats: {}
                  },
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
                      suffix: '%'
                    },
                    config: {
                      comma: true,
                      precision: 2,
                      siPrefix: false
                    },
                    expr: `(SUM (@item_profit) / SUM (@item_sale_charged) * 100)as 'item_margin'`
                  },
                  visible: true,
                  type: 'float'
                }
              ]
            }
          }
        ]
      }
    }
  },
  mixins: [configMixins, renderMixins],
  computed: {
    getTemplate() {
      return [
        {
          name: 'Comparable Table',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  methods: {
    async initSDK() {
      window.config = this.config
      this.render(
        '#comparable-table-demo',
        this.template,
        this.baseURL,
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiY2UwYmU1ODEtNDlkZi00Mjg4LThiNzItZTk2MWRkMzBhMTA1IiwidXNlcm5hbWUiOiJjYnBvX3FhQG1haWxpbmF0b3IuY29tIiwiZXhwIjoxNjU1MDE1MzY3LCJlbWFpbCI6ImNicG9fcWFAbWFpbGluYXRvci5jb20iLCJvcmlnX2lhdCI6MTY1NDg0MjU2NywiZm5hbWUiOiJDQlBPIiwibG5hbWUiOiJRQSIsImFwcCI6InByZWNpc2VfZmluYW5jaWFsIn0.PSWqg23A37gR6U4el5tLpnbVSy8JP0GwXyxlmPCMDanDTpdP0SNbHM1y8agI6Ic0MzRE02j_fV5D06mn8ZZbz6-Va_8bhGaTtS9warauQ4mFD85-OVmadulzDv48DVrsJlTzgpugtbuuaT1R7fv7WslRadIrAe_sd6Fggt1vkKbB55nj0-lfeK2J7zqXQap9x7FOQosnk4inh9yA-ZibHTPs_IA7j0nHC_ziUl732GDwtYJnc2EeA7DgIyPciHBWFiMtURI1jZ8HagQd9NRqni9Kkq5K82Ym9g76G68jyCeE2pdJe2hEn7xXJ1mpZc1SZPf_Hs6GexSbvNQMXFvJWw',
        '1dd0bded-e981-4d2f-9bef-2874016661e7'
      )
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
