import * as d3 from 'd3'
import uuidv4 from 'uuid'
import orderBy from 'lodash/orderBy'
import upperIcon from '@/assets/images/icons/bar-kpi-precise-upper.png'
import lowerIcon from '@/assets/images/icons/bar-kpi-precise-lower.png'

function numberWithCommas(x) {
  return x ? x.toLocaleString('en-US') : ''
}

class KPIBarChart {
  constructor(svg, data, props) {
    this.id = uuidv4()
    this.svg = svg
    this.data = [
      ...orderBy(data.filter(d => d.value !== null), 'value', 'desc'),
      ...data.filter(d => d.value === null)
    ]
    this.size = props.size
    this.max = props.max
    this.bar = props.bar
    this.point = props.point
    this.background = props.background
    this.legendColor = props.legendColor
    this.maxWidthBar = null
    this.labelPositions = []
    this.shadowBoxId = `drop-shadow-${uuidv4()}`
    this.shadowTriangleId = `drop-shadow-${uuidv4()}`
  }

  scale(value) {
    return d3.scaleLinear().domain([0, this.max.value])(value)
  }

  render() {
    this._fillBackground()
    this._addShadowFilter()
    this._drawPoints()
    this._calcLabelPosition()
    this._drawLabels()
    this._drawBars()
    this._drawLegends()
  }

  _calcLabelPosition() {
    const _self = this
    const fakeLabels = this.svg
      .selectAll('text.fake-label')
      .data(this.data)
    this.maxWidthBar = this.size.x - this.bar.padding * 2
    fakeLabels
      .enter()
      .append('text')
      .attr('class', 'fake-label')
      .attr('font-size', '12px')
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('visibility', 'hidden')
      .text(d => (d.formatValue || d.value))
      .each(function(d, i) {
        const node = d3.select(this)
        const size = node.node().getBoundingClientRect()
        i === 0 && (_self.maxWidthBar -= size.width + 30)
        let x = _self.scale(d.value) * _self.maxWidthBar
        let y = d.position === 'top' ? -25 : _self.bar.height + 25
        _self.labelPositions.push({ position: { x, y }, size })
        node.remove()
      })
  }

  _isRectOverlap(rectA, rectB) {
    const valueInRange = (value, min, max) => {
      return (value >= min) && (value <= max)
    }

    const isXOverlap = valueInRange(rectA.x, rectB.x, rectB.x + rectB.width) || valueInRange(rectB.x, rectA.x, rectA.x + rectA.width)
    const isYOverlap = valueInRange(rectA.y, rectB.y, rectB.y + rectB.height) || valueInRange(rectB.y, rectA.y, rectA.y + rectA.height)
    return isXOverlap && isYOverlap
  }

  _drawPoints() {
    const groupPoints = this.svg
      .selectAll('g.group-points')
      .data([0])

    const mergeGroupPoints = groupPoints
      .enter()
      .append('g')
      .merge(groupPoints)
      .attr('class', 'group-points')

    this._drawArrow(mergeGroupPoints, this.point.enabled ? [0] : [])

    const textPoints = mergeGroupPoints
      .selectAll('text.text-point')
      .data(this.point.enabled ? [0] : [])

    textPoints
      .enter()
      .append('text')
      .merge(textPoints)
      .attr('class', 'text-point')
      .attr('x', 30)
      .attr('y', 25)
      .attr('font-size', '14px')
      .attr('font-weight', 400)
      .attr('fill', this.point.color)
      .text(this.point.label)

    textPoints
      .exit()
      .remove()

    const size = mergeGroupPoints
      .node()
      .getBoundingClientRect()

    mergeGroupPoints
      .attr('transform', `translate(${(this.size.x / 2) - (size.width / 2)}, 0)`)
  }

  _drawBars() {
    const _self = this
    const groupBar = this.svg
      .selectAll('g.group-bar')
      .data(this.data)

    const mergeBars = groupBar
      .enter()
      .append('g')
      .merge(groupBar)
      .attr('class', 'group-bar')
      .attr('transform', `translate(${this.bar.padding}, ${this.size.y / 2})`)

    mergeBars
      .each(function(d) {
        const node = d3.select(this)
        // draw rectangle
        const bar = node.selectAll('rect.bar').data([d])
        bar
          .enter()
          .append('rect')
          .merge(bar)
          .attr('class', 'bar')
          .attr('width', d => d.value ? _self.scale(d.value) * _self.maxWidthBar : 0)
          .attr('height', _self.bar.height)
          .attr('fill', d.color)
      })

    mergeBars
      .exit()
      .remove()
  }

  _drawLabels() {
    const _self = this
    const groupLabel = this.svg
      .selectAll('g.group-labels')
      .data([0])

    const mergeGroupLabel = groupLabel
      .enter()
      .append('g')
      .merge(groupLabel)
      .attr('class', 'group-labels')
      .attr('transform', `translate(${this.bar.padding}, ${this.size.y / 2})`)

    const boxWidth = (i) => _self.labelPositions[i].size.width + 20
    const boxHeight = (i) => _self.labelPositions[i].size.height + 10
    const labels = mergeGroupLabel
      .selectAll('text.label')
      .data(this.data)
    labels
      .enter()
      .append('g')
      .merge(labels)
      .attr('class', d => d.label)
      .attr('transform', (d, i) => d.position !== 'left'
        ? `translate(${this.labelPositions[i].position.x - boxWidth(i) / 2}, ${this.labelPositions[i].position.y})`
        : `translate(${this.scale(d.value) * _self.maxWidthBar}, -${boxHeight(i) / 4})`
      )
      .each(function (d, i) {
        if (d.value === null) return
        const node = d3.select(this)

        node.append('rect')
          .attr('class', 'box-label')
          .attr('width', boxWidth(i))
          .attr('height', boxHeight(i))
          .attr('fill', _self.background || '#ffffff')
          .attr('rx', 1)
          .attr('ry', 1)
          .attr('filter', `url(#${_self.shadowBoxId})`)
          .attr('transform', () => d.position !== 'left'
            ? `translate(0, -${boxHeight(i) / 2})`
            : `translate(10, -${0})`)

        node.append('path')
          .attr('d', d3.symbol().type(d3.symbolTriangle).size(50))
          .attr('fill', _self.background || '#ffffff')
          .attr('filter', `url(#${_self.shadowTriangleId})`)
          .attr('transform', () => {
            const transformCondition = {
              left: {
                isApply: () => i === 0 || d.position === 'left',
                value: () => `translate(7, ${boxHeight(i) / 2}) rotate(-90)`
              },
              up: {
                isApply: () => d.position === 'bottom',
                value: () => `translate(${boxWidth(i) / 2}, -${boxHeight(i) / 2 + 3})`
              },
              down: {
                isApply: () => d.position === 'top',
                value: () => `translate(${boxWidth(i) / 2}, ${boxHeight(i) / 2 + 3})  rotate(-180)`
              }
            }
            const selected = Object
              .keys(transformCondition)
              .find(key => transformCondition[key].isApply())
            return transformCondition[selected].value()
          })

        node.append('text')
          .attr('class', 'label')
          .attr('text-anchor', 'middle')
          .attr('alignment-baseline', 'middle')
          .attr('font-size', '12px')
          .attr('fill', d => d.color.max)
          .attr('transform', d => {
            const positionX = d.position !== 'left' ? boxWidth(i) / 2 : boxWidth(i) / 2 + 10
            const positionY = d.position !== 'left' ? 1 : boxHeight(i) / 2 + 1
            return `translate(${positionX}, ${positionY})`
          })
          .text(d => d.formatValue || d.value)
          .append('svg:title')
          .text(d => `${d.formatLabel}: ${numberWithCommas(d.value)}`)
      })

    labels
      .exit()
      .remove()
  }

  _drawLegends() {
    const _self = this
    const groupLegend = this.svg
      .selectAll('g.group-legend')
      .data([0])
    const mergeGroupedLegend = groupLegend
      .enter()
      .append('g')
      .merge(groupLegend)
      .attr('class', 'group-legend')
      .attr('transform', `translate(0, ${this.size.y / 2 + 30})`)
    const fixedData = [
      this.data.find(d => d.label === 'Max_Value'),
      this.data.find(d => d.label === 'Target_Value'),
      this.data.find(d => d.label === 'Current_Value')
    ].filter(d => d.value !== null)
    const legend = mergeGroupedLegend
      .selectAll('g.legend')
      .data(fixedData)
    let padding = 0

    legend
      .enter()
      .append('g')
      .merge(legend)
      .attr('class', 'legend')
      .each(function(_d, i) {
        const node = d3.select(this)

        node
          .append('rect')
          .attr('width', 12)
          .attr('height', 12)
          .attr('rx', 1)
          .attr('ry', 1)
          .attr('fill', d => d.color)
          .attr('transform', 'translate(1, 1)')

        node
          .append('text')
          .attr('x', 18)
          .attr('y', 8)
          .attr('alignment-baseline', 'middle')
          .attr('fill', _self.legendColor)
          .attr('font-size', '12px')
          .text(d => d.formatLabel)

        const size = node.node().getBoundingClientRect()
        padding = i !== 0 ? padding + size.width + 20 : 230

        node.attr('transform', `translate(${_self.size.x - padding}, 0)`)
      })

    legend
      .exit()
      .remove()

    const [data] = this.data.filter(d => d.position === 'bottom')
    const bottomLabel = data ? this.svg.select(`g.group-labels > g.${data.label}`) : null
    const bottomLabelRect = bottomLabel ? bottomLabel.node().getBoundingClientRect() : null
    const legendRect = mergeGroupedLegend.node().getBoundingClientRect()
    const isOverlapping = bottomLabelRect ? this._isRectOverlap(legendRect, bottomLabelRect) : false
    isOverlapping && mergeGroupedLegend.attr('transform', `translate(0, ${this.size.y / 2 + 60})`)
  }

  _fillBackground() {
    const size = this.svg
      .node()
      .getBoundingClientRect()

    const background = this.svg
      .selectAll('rect.bar-background')
      .data([0])

    background
      .enter()
      .append('rect')
      .merge(background)
      .attr('class', 'background')
      .attr('width', size.width)
      .attr('height', size.height)
      .attr('fill', this.background)
  }

  _drawArrow(selector, data) {
    selector
      .data(data)
      .append('svg:image')
      .attr('width', 24)
      .attr('height', 24)
      .attr('transform', 'translate(0, 8)')
      .attr('xlink:href', this.point.direction === 'bottom' ? lowerIcon : upperIcon)
  }

  _addShadowFilter() {
    const defs = this.svg.append('defs')

    const filterBox = defs.append('filter')
      .attr('id', this.shadowBoxId)
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%')
      .attr('filterUnits', 'objectBoundingBox')

    filterBox.append('feDropShadow')
      .attr('in', 'SourceGraphic')
      .attr('stdDeviation', 3)
      .attr('dx', 0)
      .attr('dy', 8)
      .attr('flood-color', '#101828')
      .attr('flood-opacity', 0.1)

    const filterTriangle = defs.append('filter')
      .attr('id', this.shadowTriangleId)
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%')
      .attr('filterUnits', 'objectBoundingBox')

    filterTriangle.append('feDropShadow')
      .attr('in', 'SourceGraphic')
      .attr('stdDeviation', 3)
      .attr('dx', 0)
      .attr('dy', -2)
      .attr('flood-color', '#101828')
      .attr('flood-opacity', 0.1)
  }
}

class KPIPreciseChart {
  renderRadialKPI() {
    throw new Error('SDK haven\'t support radial chart with precise style yet.')
  }

  renderBarKPI(selector, { config, data }) {
    const nodeDiv = d3.select(selector)
      .style('width', config.size.x + 'px')
      .style('height', config.size.y + 'px')
    // create svg node
    const svg = nodeDiv
      .append('svg')
      .attr('width', config.size.x)
      .attr('height', config.size.y)
    // create new Radial class and render
    const barChart = new KPIBarChart(svg, data, config)
    barChart.render()
  }
}

export default new KPIPreciseChart()
