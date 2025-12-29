<template>
  <b-card class="progress-detail">
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong>
              <i class="fa fa-tasks mr-1"></i>
              Bulk Progress / {{ params.bulk_id }}
            </strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <div v-if="currentBulkProgressDetail">
      <b-row>
        <b-col class="col-6" v-if="currentBulkProgressDetail.meta">
          <div class="d-flex" v-if="currentBulkProgressDetail.meta.user_info">
            <img
              :src="currentBulkProgressDetail.meta.user_info.avatar || placeholderURL"
              :alt="currentBulkProgressDetail.meta.user_info.first_name"
              class="progress-detail__avatar"
            />
            <div>
              <div class="progress-detail__name">
                {{ getFullName(currentBulkProgressDetail.meta.user_info) }}
                <div class="email">
                  <span>&lt;</span>
                  {{ currentBulkProgressDetail.meta.user_info.email }}
                  <span>&gt;</span>
                </div>
              </div>
              <div class="progress-detail__created">
                Created: {{ getDateTime(currentBulkProgressDetail.created) }}
              </div>
              <div class="progress-detail__created">
                Modified: {{ getDateTime(currentBulkProgressDetail.modified) }}
              </div>
            </div>
          </div>
          <div v-else>Anonymous</div>
        </b-col>
        <b-col class="col-6">
          <div
            class="label-wrapper mb-1 d-flex align-items-center"
            v-if="currentBulkProgressDetail.meta.command"
          >
            <strong class="command-label m-0">Command</strong>
            <b-badge
              :variant="getAssetsByCommand(currentBulkProgressDetail.meta.command, 'variant')"
              class="ml-3"
              size="lg"
              pill
            >
              <i :class="[`fa fa-${getAssetsByCommand(currentBulkProgressDetail.meta.command, 'icon')}`]" />
              <span class="ml-1 text-uppercase">
                {{ currentBulkProgressDetail.meta.command }}
              </span>
            </b-badge>
          </div>
          <div class="label-wrapper mb-2 d-flex align-items-center">
            <p class="command-label m-0">Progress</p>
            <b-progress
              :max="100"
              show-progress
              :animated="!isProgressCompleted(currentBulkProgressDetail.progress)"
              variant="success"
              class="progress-detail__progress ml-3"
            >
              <b-progress-bar
                :value="currentBulkProgressDetail.progress"
                :label="`${currentBulkProgressDetail.progress}%`"
              />
            </b-progress>
            <b-button v-if="hasRevertBulkEdit" class="ml-5" size="sm" variant="secondary" @click="openRevertConfirm" >Revert</b-button>
            <b-modal id="revert_confirm" variant="danger" centered title="Please confirm">
              <div>This operation will revert all the changes to what they were before applying the bulk processing.</div>
              <template v-slot:modal-footer>
                <b-button variant="warning" @click="handleRevertBulkEdit()">
                    <i class="icon-check"></i> Yes, I understand &amp; confirm!
                </b-button>
                <b-button variant @click="$bvModal.hide('revert_confirm')">
                    <i class="icon-close"></i> No
                </b-button>
              </template>
            </b-modal>
          </div>
        </b-col>
      </b-row>
      <b-alert variant="primary" show class="text-center mt-2">
        <span class="mx-3">
          Total
          <b-badge variant="primary" class="px-1">
            {{ numberFormat(currentBulkProgressDetail.summary.total) }}
          </b-badge>
        </span>
        <span class="mx-3">
          Success
          <b-badge variant="success" class="px-1">
            {{ numberFormat(currentBulkProgressDetail.summary.success) }}
          </b-badge>
        </span>
        <span class="mx-3">
          Error
          <b-badge variant="danger" class="px-1">
            {{ numberFormat(currentBulkProgressDetail.summary.error) }}
          </b-badge>
        </span>
      </b-alert>
      <b-card-group class="progress-detail__item-list my-3">
        <!-- Filter Card - Show filter condition from SDK -->
        <b-card
          header="Filter"
          header-class="text-uppercase font-weight-bold"
          v-if="isPropertyExisted(currentBulkProgressDetail.meta.query, 'filter')"
        >
          <div
            v-html="$CBPO.dataQueryManager().getFilterReadableFromFilter(currentBulkProgressDetail.meta.query.filter, dsColumns)"
          />
          <div
            class="d-flex mt-2"
            v-if="isPropertyExisted(currentBulkProgressDetail.meta.query, 'timezone')"
          >
            <strong>Timezone: </strong>
            <div class="ml-1">
              {{ getTimezoneTitle(currentBulkProgressDetail.meta.query.timezone) }}
            </div>
          </div>
        </b-card>
        <!-- Query Card - Show selected items or matched items -->
        <b-card
          :header="targetedItems(currentBulkProgressDetail.meta.query)"
          header-class="text-uppercase font-weight-bold"
        >
          <ul class="progress-detail__list">
            <li
              v-for="(id, index) in currentBulkProgressDetail.meta.ids"
              :key="index"
            >
              {{ id }}
            </li>
          </ul>
        </b-card>
        <!-- Source Card - Show sync datasource (Sync command only) -->
        <b-card
          header="Sources"
          header-class="text-uppercase font-weight-bold"
          v-if="command(currentBulkProgressDetail.meta, 'sync')"
        >
          <div>
            <ul
              class="progress-detail__list"
              v-if="currentBulkProgressDetail.meta.sources"
            >
              <li
                v-for="(source, index) in currentBulkProgressDetail.meta.sources"
                :key="index"
              >
                {{ DATASOURCES_MAPPING[source] }}
              </li>
            </ul>
          </div>
          <div
            v-for="(option, index) in DATASOURCES_OPTIONS"
            :key="index"
          >
            <ul
              class="progress-detail__list"
              v-if="currentBulkProgressDetail.meta[option] && option !== 'dc_fields'"
            >
              <li>
                [ {{ DATASOURCES_OPTIONS_MAPPING[option] }} ]
              </li>
            </ul>
            <ul
              class="progress-detail__list"
              v-if="currentBulkProgressDetail.meta[option] && option === 'dc_fields'"
            >
              <li>
                [
                <span
                  v-for="(col, index) in currentBulkProgressDetail.meta[option]"
                  :key="index"
                >
                  {{ DATASOURCES_OPTIONS_MAPPING[col] }}
                  <span
                    v-if="index < currentBulkProgressDetail.meta[option].length - 1"
                  >,</span>
                </span>
                ]
              </li>
            </ul>
          </div>
        </b-card>
        <!-- Actions Card - Show actions user chose (Edit & Delete command only) -->
        <b-card
          header="Actions"
          header-class="text-uppercase font-weight-bold"
          v-if="command(currentBulkProgressDetail.meta, ['edit', 'delete'])"
        >
          <div v-if="currentBulkProgressDetail.meta.command === 'delete'">
            DELETE
          </div>
          <ul class="progress-detail__list">
            <li
              v-for="(update, index) in currentBulkProgressDetail.meta.updates"
              :key="index"
              v-html="buildExpression(update)"
            />
          </ul>
        </b-card>
      </b-card-group>

      <BulkProgressErrors
        title="Progress Details"
        :listItems="importItems"
        v-model="importParams"
      />
    </div>
  </b-card>
</template>

<script>
import { isArray } from 'lodash'
import { mapActions, mapGetters } from 'vuex'
import { filterColumnName } from '@/shared/filters'
import bulkProgressMixins from '@/mixins/bulkProgressMixins'
import placeholderURL from '@/assets/img/profile-placeholder.png'
import BulkProgressErrors from './BulkProgressErrors'
import toastMixin from '@/components/common/toastMixin'

export default {
  name: 'PFBulkProgressDetail',
  mixins: [bulkProgressMixins, toastMixin],
  components: {
    BulkProgressErrors
  },
  filters: {
    filterColumnName
  },
  data() {
    return {
      params: {},
      importParams: {
        module: this.$route.params.module,
        search: '',
        page: 1,
        isUpdatedSate: false
      },
      placeholderURL
    }
  },
  computed: {
    ...mapGetters({
      currentBulkProgressDetail: `pf/bulk/currentBulkProgressDetail`,
      importItems: `pf/bulk/importItems`,
      dsColumns: `pf/analysis/dsColumns`
    }),
    targetedItems() {
      return query =>
        query && query.filter ? 'Matched Items' : 'Selected Items'
    },
    command() {
      return (metaSource, command) => {
        if (metaSource) {
          return isArray(command) ? command.includes(metaSource.command) : metaSource.command === command
        }
        return false
      }
    },
    hasRevertBulkEdit() {
      if (this.currentBulkProgressDetail && this.isUpdatedSate) {
        return this.currentBulkProgressDetail.meta.command === 'edit' && this.currentBulkProgressDetail.status !== 'reverted'
      }
      return false
    }
  },
  methods: {
    ...mapActions({
      getBulkProgressDetail: `pf/bulk/getBulkProgressDetail`,
      revertBulkEdit: `pf/bulk/revertBulkEdit`,
      getImportItems: `pf/bulk/getImportItems`,
      fetchDSColumns: `pf/analysis/fetchDSColumns`,
      fetchAllDataSourceIDs: `pf/analysis/fetchAllDataSourceIDs`
    }),
    getFullName(userInfo) {
      return `${userInfo.first_name} ${userInfo.last_name}`
    },
    openRevertConfirm() {
      this.$bvModal.show('revert_confirm')
    },
    async handleRevertBulkEdit() {
      try {
        await this.revertBulkEdit(this.params)
        this.vueToast('success', 'Your bulk process has been queued for reverting.')
      } catch (error) {
        this.vueToast('error', error.response.data.message)
      }
      this.$bvModal.hide('revert_confirm')
    },
    getCurrentBulkProgressDetail() {
      this.getBulkProgressDetail(this.params)
      this.isUpdatedSate = true
    }
  },
  async created() {
    this.params.client_id = this.$route.params.client_id
    this.params.bulk_id = this.$route.params.bulk_id
    this.importParams.bulk_id = this.$route.params.bulk_id
    await this.fetchAllDataSourceIDs({client_id: this.params.client_id})
    this.getImportItems(this.importParams)
    this.fetchDSColumns(this.params)
    this.getCurrentBulkProgressDetail()
  },
  watch: {
    importParams: {
      deep: true,
      handler(newVal) {
        this.getImportItems(newVal)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import "./BulkProgressDetail.scss";
</style>
