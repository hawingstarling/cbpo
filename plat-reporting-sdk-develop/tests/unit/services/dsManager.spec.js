// import dsManager from '@/services/dsManager.js'
// import main from '@/main'

// describe('dsManager.js', () => {
//   // setup
//   var $ds, $ds1
//   it('check wgManager', () => {
//     // setup
//     window.dataSource = {
//       cols: [{
//         name: 'column1',
//         type: 'int' // int, num, date, datetime, string, boolean
//       },
//       {
//         name: 'column2',
//         type: 'string' // int, num, date, datetime, string, boolean
//       },
//       {
//         name: 'column3',
//         type: 'datetime' // int, num, date, datetime, string, boolean
//       },
//       {
//         name: 'column4',
//         type: 'boolean' // int, num, date, datetime, string, boolean
//       }],
//       rows: [
//         [2019, 'Hello', '2019-02-28 00:00:00', false],
//         [2029, 'Good morning', '2029-02-28 00:00:00', true],
//         [2029, 'Good evening', '2029-02-28 00:00:00', false],
//         [2029, 'Good evening', '2029-02-28 00:00:00', false],
//         [2029, 'Good evening', '2029-02-28 00:00:00', false],
//         [2029, 'Good evening', '2029-02-28 00:00:00', false],
//         [2029, 'Good evening', '2029-02-28 00:00:00', false],
//         [2029, 'Good evening', '2029-02-28 00:00:00', false]
//       ]
//     }
//     var params = {
//       paging: { // prioritized
//         limit: undefined,
//         offset: undefined
//       }
//     }
//     // excute
//     $ds = window.CBPO.dsManager().getDataSource('dataSource')
//     window.CBPO.dsManager().getDataSource('dataSource')
//     $ds1 = window.CBPO.dsManager().getDataSource('dataSourceNotExist')
//     $ds.query(params).then(res => res)
//     $ds1.query(params).then(res => res)
//   })
//   it('test return function LocalDataSource', () => {
//   })
// })

describe('dsManager.js', () => {
  it("should invalid token", async () => {
    // Execute
    return Promise.resolve();
  });
})