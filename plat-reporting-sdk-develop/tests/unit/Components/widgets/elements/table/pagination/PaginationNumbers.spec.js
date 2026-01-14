import PaginationNumbers from '@/components/widgets/elements/table/pagination/PaginationNumbers.vue'
import { shallowMount, createLocalVue } from '@vue/test-utils'

describe('PaginationSizing.vue', () => {
  // setup
  let wrapper
  const localVue = createLocalVue()
  beforeEach(() => {
    wrapper = shallowMount(PaginationNumbers, {
      localVue,
      propsData: {
        config: {
          current: 1,
          total: 3,
          numbers: {
            afterCurrent: 2,
            beforeCurrent: 2
          }
        }
      }
    })
  })
  it('test computed getPageRange case1', function () {
    // setup
    wrapper.setData({
      config: {
        current: 1,
        total: 4,
        numbers: {
          afterCurrent: 2,
          beforeCurrent: 2
        }
      }
    })
    // verify
    expect(wrapper.vm.getPageRange).toEqual([1, 2, 3, 4])
  })
  it('test computed getPageRange case2', function () {
    // setup
    wrapper.setData({
      config: {
        current: 4,
        total: 4,
        numbers: {
          afterCurrent: 2,
          beforeCurrent: 2
        }
      }
    })
    // verify
    expect(wrapper.vm.getPageRange).toEqual([1, 2, 3, 4])
  })
  it('test computed getPageRange case3', function () {
    // setup
    wrapper.setData({
      config: {
        current: 2,
        total: 10,
        numbers: {
          afterCurrent: 2,
          beforeCurrent: 2
        }
      }
    })
    // verify
    expect(wrapper.vm.getPageRange).toEqual([1, 2, 3, 4, 5])
  })
  it('test computed getPageRange case4', function () {
    // setup
    wrapper.setData({
      config: {
        current: 5,
        total: 10,
        numbers: {
          afterCurrent: 2,
          beforeCurrent: 2
        }
      }
    })
    // verify
    expect(wrapper.vm.getPageRange).toEqual([3, 4, 5, 6, 7])
  })

  it('test computed getPageRange case3', function () {
    // setup
    wrapper.setData({
      config: {
        current: 10,
        total: 10,
        numbers: {
          afterCurrent: 2,
          beforeCurrent: 2
        }
      }
    })
    // verify
    expect(wrapper.vm.getPageRange).toEqual([6, 7, 8, 9, 10])
  })
})
