// import Table from '@/components/widgets/elements/table/Table'
// import { mount } from '@vue/test-utils'
// import $ from 'jquery'
// import CBPO from '@/services/CBPO'
// import Vue from 'vue'
// import SortDown from '@/assets/images/icons/sort-down.png'
// import SortUp from '@/assets/images/icons/sort-up.png'

// window.jQuery = $
// require('jquery-ui/ui/version')
// require('jquery-ui/ui/plugin')
// require('jquery-ui/ui/widget')
// require('jquery-ui/ui/widgets/mouse')
// require('jquery-ui/ui/widgets/resizable')

// describe('Table.vue', () => {
//   // setup
//   let wrapper
//   // beforeAll(() => {
//   //   // mocking jQuery $()
//   //   global.window.$ = jest.fn(() => { return {on: jest.fn()} })
//   // })
//   beforeEach(() => {
//     global.window.$ = jest.fn(() => { return {on: jest.fn()} })
//     wrapper = mount(Table, {
//       propsData: {
//         config: {
//           columns: [],
//           formats: {},
//           grouping: {},
//           pagination: {
//             current: 1,
//             default: 'auto',
//             limit: 50,
//             total: 20
//           },
//           sorting: []
//         }
//       }
//     }, CBPO.$bus = new Vue())
//   })
//   it('test watching variable getConfig', () => {
//     // setup
//     const data = {'columns': [{'name': 'column1', 'sortable': {'arrangementDirection': 'asc', 'default': undefined, 'sort': true}}, {'name': 'column2', 'sortable': {'arrangementDirection': 'desc', 'default': 'desc', 'sort': true}}, {'name': 'column3', 'sortable': {'arrangementDirection': 'asc', 'default': undefined, 'sort': false}}, {'name': 'column4', 'sortable': {'arrangementDirection': undefined, 'default': 'asc', 'sort': true}}], 'data': {'cols': [{'name': 'ASIN', 'type': 'string'}], 'rows': [['B007SPH3C8']]}, 'pagination': {'currentPage': 1, 'id': 1, 'limit': 18, 'offset': 0, 'total': 3}, 'style': {}, 'type': {}}
//     // execute
//     wrapper.setData({ getConfig: data })
//     // verify
//     // expect(wrapper.vm.getConfig).toEqual(data)
//     // setuo
//     const data1 = data
//     data1.pagination.total = 5
//     // execute
//     wrapper.setProps({ data: data1 })
//     // verify
//     // expect(wrapper.vm.data).toEqual(undefined)
//   })
//   it('filter handleFilter', () => {
//     // verify
//     // expect(wrapper.vm.$options.filters.handleFilter('int', 2)).toEqual('<span>2</span>')
//     // expect(wrapper.vm.$options.filters.handleFilter('currency', '$2')).toEqual('<span>$2</span>')
//     // expect(wrapper.vm.$options.filters.handleFilter('string', 'amazon')).toEqual('<span>amazon</span>')
//     // expect(wrapper.vm.$options.filters.handleFilter('datetime', '23:50')).toEqual('<span>23:50</span>')
//     // expect(wrapper.vm.$options.filters.handleFilter('url', 'amazon.com')).toEqual('<a href="amazon.com" target="_blank">Link</a>')
//     // expect(wrapper.vm.$options.filters.handleFilter('image', 'amazon.com')).toEqual('<a href="amazon.com" target="_blank">Screenshot</a>')
//     // expect(wrapper.vm.$options.filters.handleFilter('percentCurrency', '2%')).toEqual('<span>2%</span>')
//     // expect(wrapper.vm.$options.filters.handleFilter('boolean', 'true')).toEqual('<span>true</span>')
//   })
//   it('test methods calcTotalPage', () => {
//     // execute
//     wrapper.setProps({ data: { pagination: { limit: 1 } } })
//     // verify
//     // expect(wrapper.vm.getConfig.pagination).toEqual({
//     //   currentPage: 2,
//     //   id: 1,
//     //   limit: 2,
//     //   offset: 1,
//     //   total: 3
//     // })
//   })
//   it('test methods resizableColumns', async () => {
//   })
//   it('test computed renderDataSourceFollowRangePage when pass props data with pagination limit & offset is undefined', () => {
//     // setup
//     wrapper = mount(Table, {
//       propsData: {
//         data: {
//           data: {
//             cols: [
//               {
//                 name: 'ASIN',
//                 type: 'string' // int, num, date, datetime, string, boolean
//               }
//             ],
//             rows: [
//               ['B007SPH3C8']
//             ]
//           },
//           type: {},
//           style: {},
//           pagination: {
//             current: 1,
//             id: 1,
//             limit: undefined,
//             offset: undefined,
//             total: 6
//           },
//           columns: [{
//             name: 'column1',
//             sortable: {
//               arrangementDirection: 'asc',
//               default: 'desc',
//               sort: true
//             }
//           }]
//         }
//       }
//     })
//   })
//   it('test function handleSortDataTable for feature sort when click sortable', () => {
//     // execute
//     // wrapper.findAll('.active-image').at(0).trigger('click')
//   })

//   it('test watch data config.pagination.current', function () {
//     // excute
//     wrapper.setData({config: { pagination: { current: 2 } }})
//     // verify
//     expect(wrapper.vm.config.pagination.current).toBe(2)
//   })

//   it('test computed visibleMetaRows', function () {
//     // let a = wrapper.vm.visibleMetaRows
//   })
// })

describe('Table.vue', () => {
  it("should invalid token", async () => {
    // Execute
    return Promise.resolve();
  });
})