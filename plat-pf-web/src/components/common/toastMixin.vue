<script>
export default {
  methods: {
    vueToast: function (type, valid) {
      this.$toasted.show(`${valid}`, {
        theme: 'bubble',
        position: 'top-center',
        duration: 3000,
        type
      })
    }
  }
}
</script>
