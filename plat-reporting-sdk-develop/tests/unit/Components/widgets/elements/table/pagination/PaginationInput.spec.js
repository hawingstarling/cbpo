import PaginationInput from '@/components/widgets/elements/table/pagination/PaginationInput.vue'
import { shallowMount, createLocalVue } from '@vue/test-utils'

describe('PaginationSizing.vue', () => {
  // setup
  let wrapper
  const localVue = createLocalVue()
  beforeEach(() => {
    wrapper = shallowMount(PaginationInput, {
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
  it('test watch data config.current', function () {
    // excute
    wrapper.setData({config: { total: 5 }})
    wrapper.setData({config: { current: 2 }})
    // verify
    expect(wrapper.vm.config.current).toBe(2)
  })
  it('test method isValidPage case 1', function () {
    // excute
    wrapper.setData({config: { total: 5 }})
    wrapper.setData({config: { current: 2 }})

    let event = {
      which: 50,
      key: 2,
      preventDefault: function() {}
    }
    // verify
    expect(wrapper.vm.isValidPage(event))
  })
  it('test method isValidPage case 1', function () {
    // excute
    wrapper.setData({config: { total: 5 }})
    wrapper.setData({config: { current: 2 }})

    let event = {
      which: 50,
      key: 2,
      preventDefault: function() {}
    }
    // verify
    expect(wrapper.vm.isValidPage(event))
  })
  it('test method isValidPage case 2', function () {
    // excute
    wrapper.setData({config: { total: 3 }})
    wrapper.setData({config: { current: 2 }})

    let event = {
      which: 50,
      key: 2,
      preventDefault: function() {}
    }
    // verify
    expect(wrapper.vm.isValidPage(event))
  })
})
