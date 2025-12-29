<template>
  <ValidationObserver ref="editObserver" slim>
    <b-modal
      :id="id"
      title="Edit Item"
      size="xl"
      centered
      modal-class="editable-modal"
    >
      <b-container class="edit-modal">
        <b-row>
          <b-card-group>
            <b-card
              v-for="(dataGroup, index) in dataRenderUI"
              :key="index"
              :header="dataGroup.group"
              header-class="font-weight-bold"
              :class="className(dataGroup.group)"
            >
              <b-row class="edit-modal__row-group">
                <div class="d-flex mb-3 px-3" :class="{'invisible': dataGroup.group === 'hide'}">
                  <div class="edit-modal__heading mr-1">Channel:</div>
                  <div>{{ getChannelLabel(internalData.channel) }}</div>
                </div>
                <b-col
                  md="12"
                  v-for="(dataField, dataKey) in dataGroup.data"
                  :key="dataKey"
                  class="mb-3"
                >
                  <div class="edit-modal__heading">
                    {{ dataField.label }}
                  </div>
                  <FormInput
                    v-model="internalData[dataField.name]"
                    :name="dataField.label"
                    :format="dataField.format"
                    :type="dataField.type"
                    :rules="dataField.rules"
                    :disabled="isReadonly(dataField.format)"
                  />
                  <Textarea
                    v-if="dataField.type === 'textarea'"
                    :name="dataField.label"
                    v-model="internalData[dataField.name]"
                    :rules="dataField.rules"
                  ></Textarea>
                  <Datepicker
                    v-if="dataField.type === 'datepicker'"
                    :name="dataField.label"
                    v-model="internalData[dataField.name]"
                    :timezone="timezone.utc"
                    type="datetime"
                    :rules="dataField.rules"
                  ></Datepicker>
                  <ComboBox
                    v-if="dataField.type === 'combobox'"
                    v-model="internalData[dataField.name]"
                    :options="selectOption[dataField.id]"
                    :type="isSelect(dataField.format) ? 'select' : null"
                    :optionType="dataField.id"
                    @keyup="handleGetVariations"
                  ></ComboBox>
                  <EditCogs
                    :type="dataField.type"
                  ></EditCogs>
                </b-col>
              </b-row>
              <template v-if="dataGroup.subGroup">
                <b-card
                  v-for="(subGroup, index) in dataGroup.subGroup"
                  :key="index"
                  :header="subGroup.group | filterGroupname"
                  header-class="text-uppercase font-weight-bold"
                >
                  <b-row class="edit-modal__row-group">
                    <b-col
                      md="12"
                      v-for="(subGroupData, subGroupKey) in subGroup.data"
                      :key="subGroupKey"
                    >
                      <div>
                        <span>
                          {{subGroupData.label}}
                        </span>
                      </div>
                      <div class="edit-modal__col">
                        <FormInput
                          :name="getColumnName(subGroupData.name)"
                          v-model="internalData[subGroupData.name]"
                          :format="subGroupData.format"
                          :type="subGroupData.type"
                          :rules="subGroupData.rules"
                          :disabled="isReadonly(subGroupData.format)"
                        />
                      </div>
                    </b-col>
                  </b-row>
                </b-card>
              </template>
            </b-card>
          </b-card-group>
        </b-row>
      </b-container>
      <div slot="modal-footer">
        <b-btn
          class="mr-2"
          variant
          @click="handleCloseModal()"
          :disabled="isUpdating"
        >
          Cancel
        </b-btn>
        <b-btn
          variant="warning"
          type="submit"
          @click.prevent="handleUpdateItem()"
          :disabled="isUpdating || isNotChanged"
        >
          Save Changes
        </b-btn>
      </div>
    </b-modal>
  </ValidationObserver>
</template>

<script>
import { EDIT_ITEMS_DATA_FIELD } from '@/shared/constants'
import { checkFieldFormatMixins } from '@/shared/utils'
import { mapActions, mapGetters } from 'vuex'
import toastMixin from '@/components/common/toastMixin'
import { filterColumnName } from '@/shared/filters'
import _ from 'lodash'

import FormInput from '@/components/common/FormInput/FormInput'
import ComboBox from '@/components/common/ComboBox/ComboBox'
import Datepicker from '@/components/common/Datepicker/Datepicker'
import Textarea from '@/components/common/Textarea/Textarea'
import EditCogs from '@/components/common/EditCogs/EditCogs'

export default {
  name: 'EditItemModal',
  components: { FormInput, Datepicker, ComboBox, Textarea, EditCogs },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  mixins: [
    checkFieldFormatMixins,
    toastMixin
  ],
  data() {
    return {
      dataRenderUI: EDIT_ITEMS_DATA_FIELD,
      internalData: {},
      originalInternalData: {},
      selectOption: {
        size: [],
        style: [],
        brand: []
      },
      variationMapping: {
        size: { hasVariation: true, type: 'size' },
        style: { hasVariation: true, type: 'style' },
        brands: { hasVariation: false, type: 'brand' }
      },
      isUpdating: false,
      page: 1,
      limit: 5
    }
  },
  computed: {
    ...mapGetters({
      editData: `pf/items/editData`,
      listCogs: `pf/items/editData`,
      channelList: 'pf/analysis/channelList'
    }),
    isNotChanged() {
      return (
        JSON.stringify(this.internalData) ===
        JSON.stringify(this.originalInternalData)
      )
    }
  },
  methods: {
    ...mapActions({
      getSaleItemVariation: `pf/analysis/getSaleItemVariation`,
      updateItem: `pf/items/updateItem`,
      getListCogs: `pf/items/getListCogs`
    }),
    handleCloseModal() {
      this.internalData = _.cloneDeep(this.originalInternalData)
      this.$bvModal.hide(`${this.id}`)
    },
    getColumnName(columnValue) {
      let listCols = EDIT_ITEMS_DATA_FIELD
      let columns = listCols.map(column => column.id)
      const column = columns.find(column => column === columnValue)
      return column || null
    },
    className(group) {
      if (group === 'COGs') {
        return 'cogs-card'
      }
      if (group === 'INFO') {
        return 'info-card'
      } else {
        return 'hide-header-card'
      }
    },
    getVariation(hasVariation, type, keyword) {
      const payload = {
        clientId: this.$route.params.client_id,
        hasVariation: hasVariation,
        type,
        keyword
      }
      this.getSaleItemVariation(payload).then(response => {
        if (response.data) {
          const results = response.data.results.map(item => item.name)
          this.selectOption[this.variationMapping[type].type] = results
        }
      })
    },
    async handleGetVariations(payload) {
      for (const [key, value] of Object.entries(this.variationMapping)) {
        if (value.type === payload.type) {
          this.getVariation(value.hasVariation, key, payload.value)
        }
      }
    },
    async handleUpdateItem() {
      this.isUpdating = true
      try {
        let payload = {
          payload: _.cloneDeep(this.internalData),
          client_id: this.$route.params.client_id,
          id: this.editData.id
        }
        await this.updateItem(payload)
        this.$bvModal.hide(`${this.id}`)
        this.vueToast('success', 'Updated successfully.')
      } catch {
        this.vueToast('error', 'Updating failed. Please retry or contact administrator.')
      }
      this.isUpdating = false
    },
    handleGetListCogs() {
      let payload = {
        client_id: this.$route.params.client_id,
        item_id: this.internalData.id,
        page: this.page,
        limit: this.limit
      }
      this.getListCogs(payload)
    },
    getChannelLabel (channelName) {
      if (this.channelList && this.channelList.results) {
        const channel = this.channelList.results.find(channel => channel.name === channelName)
        if (channel) return channel.label
      }
      return channelName
    }
  },
  filters: {
    filterGroupname: function(str) {
      return str ? str.replace(/([A-Z])/g, ' $1').toUpperCase() : str
    },
    filterColumnName
  },
  watch: {
    editData: {
      handler(newObj) {
        this.originalInternalData = _.cloneDeep(newObj)
        this.internalData = _.cloneDeep(newObj)
        this.handleGetListCogs()
        for (const [key, value] of Object.entries(this.variationMapping)) {
          if (!this.selectOption[value.type].length) {
            this.getVariation(value.hasVariation, key)
          }
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.edit-modal {
  &__group {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
    justify-content: space-between;
    align-items: center;
  }
  &__group-title {
    color: white;
    text-transform: uppercase;
    font-weight: bold;
    font-size: 15px;
  }
  &__hr {
    flex-grow: 1;
    margin: 0 10px;
    hr {
      border-top: 1px solid rgba(255, 255, 255, 0.5);
    }
  }
  &__button {
    background-color: white;
    color: #20a8d8;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: pointer;
  }
  &__row-group {
    padding: 1.25rem; // from bootstrap
    margin-bottom: 10px;
  }
  &__col {
    margin-bottom: 15px;
    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }
    input[type="number"] {
      -moz-appearance: textfield;
    }
  }
  &__heading {
    font-weight: bold;
    color: #888;
  }
  .collapsed > .when-opened,
  :not(.collapsed) > .when-closed {
    display: none;
  }
}
@media (min-width: 576px){
  .card-group > .card.cogs-card {
    flex: 30%;
  }
  .card-group > .card.info-card {
    border-right: 0px;
  }
  .card-group > .card.hide-header-card {
    .card-header {
      height: 46px;
      div {
        display: none;
      }
    }
  }
}
</style>
