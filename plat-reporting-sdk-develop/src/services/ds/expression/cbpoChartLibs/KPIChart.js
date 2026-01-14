import get from 'lodash/get'
import isEmpty from 'lodash/isEmpty'
import isFunction from 'lodash/isFunction'
import orderBy from 'lodash/orderBy'
import pick from 'lodash/pick'
import defaultsDeep from 'lodash/defaultsDeep'
import * as d3 from 'd3'

function CbpoKPIChartError(message) {
  this.message = message
  this.name = 'CbpoKPIChart'
}

CbpoKPIChartError.prototype = Error.prototype

const arrowUpPath = (size) => {
  let sqrt3 = Math.sqrt(3)
  let y = -Math.sqrt(size / (sqrt3 * 3))
  return `M 0,${y * 2} ${-sqrt3 * y}, ${-y} ${sqrt3 * y},${-y} z`
}

const getTextSize = (selection, text, type = 'width') => {
  let els = selection.selectAll('text.cal-width-unique').data([0])
  let newEl = els.enter().append('text')
    .attr('class', 'cal-width-unique')
    .attr('visibility', 'hidden')
  newEl.merge(els).text(text)
  return type === 'width'
    ? newEl.merge(els).node().getBoundingClientRect().width
    : newEl.merge(els).node().getBoundingClientRect().height
}

const formatText = (d, config) => {
  if (!config.options.labels.formatter || !isFunction(config.options.labels.formatter)) return d.label
  return config.options.labels.formatter.bind({ ...d })()
}

class CbpoKPIChart {
  config = null

  constructor() {
    this.config = {
      size: {
        width: 500,
        height: 140
      },
      margin: {
        top: 15,
        left: 15,
        right: 15,
        bottom: 5
      },
      options: {
        labels: {
          formatter: null
        },
        needle: {
          fillColor: '#000000'
        },
        background: '#ffffff',
        bar: {
          height: 30,
          labelHeight: 16
        },
        sum: {},
        legend: {
          enabled: true,
          height: 40,
          color: '#000000'
        },
        dialRadiusOffset: 0
      },
      max: {
        enabled: false,
        value: null,
        label: 'Target',
        fillColor: '#6c757d'
      },
      percentage: {
        enabled: false,
        fillColor: 'green',
        value: null,
        reversed: false
      },
      series: []
    }
  }

  // type radial
  renderRadialKPI(node, config) {
    // check Series
    if (isEmpty(get(config, 'series', []))) {
      throw new CbpoKPIChartError('Chart must have at least 1 series')
    }

    // default config
    defaultsDeep(config, this.config)

    // create max value and add into series
    if (config.max.enabled) {
      config.series = [...config.series, pick(config.max, ['label', 'value', 'fillColor', 'markerWidth', 'opacity'])]
    }

    // define scale
    let PI = Math.PI
    let RADIUS_THICK = 50
    let RADIUS_LABEL_DISTANCE = 20
    let chartWidth = config.size.width - config.margin.left - config.margin.right
    let dialCenterX = chartWidth / 2
    let dialCenterY = config.size.height * 0.55
    let dialRadiusY = dialCenterY - config.options.bar.labelHeight - RADIUS_LABEL_DISTANCE * 2
    let dialRadiusX = dialCenterX - RADIUS_LABEL_DISTANCE
    let dialRadius = d3.min([dialRadiusX, dialRadiusY])
    let dialInnerRadius = dialRadius - RADIUS_THICK
    let dialMinAngle = -125
    let dialMaxAngle = 125
    let series = orderBy(config.series, 'value', 'desc')
    let max = d3.max(config.series, d => d.value)
    let dialRadiusOffset = config.options.dialRadiusOffset

    let scale = d3.scaleLinear()
      .domain([0, max])
      .range([dialMinAngle, dialMaxAngle])

    let dialPath = d3.arc()
      .innerRadius(dialInnerRadius)
      .outerRadius((d, i) => {
        return dialRadius - i * dialRadiusOffset
      })
      .startAngle(dialMinAngle * PI / 180)
      .endAngle(function(serie, i) {
        return scale(serie.value) * (PI / 180)
      })

    let needlePath = d3.arc()
      .innerRadius(dialInnerRadius)
      .outerRadius(0)
      .startAngle(d => scale(d.value) * (PI / 180) - PI / 180)
      .endAngle(d => scale(d.value) * (PI / 180))

    let makerPath = d3.arc()
      .innerRadius(dialInnerRadius - 3)
      .outerRadius(dialRadius + 3)
      .startAngle(d => scale(d.value) * (PI / 180) - PI / 180)
      .endAngle(d => scale(d.value) * (PI / 180))

    let el = d3.select(node)
    let svg = el.selectAll('svg').data([0])
    let newSvg = svg.enter().append('svg')
    // eslint-disable-next-line no-unused-vars
    let backgroundSvg = newSvg.append('rect').attr('class', 'g-bg')
    svg = svg.merge(newSvg)
    svg.select('rect.g-bg')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', config.size.width)
      .attr('height', config.size.height)
      .attr('fill', config.options.background)
    let newWrapper = newSvg.append('g').attr('class', 'kpi-wrapper')
    newWrapper.append('g').attr('class', 'kpi-legend-wrapper')
    newWrapper.append('g').attr('class', 'kpi-dial-wrapper')
    newWrapper.append('g').attr('class', 'kpi-sum-wrapper')
    svg = svg.merge(newSvg) // must
      .attr('width', config.size.width)
      .attr('height', config.size.height)

    svg.select('.kpi-wrapper')
      .attr('transform', 'translate(' + config.margin.left + ', ' + config.margin.top + ')')

    // draws slices
    let slices = svg.select('.kpi-dial-wrapper')
      .attr('transform', 'translate(' + dialCenterX + ', ' + dialCenterY + ')')
      .selectAll('.kpi-dial').data(series)
    slices.exit().remove()

    let newSlices = slices.enter().append('g').attr('class', 'kpi-dial')
    newSlices.append('path').attr('class', 'dial')
    newSlices.append('path').attr('class', 'marker')
      .attr('stroke-width', d => d.markerWidth || config.options.marker.width)
      .attr('stroke', config.options.needle.fillColor)
      .attr('fill', config.options.needle.fillColor)
      .attr('height', config.options.bar.height + 8)
    newSlices.append('path').attr('class', 'needle')
      .attr('width', config.options.needle.width)
      .attr('stroke-width', config.options.needle.width)
      .attr('stroke', config.options.needle.fillColor)
      .attr('fill', config.options.needle.fillColor)
      .attr('height', config.options.bar.height + 8)
    newSlices.append('text').attr('class', 'label')
    slices.merge(newSlices)
      .attr('class', d => 'kpi-dial ' + d.type)
      .select('path.dial')
      .attr('d', dialPath)
      .attr('fill', d => d.fillColor)
      .attr('fill-opacity', d => {
        return d.opacity
      })
      .attr('width', d => scale(d.value))
      .attr('height', config.options.bar.height)

    slices.merge(newSlices)
      .select('path.marker')
      .attr('d', makerPath)

    slices.merge(newSlices)
      .select('path.needle')
      .attr('d', needlePath)
      .attr('visibility', d => d.needle ? 'visible' : 'hidden')

    let legendWrapper = svg.select('.kpi-legend-wrapper')
    let labelDistance = RADIUS_LABEL_DISTANCE + dialRadius
    slices.merge(newSlices)
      .select('text.label')
      .text(d => formatText(d, config))
      .attr('dx', d => {
        let distance = Math.sin(scale(d.value) * PI / 180) * labelDistance
        let textWidth = getTextSize(legendWrapper, formatText(d, config)) / 2.5
        return distance > 0 ? distance + textWidth : distance - textWidth
      })
      .attr('dy', d => {
        let distance = -Math.cos(scale(d.value) * PI / 180) * labelDistance
        let textHeight = getTextSize(legendWrapper, formatText(d, config), 'height') / 2
        return distance > 0 ? distance - textHeight : distance + textHeight
      })
      .attr('fill', d => d.fillColor)
      .attr('text-anchor', 'middle')

    // draws center circle
    let centers = svg.select('.kpi-dial-wrapper').selectAll('circle.center').data([0])
    let newCenters = centers.enter().append('circle').attr('class', 'center')
    centers
      .merge(newCenters)
      .attr('x', dialCenterX)
      .attr('dy', dialCenterY)
      .attr('r', 5)
      .attr('fill', config.options.needle.fillColor)

    // draws legend
    series.map((d, i) => {
      d._legendTextWidth = getTextSize(legendWrapper, d.label)
    })
    let legs = svg.select('.kpi-legend-wrapper')
      .attr('transform', 'translate(' + 0 + ', ' + (0) + ')')
      .selectAll('.kpi-legend').data(config.options.legend.enabled ? series : [])
    legs.exit().remove()
    let newLegs = legs.enter().append('g').attr('class', 'kpi-legend')
    let RECT_WIDTH = 10
    let RECT_TO_TEXT_DISTANCE = 5
    let LEGEND_DISTANCE = 20
    newLegs.append('rect')
      .attr('width', RECT_WIDTH)
      .attr('height', 10)
      .attr('stroke', 'gray')
    newLegs.append('text')
      .attr('dx', RECT_WIDTH + RECT_TO_TEXT_DISTANCE)
      .attr('dy', 10)

    let mergedLegs = legs.merge(newLegs)

    function getDx(d, n) {
      let previousWidth = 0
      for (let i = 0; i < n; i++) {
        previousWidth += series[i]._legendTextWidth
      }
      return n * (RECT_WIDTH + RECT_TO_TEXT_DISTANCE + LEGEND_DISTANCE) + previousWidth
    }

    mergedLegs.attr('transform', (d, i) => {
      return `translate(${getDx(d, i)}, 0)`
    })
    mergedLegs.select('rect').attr('fill', d => d.fillColor)
    mergedLegs.select('text').text(d => d.label).attr('fill', config.options.legend.color)

    // draws SUM
    let sumWrapper = svg.select('.kpi-sum-wrapper')
    let sums = sumWrapper.selectAll('g.sum').data(config.percentage.enabled ? [0] : [])
    let newSums = sums.enter().append('g').attr('class', 'sum')
    let arrowTransform = config.percentage.reversed ? 'translate(0 2.5) rotate(180)' : 'translate(2 5.5)'
    newSums.append('path').attr('class', 'arrow')
      .attr('d', arrowUpPath(70))
      .attr('fill', 'red')
    newSums.append('text').attr('class', 'label')
      .attr('dx', 15)
      .attr('dy', 5)
      .attr('fill', 'red')
    sums.merge(newSums).select('path')
      .attr('fill', config.percentage.fillColor)
      .attr('transform', arrowTransform)
    sums.merge(newSums).select('text')
      .attr('fill', config.percentage.fillColor)
      .text(config.percentage.value + '%')
    let sumNode = sums.merge(newSums).node()
    sumWrapper.attr('transform', `translate(${chartWidth - (sumNode ? sumNode.getBoundingClientRect().width : 0)}, 0)`)
  }

  // type bar
  renderBarKPI(node, config) {
    if (isEmpty(get(config, 'series', []))) {
      throw new CbpoKPIChartError('Chart must have at least 1 series')
    }

    // default config
    defaultsDeep(config, this.config)

    // create max value and add into series
    if (config.max.enabled) {
      config.series = [...config.series, pick(config.max, ['label', 'value', 'fillColor', 'opacity'])]
    }

    // define scale
    let chartWidth = config.size.width - config.margin.left - config.margin.right

    let series = orderBy(config.series, 'value', 'desc')
    let max = d3.max(config.series, d => d.value)
    let scale = d3.scaleLinear()
      .domain([0, max])
      .range([0, chartWidth])

    let el = d3.select(node)
    let svg = el.selectAll('svg').data([0])
    let newSvg = svg.enter().append('svg')

    // eslint-disable-next-line no-unused-lets, no-unused-vars
    let backgroundSvg = newSvg.append('rect').attr('class', 'g-bg')
    let newWrapper = newSvg.append('g').attr('class', 'kpi-wrapper')
    newWrapper.append('g').attr('class', 'kpi-legend-wrapper')
    newWrapper.append('g').attr('class', 'kpi-bar-wrapper')
    newWrapper.append('g').attr('class', 'kpi-sum-wrapper')
    svg = svg.merge(newSvg) // must
      .attr('width', config.size.width)
      .attr('height', config.size.height)

    svg.select('rect.g-bg')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', config.size.width)
      .attr('height', config.size.height)
      .attr('fill', config.options.background)
    svg.select('.kpi-wrapper')
      .attr('transform', 'translate(' + config.margin.left + ', ' + config.margin.top + ')')

    // draws bars
    let bars = svg.select('.kpi-bar-wrapper')
      .attr('transform', 'translate(' + 0 + ', ' + (config.options.legend.height + config.options.bar.labelHeight) + ')')
      .selectAll('.kpi-bar').data(series)
    bars.exit().remove()
    let newBars = bars.enter().append('g').attr('class', 'kpi-bar')
    let textWrapper = svg.select('.kpi-legend-wrapper')

    // draws makers
    newBars.append('rect')
      .attr('class', 'bar')

    newBars.append('rect')
      .attr('class', 'marker')
      .attr('width', config.options.marker.width)
      .attr('height', config.options.bar.height + 8)
      .attr('fill', config.options.needle.fillColor)

    newBars.append('text')
      .attr('class', 'label')

    bars.merge(newBars)
      .select('rect.bar')
      .attr('fill', d => d.fillColor)
      .attr('fill-opacity', d => d.opacity)
      .attr('width', d => scale(d.value))
      .attr('height', config.options.bar.height)

    bars.merge(newBars)
      .select('rect.marker')
      .attr('transform', d => `translate(${scale(d.value)},${-4})`)

    bars.merge(newBars)
      .select('text.label')
      .text(d => formatText(d, config))
      .attr('dx', d => {
        let size = getTextSize(textWrapper, formatText(d, config))
        let scaleSize = scale(d.value)
        if (size + scaleSize + 10 > config.size.width) {
          return scaleSize - size / 2
        } else if (scaleSize - size - 10 < 0) {
          let diffSize = scaleSize - size
          return scaleSize - diffSize * 0.5
        }
        return scaleSize
      })
      .attr('dy', (d, i) => {
        return i % 2 === 0 ? (config.options.bar.height + config.options.bar.labelHeight + 10) : -10
      })
      .attr('text-anchor', 'middle')
      .attr('fill', d => d.fillColor)

    // draws legend
    series.map((d, i) => {
      d._legendTextWidth = getTextSize(textWrapper, d.label)
    })
    let legs = svg.select('.kpi-legend-wrapper')
      .attr('transform', 'translate(' + 0 + ', ' + (0) + ')')
      .selectAll('.kpi-legend').data(series)
    legs.exit().remove()
    let newLegs = legs.enter().append('g').attr('class', 'kpi-legend')
    let RECT_WIDTH = 10
    let RECT_TO_TEXT_DISTANCE = 5
    let LEGEND_DISTANCE = 20
    newLegs.append('rect')
      .attr('width', RECT_WIDTH)
      .attr('height', 10)
    newLegs.append('text')
      .attr('dx', RECT_WIDTH + RECT_TO_TEXT_DISTANCE)
      .attr('dy', 10)

    let mergedLegs = legs.merge(newLegs)

    function getDx(d, n) {
      let previousWidth = 0
      for (let i = 0; i < n; i++) {
        previousWidth += series[i]._legendTextWidth
      }
      return n * (RECT_WIDTH + RECT_TO_TEXT_DISTANCE + LEGEND_DISTANCE) + previousWidth
    }

    mergedLegs.attr('transform', (d, i) => {
      return `translate(${getDx(d, i)}, 0)`
    })
    mergedLegs
      .select('rect')
      .attr('fill', d => d.fillColor)
      .attr('stroke', d => d.fillColor)
      .attr('transform', 'translate(0, -1)')
    mergedLegs.select('text').attr('fill', config.options.legend.color).text(d => d.label)

    // draws SUM
    let sumWrapper = svg.select('.kpi-sum-wrapper')
    let sums = sumWrapper.selectAll('g.sum').data(config.percentage.enabled ? [0] : [])
    let newSums = sums.enter().append('g').attr('class', 'sum')
    let arrowTransform = config.percentage.reversed ? 'translate(0 2.5) rotate(180)' : 'translate(2 5.5)'
    newSums.append('path')
      .attr('class', 'arrow')
      .attr('d', arrowUpPath(90))
      .attr('fill', 'red')
    newSums.append('text').attr('class', 'label')
      .attr('dx', 15)
      .attr('dy', 10)
      .attr('fill', 'red')
    sums.merge(newSums)
      .select('path')
      .attr('fill', config.percentage.fillColor)
      .attr('transform', arrowTransform)
    sums.merge(newSums)
      .select('text')
      .attr('fill', config.percentage.fillColor)
      .text(config.percentage.value + '%')
    sums.exit().remove()
    let sumNode = sums.merge(newSums).node()
    sumWrapper.attr('transform', `translate(${chartWidth - (sumNode ? sumNode.getBoundingClientRect().width : 0)}, 0)`)
  }
}

export default new CbpoKPIChart()
