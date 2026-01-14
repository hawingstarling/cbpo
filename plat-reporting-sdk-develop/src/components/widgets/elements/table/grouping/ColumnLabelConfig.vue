<template>
  <div class="cbpo-grouping-container">
      <ValidationProvider name="Label" rules="required|isUnique" v-slot="{ errors }">
        <b-form-group label="Label">
          <b-form-input type="text" v-model.trim="computeSelected.col.displayName"/>
          <span class="text-error">{{ errors[0] }}</span>
        </b-form-group>
      </ValidationProvider>
  </div>
</template>

<script>
import {ValidationProvider, extend} from 'vee-validate'

export default {
  name: 'ColumnLabelConfig',
  components: {
    ValidationProvider
  },
  props: {
    selected: Object,
    columnsData: Array
  },
  data() {
    return {
      // columnNameData: this.columnName
    }
  },
  computed: {
    computeSelected: {
      get() {
        return this.selected
      },
      set(selected) {
        this.$emit('update:selected', selected)
      }
    }
  },
  mounted() {
    extend('isUnique', {
      validate: (value) => {
        return !this.columnsData.find((col, index) => col.displayName === value && this.selected.colIndex !== index)
      },
      message: 'The label already existed. Please choose another one.'
    })
  },
  methods: {
    changeLabel () {
      this.$emit('update:columnName', this.columnNameData)
    }
  }
}
</script>
<style scoped lang="scss">
</style>
