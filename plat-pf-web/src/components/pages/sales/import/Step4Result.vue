<template>
  <div>
    <Step4Result
      :inputOptions="options"
    ></Step4Result>
  </div>
</template>

<script>
export default {
  name: 'PFStep4Result',
  data () {
    return {
      options: {
        title: 'Processing Results',
        nextStepRouter: '',
        module: this.$route.params.module,
        progressBar: true,
        downloadInvalidEnabled: true,
        estimateTimeBar: true
      }
    }
  },
  created() {
    if (this.$route.params.module === 'SaleItem') {
      this.options.nextStepRouter = 'PFStep1Import'
    }
    if (this.$route.params.module === 'ItemModule') {
      this.options.nextStepRouter = 'PFItems'
    }
    if (this.$route.params.module === 'BrandSettingModule') {
      this.options.nextStepRouter = 'PFBrands'
    }
    if (this.$route.params.module === 'BrandModule') {
      this.options.nextStepRouter = 'PFStep1ImportBrand'
    }
    if (this.$route.params.module === 'FedExShipmentModule') {
      this.options.nextStepRouter = 'PFShippingInvoices'
    }
    if (this.$route.params.module === 'AppEagleProfileModule') {
      this.options.nextStepRouter = 'PFRepricing'
    }
    if (this.$route.params.module === 'TopASINs' || this.$route.params.module === 'TopASINsDelete') {
      this.options.nextStepRouter = 'PFTopASINs'
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
