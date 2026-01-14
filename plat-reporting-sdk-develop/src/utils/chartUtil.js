import * as d3 from 'd3'
import { colorSchemes, TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import { createBinColumnAlias } from '@/utils/binUtils'
import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import isEmpty from 'lodash/isEmpty'
import findIndex from 'lodash/findIndex'
import range from 'lodash/range'
import isObject from 'lodash/isObject'
import get from 'lodash/get'
import orderBy from 'lodash/orderBy'
import uniq from 'lodash/uniq'
import maxBy from 'lodash/maxBy'
import isArray from 'lodash/isArray'

let style = {
  accentColor: '#000000',
  mainColor: '#ffffff',
  hoverItemColor: '#000000',
  navigationActive: '#17a2b8',
  navigationInactive: '#cecece'
}

const SCHEME20 = [
  '#1f77b4', '#aec7e8',
  '#ff7f0e', '#ffbb78',
  '#2ca02c', '#98df8a',
  '#d62728', '#ff9896',
  '#9467bd', '#c5b0d5',
  '#8c564b', '#c49c94',
  '#e377c2', '#f7b6d2',
  '#7f7f7f', '#c7c7c7',
  '#bcbd22', '#dbdb8d',
  '#17becf', '#9edae5'
]

// eslint-disable-next-line no-unused-vars
const SCHEME10 = [
  '#1f77b4', '#ff7f0e',
  '#2ca02c', '#d62728',
  '#9467bd', '#8c564b',
  '#e377c2', '#7f7f7f',
  '#bcbd22', '#17becf'
]

const GOOGLE = [
  '#3366CC', '#DC3912',
  '#FF9900', '#109618',
  '#990099', '#3B3EAC',
  '#0099C6', '#DD4477',
  '#66AA00', '#B82E2E',
  '#316395', '#994499',
  '#22AA99', '#AAAA11',
  '#6633CC', '#E67300',
  '#8B0707', '#329262',
  '#5574A6', '#3B3EAC'
]

const SCHEME30 = [
  '#2A7B9B', '#900C3F',
  '#FFC300', '#00BAAD',
  '#FF5733', '#3D3D6B',
  '#ADD45C', '#FF8D1A',
  '#EDDD53', '#BA2C29',
  '#2E6297', '#6629CF'
]

const SCHEME_COLOR_GRADIENT_1 = [
  ['#3664F4', '#669FFE'],
  ['#419421', '#AADB53'],
  ['#FD432A', '#F16F0F'],
  ['#004E65', '#0099C6'],
  ['#084C0C', '#109618'],
  ['#824E00', '#FF9900'],
  ['#565609', '#AAAA11'],
  ['#341A68', '#6633CC'],
  ['#11564E', '#22AA99'],
  ['#701D09', '#DC3912'],
  ['#4E004E', '#990099']
]

export const getColorSchemes = (type) => {
  switch (type) {
    case colorSchemes.D3_10:
      return SCHEME10
    case colorSchemes.D3_20:
      return SCHEME20
    case colorSchemes.D3_30:
      return SCHEME30
    case colorSchemes.SC_1:
      return SCHEME_COLOR_GRADIENT_1
    default:
      break
  }
  return GOOGLE
}

export const randomColor = (type, length) => {
  let colors = []
  if (isNaN(length)) {
    return colors
  }
  let scheme
  switch (type) {
    case colorSchemes.D3_10:
      scheme = SCHEME10
      break
    case colorSchemes.D3_20:
      scheme = SCHEME20
      break
    default:
      scheme = GOOGLE
      break
  }
  let c20 = d3.scaleOrdinal(scheme)
  range(0, length).forEach(c => colors.push(c20(c)))
  return colors
}

export const buildDataChartByLabelAndValue = (metaData, data, bins = []) => {
  let colX = findIndex(metaData.cols, { 'name': data.x })
  let colY = findIndex(metaData.cols, { 'name': data.y })
  let binnedCol = -1
  if (bins && bins.length) binnedCol = bins.findIndex(bin => bin === data.x)
  const mappedLabels = metaData.rows.map(r => r[colX])
  if (binnedCol === -1) {
    return {
      data: metaData.rows.map(r => r[colY]),
      labels: mappedLabels
    }
  }
  const sortedLabels = orderBy(mappedLabels, (cate) => {
    if (cate) {
      if (cate.max) {
        return cate.max
      } else if (cate.min) {
        return cate.min
      } else {
        return null
      }
    }
    return cate
  })
  return {
    data: metaData.rows.map(r => r[colY]),
    labels: sortedLabels.map(data => data && data.label ? data.label : data)
  }
}

export const parseDate = (data) => {
  const parsedDate = Date.parse(data)
  return isNaN(parsedDate) ? data : parsedDate
}

export const buildDataChartByXYZPoint = (metaData, data, bins = [], nameAxis = { x: 'name', y: 'y', z: 'z' }) => {
  if (data.xCategories) {
    const colX = findIndex(metaData.cols, { 'name': data.xCategories })
    let binnedCol = -1
    if (bins && bins.length) {
      binnedCol = bins.findIndex(bin => bin === data.xCategories)
    }
    if (binnedCol !== -1) {
      const uniqCategories = uniq(metaData.rows.map(r => r[colX]))
      const sortedCategories = orderBy(uniqCategories, (cate) => {
        if (cate) {
          if (cate.max) {
            return cate.max
          } else if (cate.min) {
            return cate.min
          } else {
            return null
          }
        }
        return cate
      })
      return uniq(sortedCategories.map(cate => cate && cate.label ? cate.label : cate))
    }
    return metaData.rows.map(r => r[colX])
  }
  if (data.series && data.series.length) {
    let maxCategories = []
    let maxObj = null
    let sortedMaxCategories = []
    if (bins && bins.length) {
      data.series.forEach(ser => {
        const yColumnAlias = ser.type !== TYPES.BUBBLE ? createBinColumnAlias(ser.data.y, `${ser.id}_bin`) : createBinColumnAlias(ser.data.y)
        const colY = findIndex(metaData.cols, { 'name': yColumnAlias })
        const uniqCategories = colY !== -1 ? uniq(metaData.rows.map(r => r[colY])) : []
        const maxItem = maxBy(uniqCategories, (item) => {
          return item.max || item.min || item
        })
        if (maxItem && (isEmpty(maxObj) ||
          (maxItem.max && maxObj.max && maxItem.max > maxObj.max) || (maxItem.min && maxObj.min && maxItem.min > maxObj.min))) {
          maxObj = { ...maxItem }
          maxCategories = [...uniqCategories]
        }
      })
      sortedMaxCategories = orderBy(maxCategories, (cate) => {
        if (cate.max) {
          return cate.max
        } else if (cate.min) {
          return cate.min
        } else {
          return null
        }
      })
    }
    return uniq(sortedMaxCategories.map(cate => cate && cate.label ? cate.label : cate))
  }
  if (data.yCategories) {
    const colY = findIndex(metaData.cols, { 'name': data.yCategories })
    let binnedCol = -1
    if (bins && bins.length) {
      binnedCol = bins.findIndex(bin => bin === data.yCategories)
    }
    const uniqCategories = uniq(metaData.rows.map(r => r[colY]))
    const sortedCategories = orderBy(uniqCategories, (cate) => {
      if (binnedCol !== -1 && cate) {
        if (cate.max) {
          return cate.max
        } else if (cate.min) {
          return cate.min
        } else {
          return null
        }
      }
      return cate
    })
    return binnedCol !== -1 ? uniq(sortedCategories.map(cate => cate && cate.label ? cate.label : cate)) : sortedCategories
  }
  let isZAxisExist = !!data.z
  let colX = findIndex(metaData.cols, { 'name': data.x })
  let colY = findIndex(metaData.cols, { 'name': data.y })
  let colZ = findIndex(metaData.cols, { 'name': data.z })
  const colXType = colX !== -1 ? metaData.cols[colX].type : null
  const isTemporal = DataTypeUtil.isTemporal(colXType)
  return metaData.rows.map(r => {
    if (isZAxisExist) {
      return {
        [nameAxis.x]: isObject(r[colX]) && r[colX].label ? r[colX].label : isTemporal ? parseDate(r[colX]) : r[colX],
        [nameAxis.y]: isObject(r[colY]) && r[colY].label ? r[colY].label : r[colY],
        [nameAxis.z]: r[colZ]
      }
    } else {
      return {
        [nameAxis.x]: isObject(r[colX]) && r[colX].label ? r[colX].label : isTemporal ? parseDate(r[colX]) : r[colX],
        [nameAxis.y]: isObject(r[colY]) && r[colY].label ? r[colY].label : r[colY],
        root_Data: {
          x: r[colX],
          y: r[colY]
        }
      }
    }
  })
}

export const buildDataChartByXYZPointForHC = (metaData, data, config, bins = [], nameAxis = {
  name: 'name',
  x: 'x',
  y: 'y',
  z: 'z'
}) => {
  let isZAxisExist = !!data.z
  let colX = findIndex(metaData.cols, { 'name': data.x })
  let colY = findIndex(metaData.cols, { 'name': data.y })
  let colZ = findIndex(metaData.cols, { 'name': data.z })
  const colXType = colX !== -1 ? metaData.cols[colX].type : null
  const isTemporal = DataTypeUtil.isTemporal(colXType)
  let binnedCol = -1
  if (bins && bins.length) binnedCol = bins.findIndex(bin => bin === data.x)
  const xCategories = get(config, 'xAxis.categories', [])
  if (xCategories && xCategories.length && binnedCol !== -1) {
    return metaData.rows.map(r => {
      if (isZAxisExist) {
        return {
          [nameAxis.name]: isObject(r[colX]) && r[colX].label ? r[colX].label : isTemporal ? parseDate(r[colX]) : r[colX],
          [nameAxis.x]: xCategories.indexOf(r[colX].label),
          [nameAxis.y]: r[colY],
          [nameAxis.z]: r[colZ]
        }
      } else {
        return {
          [nameAxis.name]: isObject(r[colX]) && r[colX].label ? r[colX].label : isTemporal ? parseDate(r[colX]) : r[colX],
          [nameAxis.x]: xCategories.indexOf(r[colX].label),
          [nameAxis.y]: r[colY],
          // for drill down only
          root_Data: {
            x: r[colX],
            y: r[colY]
          }
        }
      }
    })
  }
  return metaData.rows.map(r => {
    if (isZAxisExist) {
      return {
        [nameAxis.x]: isObject(r[colX]) && r[colX].label ? r[colX].label : isTemporal ? parseDate(r[colX]) : r[colX],
        [nameAxis.y]: r[colY],
        [nameAxis.z]: r[colZ]
      }
    } else {
      return {
        [nameAxis.x]: isObject(r[colX]) && r[colX].label ? r[colX].label : isTemporal ? parseDate(r[colX]) : r[colX],
        [nameAxis.y]: isObject(r[colY]) && r[colY].label ? r[colY].label : r[colY],
        root_Data: {
          x: r[colX],
          y: r[colY]
        }
      }
    }
  })
}

export const isEmptyData = (data) => {
  let empty = true
  if (!isEmpty(data)) {
    data.forEach(el => {
      if (!isEmpty(el.data)) {
        empty = false
        return empty
      }
    })
  }
  return empty
}

export const invertColor = (hex, bw) => {
  function padZero(str, len) {
    len = len || 2
    let zeros = new Array(len).join('0')
    return (zeros + str).slice(-len)
  }

  if (hex.indexOf('#') === 0) {
    hex = hex.slice(1)
  }
  // convert 3-digit hex to 6-digits.
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]
  }
  if (hex.length !== 6) {
    throw new Error('Invalid HEX color.')
  }
  let r = parseInt(hex.slice(0, 2), 16)
  let g = parseInt(hex.slice(2, 4), 16)
  let b = parseInt(hex.slice(4, 6), 16)
  if (bw) {
    return (r * 0.299 + g * 0.587 + b * 0.114) > 186
      ? '#000000'
      : '#FFFFFF'
  }
  // invert color components
  r = (255 - r).toString(16)
  g = (255 - g).toString(16)
  b = (255 - b).toString(16)
  // pad each with zeros and return
  return '#' + padZero(r) + padZero(g) + padZero(b)
}

/**
 * Find alias name in aggregations of grouping and replace into current data in series item
 * Will be called before call method buildDataChartByXYPoint
 * @param {Object} seriesItem - an item of Series
 * @param {Object} elementConfig - config of an element
 * */
export const mappingColumnNameToAliasNameWithGrouping = (seriesItem, elementConfig) => {
  let { library, grouping = { columns: [], aggregations: [] }, bins } = elementConfig
  let { id = '', data = { x: '', y: '', z: '' } } = seriesItem
  const chartType = get(elementConfig, 'charts[0].series[0].type', '')
  let dataX = data.x
  let dataY = data.y
  let dataZ = data.z
  if (!id) return data
  if (!grouping.aggregations.length) {
    if (!bins || !bins.length) return data
    // set alias to x
    let binX = bins.find(bin => bin.column.name === dataX)
    if (binX) {
      dataX = binX.alias
    }
    // only for scatter in chartjs
    if (library === 'chartjs' && chartType === TYPES.SCATTER) {
      const yBinned = createBinColumnAlias(dataY, `${id}_bin`)
      let binY = bins.find(bin => bin.alias === yBinned)
      if (binY) {
        dataY = binY.alias
      }
    }
    return {
      x: dataX,
      y: dataY,
      z: dataZ
    }
  }
  let aggregation = grouping.aggregations.find(aggr => aggr.alias.includes(id))
  if (aggregation) {
    if (chartType === TYPES.BUBBLE) dataZ = aggregation.alias
    else dataY = aggregation.alias
  }
  if (bins.length) {
    let binX = bins.find(bin => bin.column.name === dataX)
    if (binX) dataX = binX.alias
    let yBinned = ''
    if (library === 'chartjs' && chartType === TYPES.BUBBLE) {
      yBinned = createBinColumnAlias(dataY)
      let binY = bins.find(bin => bin.alias === yBinned)
      if (binY) dataY = binY.alias
    } else {
      yBinned = createBinColumnAlias(dataY, `${id}_bin`)
      let binY = bins.find(bin => bin.alias === yBinned)
      if (binY) dataY = binY.alias
    }
  }
  return { x: dataX, y: dataY, z: dataZ }
}

export const formatNumberWithSiPrefix = (value) => {
  if (isNaN(value)) {
    return value
  }
  if (value < 1000) {
    return value
  }
  return d3.format('s')(value)
}

export const getStyle = () => style
export const setStyle = (s) => {
  style = s
}

export const setColorGradient = (listColor) => listColor.reduce((colors, [color1, color2, direction = {}] = []) => {
  const defaultDirection = { x1: 0, y1: 0, x2: 0, y2: 1 }
  const color = {
    linearGradient: isObject(direction) ? {...defaultDirection, ...direction} : {...defaultDirection},
    stops: [[0, color1], [1, color2]]
  }
  return [...colors, color]
}, [])

export const getColorForSpecificItemSeries = (seriesItem) => {
  const color = get(seriesItem, 'options.color')
  const getColor = {
    hexColor: {
      apply: () => typeof color === 'string',
      value: () => color
    },
    gradientColor: {
      apply: () => isArray(color),
      value: () => setColorGradient([color])[0]
    }
  }
  const applyColorKey = Object.keys(getColor).find(key => getColor[key].apply())
  return applyColorKey ? getColor[applyColorKey].value() : null
}
