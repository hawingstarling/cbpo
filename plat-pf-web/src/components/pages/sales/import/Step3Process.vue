<template>
  <div>
    <Step3Process
      :inputOptions="options"
    ></Step3Process>
  </div>
</template>

<script>
export default {
  name: 'PFStep3Process',
  data () {
    return {
      options: {
        title: 'Validation Results',
        nextStepRouter: '',
        module: this.$route.params.module,
        progressBar: true,
        estimateTimeBar: true,
        downloadInvalidEnabled: true
      }
    }
  },
  created() {
    if (this.$route.params.module === 'SaleItem') {
      this.options.nextStepRouter = 'PFStep4Result'
    }
    if (this.$route.params.module === 'ItemModule') {
      this.options.nextStepRouter = 'PFStep4ResultItems'
    }
    if (this.$route.params.module === 'BrandSettingModule') {
      this.options.nextStepRouter = 'PFStep4ResultBrandSetting'
    }
    if (this.$route.params.module === 'BrandModule') {
      this.options.nextStepRouter = 'PFStep4ResultBrand'
    }
    if (this.$route.params.module === 'FedExShipmentModule') {
      this.options.nextStepRouter = 'PFStep4ResultFedex'
    }
    if (this.$route.params.module === 'AppEagleProfileModule') {
      this.options.nextStepRouter = 'PFStep4ResultRepricing'
    }
    if (this.$route.params.module === 'TopASINs') {
      this.options.nextStepRouter = 'PFStep4ResultTopASIN'
    }
    if (this.$route.params.module === 'TopASINsDelete') {
      this.options.nextStepRouter = 'PFStep4ResultDeleteTopASIN'
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
