<template>
  <div :class="{'d-none': !configObj.visible}" class="cbpo-timezone-selector">
    <slot :openModal="openTimezoneModal" name="button">
      <b-btn
        id="cbpo-timezone-value"
        class="cbpo-timezone-button"
        size="sm"
        variant="outline-secondary"
        @click="openTimezoneModal()"
        :disabled="configObj.readonly === undefined ? false : configObj.readonly"
      >
        <i class="fa fa-globe" aria-hidden="true"></i>
        {{ timezoneTitle }}
      </b-btn>
      <b-popover custom-class="custom-timezone-tooltip" target="cbpo-timezone-value" triggers="hover" placement="top">
        {{ timezoneValue }}
      </b-popover>
    </slot>
    <!-- Timezone Settings Modal -->
    <b-modal
      :id="modalID"
      title="Time Zone Settings"
      dialog-class="cbpo-custom-modal"
      no-close-on-backdrop
      @close="closeTimezoneModal()"
      scrollable
    >
      <div class="d-flex justify-content-center mb-3">
          <div class="position-relative">
              <input v-model.trim="searchInput" class="search-timezone-input d-flex align-items-center" placeholder="Search time zone">
              <div class="search-timezone-icon"></div>
          </div>
      </div>
      <b-form-group v-if="timezoneBySearchOptions.length" class="cbpo-timezone-list">
        <b-form-radio
          v-for="(item, index) in timezoneBySearchOptions"
          :key="index"
          :id="`timezone-item-${index}`"
          :value="item.utc[0]"
          name="timezone-item"
          v-model="currentTimezone"
        >
          <span>
            {{ `${ item.text }; ${ item.abbr.length === 2 ? item.abbr : item.value } ` }}
          </span>
          <i class="fa fa-info-circle text-primary mx-1" v-b-popover.hover.top="`${ item.utc.join(', ') }`" title="Locations" aria-hidden="true"></i>
          <span :key="modalKey" v-if="isShowCurrentTime" class="current-time">{{ showCurrentTimeOfTZ(item.utc[0]) }}</span>
        </b-form-radio>
      </b-form-group>
      <template v-slot:modal-footer>
        <div class="footer-actions d-flex w-100 align-items-center justify-content-between">
          <div class="footer-actions__left d-flex align-items-center">
            <button @click="setLocalTimezone()" class="cbpo-btn">
              <span>Use Local Time Zone</span>
            </button>
            <b-form-checkbox
              id="show-current-time"
              v-model="isShowCurrentTime"
              class="ml-2"
            >
              Show current time
            </b-form-checkbox>
          </div>
          <div class="footer-actions__right">
            <button @click="applyTimezone()" class="cbpo-btn btn-primary">
              <span>Apply</span>
            </button>
            <button @click="closeTimezoneModal()" class="ml-2 cbpo-btn">
              <span>Close</span>
            </button>
          </div>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
import CBPO from '@/services/CBPO'
import moment from 'moment-timezone'
const timezoneData = require('./timezoneData.json')
const DAYLIGHT_SAVING_TIME_ZONES = {
  PT: [{
    value: 'Pacific Daylight Time',
    abbr: 'PDT'
  },
  {
    value: 'Pacific Standard Time',
    abbr: 'PST'
  }],
  CT: [{
    value: 'Central Daylight Time',
    abbr: 'CDT'
  },
  {
    value: 'Central Standard Time',
    abbr: 'CST'
  }],
  ET: [{
    value: 'Eastern Daylight Time',
    abbr: 'EDT'
  },
  {
    value: 'Eastern Standard Time',
    abbr: 'EST'
  }],
  MT: [{
    value: 'Mountain Daylight Time',
    abbr: 'MDT'
  },
  {
    value: 'Mountain Standard Time',
    abbr: 'MST'
  }]
}
export default {
  name: 'TimezoneSelector',
  props: {
    columns: Object,
    configObj: Object
  },
  data() {
    return {
      modalID: 'cbpo-timezone-selector-modal',
      timezoneOptions: timezoneData,
      currentTimezone: this.configObj.storable ? localStorage.getItem('_cbpo_selected_time_zone') || this.configObj.utc : this.configObj.utc,
      searchInput: '',
      modalKey: 0,
      isShowCurrentTime: false
    }
  },
  computed: {
    globalTimezoneState() {
      return (
        CBPO.channelManager()
          .getChannel()
          .getTimezoneSvc()
          .getTimezone() || this.currentTimezone
      )
    },
    currentTimezoneUTC() {
      // special case
      return this.timezoneOptions[this.findUTCIndex(this.configObj.storable ? this.currentTimezone : this.globalTimezoneState)]
    },
    timezoneTitle() {
      // return this.currentTimezoneUTC
      //   ? `UTC${this.convertNumberToTime(this.currentTimezoneUTC.offset)} (${
      //     this.currentTimezoneUTC.abbr
      //   })`
      //   : ''
      // return this.currentTimezoneUTC
      //   ? `${this.currentTimezoneUTC.text} (${
      //     this.currentTimezoneUTC.abbr
      //   })`
      //   : ''
      let title = ''
      if (this.currentTimezoneUTC) {
        title = `${this.currentTimezoneUTC.text_utc} (${this.currentTimezoneUTC.abbr})`
        if (this.currentTimezoneUTC.isdst) {
          for (const [key, value] of Object.entries(DAYLIGHT_SAVING_TIME_ZONES)) {
            if (this.currentTimezoneUTC.abbr === key) {
              title = moment().tz(this.globalTimezoneState).format('z') === value[0].abbr ? `UTC${this.convertNumberToTime(this.currentTimezoneUTC.offset)} (${value[0].abbr})`
                : `UTC${this.convertNumberToTime(this.currentTimezoneUTC.offset - 1)} (${value[1].abbr})`
            }
          }
        }
      }
      return title
    },
    timezoneValue() {
      const isdst = Object.keys(DAYLIGHT_SAVING_TIME_ZONES).includes(this.currentTimezoneUTC.abbr)
      if (isdst) {
        const suffixed = this.timezoneTitle.slice(11, 14)
        for (let timezone of Object.values(DAYLIGHT_SAVING_TIME_ZONES)) {
          for (let item of timezone) {
            if (item.abbr === suffixed) return item.value
          }
        }
      }
      return this.currentTimezoneUTC.value
    },
    timezoneBySearchOptions() {
      return this.searchInput.length ? this.timezoneOptions.filter(timezone => timezone.text.toLowerCase().includes(this.searchInput.toLowerCase()) || timezone.abbr.toLowerCase().includes(this.searchInput.toLowerCase()) || timezone.value.toLowerCase().includes(this.searchInput.toLowerCase())) : this.timezoneOptions
    }
  },
  methods: {
    setGlobalTimezoneState(timezone) {
      if (timezone) {
        CBPO.channelManager()
          .getChannel()
          .getTimezoneSvc()
          .setTimezone(timezone)
      }
    },
    findUTCIndex(datetime) {
      return this.timezoneOptions.findIndex((item) =>
        item.utc.find((utcItem) => utcItem === datetime)
      )
    },
    toggleTimezoneModal(isOpen = false) {
      isOpen
        ? this.$bvModal.show(this.modalID)
        : this.$bvModal.hide(this.modalID)
    },
    openTimezoneModal() {
      this.modalKey += 1
      this.toggleTimezoneModal(true)
    },
    closeTimezoneModal() {
      this.toggleTimezoneModal()
    },
    applyTimezone() {
      this.setGlobalTimezoneState(this.currentTimezone)
      this.$emit('update', this.currentTimezone)
      if (this.configObj.storable) localStorage.setItem('_cbpo_selected_time_zone', this.currentTimezone)
      this.closeTimezoneModal()
    },
    setLocalTimezone() {
      const offset = new Date().getTimezoneOffset() / (-60)
      const tz = moment.tz.guess()
      let tzData = [...timezoneData].filter((item) => item.offset === offset).find(item => item.utc.includes(tz))
      this.currentTimezone = tzData.utc[0]
      this.applyTimezone()
    },
    convertNumberToTime(number) {
      const convertTime = (num) =>
        moment.utc(moment.duration(num, 'h').asMilliseconds()).format('HH:mm')
      if (number > 0) {
        return '+' + convertTime(number)
      } else if (number < 0) {
        return '-' + convertTime(-number)
      }
      return ''
    },
    showCurrentTimeOfTZ(timeZone) {
      try {
        const currentDate = new Date()
        const options = {
          timeZone,
          hour: '2-digit',
          minute: '2-digit',
          month: '2-digit',
          day: '2-digit'
        }

        return Intl.DateTimeFormat('en-US', options).format(currentDate)
      } catch (error) {
        console.error(`Error with time zone: ${timeZone}`, error)
        return 'Invalid time zone'
      }
    }
  },
  created() {
  },
  watch: {
    currentTimezoneUTC: {
      immediate: true,
      handler: function(val) {
        this.currentTimezone = val.utc[0]
      }
    }
  }
}
</script>

<style lang="scss" scoped>
::v-deep .modal-dialog {
  @media (min-width: 768px) {
    min-width: 600px;
  }
}
.cbpo-timezone-button {
  font-size: 12px;
  color: #23282c;
}
.cbpo-timezone-list {
  border: 1px solid #d9d9d9;
  .custom-control {
    border-bottom: 1px solid #d9d9d9;
    padding-left: calc(1.5rem + 15px);
    &:last-child {
      border-bottom: 0;
    }
    &:hover {
      background-color: rgba(194, 219, 255, 0.5);
    }
    label {
      cursor: pointer;
      display: block;
      padding: 10px 15px;
      &::after, &::before {
        top: 0.75rem !important
      }
    }
  }
  .current-time {
    width: 150px !important;
    text-align: right;
    padding-right: 4px
  }
}

::v-deep.cbpo-timezone-list .custom-control-label {
  width:100%;
  display:flex;
  justify-content:space-between;
  align-items:center;
  span {
    width:90%;
  }

  i {
    font-size:12px;
    cursor:pointer
  }
}
.search-timezone-input {
    position: relative;
    width: 320px;
    height: 32px;
    padding: 4px 14px 6px 42px;
    border-radius: 1px;
    box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.05);
    border: solid 1px #d2d6db;
    background-color: #ffffff;
}
.search-timezone-input::placeholder {
  font-size: 12px;
  font-weight: 500;
  font-stretch: normal;
  font-style: 12px;
  line-height: 1.14;
  letter-spacing: 0.07px;
  color: #73818F;
  display: flex;
  align-items: center;
}
.search-timezone-input:focus {
    border-color: #146EB4;
}
.search-timezone-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    content: '';
    width: 20px;
    height: 20px;
    background-image: url('~@/assets/images/icons/search-icon.svg');
    background-size: 100%;
}
</style>
