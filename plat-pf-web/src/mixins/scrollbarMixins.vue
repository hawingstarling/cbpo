<script>
export default {
  data() {
    return {
      innerHeight:
        window.innerHeight ||
        document.documentElement.clientHeight ||
        document.body.clientHeight,
      widgetElement: null,
      marginBottomTable: 10
    }
  },
  methods: {
    updateInnerHeight() {
      this.innerHeight =
        window.innerHeight ||
        document.documentElement.clientHeight ||
        document.body.clientHeight
    },
    calcContainerHeight(el) {
      if (el) {
        return `${this.innerHeight -
          el.getBoundingClientRect().top -
          50 -
          this.marginBottomTable}px`
      }
      return 'auto'
    },
    setContainerHeight() {
      this.updateInnerHeight()
      if (this.widgetElement) {
        this.widgetElement.style.height = this.calcContainerHeight(
          this.widgetElement
        )
        this.widgetElement.style.marginBottom = `${this.marginBottomTable}px`
      }
    }
  },
  mounted() {
    window.addEventListener('resize', this.setContainerHeight)
  },
  watch: {
    configInitialized: {
      handler(val) {
        this.$nextTick(async () => {
          if (val) {
            this.widgetElement = await document.querySelector(
              '.cbpo-widget-wrapper'
            )
            this.setContainerHeight()
          }
        })
      }
    }
  }
}
</script>
