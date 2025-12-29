<template>
  <b-modal :id="id" variant="danger" centered title="Please confirm">
    <div
      class="confirmation-modal__body"
      v-if="internalData && internalData.data"
    >
      Are you sure you want to delete this sale item?
    </div>
    <div class="confirmation-modal__body" v-if="internalBulkData.length">
      Are you sure you want to delete these sale items?
    </div>
    <template v-slot:modal-footer>
      <b-btn
        variant="warning"
        v-if="internalData && internalData.data"
        @click="handleDeleteSingleSale()"
        :disabled="deleting"
      >
        <i class="icon-check"></i> Yes, I understand &amp; confirm!
      </b-btn>
      <b-btn
        variant="warning"
        v-if="internalBulkData.length"
        @click="handleDeleteBulkSale()"
        :disabled="deleting"
      >
        <i class="icon-check"></i> Yes, I understand &amp; confirm!
      </b-btn>
      <b-btn variant @click="handleCloseModal()" :disabled="deleting">
        <i class="icon-close"></i> No
      </b-btn>
    </template>
  </b-modal>
</template>

<script>
import { mapActions } from 'vuex'
import { UNIQUE_KEY_BE } from '@/shared/constants/column.constant'
import editSaleItemMixins from '@/mixins/editMixins/editSaleItemMixins'
import toastMixin from '@/components/common/toastMixin'

export default {
  name: 'ConfirmationModal',
  props: {
    id: {
      type: String,
      required: true
    },
    dataRow: {
      type: [Object, Array]
    },
    columns: {
      type: Array
    }
  },
  data() {
    return {
      deleting: false
    }
  },
  mixins: [editSaleItemMixins, toastMixin],
  methods: {
    ...mapActions({
      deleteSaleItem: `pf/analysis/deleteSaleItem`,
      deleteBulkSaleItems: `pf/bulk/deleteBulkSaleItems`
    }),
    async handleDeleteSingleSale() {
      this.deleting = true
      const data = {
        client_id: this.clientID,
        id: this.internalData.data[UNIQUE_KEY_BE].base
      }
      await this.deleteSaleItem(data).then(resp => {
        this.$CBPO.$bus.$emit(
          `SINGLE_DELETE${this.sdkID}`,
          this.internalData.pk_id_sdk
        )
        this.handleCloseModal()
        this.vueToast('success', 'Deleted successfully')
      })
      this.deleting = false
    },
    async handleDeleteBulkSale() {
      this.deleting = true
      const data = {
        params: {
          client_id: this.clientID
        },
        payload: this.latestBulkDataForApi('delete')
      }
      await this.deleteBulkSaleItems(data).then(resp => {
        this.$CBPO.$bus.$emit(`BULK_DELETE${this.sdkID}`)
        this.$bus.$emit('updateBulkProgress')
        this.handleCloseModal()
        this.vueToast('success', this.BULK_PROGRESS.deleteCreated)
      })
      this.deleting = false
    }
  }
}
</script>
