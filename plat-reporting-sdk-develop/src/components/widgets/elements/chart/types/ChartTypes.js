import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { v4 as uuid } from 'uuid'

export const INDEX_CHART = {
  pie: 0,
  bar_line: 1,
  scatter: 2,
  area: 3,
  bubble: 4,
  bar: 1,
  line: 1
}

export const TYPES_SUPPORTED_CHARTJS = [
  TYPES.PIE,
  TYPES.BAR,
  TYPES.LINE,
  TYPES.SCATTER,
  TYPES.AREA,
  TYPES.BUBBLE
]

export const TYPES_SUPPORTED_HC = [
  TYPES.PIE,
  TYPES.BAR,
  TYPES.LINE,
  TYPES.SCATTER,
  TYPES.AREA,
  TYPES.BUBBLE,
  TYPES.BULLETGAUGE,
  TYPES.SOLIDGAUGE,
  TYPES.HEAT_MAP
]

export const DEFAULT_CHART_CONFIG_CHARTJS = {
  margin: {},
  axis: {
    x: [],
    y: []
  },
  options: {
    legend: {
      enabled: true,
      position: 'bottom',
      widthPercent: 40,
      isHorizontal: false
    }
  },
  series: []
}

export const DEFAULT_CHART_CONFIG_HEAT_MAP = () => {
  const id = uuid()
  return {
    axis: {
      x: [
        {
          id: `x_${id}`,
          format: null
        }
      ],
      y: [
        {
          id: `y_${id}`,
          axisLabelColor: null,
          axisGridColor: null,
          ticks: {
            maxTicksLimit: 5,
            minColor: '#F1EEF6',
            maxColor: '#500007',
            format: null
          }
        }
      ]
    },
    options: {
      mapNavigation: {
        enabled: true
      },
      labelDrillUpButton: null,
      gridBorderColor: null,
      dataLabelColor: null,
      legend: {
        enabled: true,
        isHorizontal: true,
        position: 'right'
      }
    },
    series: [{
      id,
      type: TYPES.HEAT_MAP,
      axis: {
        x: `x_${id}`,
        y: `y_${id}`
      },
      data: {
        x: '',
        y: '',
        name: '',
        country: {
          geo: 'us',
          geoDetail: 'us'
        }
      }
    }]
  }
}

export const DEFAULT_CONFIG_Y_AXIS = {
  type: 'linear',
  format: null,
  position: 'left',
  stack: false,
  ticks: {
    beginAtZero: true,
    stepSize: '',
    maxTicksLimit: 5,
    // fontColor: '#666',
    fontSize: 11,
    fontStyle: 'bold'
  },
  scaleLabel: {
    display: false,
    labelString: ''
  }
}

export const DEFAULT_CONFIG_X_AXIS = {
  type: 'category',
  display: true,
  format: null,
  scaleLabel: {
    display: false,
    labelString: ''
  },
  ticks: {
    // fontColor: '#666',
    fontSize: 11,
    fontStyle: 'bold'
  }
}

export const DEFAULT_SERIES_CONFIG = {
  type: null,
  name: null,
  axis: {
    x: null,
    y: null
  },
  options: {
  },
  data: {
    x: null,
    y: null
  }
}

export const getTypesSupported = (library) => {
  let type = []
  switch (library) {
    case CHART_LIBRARY.CHART_JS:
      type = TYPES_SUPPORTED_CHARTJS
      break
    case CHART_LIBRARY.HIGH_CHART:
      type = TYPES_SUPPORTED_HC
      break
  }
  return type
}

export const getDefaultOptionsConfigFromChartTypeChartJs = (type) => {
  switch (type) {
    case TYPES.PIE: {
      return {
        pie: {
          type: 'pie'
        },
        borderWidth: 0
      }
    }
    case TYPES.BUBBLE: {
      return {
        radius: {
          scale: 24
        }
      }
    }
    case TYPES.AREA: {
      return {
        stacking: 'normal',
        spanGaps: false,
        elements: {
          line: {
            tension: 0.4
          }
        },
        plugin: {
          filter: {
            propagate: false
          }
        }
      }
    }
    case TYPES.BAR: {
      return {
        stacking: '',
        isHorizontal: false,
        pointPadding: 0,
        borderColor: null
      }
    }
    case TYPES.LINE: {
      return {
        step: 'right'
      }
    }
    default: {
      return {}
    }
  }
}

export const makeDOMId = (type, id) => {
  switch (type) {
    case CHART_LIBRARY.CHART_JS: return 'chartjs_' + id
    case CHART_LIBRARY.HIGH_CHART: return 'hc_' + id
    default: return id
  }
}

export const extractConfigId = (type, domId) => {
  let parts = []
  switch (type) {
    case CHART_LIBRARY.CHART_JS:
      parts = domId.split('chartjs_')
      break
    case CHART_LIBRARY.HIGH_CHART:
      parts = domId.split('hc_')
      break
  }
  return parts[1] || domId
}
