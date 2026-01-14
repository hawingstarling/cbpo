import ChartLib from '@/components/widgets/elements/chart/ChartLib.js'

describe('ChartLib.js', () => {
  it('check class ChartjsLib', () => {
    ChartLib.getInstance('chartjs')
  })
  it('check class CBPOLib', () => {
    ChartLib.getInstance('cbpo')
  })
})
