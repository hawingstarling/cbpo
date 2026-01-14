const sdkPerformanceWidget = Vue.component('sdkPerformanceWidget', {
  template: `
    <div class='1k-row-demo'>
      <h5>Example: </h5>
      <div style="height: 400px" id='performance-table-demo'>
      </div>
      <div class='mt-2'>
        <sdk-export-code :templates='getTemplate'/>
      </div>
    </div>
  `,
  mixins: [configMixins, renderMixins],
  data() {
    return {
      template: '<cbpo-widget class="p-0" config-ref="config"></cbpo-widget>',
      config: {
        autoHeight: true,
        widget: {
          title: {
            text: `1k Row Table With Lazy Loading`,
            enabled: false
          }
        },
        columnManager: {
          enabled: true
        },
        filter: {
          builder: {
            enabled: true
          }
        },
        elements: [
          {
            type: 'cbpo-element-table',
            config: {
              header: {
                multiline: true
              },
              dataSource: 'dataSource',
              columns: [
                {
                  name: 'seller_name',
                  displayName: 'Seller Name',
                  cell: {
                    format: {
                      type: 'text'
                    }
                  }
                },
                {
                  name: 'sku',
                  cell: {
                    format: {
                      type: 'text'
                    }
                  }
                },
                {
                  name: 'upc/ean',
                  cell: {
                    format: {
                      type: 'text'
                    }
                  }
                },
                {
                  name: 'asin',
                  cell: {
                    format: {
                      type: 'text'
                    }
                  }
                },
                {
                  name: 'seller_price',
                  cell: {
                    format: {
                      type: 'text',
                      common: {
                        prefix: '$'
                      }
                    }
                  }
                },
                {
                  name: 'map_price',
                  cell: {
                    format: {
                      type: 'text',
                      common: {
                        prefix: '$'
                      }
                    },
                    formatTooltip: {
                      type: 'custom',
                      config: {
                        condition: function(cellValue, rowValue) {
                          return {
                            type: 'override',
                            config: {
                              format: {
                                text: `UTWH - ${rowValue.map_price.base} \r\nUTWH - ${rowValue.seller_price.base}`
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                },
                {
                  name: 'diff',
                  cell: {
                    format: {
                      type: 'currency'
                    }
                  }
                },
                {
                  name: 'diff_percent',
                  cell: {
                    format: {
                      type: 'text',
                      common: {
                        suffix: ' %'
                      }
                    }
                  }
                },
                {
                  name: 'captured_at',
                  cell: {
                    format: {
                      type: 'temporal'
                    }
                  }
                },
                {
                  name: 'prime',
                  cell: {
                    format: {
                      type: 'bool',
                      positive: {
                        text: 'Yes', // default Yes
                        html: '<span class="d-bool-p">Yes</span>'
                      },
                      negative: {
                        text: 'No', // default No
                        html: '<span class="d-bool-n">No</span>'
                      }
                    }
                  }
                }
              ],
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
              rowActions: {
                enabled: true,
                inline: 1, // number of inline item, max inline items are 2, else -> dropdown
                display: 'always', // always | onhover
                position: 'left',
                colWidth: 150,
                controls: [
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: { padding: '0px 5px' },
                    icon: 'fa-gear',
                    label: 'Edit',
                    event: function (dataRow) { console.log('action 1', dataRow) }
                  },
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-home',
                    label: 'Action 2',
                    event: function (dataRow) { console.log('action 2', dataRow) }
                  },
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-home',
                    label: 'Action 3',
                    event: function (dataRow) { console.log('action 3', dataRow) }
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
                    event: function (dataRow) { console.log('bulk action 1', dataRow) }
                  },
                  {
                    display: true,
                    props: { size: 'sm', variant: 'primary' },
                    style: {},
                    icon: 'fa-home',
                    label: 'Action 3',
                    event: function (dataRow) { console.log('bulk action 3', dataRow) }
                  }
                ]
              },
              pagination: {
                type: 'lazy',
                limit: 10
              }
            }
          }
        ]
      }
    }
  },
  computed: {
    getTemplate() {
      return [
        {
          name: '1k Row Table Demo',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  methods: {
    async fetchDataSource() {
      try {
        window.dataSource = await $.getJSON('live-docs/assets/json/10kRowDataSource.json')
      } catch (e) {
        console.log(e)
      }
    },
    initSDK() {
      window.config = this.config
      this.render('#performance-table-demo', this.template, '', '', '')
    }
  },
  async mounted() {
    await this.fetchDataSource()
    this.initSDK()
  }
})
