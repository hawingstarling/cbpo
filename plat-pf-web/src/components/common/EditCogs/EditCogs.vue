<template>
  <div v-if="type === 'cogs'">
    <b-table
      outlined
      striped
      head-variant="light"
      table-variant="secondary"
      :fields="listCogsFields"
      :items="listCogs.results"
      empty-text="There are no COG to show"
      show-empty
    >
      <template v-slot:cell(cog)="row">
        {{row.item.cog.toFixed(2)}}
      </template>
      <template v-slot:cell(effect_start_date)="row">
        {{row.item.effect_start_date | moment("MM/DD/YYYY")}}
      </template>
      <template v-slot:cell(effect_end_date)="row">
        {{row.item.effect_end_date | moment("MM/DD/YYYY")}}
      </template>
      <template v-slot:cell(actions)="row">
        <b-button size="sm" @click="showModalRemove(row)" :disabled="listCogs.results.length < 2"><i class="fa fa-trash-o"></i></b-button>
      </template>
    </b-table>
    <b-modal id="remove-cog-confirm-modal" variant="danger" centered title="Please confirm">
      <div>Are you sure you want to remove this COG?</div>
      <template v-slot:modal-footer>
        <b-button variant="warning" @click="handelRemoveCog()" :disabled="deleting">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
        </b-button>
        <b-button variant @click="$bvModal.hide('remove-cog-confirm-modal')" :disabled="deleting">
            <i class="icon-close"></i> No
        </b-button>
      </template>
    </b-modal>
    <div class="d-flex align-items-top justify-content-between">
      <div class="w-25 mr-3">
        COG
        <FormInput
          name='COG'
          v-model="dataPost.cog"
          :format="['currency']"
          :rules="['currency']"
          type='input'
        />
      </div>
      <div class="pf-datepicker w-25 mr-3">
        Effective Start Date <date-picker format="MM-DD-YYYY" v-model="dataPost.effect_start_date"></date-picker>
      </div>
      <div class="pf-datepicker w-25 mr-3">
        Effective End Date <date-picker format="MM-DD-YYYY" v-model="dataPost.effect_end_date"></date-picker>
      </div>
      <div class="add-button">
        <b-button @click="handleAddCog" :disabled="updating">Add</b-button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import DatePicker from 'vue2-datepicker'
import toastMixin from '@/components/common/toastMixin'
import _ from 'lodash'

import FormInput from '@/components/common/FormInput/FormInput'

export default {
  name: 'EditCogs',
  props: {
    type: String
  },
  components: {
    DatePicker,
    FormInput
  },
  data() {
    return {
      listCogsFields: [
        {key: 'cog', label: 'COG', tdClass: 'align-middle'},
        {key: 'effect_start_date', label: 'Effective Start Date', tdClass: 'align-middle pr-5'},
        {key: 'effect_end_date', label: 'Effective End Date', tdClass: 'align-middle pr-5'},
        {key: 'actions', label: '', tdClass: 'align-middle'}
      ],
      dataRemove: {},
      deleting: false,
      dataPost: {
        cog: null,
        effect_start_date: null,
        effect_end_date: null
      },
      updating: false
    }
  },
  mixins: [
    toastMixin
  ],
  computed: {
    ...mapGetters({
      editData: `pf/items/editData`,
      listCogs: `pf/items/listCogs`
    })
  },
  methods: {
    ...mapActions({
      removeCog: `pf/items/removeCog`,
      addCog: `pf/items/addCog`
    }),
    showModalRemove(row) {
      this.dataRemove = _.cloneDeep(row.item)
      this.$bvModal.show('remove-cog-confirm-modal')
    },
    async handelRemoveCog() {
      this.deleting = true
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          item_id: this.editData.id,
          cog_id: this.dataRemove.id
        }
        await this.removeCog(payload)
        this.$bvModal.hide('remove-cog-confirm-modal')
        this.vueToast('success', 'Removed successfully.')
      } catch {
        this.vueToast('error', 'Removing failed. Please retry or contact administrator.')
      }
      this.deleting = false
    },
    async handleAddCog() {
      this.updating = true
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          item_id: this.editData.id,
          payload: this.dataPost
        }
        await this.addCog(payload)
        this.vueToast('success', 'Added successfully.')
        this.dataPost = {
          cog: null,
          effect_start_date: null,
          effect_end_date: null
        }
      } catch {
        this.vueToast('error', 'Adding failed. Please retry or contact administrator.')
      }
      this.updating = false
    }
  }
}
</script>

<style lang="scss" scoped>
.add-button {
  width: 52px;
  padding-top: 22px;
  .btn {
    padding-block: 8px;
  }
}
::v-deep .pf-input {
  background-color: red;
  input {
    height: calc(1.5em + 1rem + 2px);
  }
}
</style>
