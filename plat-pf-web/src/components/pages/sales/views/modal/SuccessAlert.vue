<template>
  <b-modal id="success-alert-modal" variant="danger" hide-header hide-footer centered>
    <div class="text-center pb-4"><img src="@/assets/img/icon/success.svg"></div>
    <strong><p>{{ title }}</p></strong>
    <p>{{ content }}</p>
  </b-modal>
</template>

<script>
export default {
  name: 'SuccessAlert',
  props: {
    title: {
      type: String,
      required: true
    },
    content: {
      type: String,
      required: true
    }
  }
}
</script>

<style lang="scss" scoped>
  ::v-deep #success-alert-modal {
    .modal-dialog {
      max-width: 400px;
    }
    .modal-body {
      padding: 24px;
    }
  }
  .content {
    font-size: 14px;
    line-height: 20px;
    color: #667085;
  }
  .title {
    color: #232F3E;
    font-weight: 500;
    font-size: 18px;
  }
</style>
