import { BarChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/BarChartBuilder'
import { getColorForSpecificItemSeries, getColorSchemes, getStyle } from '@/utils/chartUtil'
import defaultsDeep from 'lodash/defaultsDeep'
import get from 'lodash/get'

export class LineChartBuilder extends BarChartBuilder {
  __buildSeries(config, data, { axis, chartConfig }) {
    config.series = data.map((item, index) => {
      const seriesItem = chartConfig.charts[0].series[index]
      // step size for line chart
      let step = get(chartConfig, `charts[0].series[${index}].options.step`)
      if (!['left', 'right', 'center'].includes(step)) step = undefined

      return {
        yAxis: 0,
        data: item,
        name: seriesItem.name || 'Series ' + (index + 1),
        step,
        dashStyle: get(seriesItem, 'options.dashStyle', 'solid'),
        color: getColorForSpecificItemSeries(seriesItem)
      }
    })
  }

  __buildPlotOptions(chartConfig) {
    const plotOptions = super.__buildPlotOptions(chartConfig)
    plotOptions.dashStyle = get(chartConfig, 'charts[0].options.dashStyle', 'solid')
    return plotOptions
  }

  __buildConfig(config, { chartConfig, legend, axis, plotOptions, tooltip }) {
    const color = getStyle()

    defaultsDeep(config, {
      chart: {
        type: 'spline',
        backgroundColor: color.mainColor
      },
      colors: getColorSchemes(chartConfig.color_scheme),
      plotOptions,
      legend,
      tooltip,
      xAxis: axis.xAxis,
      yAxis: axis.yAxis
    })
  }
}
