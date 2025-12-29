import moment from 'moment'

export let convertYToCurrentYear = (allConfigs) => {
  let thisYear = new Date().getFullYear()
  for (let config in allConfigs) {
    if (allConfigs[config].config && allConfigs[config].config.elements && allConfigs[config].config.elements[0].config && allConfigs[config].config.elements[0].config.charts) {
      allConfigs[config].config.elements[0].config.charts[0].series.forEach(serie => {
        if (serie.data.x.startsWith('y') || serie.data.y.startsWith('y')) {
          serie.name = thisYear - serie.name.slice(1)
          serie.name.toString()
        }
      })
      allConfigs[config].config.elements[0].config.charts[0].series = allConfigs[config].config.elements[0].config.charts[0].series.filter(serie => serie.name !== 2018 && serie.name !== 2019)
    }
    if (allConfigs[config].config && allConfigs[config].config.elements && allConfigs[config].config.elements[0].config && allConfigs[config].config.elements[0].config.columns) {
      allConfigs[config].config.elements[0].config.columns.forEach(column => {
        if (column.displayName.startsWith('d')) {
          const showDay = column.displayName.endsWith('_day')
          const dayNumber = parseInt(showDay
            ? column.displayName.replace('_day', '').slice(1)
            : column.displayName.slice(1))
          if (Number.isNaN(dayNumber)) return

          const day = moment(moment().subtract(dayNumber + 1, 'days'))
          column.displayName = showDay
            ? `${day.format('MM/DD')} (${day.format('ddd')})`
            : day.format('MM/DD')
        }
        if (column.displayName.startsWith('m')) {
          column.displayName = moment(moment().subtract(column.displayName.slice(1), 'months')).format('MMM')
        }
      })
    }
  }
}
let columnFormatWidget = (currentCol, compareCol) => {
  return {
    type: 'custom',
    config: {
      condition(cellValue, rowValue) {
        let d0 = rowValue[currentCol]
        let d1 = rowValue[compareCol]
        const baseValue = d0.base < d1.base
          ? cellValue + 1
          : cellValue - 1
        return {
          type: 'segments',
          config: {
            segmentType: 'custom',
            segments: [
              {
                conditions: { gt: baseValue },
                iconClass: 'custom-arrow-up', // css class
                iconStyle: {}, // css styles
                labelCss: '', // css class
                labelStyle: {} // css styles
              },
              {
                conditions: { lt: baseValue },
                iconClass: 'custom-arrow-down', // css class
                iconStyle: {}, // css styles
                labelCss: '', // css class
                labelStyle: {} // css styles
              },
              {
                conditions: { eq: baseValue },
                iconClass: 'fa fa-minus', // css class
                iconStyle: { color: 'grey' }, // css styles
                labelCss: '', // css class
                labelStyle: {} // css styles
              }
            ]
          }
        }
      }
    }
  }
}
export let compareTwoColInWidget = (widget) => {
  widget.config.elements[0].config.columns.forEach(column => {
    switch (column.name) {
      case 'd0':
        column.cell.format = columnFormatWidget('d0', 'd1')
        break
      case 'd1':
        column.cell.format = columnFormatWidget('d1', 'd2')
        break
      case 'd2':
        column.cell.format = columnFormatWidget('d2', 'd3')
        break
      case 'd3':
        column.cell.format = columnFormatWidget('d3', 'd4')
        break
      case 'd4':
        column.cell.format = columnFormatWidget('d4', 'd5')
        break
      case 'd5':
        column.cell.format = columnFormatWidget('d5', 'd6')
        break
      case 'd6':
        column.cell.format = columnFormatWidget('d6', 'd7')
        break
      case 'd7':
        column.cell.format = columnFormatWidget('d7', 'd8')
        break
      case 'd8':
        column.cell.format = columnFormatWidget('d8', 'd9')
        break
      case 'd9':
        column.cell.format = columnFormatWidget('d9', 'd10')
        break
      case 'sale_total_30d':
        column.cell.format = columnFormatWidget('sale_total_30d', 'sale_total_30d_prior')
        break
      case 'sale_avg_30d':
        column.cell.format = columnFormatWidget('sale_avg_30d', 'sale_avg_30d_prior')
        break
      case 'm0':
        column.cell.format = columnFormatWidget('m0', 'm1')
        break
      case 'm1':
        column.cell.format = columnFormatWidget('m1', 'm2')
        break
      case 'm2':
        column.cell.format = columnFormatWidget('m2', 'm3')
        break
    }
  })
}

let maxValueProgressBar = (maxCol) => {
  return {
    fallbackType: 'progress',
    condition(cellValue, rowValue) {
      let maxConfigProgress = rowValue[maxCol]
      return {
        type: 'progress',
        config: {
          visualization: 'bar_with_conditions',
          base: maxConfigProgress.base,
          conditions: [
            { max: 25, color: '#FF9A9A' },
            { max: 50, color: '#05A0D1' },
            { max: 75, color: '#52C0E1' },
            { max: 100, color: '#91E4AB' }
          ]
        }
      }
    }
  }
}

export let configMaxProgressBar = (maxColFromDS, processCols, widgetConfig) => {
  maxColFromDS.forEach(maxCol => {
    widgetConfig.config.elements[0].config.columns.forEach(column => {
      if (processCols.indexOf(column.name) >= 0) {
        column.cell.format.config = maxValueProgressBar(maxCol)
      }
    })
  })
}
