<template>
  <b-card>
    <Step1Import class="pf-custom" :class="{'sale-item-custom': $route.params.module === 'SaleItem'}" :inputOptions="options" :appProfile="appProfile"></Step1Import>
  </b-card>
</template>

<script>
import PermissionsMixin from '@/components/common/PermissionsMixin'

export default {
  name: 'PFStep1Import',
  mixins: [PermissionsMixin],
  data() {
    return {
      appProfile: process.env.VUE_APP_PS_BUILD_APP,
      options: {
        title: '',
        selectFileLabel: 'Select CSV/XLSX File',
        nextStepRouter: '',
        module: this.$route.params.module,
        progressBar: true,
        showHelpInfo: true,
        meta: {
          meta: JSON.stringify({
            client_id: this.$route.params.client_id
          })
        },
        uploadBtnText: 'Upload File',
        downloadBtnText: 'Download Sample File'
      }
    }
  },
  watch: {
    '$route.params.module': {
      handler: function(value) {
        if (value === 'SaleItem') {
          this.options.title = 'Import Sale Items'
          this.options.showHelpInfo = false
          this.options.nextStepRouter = 'PFStep2Validate'
        }
        if (value === 'ItemModule') {
          this.options.title = 'Import Items'
          this.options.nextStepRouter = 'PFStep2ValidateItems'
        }
        if (value === 'BrandSettingModule') {
          this.options.title = 'Import Brand Setting'
          this.options.nextStepRouter = 'PFStep2ValidateBrandSetting'
        }
        if (value === 'BrandModule') {
          this.options.title = 'Import Brand'
          this.options.nextStepRouter = 'PFStep2ValidateBrand'
        }
        if (value === 'FedExShipmentModule') {
          this.options.title = 'Import Shipping Invoices'
          this.options.showHelpInfo = false
          this.options.nextStepRouter = 'PFStep2ValidateFedex'
        }
        if (value === 'AppEagleProfileModule') {
          this.options.title = 'Import Repricing'
          this.options.nextStepRouter = 'PFStep2ValidateRepricing'
        }
        if (value === 'TopASINs') {
          this.options.title = 'Import Top ASINs'
          this.options.nextStepRouter = 'PFStep2ValidateTopASIN'
        }
        if (value === 'TopASINsDelete') {
          this.options.title = 'Import To Delete Top ASINs'
          this.options.nextStepRouter = 'PFStep2ValidateDeleteTopASIN'
        }
        this.options.module = value
      },
      deep: true,
      immediate: true
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

.pf-custom {
  ::v-deep div:first-child {
    justify-content: center;
    border: none !important;
  }

  ::v-deep .card-header {
    padding: 0.75rem 1.25rem 1rem;
    background-color: unset;
    border-bottom: unset;
    display: block;
    font-size: 18px;

    div:first-child {
      justify-content: center !important;

      b {
        font-weight: 700;
        font-size: 18px;
        color: #101828;
        line-height: 24px;
      }
    }
  }

  ::v-deep .card-body {
    padding: 0 1.25rem;

    .form-group {
      margin: 0;
    }

    .pf-form-file-input {
      display: flex;
      flex-direction: column;
      justify-content: center;

      label {
        margin: 0 0 2rem 0;

        &:first-child {
          text-align: center;
          font-weight: 500;
          font-size: 18px;
          color: #6C6C6C;
        }
      }

      .b-form-file label {
        margin: 0;
        font-size: 16px;
      }
    }
  }

  ::v-deep .card-footer {
    padding-top: 0;
    background-color: unset;
    border-top: unset;
    display: flex;
    flex-direction: column;
    align-items: center;

    button {
      height: 40px;
      margin: 16px 0 0 0 !important;
      font-weight: 500 !important;

      i {
        display: none;
      }
    }

    button:nth-child(1) {
      display: none;
    }

    button:nth-child(2) {
      @include button-icon(false, 'upload.svg', 20px, 20px);
      @include button-color(#232F3E);

      padding: 12px 20px !important;
      font-size: 16px !important;
      line-height: 24px !important;
    }

    button:nth-child(3) {
      @include button-icon(false, 'download.svg', 20px, 20px);
      @include button-color(#232F3E);

      padding: 10px 16px !important;
      font-size: 14px !important;
      line-height: 20px !important;
    }
  }

  ::v-deep .custom-file {
    height: 48px;

    .custom-file-label {
      height: 100%;
      display: flex;
      align-items: center;

      &::before {
        content: url(/img/question.c7daca7e.svg);
        position: absolute;
        width: 16px;
        height: 16px;
        top: 50%;
        right: 85px;
        transform: translateY(-50%);
      }

      &::after {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 0;
      }
    }
  }

  &.sale-item-custom ::v-deep .custom-file .custom-file-label {
    border-radius: 8px !important;
  }
}
</style>
