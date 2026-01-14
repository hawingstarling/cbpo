import ChartjsLib from '@/components/widgets/elements/chart/libs/ChartjsLib.js'

const $ = require('jquery')
describe('ChartjsLib.js', () => {
  it('test method updateChart', () => {
    let lib = new ChartjsLib()
    lib.updateChart('abc', 1)
  })
  xit('check method buildTemplatePieLegend', () => {
    let lib = new ChartjsLib()
    let chart = {
      id: 1,
      data: {
        labels: ['abc', 'cde'],
        datasets: [{
          backgroundColor: ['#fff', '#eee'],
          _meta: {
            0: {
              data: [
                { hidden: false },
                { hidden: false }
              ]
            }
          }
        }]
      }
    }
    expect(lib.buildTemplatePieLegend(chart).trim()).toEqual(`<ul class="1-legend"><li title="abc"><span class="circle" style="background-color: #fff"></span><div class="text">abc</div></li><li title="cde"><span class="circle" style="background-color: #eee"></span><div class="text">cde</div></li></ul>`.trim())
  })
  it('check method formatPieTooltip', () => {
    let lib = new ChartjsLib()
    let dataChart = {
      x: 'column1',
      y: 'column2'
    }
    let columnFormat = {}
    expect(lib.formatPieTooltip(dataChart, columnFormat)).toMatchObject({
      borderWidth: 1,
      mode: 'nearest',
      position: 'nearest',
      titleFontStyle: 'normal',
      titleSpacing: 10,
      bodyFontSize: 12,
      bodySpacing: 10,
      cornerRadius: 3
    })
  })
  it('check method formatBarTooltip', () => {
    let lib = new ChartjsLib()
    let dataChart = {
      x: 'column1',
      y: 'column2'
    }
    let columnFormat = {}
    expect(lib.formatBarTooltip(dataChart, columnFormat)).toMatchObject({
      borderWidth: 1,
      mode: 'index',
      intersect: true,
      position: 'nearest',
      titleFontStyle: 'normal',
      titleSpacing: 10,
      bodyFontSize: 12,
      bodySpacing: 10,
      cornerRadius: 3
    })
  })
  xit('check method drawChart', () => {
    let lib = new ChartjsLib()
    document.body.innerHTML = '<div class="chart-container"><div class="chartSets"></div></div>'
    let el = document.querySelector('.chart-container')
    let id = 'abc'
    let indexObject = {
      chart: 0,
      series: 0
    }
    let config = {
      type: 'pie',
      data: {
        datasets: [{
          data: [
            50, 50
          ],
          backgroundColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)'
          ],
          label: 'Dataset 1'
        }],
        labels: [
          'A', 'B'
        ]
      },
      options: {
        responsive: true
      }
    }
    expect(lib.drawChart(el, id, indexObject, config))
  })
  it('check method render case 1', () => {
    let lib = new ChartjsLib()
    document.body.innerHTML = '<div class="chart-container"><div class="chartSets"></div></div>'
    let el = document.querySelector('.chart-container')
    let componentConfig = {
      id: 'abc',
      columns: {},
      charts: [
        {
          axis: {
            x: [],
            y: []
          },
          options: {
            title: {
              display: true,
              text: 'Demo Pie Chart'
            },
            column: {
              stacking: 'normal' // normal | percentage
            }
          },
          series: [
            {
              type: 'pie',
              label: 'DataSet 1',
              data: {
                x: 'column1',
                y: 'column2'
              }
            }
          ]
        }
      ]
    }
    let data = {
      cols: [{
        name: 'column1',
        type: 'int' // int, num, date, datetime, string, boolean
      }, {
        name: 'column2',
        type: 'string' // int, num, date, datetime, string, boolean
      }],
      rows: [
        ['a', 2],
        ['b', 4]
      ]
    }
    expect(lib.render(el, componentConfig, data))
  })
  xit('check method render case 2', () => {
    let lib = new ChartjsLib()
    document.body.innerHTML = '<div class="chart-container"><div class="chartSets"></div></div>'
    let el = document.querySelector('.chart-container')
    let componentConfig = {
      id: 'abc',
      columns: {},
      charts: [
        {
          axis: {
            x: [],
            y: []
          },
          options: {
            title: {
              display: true,
              text: 'Demo Pie Chart'
            },
            column: {
              stacking: 'normal' // normal | percentage
            }
          },
          series: [
            {
              type: 'fake',
              label: 'DataSet 1',
              data: {
                x: 'column1',
                y: 'column2'
              }
            }
          ]
        }
      ]
    }
    let data = {
      cols: [{
        name: 'column1',
        type: 'int' // int, num, date, datetime, string, boolean
      }, {
        name: 'column2',
        type: 'string' // int, num, date, datetime, string, boolean
      }],
      rows: [
        ['a', 2],
        ['b', 4]
      ]
    }
    expect(lib.render(el, componentConfig, data))
  })
  it('check method render case 3', () => {
    let lib = new ChartjsLib()
    document.body.innerHTML = '<div class="chart-container"><div class="chartSets"></div></div>'
    let el = document.querySelector('.chart-container')
    let componentConfig = {
      id: 'abc',
      columns: {},
      charts: [
        {
          axis: {
            x: [],
            y: []
          },
          options: {
            title: {
              display: true,
              text: 'Demo Pie Chart'
            },
            column: {
              stacking: 'normal' // normal | percentage
            }
          },
          series: [
            {
              type: 'bar',
              label: 'DataSet 1',
              data: {
                x: 'column1',
                y: 'column2'
              }
            }
          ]
        }
      ]
    }
    let data = {
      cols: [{
        name: 'column1',
        type: 'int' // int, num, date, datetime, string, boolean
      }, {
        name: 'column2',
        type: 'string' // int, num, date, datetime, string, boolean
      }],
      rows: [
        ['a', 2],
        ['b', 4]
      ]
    }
    expect(lib.render(el, componentConfig, data))
  })
  xit('check method mappingAxis', () => {
    let lib = new ChartjsLib()
    let chart = {
      axis: {
        x: [
          {
            id: 'ab',
            position: 'bottom',
            display: true,
            type: 'linear',
            ticks: {},
            scaleLabel: {},
            stacked: false
          }
        ],
        y: [
          {
            type: 'linear',
            id: 'y0',
            display: true,
            position: 'right',
            stacked: true,
            scaleLabel: {
              display: true,
              labelString: 'Value'
            },
            ticks: {
              beginAtZero: true
            }
          }
        ]
      }
    }
    expect(lib.mappingAxis(chart)).toMatchObject({
      'xAxes': [
        {
          'id': 'ab',
          'position': 'bottom',
          'display': true,
          'type': 'linear',
          'ticks': {},
          'scaleLabel': {},
          'stacked': false
        }
      ],
      'yAxes': [
        {
          'display': true,
          'id': 'y0',
          'position': 'right',
          'scaleLabel': {
            'display': true,
            'labelString': 'Value'
          },
          'stacked': false,
          'ticks': {
            'beginAtZero': true,
            'maxTicksLimit': 5
          },
          'type': 'linear'
        }
      ]
    })
  })
})
