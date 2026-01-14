<template>
  <div class="cbpo-pagination-next-previous">
    <div>
      <button
        v-show="config.buttons && config.buttons.first.visibility"
        title="First"
        class="cbpo-btn"
        data-button="first"
        :class="{'btn-pagination-default': config.current > 1}"
        :style="config.buttons && config.buttons.first.style"
        @click="goToPage(1)"
        :disabled="config.current <= 1">{{config.buttons && config.buttons.first.label}}</button>
      <button
        v-show="config.buttons && config.buttons.prev.visibility"
        title="Previous"
        data-button="prev"
        class="cbpo-btn"
        :class="{'btn-pagination-default': config.current > 1}"
        :style="config.buttons && config.buttons.prev.style"
        @click="linkPage(-1)"
        :disabled="config.current <= 1">{{config.buttons && config.buttons.prev.label}}</button>
    </div>
    <p class="cbpo-pagination-page-of">Page {{config.current}} of {{config.total}}</p>
    <div>
      <button
        v-show="config.buttons && config.buttons.next.visibility"
        title="Next"
        data-button="next"
        class="cbpo-btn"
        :class="{'btn-pagination-default': config.current < config.total}"
        :style="config.buttons && config.buttons.next.style"
        @click="linkPage(1)"
        :disabled="config.current >= config.total">{{config.buttons && config.buttons.next.label}}</button>
      <button
        v-show="config.buttons && config.buttons.last.visibility"
        title="Last"
        data-button="last"
        class="cbpo-btn"
        :class="{'btn-pagination-default': config.current < config.total}"
        :style="config.buttons && config.buttons.last.style"
        @click="goToPage(config.total)"
        :disabled="config.current >= config.total">{{config.buttons && config.buttons.last.label}}</button>
    </div>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import PaginationMixins from '@/components/widgets/elements/table/pagination/PaginationMixins'

export default {
  name: 'PaginationButtons',
  extends: WidgetBase,
  mixins: [
    WidgetBaseMixins,
    PaginationMixins
  ]
}
</script>
<style lang="scss" scoped>
  @import './PaginationButtons.scss';
</style>
