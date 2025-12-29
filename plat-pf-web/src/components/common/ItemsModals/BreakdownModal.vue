<template>
  <b-modal
    :id="id"
    :title="typeName + ' Breakdown'"
    size="lg"
    centered
  >
    <b-table v-if="listBreakdown && listBreakdown.results && listBreakdown.results.length > 0" outlined striped head-variant="light" :fields="breakdownFields" :items="listBreakdown.results">
      <template v-slot:cell(date)="row">
        {{row.item.date | moment("MM/DD/YYYY hh:mm A")}}
      </template>
      <template v-slot:cell(event)="row">
        {{upCaseEvent(row.item.event)}}
      </template>
      <template v-slot:cell(amount)="row">
        {{row.item.item_amount}} <span v-if="showItemAmount(row.item)">(over {{row.item.amount}}) <i class="fa fa-info-circle ml-1 text-warning" :title="tooltipText(row.item)" /></span>
      </template>
    </b-table>
    <div v-else class="align-middle d-flex justify-content-center">There is no breakdown for {{amount}} of the {{typeName}}.</div>
    <template slot="modal-footer">
      <b-button @click="$bvModal.hide('breakdown-modal')">Close</b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'BreakdownModal',
  props: {
    typeID: String,
    id: String,
    dataRow: Object
  },
  data() {
    return {
      breakdownFields: [
        {key: 'date', label: 'Posted At', tdClass: 'align-middle'},
        {key: 'event', label: 'Event', tdClass: 'align-middle'},
        {key: 'type_trans', label: 'Type', tdClass: 'align-middle'},
        {key: 'currency', label: 'Currency', tdClass: 'align-middle'},
        {key: 'amount', label: 'Amount', tdClass: 'align-middle text-nowrap'}
      ],
      typeName: '',
      amount: '',
      listBreakdown: []
    }
  },
  computed: {
    ...mapGetters({
      listBreakdownListing: `pf/analysis/listBreakdownListing`,
      listBreakdownOther: `pf/analysis/listBreakdownOther`,
      listBreakdownTaxCharged: `pf/analysis/listBreakdownTaxCharged`,
      listBreakdownShippingCost: `pf/analysis/listBreakdownShippingCost`,
      listBreakdownReimbursementCosts: `pf/analysis/listBreakdownReimbursementCosts`,
      listBreakdownChannelTaxWithheld: `pf/analysis/listBreakdownChannelTaxWithheld`,
      listBreakdownSaleCharged: `pf/analysis/listBreakdownSaleCharged`,
      listBreakdownReturnPostageBilling: `pf/analysis/listBreakdownReturnPostageBilling`
    }),
    showItemAmount() {
      return item => Math.abs(item.item_amount) < Math.abs(item.amount)
    },
    tooltipText() {
      return item => `This sale item has ${this.quantityCurrentSaleItem()} units over ${item.total_sale_item} total sale units.`
    }
  },
  methods: {
    prepareForModal() {
      let typeNameObject = {
        other_channel_fees: 'Other Channel Fees',
        channel_listing_fee: 'Channel Listing Fee',
        actual_shipping_cost: 'Actual Shipping Cost',
        tax_charged: 'Tax Charged',
        reimbursement_costs: 'Reimbursement Costs',
        channel_tax_withheld: 'Channel Tax Withheld',
        sale_charged: 'Sale Charged',
        return_postage_billing: 'Return Postage Billing'
      }
      let listBreakdownObject = {
        other_channel_fees: this.listBreakdownOther,
        channel_listing_fee: this.listBreakdownListing,
        actual_shipping_cost: this.listBreakdownShippingCost,
        tax_charged: this.listBreakdownTaxCharged,
        reimbursement_costs: this.listBreakdownReimbursementCosts,
        channel_tax_withheld: this.listBreakdownChannelTaxWithheld,
        sale_charged: this.listBreakdownSaleCharged,
        return_postage_billing: this.listBreakdownReturnPostageBilling
      }
      if (['channel_tax_withheld', 'actual_shipping_cost', 'return_postage_billing'].includes(this.$props.typeID)) {
        this.amount = this.$props.dataRow.data[this.$props.typeID].base
      } else this.amount = this.$props.dataRow.data[`item_${this.$props.typeID}`].base
      this.typeName = typeNameObject[this.$props.typeID]
      this.listBreakdown = listBreakdownObject[this.$props.typeID]
    },
    upCaseEvent(event) {
      return event.charAt(0).toUpperCase() + event.slice(1)
    },
    quantityCurrentSaleItem() {
      let quantitySaleItem = 0
      this.listBreakdown.results.forEach((item) => {
        if (Math.abs(item.item_amount) < Math.abs(item.amount)) {
          quantitySaleItem++
        }
      })
      return quantitySaleItem
    }
  },
  watch: {
    typeID: {
      handler() {
        this.prepareForModal()
      }
    },
    dataRow: {
      handler() {
        this.prepareForModal()
      }
    }
  }
}
</script>
