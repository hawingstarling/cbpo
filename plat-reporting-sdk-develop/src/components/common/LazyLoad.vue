<template>
  <div ref="target" class="h-100">
    <slot v-if="isVisible"></slot>
    <div v-else class="default-layout" :style="`height: ${defaultHeight}px`" />
  </div>
</template>

<script>
export default {
  name: 'LazyLoad',
  props: {
    defaultHeight: {
      type: Number,
      default: 200
    },
    threshold: {
      // threshold: percent of the target is visible to invoke the callback
      // range value: 0 - 1
      type: Number,
      default: 0.2
    }
  },
  data() {
    return {
      isVisible: false,
      observer: null
    }
  },
  mounted() {
    this.observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.isVisible = true
          this.observer.unobserve(this.$refs.target)
        }
      })
    }, { threshold: this.threshold })
    this.observer.observe(this.$refs.target)
  },
  beforeDestroy() {
    if (this.observer) {
      this.observer.disconnect()
    }
  }
}
</script>
<style scoped lang="scss">
.default-layout {
  padding: 10px 15px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  border: solid 1px #d9d9d9;
}
</style>
