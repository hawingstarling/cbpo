<template>
  <b-modal
    :id="id"
    size="sync-size"
    variant="danger"
    centered
    title="Please confirm"
    @hidden="resetOptions"
  >
    <div class="confirmation-modal__body">
      Are you sure you want to start syncing the data from external data
      sources?
      <b-form-checkbox-group
        v-model="selectedRS"
        name="resource-checkboxes"
        class="resource-checkboxes mt-2"
        stacked
      >
        <div v-for="(source, index) in optionsRS" :key="`source-${index}`">
          <b-form-checkbox
            :value="source.value"
            :class="{ 'font-weight-bold': isSourceOptionsActive(source) }"
          >
            {{ source.text }}
          </b-form-checkbox>
          <!-- sub-options -->
          <div
            v-if="isSourceOptionsActive(source)"
            class="resource-checkboxes__sub"
          >
            <b-form-checkbox-group
              v-if="subOptions[source.subOptions].data.fields"
              v-model="subOptions[source.subOptions].data.fields"
              name="resource-checkboxes-sub"
              stacked
              class="mt-2"
            >
              <div class="ml-4">Fields</div>
              <b-form-checkbox
                v-for="fieldOption in subOptions[source.subOptions]
                  .selectOptions.fields"
                :key="`fieldOption-${fieldOption.value}`"
                :value="fieldOption.value"
                class="ml-5"
                @change.native="
                  onChangeSelection(
                    $event,
                    subOptions[source.subOptions].data.fields,
                    subOptions[source.subOptions].rules.fields
                  )
                "
              >
                {{ fieldOption.text }}
              </b-form-checkbox>
            </b-form-checkbox-group>
            <b-form-checkbox-group
              v-if="subOptions[source.subOptions].data.jobs"
              v-model="subOptions[source.subOptions].data.jobs"
              name="resource-checkboxes-sub"
              stacked
              class="mt-2"
            >
              <div class="ml-4">Jobs</div>
              <b-form-checkbox
                v-for="dataOption in subOptions[source.subOptions].selectOptions
                  .jobs"
                :key="`dataOption-${dataOption.value}`"
                :id="`dataOption-${dataOption.value}`"
                :value="dataOption.value"
                class="ml-5"
                @change.native="
                  onChangeSelection(
                    $event,
                    subOptions[source.subOptions].data.jobs,
                    subOptions[source.subOptions].rules.jobs
                  )
                "
                :disabled="optionDisabled(dataOption)"
              >
                {{ dataOption.text }}
              </b-form-checkbox>
            </b-form-checkbox-group>
            <b-form-checkbox-group
              v-if="subOptions[source.subOptions].data.options"
              v-model="subOptions[source.subOptions].data.options"
              stacked
              class="mt-2"
            >
              <div class="ml-4">Options</div>
              <b-form-checkbox
                v-for="dataOption in subOptions[source.subOptions].selectOptions
                  .options"
                :key="`dataOption-${dataOption.value}`"
                :id="`dataOption-${dataOption.value}`"
                :value="dataOption.value"
                class="ml-5"
                @change.native="
                  onChangeSelection(
                    $event,
                    subOptions[source.subOptions].data.options,
                    subOptions[source.subOptions].rules.options
                  )
                "
                :disabled="optionDisabled(dataOption)"
              >
                {{ dataOption.text }}
              </b-form-checkbox>
            </b-form-checkbox-group>
          </div>
          <!-- sub-options -->
        </div>
      </b-form-checkbox-group>
    </div>
    <template v-slot:modal-footer>
      <b-btn
        variant="warning"
        @click="handleSyncBulkSale()"
        :disabled="syncing || !hasSourceChosen"
      >
        <i class="icon-check"></i> Yes, I understand &amp; confirm!
      </b-btn>
      <b-btn variant @click="handleCloseModal()" :disabled="syncing">
        <i class="icon-close"></i> No
      </b-btn>
    </template>
  </b-modal>
</template>

<script>
import { mapActions } from 'vuex'
import {
  DATASOURCES,
  DATASOURCES_IGNORE,
  DATASOURCES_MAPPING,
  DATASOURCES_OPTIONS,
  DATASOURCES_OPTIONS_MAPPING
} from '@/shared/constants/sync.constant'
import editSaleItemMixins from '@/mixins/editMixins/editSaleItemMixins'
import toastMixin from '@/components/common/toastMixin'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'

export default {
  name: 'SyncModal',
  props: {
    id: {
      type: String,
      required: true
    },
    dataRow: {
      type: [Object, Array]
    }
  },
  data() {
    return {
      syncing: false,
      selectedRS: [],
      permissions,
      optionsRS: [
        {
          text: DATASOURCES_MAPPING[DATASOURCES.AC],
          value: DATASOURCES.AC,
          subOptions: DATASOURCES.AC
        },
        {
          text: DATASOURCES_MAPPING[DATASOURCES.DC],
          value: DATASOURCES.DC,
          subOptions: DATASOURCES.DC
        },
        {
          text: DATASOURCES_MAPPING[DATASOURCES.PF],
          value: DATASOURCES.PF,
          subOptions: DATASOURCES.PF
        }
      ],
      subOptions: {
        [DATASOURCES.AC]: {
          data: {
            options: []
          },
          selectOptions: {
            options: [
              {
                value: DATASOURCES_OPTIONS.AC_IS_FORCED,
                text:
                  DATASOURCES_OPTIONS_MAPPING[DATASOURCES_OPTIONS.AC_IS_FORCED]
              }
            ]
          },
          rules: {}
        },
        [DATASOURCES.DC]: {
          data: {
            fields: [DATASOURCES_OPTIONS.UPC, DATASOURCES_OPTIONS.BRAND],
            options: []
          },
          selectOptions: {
            fields: [
              {
                value: DATASOURCES_OPTIONS.UPC,
                text: DATASOURCES_OPTIONS_MAPPING[DATASOURCES_OPTIONS.UPC]
              },
              {
                value: DATASOURCES_OPTIONS.BRAND,
                text: DATASOURCES_OPTIONS_MAPPING[DATASOURCES_OPTIONS.BRAND]
              },
              {
                value: DATASOURCES_OPTIONS.COG,
                text: DATASOURCES_OPTIONS_MAPPING[DATASOURCES_OPTIONS.COG]
              },
              {
                value: DATASOURCES_OPTIONS.CHANNEL_BRAND,
                text: DATASOURCES_OPTIONS_MAPPING[DATASOURCES_OPTIONS.CHANNEL_BRAND]
              }
            ],
            options: [
              {
                value: DATASOURCES_OPTIONS.DC_IS_OVERRIDE,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.DC_IS_OVERRIDE
                  ]
              }
            ]
          },
          rules: {
            fields: ['min:1']
          }
        },
        [DATASOURCES.PF]: {
          data: {
            options: [],
            jobs: []
          },
          selectOptions: {
            jobs: [
              {
                value: DATASOURCES_OPTIONS.PF_SHIPPING_COST,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_SHIPPING_COST
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.PF_COG,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_COG
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.PF_TOTAL_COST,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_TOTAL_COST
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.PF_SEGMENT,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_SEGMENT
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.SKU_SKUVAULT,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.SKU_SKUVAULT
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.PF_INBOUND_FREIGHT_COST,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_INBOUND_FREIGHT_COST
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.PF_OUTBOUND_FREIGHT_COST,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_OUTBOUND_FREIGHT_COST
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.PF_FULFILLMENT_TYPE,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_FULFILLMENT_TYPE
                  ]
              },
              {
                value: DATASOURCES_OPTIONS.PF_USER_PROVIDED_COST,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_USER_PROVIDED_COST
                  ]
              }
            ],
            options: [
              {
                value: DATASOURCES_OPTIONS.PF_OVERRIDE,
                text:
                  // eslint-disable-next-line
                  DATASOURCES_OPTIONS_MAPPING[
                    DATASOURCES_OPTIONS.PF_OVERRIDE
                  ]
              }
            ]
          },
          rules: {
            options: ['min:1']
          }
        }
      }
    }
  },
  mixins: [editSaleItemMixins, toastMixin, PermissionsMixin],
  created() {
    if (this.hasPermission(this.permissions.client.isClient)) {
      this.optionsRS = this.optionsRS.filter(option => option.value !== DATASOURCES.DC)
    }
  },
  computed: {
    hasSourceChosen() {
      let isValid = false
      let requireOptionsSrcList = [ DATASOURCES.PF ]
      if (this.selectedRS && this.selectedRS.length > 0) {
        isValid = true
        if (this.selectedRS.some(RS => requireOptionsSrcList.includes(RS))) {
          if (!requireOptionsSrcList.some(option =>
            this.subOptions[option].data.jobs.length > 0
          )) {
            isValid = false
          }
        }
      }
      return isValid
    },
    optionDisabled() {
      return option => {
        switch (option.value) {
          case DATASOURCES_OPTIONS.AC_IS_FORCED:
            return this.totalItems > 10
          default:
            return false
        }
      }
    },
    isSourceOptionsActive() {
      return source =>
        source.subOptions && this.selectedRS.includes(source.value)
    }
  },
  methods: {
    ...mapActions({
      createBulkSync: `pf/bulk/createBulkSync`
    }),
    async onChangeSelection(e, selectedArray, rules) {
      await this.$nextTick()
      if (!rules) return
      if (rules.includes('min:1') && selectedArray.length === 0) {
        selectedArray.push(e.target.value)
      }
    },
    resetOptions() {
      this.selectedRS = []
      this.subOptions[DATASOURCES.AC].data = {
        options: []
      }
      this.subOptions[DATASOURCES.DC].data = {
        fields: [DATASOURCES_OPTIONS.UPC, DATASOURCES_OPTIONS.BRAND],
        options: []
      }
      this.subOptions[DATASOURCES.PF].data = {
        options: [],
        jobs: []
      }
    },
    prepareSyncData() {
      const sources = {
        sources:
          this.selectedRS.filter(rs => !DATASOURCES_IGNORE.includes(rs)) || []
      }
      const optionsAC = this.selectedRS.includes(DATASOURCES.AC)
        ? {
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.AC_IS_FORCED]: this.subOptions[
            DATASOURCES.AC
          ].data.options.includes(DATASOURCES_OPTIONS.AC_IS_FORCED)
        }
        : {}
      const optionsDC = this.selectedRS.includes(DATASOURCES.DC)
        ? {
          [DATASOURCES_OPTIONS.DC_FIELDS]: this.subOptions[DATASOURCES.DC]
            .data.fields,
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.DC_IS_OVERRIDE]: this.subOptions[
            DATASOURCES.DC
          ].data.options.includes(DATASOURCES_OPTIONS.DC_IS_OVERRIDE)
        }
        : {}
      const optionsPF = this.selectedRS.includes(DATASOURCES.PF)
        ? {
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.PF_SHIPPING_COST]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_SHIPPING_COST),
          // eslint-disable-next-line
          [DATASOURCES_OPTIONS.PF_COG]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_COG),
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.PF_TOTAL_COST]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_TOTAL_COST),
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.PF_SEGMENT]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_SEGMENT),
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.SKU_SKUVAULT]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.SKU_SKUVAULT),
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.PF_INBOUND_FREIGHT_COST]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_INBOUND_FREIGHT_COST),
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.PF_OUTBOUND_FREIGHT_COST]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_OUTBOUND_FREIGHT_COST),
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.PF_FULFILLMENT_TYPE]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_FULFILLMENT_TYPE),
          // eslint-disable-next-line
          [DATASOURCES_OPTIONS.PF_USER_PROVIDED_COST]: this.subOptions[
            DATASOURCES.PF
          ].data.jobs.includes(DATASOURCES_OPTIONS.PF_USER_PROVIDED_COST),
          // eslint-disable-next-line
            [DATASOURCES_OPTIONS.PF_OVERRIDE]: this.subOptions[
            DATASOURCES.PF
          ].data.options.includes(DATASOURCES_OPTIONS.PF_OVERRIDE)
        }
        : {}
      return Object.assign(
        this.latestBulkDataForApi('sync'),
        ...[sources, optionsAC, optionsDC, optionsPF]
      )
    },
    async handleSyncBulkSale() {
      this.syncing = true

      const data = {
        params: {
          client_id: this.clientID
        },
        payload: this.prepareSyncData()
      }
      await this.createBulkSync(data).then(resp => {
        if (resp.status === 200) {
          this.$bus.$emit('updateBulkProgress')
          this.handleCloseModal()
          this.vueToast('success', this.BULK_PROGRESS.syncCreated)
        } else {
          this.vueToast('error', resp.data.message)
        }
      })
      this.syncing = false
    }
  }
}
</script>

<style lang="scss" scoped>
@media (min-width: 576px) {
  /deep/ .modal-sync-size {
    max-width: 520px;
  }
}
.resource-checkboxes {
  /deep/ .custom-checkbox {
    margin-top: 0.5rem;
  }
  /deep/ .custom-control-label {
    padding-top: 1px;
  }
}
</style>
