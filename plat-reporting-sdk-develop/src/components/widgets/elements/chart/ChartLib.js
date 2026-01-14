import CBPOLib from './libs/CBPOLib'
import ChartjsLib from './libs/ChartjsLib'
import HighchartsLib from './libs/HighchartsLib'
// eslint-disable-next-line no-unused-vars
import AbstractLib from './libs/AbstractLib'
import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'

/**
 * @return {AbstractLib}
 */
export default class ChartLib {
  static getInstance (lib) {
    if (lib === 'cbpo' || !lib) {
      return new CBPOLib()
    } else if (lib === CHART_LIBRARY.CHART_JS) {
      return new ChartjsLib()
    } else if (lib === CHART_LIBRARY.HIGH_CHART) {
      return new HighchartsLib()
    } else {
      throw new Error(`Chart lib ${lib} has not been supported`)
    }
  }
  static buildChart
}
