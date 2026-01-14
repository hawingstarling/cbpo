import findIndex from 'lodash/findIndex'
import isEmpty from 'lodash/isEmpty'
import get from 'lodash/get'
import cloneDeep from 'lodash/cloneDeep'
import { defaultFormatConfig } from '@/components/widgets/elements/table/TableConfig'
import FormatConfigBuilder from '@/components/formatBuilder/FormatConfigBuilder'

export default {
  data() {
    return {
      seriesItem: null,
      formatSetting: null,
      axis: {
        index: -1,
        item: null
      },
      elementInstance: null
    }
  },
  components: {
    'format-config-builder': FormatConfigBuilder
  },
  props: {
    element: Object,
    selectedElement: Object,
    config: Object
  },
  methods: {
    /**
     * Find axis index
     * Will be called by VisualizationBuilder, when user click Save button
     * **/
    getConfig() {
      if (!get(this.axis, 'item.format.type', '')) {
        this.axis.item.format = null
      }
      this.elementInstance.config.charts[0].axis[this.config.axisType][this.axis.index] = this.axis.item
      return cloneDeep({index: this.config.index, item: this.item, element: this.elementInstance, axisIndex: this.axis.index})
    },
    /**
     * Find axis index
     * Will be called on created hook
     * @param {Number} itemId - Id of an item in series
     * **/
    findAxisIndex(itemId) {
      return findIndex(this.elementInstance.config.charts[0].axis.y, axis => axis.id.includes(itemId))
    }
  },
  created() {
    this.seriesItem = cloneDeep(this.config.item)
    this.elementInstance = cloneDeep(this.element)
    this.axis.index = this.findAxisIndex(this.config.item.id)
    this.axis.item = cloneDeep(this.element.config.charts[0].axis[this.config.axisType][this.axis.index])
    if (isEmpty(this.axis.item.format)) {
      this.axis.item.format = cloneDeep(defaultFormatConfig)
    }
  }
}
