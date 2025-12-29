<template>
  <b-col md="12" lg="12">
    <b-nav class="tab-header nav-tabs">
      <b-nav-item :to="{ name: 'PFShippingInvoices'}" class="btn" active-class="active-tab"><i class="fa fa-ship"></i>
        <template v-if="totalShippingInvoice">
          Shipping Invoices (total: {{this.totalShippingInvoice}})
        </template>
        <template v-else> Shipping Invoices</template>
      </b-nav-item>
      <b-nav-item :to="{ name: 'PFShippingInvoiceHistory'}" class="btn" active-class="active-tab"><i class="fa fa-ship"></i> Import History</b-nav-item>
      <b-nav-item v-if="currentShippingInvoiceNumber" :to="{ name: 'PFShippingInvoiceTransactions'}" class="btn" active-class="active-tab"><i class="fa fa-ship"></i>
        Invoice Number: {{currentShippingInvoiceNumber}}
      </b-nav-item>
    </b-nav>
    <router-view class="tab-body"></router-view>
  </b-col>
</template>

<script>

import {mapActions, mapGetters} from 'vuex'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'

export default {
  name: 'PFShippingManagement',
  data() {
    return {
    }
  },
  mixins: [ spapiReconnectAlertMixin ],
  computed: {
    ...mapGetters({
      totalShippingInvoice: 'pf/fedex/totalShippingInvoice',
      currentShippingInvoiceNumber: 'pf/fedex/currentShippingInvoiceNumber'
    })
  },
  methods: {
    ...mapActions({
      getTotalShippingInvoice: 'pf/fedex/getTotalShippingInvoice'
    })
  },
  async created() {
    await this.getTotalShippingInvoice({client_id: this.$route.params.client_id})
  }
}
</script>

<style lang="scss" scoped>
.nav.tab-header.nav-tabs {
  li:first-child {
    border-left-width: 0 !important;
  }
}
</style>
