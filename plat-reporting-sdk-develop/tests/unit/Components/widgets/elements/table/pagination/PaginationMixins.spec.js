import PaginationMixins from '@/components/widgets/elements/table/pagination/PaginationMixins.js'
import { shallowMount, createLocalVue } from '@vue/test-utils'

describe('PaginationMixins', () => {
  let wrapper
  const localVue = createLocalVue()
  beforeEach(() => {
    wrapper = shallowMount(PaginationMixins, {
      localVue,
      propsData: {
        config: {
          total: 4
        }
      }
    })
  })
  it('check methods linkpage', () => {
    // WidgetBaseMixins.methods.linkPage()
  })
  it('check methods goToPage', () => {
    wrapper.vm.goToPage(2)
  })
})
