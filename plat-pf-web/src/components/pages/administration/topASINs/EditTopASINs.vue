<template>
  <b-modal id="edit-top-asin-setting-modal" centered size="lg">
    <div>
      <b-row class="mb-2">
        <b-col md="6">
          <span>Channel</span>
          <b-form-select class="select-channel"
            v-model="itemEdit.channel"
            :options="channelOptions"
            :class="{'border-danger': $v.itemEdit.channel.$dirty && !$v.itemEdit.channel.required}"
          />
          <div v-show="$v.itemEdit.channel.$dirty && !$v.itemEdit.channel.required" class="text-danger">The Channel is required</div>
        </b-col>
        <b-col md="6">
          Segment
          <b-form-textarea class="custom-textarea" v-model="itemEdit.segment"></b-form-textarea>
        </b-col>
      </b-row>
      <b-row class="mb-2">
        <b-col md="6">
          <span>Parent ASIN</span>
          <b-form-input :class="{'border-danger': $v.itemEdit.parent_asin.$dirty && !$v.itemEdit.parent_asin.required}" @input="$v.itemEdit.parent_asin.$touch()" v-model="itemEdit.parent_asin"></b-form-input>
          <div v-show="$v.itemEdit.parent_asin.$dirty && !$v.itemEdit.parent_asin.required" class="text-danger">The Parent ASIN is required</div>
        </b-col>
        <b-col md="6">
          <span>Child ASIN</span>
          <b-form-input :class="{'border-danger': $v.itemEdit.child_asin.$dirty && !$v.itemEdit.child_asin.required}" @input="$v.itemEdit.child_asin.$touch()" v-model="itemEdit.child_asin"></b-form-input>
          <div v-show="$v.itemEdit.child_asin.$dirty && !$v.itemEdit.child_asin.required" class="text-danger">The Child ASIN is required</div>
        </b-col>
      </b-row>
    </div>
    <template v-slot:modal-header>
      <div class="d-flex justify-content-center w-100">
        <h4 class="mb-0">
          Edit for Top ASIN on the channel {{ channelOfEditModal.label }}
        </h4>
      </div>
    </template>
    <template v-slot:modal-footer>
      <b-button
        @click="handleEditTopASIN"
        variant="primary"
        :disabled="disableUpdate"
      >
        Update
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import _ from 'lodash'
import { required } from 'vuelidate/lib/validators'

export default {
  name: 'EditTopASINs',
  props: {
    item: Object,
    tooltipInfo: Array,
    channelOfEditModal: String
  },
  data() {
    return {
      itemEdit: {}
    }
  },
  validations() {
    return {
      itemEdit: {
        parent_asin: { required },
        child_asin: { required },
        channel: { required }
      }
    }
  },
  async created() {
    this.itemEdit = _.cloneDeep(this.$props.item)
    try {
      await this.getChannelList({ client_id: this.$route.params.client_id })
    } catch (e) {
      console.error(e)
    }
  },
  computed: {
    ...mapGetters({
      channelList: 'pf/analysis/channelList'
    }),
    channelOptions() {
      let channelList = []
      if (this.channelList && this.channelList.results) {
        channelList = this.channelList.results.reduce((acc, item) => {
          acc.push({ text: item.label, value: item.name })
          return acc
        }, [])
      }
      return channelList
    },
    disableUpdate() {
      return Object.keys(this.$v.itemEdit).some(
        key => this.$v.itemEdit[key].$dirty && !this.$v.itemEdit[key].required
      )
    }
  },
  methods: {
    ...mapActions({
      getChannelList: 'pf/analysis/getChannelList'
    }),
    handleEditTopASIN() {
      this.$emit('handleEditTopASIN', this.itemEdit)
    }
  },
  watch: {
    item: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.itemEdit = _.cloneDeep(newVal)
        }
      }
    }
  }
}
</script>
<style scoped>
::v-deep .custom-select {
  height: 35px;
  min-height: 35px;
}
.custom-textarea {
  height: 35px;
}
.clear-icon .is-invalid {
  background-image: none;
}
::v-deep .select-channel:focus {
  border: 1px solid #e6e8f0 !important;
}
::v-deep .border-danger {
  border-color: #f86c6b !important;
}
::v-deep .border-danger:focus {
  border-color: #f86c6b !important;
  box-shadow: 0 0 0 0.2rem rgba(248, 108, 107, 0.25) !important;
}
</style>
