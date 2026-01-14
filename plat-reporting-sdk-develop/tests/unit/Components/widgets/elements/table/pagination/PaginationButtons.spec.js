import PaginationPreviousNext from '@/components/widgets/elements/table/pagination/PaginationButtons.vue'
import { mount } from '@vue/test-utils'

describe('PaginationPreviousNext.vue', () => {
  // setup
  let wrapper
  beforeEach(() => {
    wrapper = mount(PaginationPreviousNext, {
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
  })
  it('test methods handleClickToPage next', function () {
    // execute
    wrapper.findAll('[data-button="next"]').trigger('click')
    // verify
    // expect(wrapper.vm.pagination.pagination.currentPage).toEqual(3)
  })
  it('test methods handleClickToPage previous', function () {
    // execute
    wrapper.findAll('[data-button="prev"]').trigger('click')
    // verify
    // expect(wrapper.vm.pagination.pagination.currentPage).toEqual(1)
  })
})
