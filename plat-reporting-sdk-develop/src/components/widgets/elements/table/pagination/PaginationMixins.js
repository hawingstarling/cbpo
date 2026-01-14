export default {
  methods: {
    linkPage: function (change) {
      this.config.current = this.config.current - 0 + change
      this.$emit('update:configObj', this.config)
    },
    goToPage: function (change) {
      if (this.config) {
        const {
          total
        } = this.config
        if (change > 0 && change <= total) {
          this.config.current = change - 0
          this.$emit('update:configObj', this.config)
        }
      }
    }
  }
}
