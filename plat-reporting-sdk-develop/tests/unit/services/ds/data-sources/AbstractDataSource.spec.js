import AbstractDataSource from '@/services/ds/data-sources/AbstractDataSource.js'

describe('AbstractDataSource.js', () => {
  it('check class AbstractDataSource', () => {
    // setup
    let abstractDataSource = new AbstractDataSource()
    // excute
    abstractDataSource.query()
    abstractDataSource.total()
  })
})
