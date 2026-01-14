import { LineChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/LineChartBuilder'
import { getColorForSpecificItemSeries, getStyle } from '@/utils/chartUtil'
import defaultsDeep from 'lodash/defaultsDeep'
import get from 'lodash/get'

export class AreaChartBuilder extends LineChartBuilder {
  __buildSeries(config, data, chartConfig) {
    config.series = data.map((item, index) => {
      const seriesItem = chartConfig.charts[0].series[index]
      // step size for line chart
      let step = get(seriesItem, 'options.step')
      if (!['left', 'right', 'center'].includes(step)) step = undefined

      return {
        yAxis: 0,
        data: item,
        name: get(seriesItem, `.name`, 'Series ' + (index + 1)),
        step,
        fillOpacity: get(seriesItem, `options.opacity`),
        dashStyle: get(seriesItem, `options.dashStyle`, 'solid'),
        color: getColorForSpecificItemSeries(seriesItem)
      }
    })
  }

  __buildConfig(config, { chartConfig, legend, axis, plotOptions, tooltip, colors }) {
    const color = getStyle()

    defaultsDeep(config, {
      chart: {
        type: 'areaspline',
        backgroundColor: color.mainColor
      },
      colors,
      plotOptions,
      tooltip,
      legend,
      xAxis: axis.xAxis,
      yAxis: axis.yAxis
    })
  }
}
