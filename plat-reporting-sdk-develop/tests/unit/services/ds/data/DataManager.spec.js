import DataManager from '@/services/ds/data/DataManager.js'

describe('DataManager.js', () => {
  it('test DataManager', function () {
    // setup
    let dataManager = new DataManager()
    // excute
    dataManager.createMetaRows([1], 2)
  })
  it('test filterData', function () {
    // setup
    let dataManager = new DataManager()
    // excute
    // dataManager.filterData('')
  })
  it('test getColumnByName', function () {
    // setup
    let dataManager = new DataManager()
    // excute
    dataManager.getColumnByName((value) => {
      return '&lt;a href="' + value + '" target="_blank"&gt;Link&lt;/a&gt;'
    })
  })
  it('test hasChild', function () {
    // setup
    let dataManager = new DataManager()
    dataManager.metaRows = [{parent: 1}]
    // excute
    dataManager.hasChild(1)
  })
})
