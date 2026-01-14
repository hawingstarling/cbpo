<template>
  <div class="cbpo-pagination-sizing align-button">
    <button
      v-show="config.buttons && config.buttons.first.visibility"
      :style="config.buttons && config.buttons.first.style"
      class="cbpo-btn"
      data-button="first"
      title="First"
      :class="{'btn-pagination-default': config.current !== 1}"
      @click="goToPage(1)"
      :disabled="config.current <= 1"
    >{{config.buttons && config.buttons.first.label}}</button>
    <button
      v-show="config.buttons && config.buttons.prev.visibility"
      :style="config.buttons && config.buttons.prev.style"
      data-button="prev"
      class="cbpo-btn"
      :class="{'btn-pagination-default': config.current !== 1}"
      @click="linkPage(-1)"
      :disabled="config.current === 1"
    >Prev</button>
    <button
      class="cbpo-btn"
      v-for="(page, index) in getPageRange"
      data-button="page"
       :key="page === '...' ? `ellipsis-${index}` : page"
      :class="{'btn-primary': page === config.current, 'btn-pagination-default': page !== config.current, 'btn-three-dots' : page === '...'}"
      @click="goToPage(page)"
      :disabled="page === config.current && (config.total > 0 || config.current <= 1) || page === '...'"
    >{{page}}</button>
    <button
      v-show="config.buttons && config.buttons.next.visibility"
      :style="config.buttons && config.buttons.next.style"
      class="cbpo-btn"
      data-button="next"
      :class="{'btn-pagination-default': config.current !== config.total}"
      @click="linkPage(1)"
      :disabled="config.current === config.total || config.total < config.current"
    >Next</button>
    <button
      v-show="config.buttons && config.buttons.last.visibility"
      :style="config.buttons && config.buttons.last.style"
      class="cbpo-btn"
      data-button="last"
      :class="{'btn-pagination-default': config.current !== config.total}"
      @click="goToPage(config.total)"
      :disabled="config.current === config.total || config.total < config.current"
    >{{config.buttons && config.buttons.last.label}}</button>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import PaginationMixins from '@/components/widgets/elements/table/pagination/PaginationMixins'
import WidgetBase from '@/components/WidgetBase'

export default {
  name: 'PaginationNumbers',
  extends: WidgetBase,
  mixins: [WidgetBaseMixins, PaginationMixins],
  computed: {
    getPageRange: function() {
      let range = []
      if (this.config.numbers !== undefined) {
        const pageRange = this.config.numbers.beforeCurrent + this.config.numbers.afterCurrent + 1
        let current = parseInt(this.config.current)
        let total = parseInt(this.config.total)
        let left = total <= pageRange ? 1 : current - this.config.numbers.beforeCurrent
        let right = total <= pageRange ? pageRange + 1 : (current + this.config.numbers.afterCurrent + 1)
        const showThreeDots = this.config.numbers.showThreeDots
        if (total !== null) {
          for (let i = 1; i <= total; i++) {
            if (i >= left && i < right) {
              range.push(i)
            }
          }
          if (
            (left <= 0 || right > total) &&
            total >= pageRange
          ) {
            let size = range.length
            for (let i = 0; i < pageRange - size; i++) {
              if (left <= 0) {
                let last = range[range.length - 1]
                range.push(last + 1)
              } else {
                let first = range[0]
                range.unshift(first - 1)
              }
            }
          }
          if (showThreeDots && range.length >= pageRange) {
            const lastPage = range[range.length - 1]
            if (this.config.current >= pageRange - 1) {
              range = ['...', ...range.slice(1)]
            }
            if (lastPage !== this.config.total) {
              range = [...range.slice(0, -1), '...']
            }
          }
        }
      }

      return range
    }
  }
}
</script>
<style lang="scss" scoped>
@import './PaginationNumbers.scss';
</style>
