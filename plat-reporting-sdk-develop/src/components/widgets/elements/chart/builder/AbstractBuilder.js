import $ from 'jquery'
import { makeDOMId } from '@/components/widgets/elements/chart/types/ChartTypes'
import { CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'

export class AbstractBuilder {
  highcharts = null

  constructor(highchartsInstance) {
    this.highcharts = highchartsInstance
  }

  buildAndRender(domId, dataSource, chartConfig, options) {
    console.error('Please override this abstract method ')
  }

  getBaseConfig() {
    return {}
  }

  render(id, config) {
    const prefixId = makeDOMId(CHART_LIBRARY.HIGH_CHART, id)
    const chartSetsNode = $(`#${prefixId} .chartSets`)[0]
    if (chartSetsNode) {
      window[prefixId] = this.highcharts.mapChart(chartSetsNode, config)
      /* Some charts doesn't fit the content when first load
       * this method make sure everything will work well after it loaded
       */
      setTimeout(() => {
        window[prefixId].reflow()
      }, 500)
    }
  }

  resize(id) {
    const prefixId = makeDOMId(CHART_LIBRARY.HIGH_CHART, id)
    const chartSetsNode = $(`#${prefixId} .chartSets`)[0]
    if (window[prefixId] && chartSetsNode) {
      try {
        setTimeout(() => {
          console.log('setFlow heree')
          window[prefixId].setSize(chartSetsNode.clientWidth, chartSetsNode.clientHeight)
          window[prefixId].reflow()
        }, 0)
      } catch {
        console.log('There is no setSize function')
      }
    }
  }
}
