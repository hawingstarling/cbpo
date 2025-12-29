<template>
  <b-card class="sales-amount-card rounded-0 h-100">
    <div class="h-100 d-flex flex-column overflow-hidden" style="background-color: #f9fbfb;">
      <widget-header title="Sale By $ Amount" :lastUpdated="lastUpdated">
        <template #menu-control>
          <cbpo-widget-menu-control :config-obj="mixinsWidgetMenuConfig"
          @click="menuEventHandler"/>
        </template>
      </widget-header>

      <div class="card-movement-filer d-flex justify-content-start align-items-end flex-wrap flex-grow-1">
        <div class="d-flex align-items-end flex-grow-1">
          <div class="position-relative w-25 flex-column align-items-start mr-2">
            <div class="d-flex justify-content-between">
              <label class="label-name mb-2">Group By</label>
              <b-form-checkbox class="save-as-default pr-3" :checked="saveAsDefault" @change="selectSaveAsDefault">
                Save as default
              </b-form-checkbox>
            </div>
            <div class="position-relative">
              <v-select v-if="!isLoading" :options="groupBy.options" :clearable="false" v-model="groupBy.selected"
                class="custom-v-select">
                <template #open-indicator="{ attributes }">
                  <i class="fa fa-angle-down" v-bind="attributes"></i>
                </template>
              </v-select>
              <input v-if="isLoading" type="text" class="select-box-mark w-25" placeholder="All brands">
              <div v-if="isLoading" class="icon-loading">
                <i class="fa fa-circle-o-notch fa-spin"></i>
              </div>
            </div>
          </div>
          <div v-if="groupBy.selected.value === 'sku'"
            class="position-relative w-25 flex-column align-items-start mr-2">
            <label class="label-name mb-2">SKU</label>
            <div class="position-relative">
              <v-select v-if="!isLoading" :options="getDropdownList" :clearable="false" v-model="filterSelected"
                class="custom-v-select" placeholder="Search Brands">
                <template #open-indicator="{ attributes }">
                  <i class="fa fa-angle-down" v-bind="attributes"></i>
                </template>
                <span slot="no-options">
                  This SKU does not exist.
                </span>
              </v-select>
              <input v-if="isLoading" type="text" class="select-box-mark w-25" placeholder="All SKU">
              <div v-if="isLoading" class="icon-loading">
                <i class="fa fa-circle-o-notch fa-spin"></i>
              </div>
            </div>
          </div>
          <div v-if="groupBy.selected.value === 'brand'"
            class="position-relative w-25 flex-column align-items-start mr-2">
            <label class="label-name mb-2">Brand</label>
            <div class="position-relative">
              <v-select v-if="!isLoading" :options="getDropdownList" :clearable="false" v-model="filterSelected"
                class="custom-v-select" placeholder="Search Brands">
                <template #open-indicator="{ attributes }">
                  <i class="fa fa-angle-down" v-bind="attributes"></i>
                </template>
                <span slot="no-options">
                  This brand does not exist.
                </span>
              </v-select>
              <input v-if="isLoading" type="text" class="select-box-mark w-100" placeholder="All brands">
              <div v-if="isLoading" class="icon-loading">
                <i class="fa fa-circle-o-notch fa-spin"></i>
              </div>
            </div>
          </div>
          <div class="position-relative w-25 flex-column align-items-start">
            <label class="label-name mb-2">Fulfillment</label>
            <div class="position-relative">
              <v-select v-if="!isLoading" :options="fulfillmentOptions" :clearable="false" v-model="fulfillmentSelected"
                class="custom-v-select" placeholder="Search Fulfillment">
                <template #open-indicator="{ attributes }">
                  <i class="fa fa-angle-down" v-bind="attributes"></i>
                </template>
                <span slot="no-options">
                  This Fulfillment does not exist.
                </span>
              </v-select>
              <input v-if="isLoading" type="text" class="select-box-mark w-100" placeholder="All fulfillment">
              <div v-if="isLoading" class="icon-loading">
                <i class="fa fa-circle-o-notch fa-spin"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-2 px-0 h-100 overflow-hidden widget-sales-by-amount">
        <template v-if="isSDKReady">
          <cbpo-widget ref="widget" class="border-right-0 border-bottom-0 border-left-0 sales-by-amount-table"
            :key="sdkKey" :config-obj="sdkConfig.config" @getLastUpdated="lastUpdated = $event"/>
        </template>
        <template v-else>
          <div class="w-100 h- 100 d-flex justify-content-center align-items-center">
            <i class="fa fa-circle-o-notch fa-spin"></i>
          </div>
        </template>
      </div>
    </div>
  </b-card>
</template>

<script>
import { mapActions } from 'vuex'
import get from 'lodash/get'
import 'vue-select/dist/vue-select.css'
import Vue from 'vue'
import vSelect from 'vue-select'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import widgetSellerMixins from '@/mixins/widgetSellerMixins'
import { WIDGET_NAME, SKU_OPTION } from '@/shared/constants'
import WidgetHeader from '@/components/pages/sales/overview/common/WidgetHeader.vue'

Vue.component('v-select', vSelect.VueSelect)

export default {
  components: { WidgetHeader },
  name: 'SalesAmount',
  mixins: [WidgetMenu, widgetSellerMixins],
  props: {
    sdkConfig: Object
  },
  data() {
    return {
      widget: WIDGET_NAME.dollar,
      lastUpdated: null
    }
  },
  methods: {
    ...mapActions({
      fetchUserTrack: 'pf/saleWidget/getUserTrack'
    }),
    async initData() {
      // create default params
      const defaultParams = {
        clientId: this.$route.params.client_id,
        widget: this.widget,
        hasVariation: false,
        type: 'fulfillment-types'
      }
      // fetch api to get all brand data and set into SDK
      await this.getAllBrandsAndFulfillment(defaultParams)
      const userTrack = await this.fetchUserTrack(defaultParams)
      this.saveAsDefault = get(userTrack, 'data.widget.sale_by_dollar.save_as_default', false)
      this.groupBy.selected = this.groupBy.options.find(item => item.value === get(userTrack, 'data.widget.sale_by_dollar.group_by_default', SKU_OPTION.value))
    },
    menuEventHandler(type) {
      if (type !== 'csv' || !this.$refs.widget) return
      this.$refs.widget.widgetExport(type)
    },
    getLastUpdated(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    }
  },
  async created() {
    // build key
    this.buildSDKKey()
    // init data
    await this.initData()
    this.isSDKReady = true
  }
}
</script>

<style lang="scss" scoped>

::v-deep .sales-by-amount-table {
  border: none !important;
}

::v-deep .cbpo-control-features {
  padding: 2px !important;
}

::v-deep .cbpo-control-features,
.sales-by-amount-table {
  background-color: #f9fbfb !important;
}

.sales-amount-card {
  overflow: hidden;

  .card-body {
    height: 100%;
    padding: 0 0;
    overflow: hidden;
  }

  .card-header {
    height: 37.8px;
    padding: .7rem;
    background: #ebebeb;
    text-align: center;
    font-size: 12px;
  }

  .icon-loading {
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding-right: 12px;
    position: absolute;
  }
}

.card-movement-filer {
  margin-top: 8px;
  padding: 0 8px;
}

::v-deep {
  .overview__menu-control .menu-control-select {
    margin: 0 !important;

    .btn:not(.not-button).btn-secondary.btn-secondary:not(.disabled):not(:disabled):hover {
      background-color: #fff !important;
    }
  }
}

::v-deep .custom-v-select .vs__dropdown-toggle {
  font-size: 14px;
  background-color: white;
  height: 100%;
  font-weight: 400;
  line-height: 1.5;
  color: rgb(92, 104, 115);
  border-radius: 4px;
  border: 1px solid #c8ced3;
}

// custom v-select
::v-deep .custom-v-select .vs__search {
  color: rgb(130, 139, 147);
  padding-bottom: 4px;
}

::v-deep .custom-v-select .vs__dropdown-menu {
  font-size: 14px;
  overflow-x: clip;

  li {
    font-size: 14px;
  }
}

::v-deep .dropdown-item {
  font-size: 0.875rem;

  &:hover {
    color: #fff;
    background: #5897fb;
    border-radius: 0;
  }
}

::v-deep .custom-v-select .vs__open-indicator {
  color: rgb(35, 40, 44);
  cursor: pointer;
  font-size: 16px;
}

::v-deep .custom-v-select .vs__clear,
::v-deep .custom-v-select .vs__open-indicator {
  margin-bottom: 4px;
}

::v-deep .separate {
  height: 1px;
  border-bottom: 1px solid #808080;
  margin: 5px 20px;
}

.select-box-mark {
  height: 30px;
  border-radius: 4px;
  background-color: rgb(248, 248, 248);
  border: 1px solid rgb(200, 206, 211);
  font-size: 0.85em;
  padding-left: 8px;
  padding-top: 5px;
}

::v-deep .custom-control-label {
  font-size: 12px;
  color: #667085;
  line-height: 1.33;

  &::before {
    top: 0 !important;
  }

  &::after {
    top: 0 !important;
  }
}

.label-name {
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.33;
  letter-spacing: 0.12px;
  font-size: 12px;
  color: #667085;
}

.widget-sales-by-amount::v-deep {
  .cbpo-table-container {
    .cbpo-table-footer.cbpo-table-summary .tbl-col-header {
      justify-content: flex-end;
    }

    .vue-recycle-scroller__item-view .cbpo-table-cell:not(:first-child) {
      text-align: right;
    }
  }
}

::v-deep .custom-v-select {
  width: 100%;
  height: 36px;

  .vs__dropdown-toggle {
    height: 100%;
  }

  .vs__dropdown-menu {
    max-height: 185px !important;
    margin: 0.125rem 0 0;
    border-top: 1px solid rgba(60, 60, 60, .26);
  }
}

::v-deep .custom-v-select .vs__dropdown-menu {
  max-height: 300px;
}

::v-deep .cbpo-table-element-container {
  background-color: #f9fbfb;

  .cbpo-table-reporting {
    background-color: #f9fbfb;
  }
}
</style>
