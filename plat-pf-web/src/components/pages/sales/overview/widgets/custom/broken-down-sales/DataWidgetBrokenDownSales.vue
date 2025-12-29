<template>
  <div class="d-none">
    <cbpo-element-table
      ref="table"
      :config-obj="config"
      @dataFetched="convertToDataSourceAndEmit"
    />
  </div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep'
import moment from 'moment-timezone'

export default {
  name: 'DataWidgetBrokenDown',
  props: {
    dataSource: {
      type: String,
      required: true
    }
  },
  data() {
    const today = {
      name: 'Today so far',
      alias: 'today',
      compareName: 'total_day',
      compareFormat: null
    }
    const yesterday = {
      name: 'Yesterday',
      alias: 'yesterday',
      compareName: 'percent_vs_yesterday',
      compareFormat: {
        style: 'percent'
      }
    }
    const sameDayLastWeek = {
      name: 'Same day last week',
      alias: 'same_day_last_week',
      compareName: 'percent_vs_last_week',
      compareFormat: {
        style: 'percent'
      }
    }
    const sameDayLastYear = {
      name: 'Same day last year',
      alias: 'same_day_last_year',
      compareName: 'percent_vs_last_year',
      compareFormat: {
        style: 'percent'
      }
    }
    const title = {
      name: 'division',
      alias: 'division',
      cell: {}
    }
    const timezone = 'America/Los_Angeles'
    const currentDatetime = moment.utc()
    return {
      timezone,
      today,
      yesterday,
      sameDayLastWeek,
      sameDayLastYear,
      title,
      currentDatetime,
      config: {
        dataSource: this.dataSource,
        widget: {
          title: {
            enabled: false
          }
        },
        header: {
          resizeMinWidth: null,
          multiline: false,
          draggable: false
        },
        columns: [
          title,
          {
            name: 'total_day',
            alias: 'total_day',
            displayName: 'Today so far',
            cell: {},
            format: {
              type: 'numeric',
              config: {
                precision: 0,
                comma: false
              }
            }
          },
          {
            name: 'total_yesterday',
            alias: 'total_yesterday',
            displayName: 'Yesterday',
            cell: {
              format: {
                type: 'numeric',
                config: {
                  precision: 0,
                  comma: false
                }
              }
            }
          },
          {
            name: 'total_same_day_last_week',
            alias: 'total_same_day_last_week',
            displayName: 'Same day last week',
            cell: {
              format: {
                type: 'numeric',
                config: {
                  precision: 0,
                  comma: false
                }
              }
            }
          },
          {
            name: 'total_same_day_last_year',
            alias: 'total_same_day_last_year',
            displayName: 'Same day last year',
            cell: {
              format: {
                type: 'numeric',
                config: {
                  precision: 2,
                  comma: false
                }
              }
            }
          },
          {
            name: 'percent_vs_yesterday',
            alias: 'percent_vs_yesterday',
            displayName: '% Change from yesterday',
            cell: {
              format: {
                type: 'numeric',
                config: {
                  precision: 2,
                  comma: false
                },
                common: {
                  suffix: '%'
                }
              }
            }
          },
          {
            name: 'percent_vs_last_week',
            alias: 'percent_vs_last_week',
            displayName: '% Change from last week',
            cell: {
              format: {
                type: 'numeric',
                config: {
                  precision: 2,
                  comma: false
                },
                common: {
                  suffix: '%'
                }
              }
            }
          },
          {
            name: 'percent_vs_last_year',
            alias: 'percent_vs_last_year',
            displayName: '% Change from last year',
            cell: {
              format: {
                type: 'numeric',
                config: {
                  precision: 2,
                  comma: false
                },
                common: {
                  suffix: '%'
                }
              }
            }
          },
          {
            name: 'modified',
            alias: 'modified',
            type: 'date'
          }
        ],
        pagination: {
          limit: 1000,
          current: 0
        },
        timezone: {
          enable: true,
          utc: timezone
        },
        exportConfig: {
          fileName: 'broken-down-sales'
        }
      }
    }
  },
  methods: {
    getSubtractDate(momentDate, timezone, amount, isStartDate, unit = 'd') {
      const date = momentDate.clone().tz(timezone).subtract(amount, unit)
      return isStartDate
        ? date.startOf('d').toISOString()
        : date.toISOString()
    },
    formatValue(value, formatConfig = {}) {
      return Number(value || 0).toLocaleString('en', {
        ...formatConfig,
        minimumFractionDigits: 2
      })
    },
    buildDataSource({items, columns}) {
      let colsData = [
        {
          'name': 'division',
          'alias': 'view_title',
          'type': 'string',
          'displayName': ' '
        },
        {
          'name': 'Unit-Sales',
          'alias': 'item_unit_sales_sum',
          'type': 'string',
          'displayName': 'Units Sales'
        },
        {
          'name': 'Sale-Charged',
          'alias': 'item_sale_charged_sum',
          'type': 'string',
          'displayName': 'Sales Charged'
        },
        {
          'name': 'Profit',
          'alias': 'item_profit_sum',
          'type': 'string',
          'displayName': 'Profit'
        },
        {
          'name': 'Margin',
          'alias': 'margin',
          'type': 'string',
          'displayName': 'Margin'
        }
      ]
      let viewsTitle = []
      let calculatedData = []

      viewsTitle = Object.keys(items[0].data).slice(1)

      calculatedData = viewsTitle.map(item => [item])

      items.forEach(item => {
        Object.entries(item.data).forEach(([key, value]) => {
          const row = calculatedData.find(row => row[0] === key)
          if (row) {
            row.push(value.format)
          }
        })
      })
      calculatedData = calculatedData.map(row => {
        for (const col of this.config.columns) {
          if (row[0] === col.name) {
            row.push(col.displayName)
          }
        }
        return row
      })
      return {
        cols: colsData,
        rows: calculatedData.filter(row => !row.includes('modified'))
      }
    },
    convertToDataSourceAndEmit() {
      const dataTable = cloneDeep(this.$refs.table.dataTable)
      try {
        const dataSource = this.buildDataSource(
          dataTable,
          this.today,
          [this.yesterday, this.sameDayLastWeek, this.sameDayLastYear]
        )
        const firstItem = dataTable.items && dataTable.items[0]
        const lastUpdated = firstItem && firstItem.data && firstItem.data.modified
          ? firstItem.data.modified.base
          : null

        this.$emit('changed', { dataSource, lastUpdated })
      } catch (e) {
        console.log('Datasource from widget Broken Down Sales is not valid.', e)
      }
    }
  }
}
</script>
