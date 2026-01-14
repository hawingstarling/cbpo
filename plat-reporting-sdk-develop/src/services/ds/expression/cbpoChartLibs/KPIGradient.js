import * as d3 from 'd3'
import uuidv4 from 'uuid'

class Needle {
  constructor(svg, props) {
    this.svg = svg
    this.data = [props.needle.pointValue]
    this.len = props.needle.length
    this.color = props.needle.color
    this.radius = props.radius
    this.x = props.size.x
    this.y = props.size.y
    this.minAngle = props.angle.min
    this.maxAngle = props.angle.max
  }

  render() {
    const totalDeg = (Math.abs(this.minAngle) + Math.abs(this.maxAngle))

    const group = this.svg.selectAll('g.group-needle').data([0])

    const mergedGroup = group
      .enter()
      .append('g')
      .merge(group)
      .attr('class', 'group-needle')
      .attr('transform', `translate(${this.x / 2}, ${this.y / 1.7})`)

    const needle = mergedGroup
      .selectAll('path.gauge-needle')
      .data(this.data)

    needle
      .enter()
      .append('path')
      .merge(needle)
      .attr('class', 'gauge-needle')
      .attr('fill', this.color)
      .attr('d', this._getPath.bind(this)(0))
      .attr('transform', d => `rotate(${d * totalDeg} 0 0)`)

    needle.exit().remove()

    const circle = mergedGroup
      .selectAll('circle.needle-base')
      .data([0])

    circle
      .enter()
      .append('circle')
      .merge(circle)
      .attr('class', 'needle-base')
      .attr('fill', '#bdc0c4')
      .attr('cx', 0)
      .attr('cy', 0)
      .attr('r', this.radius)
  }

  _getPath(p) {
    const diffAngle = Math.abs(this.minAngle + 90)
    const thetaRad = this.convertPercentageToRad(p / 2)
    const centerX = 0
    const centerY = 0
    const topX = centerX - this.len * Math.cos(this.convertDegToRad(diffAngle))
    const topY = centerY - this.len * (Math.sin(thetaRad) - Math.sin(this.convertDegToRad(diffAngle)))
    const leftX = centerX - (this.radius / 6) * Math.cos(thetaRad - Math.PI / 2)
    const leftY = centerY - (this.radius / 6) * Math.sin(thetaRad - Math.PI / 2)
    const rightX = centerX - (this.radius / 6) * Math.cos(thetaRad + Math.PI / 2)
    const rightY = centerY - (this.radius / 6) * Math.sin(thetaRad + Math.PI / 2)

    return `M ${leftX} ${leftY} L ${topX} ${topY} L ${rightX} ${rightY}`
  }

  convertPercentageToDeg(percent) {
    return percent * 360
  };

  convertPercentageToRad(percent) {
    return this.convertDegToRad(this.convertPercentageToDeg(percent))
  };

  convertDegToRad(deg) {
    return deg * Math.PI / 180
  };
}

class KPIRadialChart {
  constructor(selector, data, props) {
    this.id = uuidv4()
    this.svg = selector
    this.data = data
    this.minAngle = props.angle.min
    this.maxAngle = props.angle.max
    this.x = props.size.x
    this.y = props.size.y
    this.radius = props.radius
    this.max = props.max
    this.background = props.background

    this.needle = new Needle(this.svg, {
      angle: props.angle,
      size: props.size,
      needle: props.needle,
      radius: 8
    })

    this._fillBackground()
    this._buildGradientEffect()
  }

  render() {
    const _self = this
    let data = this._buildData(this.data, this.max)
    let radiusData = this._buildRadiusData(this.data, this.radius)
    let range = this.maxAngle - this.minAngle

    const scale = d3.scaleLinear()
      .domain([0, this.max.value])
      .range([this.minAngle, this.maxAngle])

    const group = this.svg
      .selectAll('g.group-gauge')
      .data([0])

    const mergedGroup = group
      .enter()
      .append('g')
      .merge(group)
      .attr('class', 'group-gauge')
      .attr('transform', `translate(${_self.x / 2}, ${_self.y / 1.7})`)

    const gauges = mergedGroup
      .selectAll('g.gauge')
      .data(data)

    const mergeGauge = gauges
      .enter()
      .append('g')
      .merge(gauges)
      .attr('class', 'gauge')

    gauges
      .exit()
      .remove()

    // draw all circle radius
    mergeGauge.each(function (d, i) {
      const node = d3.select(this)
      const arcNode = node
        .selectAll('g.arc')
        .data([0])

      const mergeArcNode = arcNode.enter()
        .append('g')
        .merge(arcNode)
        .attr('class', 'arc')

      // calc radius of circle
      const arc = d3.arc()
        .innerRadius(radiusData[i].inner)
        .outerRadius(radiusData[i].outer)
        .cornerRadius(radiusData[i].corner)
        .startAngle(_self._convertDegToRad(_self.minAngle))
        .endAngle(d => {
          const angle = d.value * range / _self.max.value
          return _self._convertDegToRad(angle + _self.minAngle)
        })

      // draw node
      const arcPath = mergeArcNode
        .selectAll('path')
        .data(d)

      arcPath
        .enter()
        .append('path')
        .merge(arcPath)
        .attr('class', 'arc-path')
        .attr('fill', d =>
          d.label === _self.max.label
            ? _self.max.color
            : `url(#${d.label}_gradient_${_self.id})`
        )
        .attr('d', arc)

      arcPath
        .exit()
        .remove()
    })

    // draw needle
    this.needle
      .render()

    // prepare for draw value
    const groupValues = this.svg
      .selectAll('g.group-value')
      .data([0])

    const mergeGroupValue = groupValues
      .enter()
      .append('g')
      .merge(groupValues)
      .attr('class', 'group-value')
      .attr('transform', `translate(${_self.x / 2}, ${_self.y / 1.7})`)

    const labelValues = mergeGroupValue
      .selectAll('text.value')
      .data(data)

    const mergeTextValue = labelValues
      .enter()
      .append('text')
      .merge(labelValues)
      .attr('class', 'value')

    const positions = []

    // draw all value text
    mergeTextValue.each(function (d, i) {
      const node = d3.select(this)
      const currentData = d[1]
      const deg = scale(currentData.value)

      const label = `${currentData.formatValue || currentData.value}`
      const valueNode = mergeGroupValue
        .selectAll('text.fake-node')
        .data([0])

      const mergeValueNode = valueNode
        .enter()
        .append('text')
        .merge(valueNode)
        .attr('class', 'fake-node')
        .attr('visibility', 'hidden')
        .text(label)
      const nodeSize = mergeValueNode.node().getBoundingClientRect()
      const length = i === 0 ? _self.needle.len + 5 : radiusData[radiusData.length - 1].inner - 20
      const pointValue = _self._getPointValue(scale, currentData.value, nodeSize, length)

      // adjust position for first value so it won't overlap with needle
      if (i === 0 && deg > 0) {
        const distancePerNumber = 4
        const valueLength = Math.floor(currentData.value).toString().length
        pointValue.dx = pointValue.dx - valueLength * distancePerNumber
      }

      if (i > 0) {
        if (deg < -90) pointValue.dx = pointValue.dx + 10
        if (deg > 90) pointValue.dx = pointValue.dx - 10
      }

      // push position into array to compare and resize if it is overlaps
      positions.push({
        pointValue,
        size: nodeSize
      })

      // Compare position and adjust if overlapping
      for (let j = 0; j < i; j++) {
        const { pointValue: prevPos, size: prevSize } = positions[j]
        const { pointValue: currentPos, size: currentSize } = positions[i]

        const currentRect = { x: Math.abs(currentPos.dx), y: currentPos.dy, width: currentSize.width, height: currentSize.height }
        const prevRect = { x: Math.abs(prevPos.dx), y: prevPos.dy, width: prevSize.width, height: prevSize.height }

        if (_self._isRectOverlap(currentRect, prevRect)) {
          currentPos.dy = prevSize.height + prevPos.dy + 10
          pointValue.dy = currentPos.dy
        }
      }

      node
        .attr('text-anchor', 'middle')
        .attr('alignment-baseline', 'middle')
        .attr('class', 'needle-value')
        .attr('paint-order', 'stroke')
        .attr('stroke', _self.background)
        .attr('stroke-width', 2.5)
        .attr('text-rendering', 'auto')
        .attr('fill', currentData.color.max)
        .attr('dx', pointValue.dx)
        .attr('dy', pointValue.dy)
        .text(label)
        .append('svg:title')
        .text(currentData.value)

      mergeValueNode.remove()
    })
  }

  _fillBackground() {
    const size = this.svg.node().getBoundingClientRect()
    this.svg
      .append('rect')
      .attr('class', 'background')
      .attr('width', size.width)
      .attr('height', size.height)
      .attr('fill', this.background)
  }

  _buildGradientEffect() {
    this.data.forEach((d) => {
      const def = this.svg.append('defs')
      const linearGradient = def
        .append('linearGradient')
        .attr('id', `${d.label}_gradient_${this.id}`)

      linearGradient
        .selectAll('stop')
        .data([d.color.min, d.color.max])
        .enter()
        .append('stop')
        .attr('offset', (_d, i) => i)
        .attr('stop-color', d => d)
    })
  }

  _buildData(data, max) {
    return data.map(d => [max, d])
  }

  _buildRadiusData(data, radius) {
    const { inner, outer, corner, padding } = radius

    return data.reduce((curr, _d, i) => {
      if (i === 0) {
        curr.push({ outer, inner, corner })
      } else {
        const { inner: prevIr, outer: prevOr } = curr[i - 1]
        const newOr = prevIr - padding
        curr.push({
          outer: newOr,
          inner: newOr - ((prevOr - prevIr) / 3),
          corner
        })
      }
      return curr
    }, [])
  }

  _hexTofeColorMatrix(hex) {
    hex = hex.split('#')[1]
    let RGB = []
    let numberList = [1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0]
    for (let i = 0; i < hex.length; i += 2) {
      const firstDigit = parseInt(hex[i], 16)

      const firstDigitPartial = firstDigit * 16

      let RGBValue = parseInt(hex[i + 1], 16) + firstDigitPartial

      RGBValue = RGBValue / 255

      RGBValue = RGBValue.toFixed(2)

      RGB.push(RGBValue)
    }

    const red = parseFloat(RGB[0])
    const green = parseFloat(RGB[1])
    const blue = parseFloat(RGB[2])

    numberList[0] = red
    numberList[6] = green
    numberList[12] = blue

    return numberList
  }

  _convertDegToRad(deg) {
    return deg * Math.PI / 180
  }

  _getPointValue(scale, p, size, length) {
    let dy = -length * Math.cos(this._convertDegToRad(scale(p)))
    let dx = length * Math.sin(this._convertDegToRad(scale(p)))
    return { dx, dy }
  }

  _valueInRange(value, min, max) {
    return (value >= min) && (value <= max)
  }

  _isRectOverlap(rectA, rectB) {
    const isXOverlap = this._valueInRange(rectA.x, rectB.x, rectB.x + rectB.width) || this._valueInRange(rectB.x, rectA.x, rectA.x + rectA.width)
    const isYOverlap = this._valueInRange(rectA.y, rectB.y, rectB.y + rectB.height) || this._valueInRange(rectB.y, rectA.y, rectA.y + rectA.height)
    return isXOverlap && isYOverlap
  }
}

class KPIBarChart {
  constructor(svg, data, props) {
    this.id = uuidv4()
    this.svg = svg
    this.data = data
    this.size = props.size
    this.max = props.max
    this.bar = props.bar
    this.point = props.point
    this.background = props.background
    this.legendColor = props.legendColor

    this._fillBackground()
    this._buildGradientEffect()
  }

  render() {
    const _self = this
    const scale = d3.scaleLinear().domain([0, this.max.value])
    const maxWidthBar = this.size.x - this.bar.padding * 2
    const data = this.data.sort((a, b) => b.value - a.value)
    const legendWidth = (this.size.x - this.bar.padding * 2) / (data.length || 1)
    const barData = [
      { value: this.max.value, color: this.max.color, position: null, label: null, formatValue: null },
      ...data
    ]

    let groupPoints = this.svg
      .selectAll('g.group-points')
      .data([0])

    let mergeGroupPoints = groupPoints
      .enter()
      .append('g')
      .merge(groupPoints)

    mergeGroupPoints
      .attr('class', 'group-points')

    const groupBar = this.svg
      .selectAll('g.group-bar')
      .data(barData)

    const mergeBars = groupBar
      .enter()
      .append('g')
      .merge(groupBar)

    mergeBars
      .attr('class', (d) => d.label ? d.label + ' group-bar' : 'group-bar')
      .attr('transform', `translate(${this.bar.padding}, ${this.size.y / 2})`)

    const groupLabel = this.svg
      .selectAll('g.group-labels')
      .data([0])

    const mergeGroupLabel = groupLabel
      .enter()
      .append('g')
      .merge(groupLabel)

    mergeGroupLabel
      .attr('class', 'group-labels')
      .attr('transform', `translate(${this.bar.padding}, ${this.size.y / 2})`)

    const groupLegend = this.svg
      .selectAll('g.group-legend')
      .data([0])

    const mergeGroupedLegend = groupLegend
      .enter()
      .append('g')
      .merge(groupLegend)

    mergeGroupedLegend.attr('class', 'group-legend')
      .attr('transform', `translate(${this.bar.padding}, ${this.size.y - 40})`)

    const nodePositions = []

    // draw point value
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
      .attr('font-size', 30)
      .attr('font-weight', 'bold')
      .attr('fill', this.point.color)
      .text(this.point.label)

    textPoints
      .exit()
      .remove()

    const size = mergeGroupPoints
      .node()
      .getBoundingClientRect()

    mergeGroupPoints
      .attr('transform', `translate(${(this.size.x / 2) - (size.width / 2)}, 30)`)

    // draw a bar
    mergeBars
      .each(function (d, i) {
        const node = d3.select(this)
        const dataCircle = [
          {
            position: 0,
            color: i === 0 ? d.color : d.color.min,
            radius: _self.bar.height / 2
          },
          {
            position: scale(d.value) * maxWidthBar,
            color: i === 0 ? d.color : d.color.max,
            radius: d.value === _self.point.targetPoint ? _self.bar.height * 0.85 : _self.bar.height / 2
          }
        ]

        // draw circle
        const circle = node
          .selectAll('circle.circle')
          .data(dataCircle)

        circle
          .enter()
          .append('circle')
          .merge(circle)
          .attr('class', 'circle')
          .attr('cx', d => d.position)
          .attr('cy', _self.bar.height / 2)
          .attr('r', d => d.radius)
          .attr('fill', d => d.color)

        // draw rectangle
        const bar = node.selectAll('rect.bar')
          .data([d])

        bar
          .enter()
          .append('rect')
          .merge(bar)
          .attr('class', 'bar')
          .attr('width', d => scale(d.value) * maxWidthBar)
          .attr('height', _self.bar.height)
          .attr('fill', i === 0 ? d.color : `url(#${d.label}_gradient_${_self.id})`)
      })

    mergeBars
      .exit()
      .remove()

    // draw fake label to calculated position
    const fakeLabels = mergeGroupLabel
      .selectAll('text.fake-label')
      .data(data)

    // this node will be removed inside for so no need to exit().remove()
    fakeLabels
      .enter()
      .append('text')
      .attr('class', 'fake-label')
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('visibility', 'hidden')
      .text(d => (d.formatValue || d.value))
      .each(function (d, i) {
        const node = d3.select(this)
        const size = node.node().getBoundingClientRect()
        let x = scale(d.value) * maxWidthBar
        let y = d.position === 'top' ? -15 : _self.bar.height + 25
        if (i > 0) {
          const { position: prevPos, size: prevSize } = nodePositions[i - 1]
          const currentRect = { x, y, width: size.width, height: size.height }
          const prevRect = { x: prevPos.x, y: prevPos.y, width: prevSize.width, height: prevSize.height }
          if (_self._isRectOverlap(currentRect, prevRect)) {
            y = prevPos.y + 20
          }
        }
        nodePositions.push({ position: { x, y }, size })

        node.remove()
      })

    // draw label
    const labels = mergeGroupLabel
      .selectAll('text.label')
      .data(data)

    labels
      .enter()
      .append('text')
      .merge(labels)
      .attr('class', 'label')
      .attr('text-anchor', 'middle')
      .attr('alignment-baseline', 'middle')
      .attr('fill', d => d.color.max)
      .attr('transform', (d, i) => {
        const { x, y } = nodePositions[i].position
        return `translate(${x}, ${y})`
      })
      .text(d => {
        return d.formatValue || d.value
      })
      .append('svg:title')
      .text(d => d.value)

    labels
      .exit()
      .remove()

    // drawl legend
    const legend = mergeGroupedLegend
      .selectAll('g.legend')
      .data(data)

    legend
      .enter()
      .append('g')
      .merge(legend)
      .attr('class', 'legend')
      .each(function (_d, i) {
        const node = d3.select(this)
        let size = null

        node
          .append('rect')
          .attr('width', 12)
          .attr('height', 12)
          .attr('rx', 3)
          .attr('ry', 3)
          .attr('fill', d => `url(#${d.label}_gradient_${_self.id})`)

        node
          .append('text')
          .attr('x', 18)
          .attr('y', 8)
          .attr('alignment-baseline', 'middle')
          .attr('fill', _self.legendColor)
          .text(d => d.formatLabel)

        size = node.node().getBoundingClientRect()

        node.attr('transform', `translate(${(legendWidth * i) + (legendWidth / 2) - (size.width / 2)}, 0)`)
      })

    legend
      .exit()
      .remove()
  }

  _buildGradientEffect() {
    this.data.forEach((d) => {
      const def = this.svg.append('defs')
      const linearGradient = def
        .append('linearGradient')
        .attr('id', `${d.label}_gradient_${this.id}`)

      linearGradient
        .selectAll('stop')
        .data([d.color.min, d.color.max])
        .enter()
        .append('stop')
        .attr('offset', (_d, i) => i)
        .attr('stop-color', d => d)
    })
  }

  _valueInRange(value, min, max) {
    return (value >= min) && (value <= max)
  }

  _isRectOverlap(rectA, rectB) {
    const isXOverlap = this._valueInRange(rectA.x, rectB.x, rectB.x + rectB.width) || this._valueInRange(rectB.x, rectA.x, rectA.x + rectA.width)
    const isYOverlap = this._valueInRange(rectA.y, rectB.y, rectB.y + rectB.height) || this._valueInRange(rectB.y, rectA.y, rectA.y + rectA.height)
    return isXOverlap && isYOverlap
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
    const svg = selector
      .data(data)
      .append('svg')
      .attr('viewBox', '0 0 512 512')
      .attr('xmlns:xlink', 'http://www.w3.org/1999/xlink')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', 30)
      .attr('height', 30)

    const group = svg
      .data(data)
      .append('g')

    group
      .data(data)
      .append('path')
      .attr('d', () => this.point.direction === 'bottom'
        ? 'M403.079,310.458c-3.627-7.232-11.008-11.797-19.093-11.797h-64v-85.333c0-11.776-9.536-21.333-21.333-21.333H213.32    c-11.776,0-21.333,9.557-21.333,21.333v85.333h-64c-8.064,0-15.445,4.565-19.072,11.797c-3.605,7.232-2.837,15.872,2.027,22.336    l128,170.667c4.011,5.376,10.347,8.533,17.045,8.533c6.72,0,13.056-3.157,17.067-8.533l128-170.667    C405.917,326.33,406.685,317.69,403.079,310.458z'
        : 'M402.067,179.2l-128-170.667c-8.533-11.378-25.6-11.378-34.133,0l-128,170.667     c-10.548,14.064-0.513,34.133,17.067,34.133h64v85.333c0,11.782,9.551,21.333,21.333,21.333h85.333     c11.782,0,21.333-9.551,21.333-21.333v-85.333h64C402.58,213.333,412.614,193.264,402.067,179.2z M299.667,170.667     c-11.782,0-21.333,9.551-21.333,21.333v85.333h-42.667V192c0-11.782-9.551-21.333-21.333-21.333h-42.667L257,56.889     l85.333,113.778H299.667z'
      )
      .attr('fill', this.point.color)

    group
      .data(data)
      .append('path')
      .attr('d', () => this.point.direction === 'bottom'
        ? 'M298.663,128.001H213.33c-11.797,0-21.333,9.536-21.333,21.333c0,11.797,9.536,21.333,21.333,21.333h85.333    c11.797,0,21.333-9.536,21.333-21.333C319.996,137.537,310.46,128.001,298.663,128.001z'
        : 'M299.667,341.333h-85.333c-11.782,0-21.333,9.551-21.333,21.333S202.551,384,214.333,384h85.333     c11.782,0,21.333-9.551,21.333-21.333S311.449,341.333,299.667,341.333z'
      )
      .attr('fill', this.point.color)

    group
      .data(data)
      .append('path')
      .attr('d', () => this.point.direction === 'bottom'
        ? 'M298.663,64.001H213.33c-11.797,0-21.333,9.536-21.333,21.333s9.536,21.333,21.333,21.333h85.333    c11.797,0,21.333-9.536,21.333-21.333S310.46,64.001,298.663,64.001z'
        : 'M299.667,405.333h-85.333c-11.782,0-21.333,9.551-21.333,21.333S202.551,448,214.333,448h85.333     c11.782,0,21.333-9.551,21.333-21.333S311.449,405.333,299.667,405.333z'
      )
      .attr('fill', this.point.color)

    group
      .data(data)
      .append('path')
      .attr('d', () => this.point.direction === 'bottom'
        ? 'M298.664,0H213.33c-11.797,0-21.333,9.536-21.333,21.333c0,11.798,9.536,21.334,21.333,21.334h85.333    c11.797,0,21.333-9.536,21.333-21.333C319.997,9.536,310.461,0,298.664,0z'
        : 'M299.667,469.333h-85.333c-11.782,0-21.333,9.551-21.333,21.333S202.551,512,214.333,512h85.333     c11.782,0,21.333-9.551,21.333-21.333S311.449,469.333,299.667,469.333z'
      )
      .attr('fill', this.point.color)
  }
}

class KPIGradientChart {
  renderRadialKPI(selector, { config, data }) {
    const nodeDiv = d3.select(selector)
      .style('width', config.size.x + 'px')
      .style('height', config.size.y + 'px')
    // create svg node
    const svg = nodeDiv
      .append('svg')
      .attr('width', config.size.x)
      .attr('height', config.size.y)
    // create new Radial class and render
    const raidal = new KPIRadialChart(svg, data, config)
    raidal.render()
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
    const raidal = new KPIBarChart(svg, data, config)
    raidal.render()
  }
}

export default new KPIGradientChart()
