<template>
  <div class="cbpo-pagination-input">
    <button
      v-show="config.buttons && config.buttons.first.visibility"
      :style="config.buttons && config.buttons.first.style"
      class="cbpo-btn btn-icon mr-1" title="First"
      :class="{'btn-pagination-default': config.current !== 1}"
      @click="goToPage(1)"
      :disabled="config.current <= 1">
      &laquo;
    </button>
    <button
      v-show="config.buttons && config.buttons.prev.visibility"
      :style="config.buttons && config.buttons.prev.style"
      class="cbpo-btn btn-icon" title="Previous"
      :class="{'btn-pagination-default': config.current !== 1}"
      @click="linkPage(-1)"
      :disabled="config.current <= 1">
      &#8249;
    </button>
    <p class="cbpo-pagination-page-current">Page</p>
    <input type="number" class="cbpo-pagination-input__search" v-model="config.current"
           @keypress="isValidPage($event)"
           :max="config.total ? config.total : 0" min="1" />
    <p class="cbpo-pagination-page-current"> of {{config.total}}</p>
    <button class="cbpo-btn btn-icon mr-1" title="Next"
            v-show="config.buttons && config.buttons.next.visibility"
            :style="config.buttons && config.buttons.next.style"
            :class="{'btn-pagination-default': config.current !== config.total}"
            @click="linkPage(1)"
            :disabled="config.current >= config.total">
      &#8250;
    </button>
    <button class="cbpo-btn btn-icon" title="Last"
            v-show="config.buttons && config.buttons.last.visibility"
            :style="config.buttons && config.buttons.last.style"
            :class="{'btn-pagination-default': config.current !== config.total}"
            @click="goToPage(config.total)"
            :disabled="config.current >= config.total">
      &raquo;
    </button>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import PaginationMixins from '@/components/widgets/elements/table/pagination/PaginationMixins'
import WidgetBase from '@/components/WidgetBase'

export default {
  name: 'PaginationInput',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins,
    PaginationMixins
  ],
  methods: {
    isValidPage: function (e) {
      e = (e) || window.event
      let charCode = (e.which) ? e.which : e.keyCode
      if (charCode >= 48 && charCode <= 57) {
        let inputs = this.config.current + e.key
        if (parseInt(inputs, 10) !== 0) {
          if (inputs <= this.config.total) {
            return true
          }
          this.config.current = this.config.total
        }
      }
      e.preventDefault()
    }
  },
  watch: {
    'config.current': {
      handler: function (newVal, oldVal) {
        if (newVal && newVal > 0 && newVal <= this.config.total) {
          this.config.current = newVal
        }
      },
      deep: true
    }
  }
}
</script>
<style lang="scss" scoped>
  @import './PaginationInput.scss';
</style>
