<template>
  <b-modal :id="id" variant="danger" centered title="Please confirm">
    <div class="confirmation-modal__body">
      {{ isConnect
        ? `${currentClientName ? `This is ${currentClientName} workspace. `: ''}Please ensure you will associate with the correct Seller Central account if you are managing multiple ones.`
        : 'Are you sure you want to revoke this Seller Central account?'
      }}
    </div>
    <div class="confirmation-modal__extend">Please type <b>{{ isConnect ? 'Connect' : 'Revoke' }}</b> to confirm.</div>
    <b-form-input class="my-3" v-model="keyword" />
    <template v-slot:modal-footer>
      <b-btn
        variant="warning"
        @click="handleConfirm()"
        :disabled="disabled"
      >
        <i class="icon-check"></i> Yes, I understand &amp; confirm!
      </b-btn>
      <b-btn variant @click="handleCloseModal()">
        <i class="icon-close"></i> No
      </b-btn>
    </template>
  </b-modal>
</template>

<script>
import { mapGetters } from 'vuex'
import LS from '@/services/_localStorage'

export default {
  name: 'ConfirmationAccessModal',
  props: {
    id: {
      type: String,
      required: true
    },
    isConnect: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      deleting: false,
      keyword: ''
    }
  },
  computed: {
    ...mapGetters({
      activitiesList: `pf/activities/activitiesList`
    }),
    disabled() {
      return this.isConnect ? this.keyword !== 'Connect' : this.keyword !== 'Revoke'
    },
    currentClientName() {
      return LS.getCurrentClientName()
    }
  },
  methods: {
    handleConfirm() {
      this.$emit('confirm', this.isConnect)
      this.handleCloseModal()
    },
    handleCloseModal() {
      this.keyword = ''
      this.$bvModal.hide(this.id)
    }
  }
}
</script>
<style scoped lang="scss">
.confirmation-modal {
  &__body {
    color: red;
  }
  &__extend {
    padding-top: 10px;
  }
}
</style>
