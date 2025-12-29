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
import upperCase from 'lodash/upperCase'
import moment from 'moment-timezone'

export default {
  name: 'SaleByDivisionsData',
  props: {
    dataSource: {
      type: String,
      required: true
    }
  },
  data() {
    const timezone = 'America/Los_Angeles'
    const currentDatetime = moment.utc()
    return {
      timezone,
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
          {
            name: 'division',
            alias: 'division',
            cell: {},
            format: {
              type: 'text',
              config: {}
            }
          },
          {
            name: 'total_quantity',
            alias: 'total_quantity',
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
            name: 'mtd_target',
            alias: 'mtd_target',
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
            name: 'mtd_current',
            alias: 'mtd_current',
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
            name: 'mtd_max',
            alias: 'mtd_max',
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
            name: 'mtd_percent',
            alias: 'mtd_percent',
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
            name: 'ytd_current',
            alias: 'ytd_current',
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
            name: 'ytd_target',
            alias: 'ytd_target',
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
            name: 'ytd_max',
            alias: 'ytd_max',
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
            name: 'ytd_percent',
            alias: 'ytd_percent',
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
            name: 'modified',
            alias: 'modified',
            cell: {
              format: {
                type: 'date'
              }
            }
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
          fileName: 'sale-by-divisions'
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
      if (items && !items.length) return null
      let calculatedData = {
        lastUpdated: items[0].data && items[0].data.modified ? items[0].data.modified.base : null
      }
      for (const item in items) {
        if (items.hasOwnProperty(item)) {
          const division = items[item].data.division.base
          calculatedData[`format__UNITS_SOLD__${upperCase(division)}`] = items[item].data.total_quantity.base
          for (const key in items[item].data) {
            const [conditionDay, type] = key.split('_')
            if (Object.hasOwnProperty.call(items[item].data, key)) {
              const element = items[item].data[key]
              if (conditionDay === 'mtd' || conditionDay === 'ytd') {
                calculatedData[`radial__${upperCase(conditionDay)}__${upperCase(division)}__${upperCase(type)}`] = element.base
              }
              if (type === 'percent') {
                calculatedData[`format__PERCENTAGE__${upperCase(conditionDay)}__${upperCase(division)}`] = element.base
              }
            }
          }
        }
      }
      return calculatedData
    },
    convertToDataSourceAndEmit() {
      const dataTable = cloneDeep(this.$refs.table.dataTable)
      try {
        const dataSource = this.buildDataSource(dataTable)
        this.$emit('changed', dataSource)
      } catch {
        console.log('Datasource from widget Sale By Divisions is not valid.')
      }
    }
  }
}
</script>
