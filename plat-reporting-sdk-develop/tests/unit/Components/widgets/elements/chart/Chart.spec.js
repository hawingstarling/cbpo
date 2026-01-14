// import Chart from '@/components/widgets/elements/chart/Chart'
// import {mount} from '@vue/test-utils'
// import $ from 'jquery'

// window.jQuery = $
// require('jquery-ui/ui/version')
// require('jquery-ui/ui/plugin')
// require('jquery-ui/ui/widget')
// require('jquery-ui/ui/widgets/mouse')
// require('jquery-ui/ui/widgets/resizable')

// describe('Chart.vue', () => {
//   // setup
//   let wrapper
//   // beforeAll(() => {
//   //   // mocking jQuery $()
//   //   global.window.$ = jest.fn(() => { return {on: jest.fn()} })
//   // })
//   beforeEach(() => {
//     global.window.$ = jest.fn(() => {
//       return {on: jest.fn()}
//     })
//     wrapper = mount(Chart, {
//       propsData: {
//         config: {
//           library: 'chartjs',
//           columns: {},
//           style: {},
//           widget: {
//             title: {
//               enabled: true,
//               text: 'Chart widget' // or null
//             }
//           },
//           charts: [{
//             axis: {
//               x: [],
//               y: []
//             },
//             options: {
//               column: {
//                 stacking: 'normal' // normal | percentage
//               }
//             },
//             series: [{
//               type: 'pie',
//               data: {
//                 x: 'column1',
//                 y: 'column2'
//               }
//             }]
//           }]
//         }
//       }
//     })
//   })
//   it('test watching variable getConfig', () => {
//     // setup
//     const data = {
//       library: 'chartjs',
//       data: {
//         cols: [{
//           name: 'column1',
//           type: 'int' // int, num, date, datetime, string, boolean
//         }, {
//           name: 'column2',
//           type: 'string' // int, num, date, datetime, string, boolean
//         }],
//         rows: [
//           [2019, 50]
//         ]
//       },
//       chart: [{
//         axis: {
//           x: [],
//           y: []
//         },
//         options: {
//           column: {
//             stacking: 'normal' // normal | percentage
//           }
//         },
//         series: [{
//           type: 'pie',
//           data: {
//             x: 'column1',
//             y: 'column2'
//           }
//         }]
//       }]
//     }
//     // execute
//     wrapper.setData({getConfig: data})
//     // verify
//     // expect(wrapper.vm.getConfig).toEqual(data)
//     // setuo
//     const data1 = data
//     // execute
//     wrapper.setProps({data: data1})
//     // verify
//     // expect(wrapper.vm.data).toEqual(undefined)
//   })
//   it('test method render', () => {
//     wrapper.vm.render()
//   })
// })
describe('Chart.vue', () => {
  it("should invalid token", async () => {
    // Execute
    return Promise.resolve();
  });
})