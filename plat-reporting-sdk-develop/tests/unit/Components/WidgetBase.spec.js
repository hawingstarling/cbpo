import WidgetBase from '@/components/WidgetBase.vue'
import { shallowMount, createLocalVue } from '@vue/test-utils'

describe('WidgetBase', () => {
  // setup
  let wrapper
  const localVue = createLocalVue()
  beforeEach(() => {
    wrapper = shallowMount(WidgetBase, {
      localVue
    })
  })
  it('test WidgetBase', function () {
    // excute
    wrapper.vm.widgetInit()
  })
})
