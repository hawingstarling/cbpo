<template>
  <div>
    <div class="col-12 p-0 pb-1">
      <cbpo-widget :config-obj="INVCustomerReturnsCategory.config"/>
    </div>
    <div class="col-12 p-0">
      <cbpo-widget :config-obj="INVCustomerReturnsBrand.config"/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'INVCustomerReturns',
  props: {
    INVCustomerReturnsBrand: Object,
    INVCustomerReturnsCategory: Object
  }
}
</script>

<style lang="scss" scoped>
  @import '@/components/pages/sales/overview/Overview.scss';
</style>
