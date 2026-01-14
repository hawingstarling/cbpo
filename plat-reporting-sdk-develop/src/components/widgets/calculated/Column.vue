<template>
  <div class="cbpo-calculated-wrapper">
    <button v-b-modal.calculatedModal class="cbpo-btn btn-primary ml-2">
      <i class="fa fa-plus" aria-hidden="true"></i>
    </button>
    <!--Add calculated columns-->
    <b-modal size="lg" ref="calculatedModal" id="calculatedModal" title="Add a new calculated column" dialog-class="cbpo-custom-modal">
      <ValidationObserver ref="calculatedForm" v-slot="{ invalid }">
        <ValidationProvider name="Name" :rules="nameRules" v-slot="{ errors }" :bails="false">
          <b-form-group label="Name">
            <b-form-input v-model="calculated.name" trim />
            <span class="text-error" v-if="invalid">{{ errors[0] }}</span>
          </b-form-group>
        </ValidationProvider>

        <ValidationProvider name="Type" rules="required" v-slot="{ errors }">
          <b-form-group label="Type">
            <b-form-select
              text-field="label"
              value-field="value"
              size="sm"
              v-model="calculated.type"
              :options="dataTypes">
              <template v-slot:first>
                <option :value="''" disabled>Please choose a type</option>
              </template>
            </b-form-select>
            <span class="text-error">{{ errors[0] }}</span>
          </b-form-group>
        </ValidationProvider>

        <ValidationProvider name="Expression" rules="required|valid" v-slot="{ errors }">
          <b-form-group label="Expression">
            <b-form-textarea
              v-model="calculated.expr"
              rows="3"
              max-rows="6"
            ></b-form-textarea>
            <span class="text-error">{{ errors[0] }}</span>
          </b-form-group>
        </ValidationProvider>
      </ValidationObserver>
      <template v-slot:modal-footer>
        <div class="control-box">
          <button class="cbpo-btn btn-primary mr-1" @click="add()">
            Save
          </button>
          <button class="cbpo-btn" @click="reset()">
            Cancel
          </button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
import { ValidationProvider, ValidationObserver, extend } from 'vee-validate'
import WidgetLoaderMixins from '@/components/widgets/WidgetLoaderMixins'
import WidgetBase from '@/components/WidgetBase'
import cloneDeep from 'lodash/cloneDeep'
import defaultsDeep from 'lodash/defaultsDeep'
import { defaultColumnConfig } from '@/components/widgets/elements/table/TableConfig'
import { uniqueRules, validExpr } from './CustomValidator'

extend('unique', uniqueRules)
extend('valid', validExpr)

export default {
  name: 'CalculatedColumn',
  extends: WidgetBase,
  mixins: [WidgetLoaderMixins],
  components: {
    ValidationProvider,
    ValidationObserver
  },
  props: {
    columns: Array
  },
  data () {
    return {
      calculated: {
        name: '',
        expr: '',
        type: ''
      },
      dataTypes: [
        {
          label: 'Text',
          value: 'text'
        }, {
          label: 'Date',
          value: 'date'
        }, {
          label: 'Numeric',
          value: 'numeric'
        }
      ],
      nameRules: {
        required: true,
        unique: this.columns || []
      }
    }
  },
  methods: {
    widgetConfig (config) {
      console.log('calculated config', cloneDeep(config))
    },
    async add () {
      let isValid = await this.$refs.calculatedForm.validate()
      if (isValid) {
        // update columns
        defaultsDeep(this.calculated, defaultColumnConfig)
        console.log('calc', cloneDeep(this.calculated))
        this.$emit('input', this.calculated)
        this.reset()
      }
    },
    reset () {
      this.$bvModal.hide('calculatedModal')
      this.$refs.calculatedForm.reset()
      this.calculated = {
        name: '',
        expr: '',
        type: ''
      }
    }
  }
}
</script>
