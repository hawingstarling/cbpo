import WidgetBaseMixins from '@/components/WidgetBaseMixins.js'
import { shallowMount, createLocalVue } from '@vue/test-utils'

describe('WidgetBaseMixins', () => {
  let wrapper
  const localVue = createLocalVue()
  beforeEach(() => {
    wrapper = shallowMount(WidgetBaseMixins, {
      localVue,
      propsData: {
        config: {
          total: 4
        }
      }
    })
  })
  xit('Check class WidgetBaseMixins', () => {
    WidgetBaseMixins.watch.configObj(1, 2)
  })
})
