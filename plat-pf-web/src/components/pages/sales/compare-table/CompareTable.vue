<template>
  <div>
    <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="!isReady">
      <slot name="loader" :isLoading="isReady">
        <div class="spinner-border thin-spinner spinner-border-sm cls-loading-analysis"></div>&nbsp;Loading...
      </slot>
    </div>
    <transition name="fade"  mode="out-in" >
      <div v-if="isReady && configFilterList" class="mt-1 analysis h-100 d-flex flex-column">
        <b-row class="row-wrapper">
          <b-col class="d-flex justify-content-start">
            <div class="d-flex h-100 align-items-center">
              <div class="table-title ml-3">
                <h5 class="m-0 text-nowrap">View Comparison Tag</h5>
                <b-badge v-if="showTag && tag" :style="{ backgroundColor: tag.tag_color || '' }">{{ tag.tag_name }}</b-badge>
              </div>
            </div>
            <div class="row-custom">
              <div v-if="isTagReload" style="padding: 0 5px 6px 5px">
                <div class="spinner-border thin-spinner spinner-border-sm cls-loading-analysis"></div>
              </div>
              <div class="column column-1">
                <b-dropdown :disabled="isTagReload" variant="primary" class="manage-tag-dropdown dropdown-manage" text="Manage Tags">
                  <template v-for="(action, index) in actions">
                    <b-dropdown-item :key="`${index}_item`" @click="action.handler">
                      <img :src="action.img">
                      <span class="ml-2">{{action.text}}</span>
                    </b-dropdown-item>
                    <b-dropdown-divider :key="`${index}_divider`" v-if="index !== actions.length - 1" />
                  </template>
                </b-dropdown>
              </div>
              <div class="column column-2">
                <b-button-group>
                  <div class="warp-save">
                    <div class="d-flex">
                      <div>
                        <ComplexRangeDatepicker
                          class="d-flex justify-content-center"
                          v-model="currentDateQuery"
                          :ignoreState="sdkConfig.filter.builder.config.ignore"
                          :currentQueryObj="currentQuery"
                          :dateOptions="this.dateOptions"
                          @onChangeDate="onChangeBaseQuery"
                        ></ComplexRangeDatepicker>
                      </div>
                    </div>
                  </div>
                </b-button-group>
              </div>
              <div class="column column-3">
                <b-button-group>
                  <div class="warp-save">
                    <div class="d-flex">
                      <div>
                        <div class="label">Timezone</div>
                        <div v-if="timezoneEl" class="timezone" @click="timezoneEl.click()">
                          {{ timezone }}
                        </div>
                      </div>
                    </div>
                  </div>
                </b-button-group>
              </div>
              <div class="column column-4">
                <b-button-group>
                  <div class="warp-save">
                    <div class="d-flex">
                      <div>
                        <cbpo-manage-columns
                          :key="sdkUniqueState"
                          v-if="configInitialized"
                          :columns="getColumnsForColumnManager"
                          :configObj.sync="sdkConfig.columnManager.config"
                          @input="handleUpdateColumns"
                        >
                          <template v-slot:button="{ openModal }">
                            <b-button
                              @click="openModal"
                              text="Small"
                              size="sm"
                              variant="success"
                            >
                              <i class="fa fa-columns"></i>
                            </b-button>
                          </template>
                        </cbpo-manage-columns>
                      </div>
                    </div>
                  </div>
                </b-button-group>
              </div>
              <div class="column column-5">
                <cbpo-widget-menu-control
                  class="custom-menu"
                  :config-obj="this.mixinsWidgetMenuConfig"
                  @click="exportData"/>
              </div>
            </div>
          </b-col>
        </b-row>
        <div class="cbpo-widget-wrapper">
          <cbpo-widget
            v-if="configInitialized && configFilterListLoaded"
            ref="widgetCompareSDK"
            :key="sdkUniqueState"
            :configObj.sync="sdkConfig"
          >
            <template v-slot:queryBuilder>
              <div class="d-none"></div>
            </template>
            <template v-slot:columnManager>
              <div class="d-none"></div>
            </template>
          </cbpo-widget>
        </div>
      </div>
    </transition>
    <div
      v-if="allDataSourceLoaded && !dsIdOfStandardView"
      class="alert alert-warning"
      role="alert"
    >
      The data source is not ready.
    </div>
  </div>
</template>

<script>
// lib
import cloneDeep from 'lodash/cloneDeep'
import get from 'lodash/get'
import snakeCase from 'lodash/snakeCase'
import isEmpty from 'lodash/isEmpty'
import { mapActions, mapGetters } from 'vuex'
// mixins
import baseQueryMixins from '@/mixins/baseQueryMixins'
import scrollbarMixins from '@/mixins/scrollbarMixins'
import sdkCompareTableMixins from '@/components/pages/sales/compare-table/sdkCompareTableMixins'
import toastMixin from '@/components/common/toastMixin'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
// filter
import ComplexRangeDatepicker from '@/components/common/ComplexRangeDatepicker/ComplexRangeDatepicker.vue'
import { DATE_QUERY_VIEW_COMPARISON_TAG_OPTIONS } from '@/shared/constants/date.constant'

/* eslint-disable */
const REMOVE_FIELDS = [{ name: "item_tax_cost" }]

export default {
  name: 'PFCompareTable',
  components: {
    ComplexRangeDatepicker
  },
  props: {
    showTag: {
      type: Boolean,
      default: true
    },
    tag: {
      type: Object,
      require: true
    },
    actions: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      // render flags
      isTagReload: false,
      isReady: false,
      configInitialized: false,
      isFilterReady: false,
      currentQuery: {},
      timezoneEl: null,
      timezone: '',
      dateOptions: DATE_QUERY_VIEW_COMPARISON_TAG_OPTIONS,
    }
  },
  mixins: [
    baseQueryMixins,
    scrollbarMixins,
    sdkCompareTableMixins,
    toastMixin,
    WidgetMenu
  ],
  computed: {
    ...mapGetters({
      allDataSourceLoaded: `pf/compareTable/allDataSourceLoaded`,
      configFilterList: `pf/compareTable/configFilterList`,
      dsIdOfStandardView: `pf/compareTable/dsIdOfStandardView`,
      localSDKConfig: `pf/compareTable/sdkConfig`,
      filter: `pf/compareTable/filter`,
      sdkUniqueState: `pf/compareTable/sdkUniqueState`,
      userToken: 'ps/userModule/GET_TOKEN',
      dsColumns: `pf/compareTable/dsColumns`,
    }),
    configFilterListLoaded() {
      return !!this.configFilterList
    }
  },
  methods: {
    ...mapActions({
      fetchAllDataSourceIDs: `pf/compareTable/fetchAllDataSourceIDs`,
      setReloadKeySDK: `pf/compareTable/setReloadKeySDK`,
      setSDKConfig: `pf/compareTable/setSDKConfig`,
      getListFilterByTag: `pf/compareTable/getListFilterByTag`,
      initCompareTable: `pf/compareTable/initCompareTable`
    }),
    onChangeBaseQuery() {
      this.sdkConfig.filter.builder.config.ignore.base.value = false
      this.setFilterConfig(this.sdkConfig.filter)
      this.forceSDKRender()
    },
    setRowFilter(configFilter) {
      if (configFilter) {
        this.sdkConfig.elements[0].config.rows = configFilter.map(item => {
          const conditionFilter = {
            type: 'AND',
            level: 0,
            conditions: item.ds_filter.builder.config.query.conditions
          }
          const data = {
            data: {
              name: item.name,
              alias: snakeCase(item.name)
            },
            filter: {
              ...item.ds_filter.base.config.query
            }
          }
          if (!isEmpty(get(item, 'ds_filter.builder.config.query.conditions', []))) {
            data.filter.conditions.push(conditionFilter)
          }
          data.filter.conditions = data.filter.conditions
            .filter(condition => condition.column !== 'sale_date') // Do not override filter of Date picker
          return data
        })
      }
      this.setConfig(this.sdkConfig)
      this.forceSDKRender()
    },
    forceSDKRender() {
      this.setReloadKeySDK()
    },
    handleUpdateColumns(columns) {
      this.currentQuery['configColumns'] = this.sdkConfig.elements[0].config.columns
      this.updateColumns(columns)
    },
    updateColumns(columns) {
      !!this.$refs.widgetCompareSDK && this.$refs.widgetCompareSDK.columnChange(columns)
    },
    exportData() {
      if (!this.$refs.widgetCompareSDK) {
        this.vueToast('error', 'Widget is not ready to export. Please try again later')
        return
      }
      this.$refs.widgetCompareSDK.widgetExport('csv')
    }
  },
  async created() {
    const params = { client_id: this.$route.params.client_id }
    await this.fetchAllDataSourceIDs(params)
    await this.getListFilterByTag({ ...params, tag: this.tag ? this.tag.tag_name : '' })
    // Init analysis table config
    await this.initCompareTable({ ...params, user_id: this.userId })
    // Init SDK data
    this.setDataSource(this.dsIdOfStandardView)
    this.setColumns(this.dsColumns)
    this.setDefaultWidth()
    this.setDefaultConfig(this.sdkConfig)
    if (!this.currentQueryId) {
      this.currentQuery = {
        q: this.sdkConfig.filter
      }
    }
    this.setFilterConfig(this.sdkConfig.filter)
    this.setRowFilter(this.configFilterList)
    // UI is ready to be rendered (e.g hide loading)
    this.isReady = true
    // Init SDK UI (this is parent mixin attribute)
    this.configInitialized = true
    await this.setReloadKeySDK()
    this.timezoneEl = this.$refs.widgetCompareSDK && this.$refs.widgetCompareSDK.$el.querySelector('#cbpo-timezone-value')
    this.timezone = this.timezoneEl && this.timezoneEl.innerText
  },
  watch: {
    sdkConfig: {
      deep: true,
      async handler(newObj) {
        await this.setSDKConfig(cloneDeep(newObj))
        this.timezone = this.timezoneEl && this.timezoneEl.innerText
      }
    },
    async tag() {
      this.isTagReload = true
      await this.getListFilterByTag({ client_id: this.$route.params.client_id, tag: this.tag.tag_name })
      this.isTagReload = false
      this.setColumns(this.dsColumns)
      this.setDefaultWidth()
      this.setDefaultConfig(this.sdkConfig)
      this.setRowFilter(this.configFilterList)
    },
    configFilterList() {
      if(!isEmpty(this.configFilterList)){
        this.setReloadKeySDK()
      }
    },
  }
}
</script>

<style lang="scss" scoped>
@import "@/components/pages/sales/analysis/Analysis.scss";
@import '@/assets/scss/listSaved.scss';

.analysis {
  ::v-deep .manage-tag-dropdown {
    height: 36px;
    .btn.btn-primary {
      @include button-color($primary);
    }
    .dropdown-menu {
      padding: 0;
      .dropdown-item {
        padding: 10px 20px;

          .remove-icon {
            width: 24px;
            transform: rotate(45deg) translate(-1px, 1px);
          }
      }
    }
  }

  .row-custom {
    .column {
      &.column-1,
      &.column-2,
      &.column-3,
      &.column-4,
      &.column-5 {
        flex: unset;
        margin: 0 0 0 8px;
      }

      &.column-1 {
        // comparison tag dropdown
        ::v-deep .dropdown .dropdown-menu {
          border-radius: unset !important;
        }
      }

      &.column-2 {
        ::v-deep {
          .dropdown-toggle {
            min-width: 150px;
            i {
              display: none;
            }
          }
          .dropdown-menu {
            min-width: 150px;
          }
          .label {
            font-size: 14px;
            color: #000;
          }
          .mx-datepicker-range {
            .mx-input-wrapper {
              margin-top: 26px;
            }
          }
        } 
      }

      &.column-3 {
        .label {
          margin-bottom: 8px;
          font-weight: normal;
          font-stretch: normal;
          font-style: normal;
          line-height: 1.33;
          letter-spacing: 0.12px;
          color: #000;
        }

        .timezone {
          display: inline-flex;
          align-items: center;
          justify-content: space-between;
          min-width: 150px;
          height: 36px;
          padding: 10px 8px 10px 40px;
          font-weight: normal;
          font-size: 12px;
          color: #232F3E;
          background: url("~@/assets/img/icon/globe.svg") no-repeat left 0.75rem center/18px 20px;
          border: 1px solid #E6E8F0;
          cursor: pointer;
        }
      }

      &.column-5 {
        height: 36px;
        align-items: flex-start;
        padding: 4px 0 0;

        ::v-deep .dropdown .dropdown-toggle:not(.disabled):not(:disabled) {
          background-color: unset !important;
        }
      }
    }
  }

  ::v-deep .cbpo-widget-wrapper {
    height: auto !important;

    .cbpo-widget {
      border: 0;
      min-height: 64px;

      .cbpo-table-element-container {
        padding: 0;

        .cbpo-table {
          min-height: 95px;
        }

        .cbpo-table-action {
          display: none !important;
        }

        .cbpo-header-col,
        .cbpo-table-cell {
          border: none;
        }

        .cbpo-table-cell {
          border-top: 1px solid #D2D6DB;

          &:not(:first-child) .tbl-cell-body {
            text-align: right;
          }
        }
      }
    }
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
  transition-delay: .5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
::v-deep .cbpo-table-message {
top: unset !important;
bottom: 0;
transform: translate(-50%, 0) !important;
}
::v-deep {
  .dropdown-toggle {
    font-size: 14px !important;
  }
  .dropdown-menu {
    font-size: 14px !important;
  }
}
</style>
