<script>
export default {
  name: 'errorsHandlerMixins',
  data() {
    return {
      errorMessages: {},
      showErrorAlert: false
    }
  },
  computed: {
    filterErrorMessage() {
      return errors => {
        if (errors && errors.code) delete errors.code
        if (errors && errors.summary) delete errors.summary
        return errors
      }
    }
  },
  watch: {
    errorMessages: {
      deep: true,
      handler(newValue) {
        this.showErrorAlert = !!Object.keys(this.errorMessages).length
      }
    }
  }
}
</script>
