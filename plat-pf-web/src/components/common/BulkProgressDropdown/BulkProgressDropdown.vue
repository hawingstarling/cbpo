<template>
  <b-button-group class="mx-1">
    <div class="warp-save">
      <div class="bulk-dropdown">
        <b-dropdown text="Bulk" right variant="secondary" size="sm" :disabled="isLoading">
          <template v-slot:button-content>
            <span class="view-combine-icon mr-1">
              <div class="bulk-icon"></div>
            </span>
            <span class="mr-1">Bulk</span>
            <span
              class="bulk-dropdown__count"
              v-if="bulkList && bulkList.count_processing"
            >
              {{ bulkList.count_processing }}
            </span>
          </template>
          <template v-if="hasBulkList">
            <li
              v-for="qBulk in quickSelectBulks"
              :key="'quick-filter-' + qBulk.id"
              class="bulk-dropdown__qbulk-item"
            >
            <div role="menuitem" class="dropdown-item d-flex justify-content-between">
              <span>
                <i
                  :class="[
                    `fa fa-${getAssetsByCommand(qBulk.meta.command, 'icon')}`,
                    getAssetsByCommand(qBulk.meta.command, 'variant')
                  ]"
                />
                {{ numberFormat(qBulk.summary.total) }} items
                <span v-if="qBulk.meta.user_info">
                  by {{ getFullName(qBulk.meta.user_info) }}
                </span>
                ({{ qBulk.modified | moment("MM/DD/YYYY") }})
              </span>
              <span class="ml-1">
                <span
                  class="bulk-dropdown__progress"
                  :class="
                    `bulk-dropdown__progress--${
                      isProgressCompleted(qBulk.progress)
                        ? 'success'
                        : 'in-progress'
                    }`
                  "
                >
                  {{ qBulk.progress }}%
                </span>
                <router-link
                  :to="{
                    name: 'PFBulkProgressDetail',
                    params: { bulk_id: qBulk.id, module: qBulk.meta.module }
                  }"
                  class="bulk-dropdown__view"
                  target="_blank"
                >
                  View
                </router-link>
              </span>
              </div>
            </li>
            <b-dropdown-divider />
            <div class="dropdown-item d-flex justify-content-between border-0 item-update-status">
              <span :key="updateStatusKey"><i class="fa fa-clock-o"></i> Updating status in {{countdownTime}}</span>
              <b-button @click="updateStatus" class="rounded button-update-status pt-0" size="sm">or now</b-button>
            </div>
            <b-dropdown-divider v-if="bulkList && bulkList.count > quickSelectBulks.length"/>
            <b-dropdown-item
              v-if="bulkList && bulkList.count > quickSelectBulks.length && hasPermission(permissions.sale.bulkProcessingView)"
              :href="
                $router.resolve({
                  name: 'PFBulkProgress'
                }).href
              "
              target="_blank"
            >
              <i class="fa fa-folder"></i> More bulk processing ...
            </b-dropdown-item>
          </template>
          <template v-else>
            <b-dropdown-item>
              <i class="fa fa-exclamation-circle" />
              There is no bulk processing progress.
            </b-dropdown-item>
          </template>
        </b-dropdown>
      </div>
    </div>
  </b-button-group>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import bulkProgressMixins from '@/mixins/bulkProgressMixins'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'

export default {
  name: 'BulkProgressDropdown',
  mixins: [bulkProgressMixins, PermissionsMixin],
  data() {
    return {
      bulkTimer: null,
      idleTimer: null,
      idleTime: 0,
      routeNames: ['PFAnalysis'],
      activeEvents: [
        'mousedown',
        'mousemove',
        'keypress',
        'scroll',
        'touchstart'
      ],
      updateStatusKey: false,
      updateStatusTimer: null,
      countdownTime: 10,
      permissions,
      isLoading: true
    }
  },
  computed: {
    ...mapGetters({
      bulkList: `pf/bulk/bulkList`,
      quickSelectBulks: 'pf/bulk/quickSelectBulks'
    }),
    hasBulkList() {
      return this.bulkList && this.bulkList.count > 0
    }
  },
  methods: {
    ...mapActions({
      getBulkList: `pf/bulk/getBulkList`
    }),
    async handleGetBulk() {
      this.isLoading = true
      let payload = {
        client_id: this.$route.params.client_id,
        ignoreLoading: true
      }
      try {
        await this.getBulkList(payload)
      } catch (error) {
        console.error('Get bulk list failed:', error)
      } finally {
        this.isLoading = false
      }
    },
    setBulkTimer() {
      if (this.routeNames.includes(this.$route.name)) {
        this.bulkTimer = setInterval(() => {
          this.handleGetBulk()
        }, 10000)
        this.updateStatusTimer = setInterval(() => {
          this.countdownTime--
          if (this.countdownTime === 0) {
            this.countdownTime = 10
          }
          this.updateStatusKey = !this.updateStatusKey
        }, 1000)
      }
    },
    setIdleTimer() {
      this.idleTimer = setInterval(() => {
        this.idleTime++
      }, 1000)
    },
    updateStatus() {
      this.clearBulkTimer()
      this.handleGetBulk()
      this.setBulkTimer()
      this.countdownTime = 10
      this.updateStatusKey = !this.updateStatusKey
    },
    activeFunction() {
      this.clearIdleTimer()
      this.setIdleTimer()
      if (!this.bulkTimer) {
        this.handleGetBulk()
        this.setBulkTimer()
      }
    },
    clearBulkTimer() {
      clearInterval(this.bulkTimer)
      this.bulkTimer = null
      clearInterval(this.updateStatusTimer)
      this.updateStatusTimer = null
    },
    clearIdleTimer() {
      clearInterval(this.idleTimer)
      this.idleTimer = null
      this.idleTime = 0
    }
  },
  created() {
    this.setBulkTimer()
    this.setIdleTimer()
  },
  mounted() {
    // force update bulk progress from EDIT FORM, then reset interval
    this.$bus.$on('updateBulkProgress', () => {
      this.clearBulkTimer()
      this.handleGetBulk()
      this.setBulkTimer()
    })
    // clearBulkTimer when client's not active on Tab of this site to secure our baby server.
    window.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        setTimeout(() => {
          this.clearBulkTimer()
        }, 10000)
      }
    })
    // setBulkTimer when client's active
    if (this.routeNames.includes(this.$route.name)) {
      this.activeEvents.forEach(name => {
        document.addEventListener(name, this.activeFunction, true)
      })
    }
  },
  watch: {
    // clearIdleTimer when client opens our site and go away for a while (2 minutes)...
    idleTime(newValue) {
      if (newValue > 30) {
        this.clearBulkTimer()
        this.countdownTime = 10
        this.updateStatusKey = !this.updateStatusKey
      }
    }
  },
  beforeDestroy() {
    this.$bus.$off('updateBulkProgress')
    this.activeEvents.forEach(name => {
      document.removeEventListener(name, this.activeFunction, true)
    })
    this.clearBulkTimer()
    this.clearIdleTimer()
  }
}
</script>

<style lang="scss" scoped>
.warp-save {
  // border: 1px solid transparent;
  // padding: 1px 0;
  border-radius: 4px;
  &--solid {
    display: flex;
    border-color: #737373;
    padding: 1px 4px 1px 4px;
  }
}
.item-update-status {
  height: 28px;
}
@media screen and (max-width: 650px) {
  .warp-save {
    &--solid {
      display: block;
    }
  }
}
.bulk-dropdown {
  &__count {
    display: inline-block;
    width: 15px;
    padding: 1px 0;
    font-size: 8px;
    background-color: #ffc107;
    border-radius: 50%;
    vertical-align: 1px;
    font-weight: bold;
  }
  &__progress {
    display: inline-block;
    font-size: 9px;
    padding: 0 5px;
    color: #fff;
    font-weight: bold;
    &--success {
      background-color: #4dbd74;
    }
    &--in-progress {
      background-color: #f86c6b;
    }
  }
  &__view {
    display: inline-block;
    font-size: 11px;
    padding: 0;
    padding-left: 10px;
  }
  &__qbulk-item {
    cursor: default;
    .primary {
      color: #20a8d8;
    }
    .success {
      color: #4dbd74;
    }
    .danger {
      color: #f86c6b;
    }
  }
}
::v-deep .dropdown-toggle {
  display: flex;
  align-items: center;
  .view-combine-icon {
    display: flex;
    align-items: center;
    .bulk-icon {
      background-image: url('~@/assets/img/icon/bulk-icon.svg');
      width: 14px;
      height: 14px;
      background-size: 100%;
    }
  }
}
</style>
