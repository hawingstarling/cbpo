import AbstractLib from '@/components/widgets/elements/chart/libs/AbstractLib.js'
import precond from 'precond'
describe('AbstractLib.js', () => {
  it('test method render', () => {
    let abs = new AbstractLib()
    abs.render(null, null, null)
  })
})
