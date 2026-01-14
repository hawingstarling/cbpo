<script>
export default {
  methods: {
    vueToast: function (valid, type) {
      this.$toasted.show(`${valid}`, {
        theme: 'bubble',
        position: 'top-center',
        duration: 5000,
        type
      })
    }
  }
}
</script>
