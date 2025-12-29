<template>
<div class="px-2">
  <b-row class="row-wrapper m-0" v-if="isSDKConfigReady">
    <b-col class="d-flex justify-content-start align-items-center p-0">
      <div class="mr-auto align-self-start text-nowrap mt-1 h-100">
        <h5><i class="fa fa-bullhorn"></i> Advertising</h5>
      </div>
      <div class="row-custom">
          <div class="column column-1">
            <b-button-group class="mx-1">
              <div class="warp-save">
                <div class="d-flex align-items-center">
                  <div v-if="isSDKConfigReady">
                    <cbpo-filter-form
                      ref="filterForm"
                      class="filter-right"
                      :controls.sync="configSearchFilter"
                      @filterChange="updateFilter($event)"
                    />
                  </div>
                  <div class="pr-1" v-if="isSDKConfigReady">
                    <Datepicker
                      v-model="dataValue"
                      valueType="YYYY-MM-DD"
                      specializedComponent="pf-analysis"
                      range
                      placeholder="Select date filter"
                      :shortcuts="datePickerShortcuts"
                      :clearable="false"
                      @change="onChangeDate"
                    ></Datepicker>
                  </div>
                </div>
              </div>
            </b-button-group>
          </div>
        </div>
    </b-col>
  </b-row>
  <b-row v-if="isSDKConfigReady" class="advertising-dashboard">
    <cbpo-widget :key="sdkUniqueState" class="p-1 w-100"  :config-obj="configWidget.config"></cbpo-widget>
  </b-row>
  <div v-if="showLoading" class="d-flex justify-content-center align-items-center loading">
    <b-spinner style="width: 3rem; height: 3rem;" label="Large Spinner"></b-spinner>
  </div>
  <div v-if="!isSDKConfigReady && !showLoading" class="alert alert-warning" role="alert">
    The data source is not ready.
  </div>
</div>
</template>
<script>
import _ from 'lodash'
import { mapActions, mapGetters } from 'vuex'
import Datepicker from '@/components/common/Datepicker/Datepicker'
import toastMixin from '@/components/common/toastMixin'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'

export default {
  name: 'PFAdvertising',
  data() {
    return {
      configWidget: _.cloneDeep(require('./config/Brands')),
      configSearchFilter: _.cloneDeep([require('./config/searchFilter')]),
      isSDKConfigReady: false,
      dataValue: '',
      sdkUniqueState: 0,
      showLoading: false,
      permissions
    }
  },
  mixins: [
    toastMixin,
    PermissionsMixin
  ],
  components: {
    Datepicker
  },
  async created() {
    this.showLoading = true
    await this.fetchAdvertisingDSId({client_id: this.$route.params.client_id})
    this.mapDSIdToWidgetConfig()
  },
  computed: {
    ...mapGetters({
      advertisingdsId: `pf/advertising/advertisingdsId`
    }),
    datePickerShortcuts() {
      return [
        {
          text: 'Today',
          onClick: () => {
            return [
              new Date(this.$moment().startOf('day')),
              new Date(this.$moment().endOf('day'))
            ]
          }
        },
        {
          text: 'Yesterday',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .subtract(1, 'days')
                  .startOf('day')
              ),
              new Date(
                this.$moment()
                  .subtract(1, 'days')
                  .endOf('day')
              )
            ]
          }
        },
        {
          text: 'Last 7 days',
          onClick: () => [
            new Date(
              this.$moment()
                .add(-7, 'day')
                .startOf('day')
            ),
            new Date(this.$moment().endOf('day'))
          ]
        },
        {
          text: 'This week',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .day(0)
                  .startOf('day')
              ),
              new Date(
                this.$moment()
                  .day(6)
                  .endOf('day')
              )
            ]
          }
        },
        {
          text: 'Last week',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .day(-7)
                  .startOf('day')
              ),
              new Date(
                this.$moment()
                  .day(-1)
                  .endOf('day')
              )
            ]
          }
        },
        {
          text: 'Last 30 days',
          onClick: () => [
            new Date(
              this.$moment()
                .add(-30, 'day')
                .startOf('day')
            ),
            new Date(this.$moment().endOf('day'))
          ]
        },
        {
          text: 'This month',
          onClick: () => {
            return [
              new Date(this.$moment().startOf('month')),
              new Date(this.$moment().endOf('month'))
            ]
          }
        },
        {
          text: 'Last month',
          onClick: () => {
            return [
              new Date(
                this.$moment()
                  .subtract(1, 'months')
                  .startOf('month')
              ),
              new Date(
                this.$moment()
                  .subtract(1, 'months')
                  .endOf('month')
              )
            ]
          }
        },
        {
          text: 'Year to date',
          onClick: () => {
            return [
              new Date(this.$moment().startOf('year')),
              new Date(this.$moment().endOf('year'))
            ]
          }
        },
        {
          text: 'Lifetime',
          onClick: () => {
            return [ undefined, undefined ]
          }
        }
      ]
    }
  },
  methods: {
    ...mapActions({
      fetchAdvertisingDSId: `pf/advertising/fetchAdvertisingDSId`
    }),
    mapDSIdToWidgetConfig() {
      if (!_.isEmpty(this.advertisingdsId)) {
        if (this.configWidget) {
          this.configWidget.config.elements[0].config.dataSource = this.advertisingdsId
        }
        this.configSearchFilter[0].config.dataSource = this.advertisingdsId
        this.isSDKConfigReady = true
      }
      this.showLoading = false
    },
    onChangeDate() {
      const filter = {
        level: 1,
        column: 'date',
        value: this.dataValue.every(item => _.isEmpty(item)) ? undefined : this.dataValue,
        operator: 'in_range'
      }
      this.updateConfigFilterSDK(filter)
    },
    updateFilter() {
      let filter = {
        level: 1,
        column: 'brand_name',
        value: this.configSearchFilter[0].config.common.value,
        operator: '$eq'
      }
      this.updateConfigFilterSDK(filter)
    },
    updateConfigFilterSDK(filter) {
      let listCondition = _.cloneDeep(this.configWidget.config.filter.base.config.query.conditions)
      if (filter && listCondition.some((config) => config.column === filter.column)) {
        listCondition.forEach((config) => {
          if (config.column === filter.column) {
            config.value = filter.value
          }
        })
      } else {
        if (!_.isEmpty(filter.value)) {
          listCondition.push(filter)
        }
      }
      this.configWidget.config.filter.base.config.query.conditions = listCondition.filter(config => !_.isEmpty(config.value) || config.column === 'ad_spend')
      this.sdkUniqueState++
    }
  },
  watch: {
  }
}
</script>

<style lang="scss" scoped>

.advertising-dashboard {
  background-color: white;
  padding: 0.5rem;
  height: 500px;
}
.loading{
  min-height: 400px;
}
/deep/.menu-position .cbpo-widget-menu {
  top: 9px !important;
  right: 9px !important;
}
/deep/.cbpo-table-element-container {
  padding: 0 !important;
  &.cbpo-table-reporting{
    padding: 0 !important;
  }
}
.row-wrapper {
  margin-bottom: 1rem;
}
/deep/ .cbpo-table-container {
  padding-top: 0;
}
/deep/.cbpo-table-element-container .cbpo-table .cbpo-table-body .cbpo-table-cell.c-grouped:before {
  display: none !important;
}
/deep/.cbpo-table-element-container .cbpo-table .cbpo-table-body .cbpo-table-cell.c-grouped span.text {
  padding-left: 0 !important;
}
/deep/ .vs__dropdown-toggle{
  background: white;
  border-radius: 4px !important;
  min-width: 180px;
}
/deep/ .vs__search {
  background: unset !important;
  margin: 4px 0 2px 0px !important;
}

/deep/ .vs__dropdown-menu {
  width: 180px;
  left: 8px;
}
</style>
