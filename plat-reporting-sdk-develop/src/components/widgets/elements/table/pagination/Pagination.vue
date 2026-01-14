<template>
  <div class="cbpo-pagination" style="{flex: 1}">
    <component :is="component" :configObj.sync="config"></component>
  </div>
</template>

<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import { makeDefaultPaginationConfig, getSuitablePagination } from './PaginationConfig'

export default {
  name: 'Pagination',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins
  ],
  data () {
    return {}
  },
  computed: {
    component: function () {
      return getSuitablePagination(this.config)
    }
  },
  methods: {
    widgetConfig (config) {
      makeDefaultPaginationConfig(config)
    },
    widgetInit () {
      console.log('Pagination::init')
    }
  },
  watch: {
    'config.current'(val) {
      this.$emit('pageChange')
    }
  }
}
</script>
