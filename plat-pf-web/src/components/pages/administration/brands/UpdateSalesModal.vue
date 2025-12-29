<template>
  <div>
    <h5 class="mb-3">Update Sales of {{$props.brand}} on the channel {{$props.channel}}</h5>
    <div class="font-italic text-danger mb-3">Shipping Cost that's 100% accurate won't be impacted by this activity.</div>
    <div class="mb-3">
      This will calculate Shipping Costs of the Sales from:
      <Datepicker
        v-model="saleDateFrom"
        format="MM-DD-YYYY"
        :disabled-date="disableDateFrom"
        @change="handleChangeDateFrom()"
      />
      to
      <Datepicker
        v-model="saleDateTo"
        format="MM-DD-YYYY"
        :disabled-date="disableDateTo"
        @change="handleChangeDateTo()"
      />
    </div>
    <div>
      <div class='d-flex'>
        <b-form-checkbox v-model="recalculate">Recalculate the shipping costs.</b-form-checkbox>
      </div>
      <h6 class="font-italic font-weight-light">By checking this option, Shipping Costs that are calculated or updated before will be recalculated.</h6>
    </div>
  </div>
</template>

<script>
import Datepicker from 'vue2-datepicker'

export default {
  name: 'UpdateSalesModal',
  components: {
    Datepicker
  },
  props: {
    brand: String,
    channel: String
  },
  data() {
    return {
      saleDateFrom: new Date(new Date().getTime() - (7 * 24 * 60 * 60 * 1000)),
      saleDateTo: new Date(),
      recalculate: false
    }
  },
  methods: {
    disableDateFrom(date) {
      return date.getTime() > this.saleDateTo.getTime()
    },
    disableDateTo(date) {
      return date.getTime() >= new Date().getTime()
    },
    handleChangeDateTo() {
      if (this.saleDateTo.getTime() < this.saleDateFrom.getTime()) {
        this.saleDateFrom = this.saleDateTo
      }
      this.$emit('checkCountUpdateSales')
    },
    handleChangeDateFrom() {
      this.$emit('checkCountUpdateSales')
    }
  },
  mounted() {
    this.$emit('checkCountUpdateSales')
  },
  watch: {
    recalculate(newValue) {
      this.$emit('checkCountUpdateSales')
    }
  }
}
</script>
