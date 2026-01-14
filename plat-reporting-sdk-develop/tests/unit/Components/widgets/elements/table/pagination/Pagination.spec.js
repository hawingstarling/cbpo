import Pagination from '@/components/widgets/elements/table/pagination/Pagination.vue'
import PaginationPreviousNext from '@/components/widgets/elements/table/pagination/PaginationButtons.vue'
import { mount } from '@vue/test-utils'
import Vue from 'vue'

describe('Pagination.vue', () => {
  // setup
  let wrapper, wrapperChildren
  beforeEach(() => {
    wrapper = mount(Pagination, {
      propsData: {
        paginationConfig: {
          data: {
            cols: [
              {
                name: 'ASIN',
                type: 'string' // int, num, date, datetime, string, boolean
              }
            ],
            rows: [
              ['B007SPH3C8']
            ]
          },
          type: {},
          style: {},
          pagination: {
            currentPage: 1,
            id: 1,
            limit: 18,
            offset: 0,
            total: 6
          }
        }
      }
    })
  })
  // setup
  wrapperChildren = mount(PaginationPreviousNext, {
    propsData: {
      config: {
        data: {
          cols: [
            {
              name: 'ASIN',
              type: 'string' // int, num, date, datetime, string, boolean
            }
          ],
          rows: [
            ['B007SPH3C8']
          ]
        },
        type: {},
        style: {},
        pagination: {
          currentPage: 2,
          id: 1,
          limit: 18,
          offset: 0,
          total: 6
        }
      }
    }
  })
  it('test computed render pagination', () => {
    // execute
    wrapper.setData({config: { pagination: { id: -2 } }})
    // verify
    // expect(wrapper.vm.renderPagination).toEqual(wrapper.vm.routePagination.default)
  })
  it('test event bus handleClickToPage next', () => {
    // setup
    const config = {'currentPage': 1, 'id': 1, 'limit': 18, 'offset': 0, 'total': 6}
    // execute
    // verify
    // expect(wrapper.vm.config.pagination).toEqual(config)
    // execute
    wrapperChildren.findAll('[data-button="next"]').trigger('click')
  })
  it('test event bus handleClickToPage previous', () => {
    // setup
    wrapper.setData({config: { pagination: { currentPage: 2 } }})
    const config = {'currentPage': 2, 'id': 1, 'limit': 18, 'offset': 0, 'total': 6}
    // execute
    // verify
    // expect(wrapper.vm.config.pagination).toEqual(config)
    // execute
    wrapperChildren.findAll('[data-button="prev"]').trigger('click')
  })
  it('test event bus handleClickSpecificPage', () => {
    // setup
    const config = {'currentPage': 1, 'id': 1, 'limit': 18, 'offset': 0, 'total': 6}
    // execute
    // verify
    // expect(wrapper.vm.config.pagination).toEqual(config)
  })
})
