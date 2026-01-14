export default {
  data () {
    return {
      loading: false,
      lazyLoading: false
    }
  },
  methods: {
    showLoading () {
      this.loading = true
    },
    hideLoading () {
      this.loading = false
    },
    showLazyLoading() {
      this.lazyLoading = true
    },
    hideLazyLoading() {
      this.lazyLoading = false
    }
  }
}
