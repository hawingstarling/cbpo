<template>
  <b-modal @hidden="resetModal" :id="id" modal-class="multiple-export-modal" size="md" centered hide-header-close>
        <template v-slot:modal-title>
        <span class="title-modal">Select widgets to show</span>
        </template>
        <div class="py-2 manage-widgets-body">
        <div class="d-flex justify-content-center">
            <div class="position-relative">
                <input v-model.trim="searchInput" class="search-input d-flex align-items-center" placeholder="Search Widget">
                <div class="search-icon"></div>
            </div>
        </div>
        <div class="w-100 mt-2">
            <div v-show="widgetsBySearch.length > 0" class="select-all">
                <div @click="toggleCheckAll()" class="check-box" :class="{'checked': isCheckedAll}">
                    <div class="check-box-img"></div>
                </div>
                <span class="pl-2">Select All</span>
            </div>
            <div class="d-flex align-items-center flex-wrap">
                <div @click="toggleCheckedWidget(widget)" class="select-widget" v-for="(widget, index) of widgetsBySearch" :key="index">
                    <div class="check-box" :class="{'checked': widget.enabled}">
                        <div class="check-box-img"></div>
                    </div>
                    <span :id="`widget-name-${widget.widget.key}`" class="px-2 text-truncate">{{widget.widget.value}}</span>
                    <b-popover :target="`widget-name-${widget.widget.key}`" triggers="hover" placement="top">
                      <span>{{ widget.widget.value }}</span>
                    </b-popover>
                </div>
                <div v-if="widgetsBySearch.length % 2" class="select-widget">
                </div>
            </div>
        </div>
        </div>
        <template v-slot:modal-footer>
          <div class="d-flex align-items-center">
            <b-button :disabled="isCheckedAll" @click="clickResetToDefault" class="mr-2 reset-to-default-btn">Reset to Default</b-button>
            <b-button @click="saveDashBoard" :disabled="!selectedWidgets.length" class="save-btn">
                <span>Save</span>
            </b-button>
          </div>
        </template>
  </b-modal>
</template>
<script>
import cloneDeep from 'lodash/cloneDeep'
import { mapActions } from 'vuex'
import toastMixin from '@/components/common/toastMixin'
export default {
  name: 'Overview',
  props: {
    id: {
      type: String
    },
    widgetsDashboard: {
      type: Array
    },
    dashboard: {
      type: String
    }
  },
  data() {
    return {
      searchInput: '',
      widgetsDashboardSettings: cloneDeep(this.widgetsDashboard)
    }
  },
  mixins: [
    toastMixin
  ],
  computed: {
    widgetsBySearch() {
      return this.searchInput ? this.widgetsDashboardSettings.filter(p => p.widget.value.toLowerCase().includes(this.searchInput.toLowerCase())) : cloneDeep(this.widgetsDashboardSettings)
    },
    isCheckedAll() {
      return this.widgetsBySearch.every(widget => widget.enabled)
    },
    selectedWidgets() {
      return this.widgetsDashboardSettings.filter(widget => widget.enabled)
    }
  },
  methods: {
    ...mapActions({
      saveWidgetsDashboard: `pf/manageWidgetDashboard/saveWidgetsDashboard`
    }),
    toggleCheckAll() {
      const isChecked = !this.isCheckedAll
      const widgetIds = this.widgetsBySearch.map(w => w.id)
      this.widgetsDashboardSettings.filter(w => widgetIds.includes(w.id)).forEach(w => {
        w.enabled = isChecked
      })
    },
    toggleCheckedWidget(widget) {
      const index = this.widgetsDashboardSettings.findIndex(p => p.id === widget.id)
      if (index !== -1) {
        this.widgetsDashboardSettings[index].enabled = !this.widgetsDashboardSettings[index].enabled
      }
    },
    async saveDashBoard() {
      try {
        const data = this.widgetsDashboardSettings.map(item => {
          return { widget: item.widget.key, enabled: item.enabled }
        })
        const params = {
          client_id: this.$route.params.client_id,
          dashboard: this.dashboard,
          payload: {
            data
          }
        }
        await this.saveWidgetsDashboard(params)
        this.vueToast('success', 'The widgets has been saved successfully.')
        this.$emit('changeSettings')
        this.$bvModal.hide(this.id)
      } catch (error) {
        console.log(error)
      }
    },
    resetModal() {
      this.widgetsDashboardSettings = cloneDeep(this.widgetsDashboard)
    },
    clickResetToDefault() {
      const widgetIds = this.widgetsBySearch.map(w => w.id)
      this.widgetsDashboardSettings.filter(w => widgetIds.includes(w.id)).forEach(w => {
        w.enabled = true
      })
      this.saveDashBoard()
    }
  },
  watch: {
    widgetsDashboard: {
      deep: true,
      immediate: true,
      handler(newValue) {
        this.widgetsDashboardSettings = cloneDeep(newValue)
      }
    }
  }
}
</script>
<style lang="scss" scoped>
.manage-widgets-body {
  min-height: 376px;
}
.multi-export-open-btn {
  padding: 10px 16px;
  border-radius: 1px;
  box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.05);
  border: solid 0.5px #e6e8f0;
  background-color: #fff;
}
.multi-export-open-btn:focus {
    outline: unset !important;
    background-color: #fff !important;
}
.title-modal {
    font-size: 14px;
    font-weight: 500;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.14;
    letter-spacing: 0.07px;
    text-align: left;
    color: #232f3e;
}
.multi-export-icon {
    width: 24px;
    height: 24px;
    background-image: url('~@/assets/img/icon/menu-icon.svg');
    background-size: 100%;
}
.search-input {
    position: relative;
    width: 320px;
    height: 32px;
    padding: 4px 14px 6px 42px;
    border-radius: 1px;
    box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.05);
    border: solid 1px #d2d6db;
    background-color: #ffffff;
}
.search-input::placeholder {
    font-size: 14px;
    font-weight: 500;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.14;
    letter-spacing: 0.07px;
    color: #667085;
    display: flex;
    align-items: center;
}
.search-input:focus {
    border-color: #146EB4;
}
.search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    content: '';
    width: 20px;
    height: 20px;
    background-image: url('~@/assets/img/icon/search-icon.svg');
    background-size: 100%;
}
.select-all {
    display: flex;
    align-items: center;
    width: 100%;
    height: 40px;
    border: solid 1px #e6e8f0;
    background-color: #fff;
}
.check-box {
    width: 30px;
    min-width: 30px;
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-right: solid 1px #e6e8f0 ;
}
.check-box-img {
    padding: 2px;
    border-radius: 4px;
    border: solid 1px #e6e8f0;
    background-color: #ffffff;
    width: 20px;
    height: 20px;
    background-image: url('~@/assets/img/icon/check-icon.svg');
    background-size: 100%;
    background-repeat: no-repeat;
}
.checked {
    .check-box-img {
       background-color: #205fdc;
    }
}
.select-widget {
    display: flex;
    align-items: center;
    width: 50%;
    height: 40px;
    border: solid 1px #e6e8f0;
    background-color: #fff;
    border-top: unset;
}
.select-widget:nth-child(2n) {
    border-left: unset;
}
.reset-to-default-btn {
  height: 36px;
}
.save-btn {
    width: 100px;
    height: 36px;
    padding: 10px 16px;
    border-radius: 1px;
    box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.05);
    border: solid 1px #254164;
    background-color: #254164;
    display: flex;
    align-items: center;
    justify-content: center;
    .export-img {
    width: 20px;
    height: 20px;
    background-image: url('~@/assets/img/icon/download.svg');
    background-size: 100%;
    }
    span {
        color: #fff;
        font-size: 14px;
        font-weight: normal;
        font-stretch: normal;
        font-style: normal;
        line-height: 1.43;
        letter-spacing: 0.07px;
    }
}
::v-deep .multiple-export-modal .modal-dialog {
  max-width: 516px !important;
}
::v-deep .multiple-export-modal .modal-header {
  padding: 16px 14.5px 0px;
  border-bottom: unset !important;
}
::v-deep .multiple-export-modal .modal-body {
   padding: 0px 8px;
}
::v-deep .multiple-export-modal .modal-footer {
  padding: 8px;
  border-top: unset !important;
}
::v-deep .export-widget-complete-modal .modal-dialog {
  max-width: 392px !important;
}
.export-widget-complete-modal {
  .export-complete {
    display: flex;
    flex-direction: column;
    align-items: center;
    .export-complete-msg {
      font-size: 18px;
      font-weight: normal;
      font-stretch: normal;
      font-style: normal;
      line-height: 1.33;
      letter-spacing: normal;
      text-align: center;
      color: #080e2c;
      margin-bottom: 19px;
    }
    .export-complete-list {
      padding-left: 0;
      margin-bottom: 16px;
      li {
        list-style: none;
      }
    }
    .export-complete-widget-name {
      font-size: 18px;
      font-weight: normal;
      font-stretch: normal;
      font-style: normal;
      line-height: 1.33;
      letter-spacing: normal;
      text-align: center;
      color: #0645ad;
    }
  }
}
</style>
