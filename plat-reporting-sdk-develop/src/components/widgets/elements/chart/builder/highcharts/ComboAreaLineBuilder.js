// import { LineChartBuilder } from '@/components/widgets/elements/chart/builder/highcharts/LineChartBuilder'
import get from 'lodash/get'
import { HC_TYPES } from '@/components/widgets/elements/chart/ChartConfig'
import { ComboBarLineBuilder } from '@/components/widgets/elements/chart/builder/highcharts/ComboBarLineBuilder'
import { getColorForSpecificItemSeries } from '@/utils/chartUtil'

export class ComboAreaLineBuilder extends ComboBarLineBuilder {
  __buildSeries(config, data, { axis, chartConfig }) {
    config.series = data.map((item, index) => {
      const seriesItem = chartConfig.charts[0].series[index]
      let step = get(seriesItem, `options.step`)
      let type = seriesItem.type
      const fillOpacity = type === 'area' ? get(seriesItem, 'options.opacity', 0.25) : null
      if (type === 'area') type = HC_TYPES.AREASPLINE
      if (type === 'line' && !step) type = HC_TYPES.SPLINE

      const yAxisIndex = axis.yAxis.findIndex(axis => axis.dataId === seriesItem.axis.y)

      return {
        data: item,
        yAxis: yAxisIndex !== -1 ? yAxisIndex : index,
        name: seriesItem.name || ('Series ' + index),
        type,
        step: ['left', 'right', 'center'].includes(step) ? step : undefined,
        color: getColorForSpecificItemSeries(seriesItem),
        fillOpacity,
        dashStyle: get(seriesItem, `options.dashStyle`, 'solid')
      }
    })
  }
}
