<template>
  <div>
    <Step2Validate
      :inputOptions="options"
    ></Step2Validate>
  </div>
</template>

<script>
export default {
  name: 'PFStep2Validate',
  data () {
    return {
      options: {
        title: 'Data Preview',
        nextStepRouter: '',
        module: this.$route.params.module,
        progressBar: true,
        estimateTimeBar: true
      }
    }
  },
  created() {
    if (this.$route.params.module === 'SaleItem') {
      this.options.nextStepRouter = 'PFStep3Process'
    }
    if (this.$route.params.module === 'ItemModule') {
      this.options.nextStepRouter = 'PFStep3ProcessItems'
    }
    if (this.$route.params.module === 'BrandSettingModule') {
      this.options.nextStepRouter = 'PFStep3ProcessBrandSetting'
    }
    if (this.$route.params.module === 'BrandModule') {
      this.options.nextStepRouter = 'PFStep3ProcessBrand'
    }
    if (this.$route.params.module === 'FedExShipmentModule') {
      this.options.nextStepRouter = 'PFStep3ProcessFedex'
    }
    if (this.$route.params.module === 'AppEagleProfileModule') {
      this.options.nextStepRouter = 'PFStep3ProcessRepricing'
    }
    if (this.$route.params.module === 'TopASINs') {
      this.options.nextStepRouter = 'PFStep3ProcessTopASIN'
    }
    if (this.$route.params.module === 'TopASINsDelete') {
      this.options.nextStepRouter = 'PFStep3ProcessDeleteTopASIN'
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
