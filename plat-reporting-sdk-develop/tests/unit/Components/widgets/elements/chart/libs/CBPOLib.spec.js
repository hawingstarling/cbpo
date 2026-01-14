import CBPOLib from '@/components/widgets/elements/chart/libs/CBPOLib.js'
import precond from 'precond'
describe('CBPOLib.js', () => {
  it('test method render', () => {
    let cbpo = new CBPOLib()
    cbpo.render(null, null, null)
  })
})
