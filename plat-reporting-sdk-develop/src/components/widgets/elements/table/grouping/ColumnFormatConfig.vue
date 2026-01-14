<template>
  <div class="cbpo-grouping-container">
    <div>
      <b-form-group label="Format">
        <b-card no-body class="mb-1">
          <b-card-header header-tag="header" class="p-1 pointer" role="tab" v-b-toggle.formatGroup>
            <span>Options</span>
          </b-card-header>
          <!--Format Type Config-->
          <b-collapse id="formatGroup">
            <b-card-body class="cbpo-form-control">
              <format-config-builder :format-config.sync="computeSelected.col.cell.format" v-if="isReady"/>
            </b-card-body>
          </b-collapse>
        </b-card>
      </b-form-group>
    </div>
  </div>
</template>
<script>
import FormatConfigBuilder from '@/components/formatBuilder/FormatConfigBuilder'
import { defaultFormatConfig } from '@/components/widgets/elements/table/TableConfig'
import defaultsDeep from 'lodash/defaultsDeep'

export default {
  name: 'ColumnFormatConfig',
  props: {
    selected: {
      type: Object
    }
  },
  components: {
    'format-config-builder': FormatConfigBuilder
  },
  data() {
    return {
      columnData: null,
      isReady: false
    }
  },
  methods: {
  },
  computed: {
    computeSelected: {
      get() {
        return this.selected
      },
      set(val) {
        this.$emit('updated:selected', val)
      }
    }
  },
  mounted() {
    if (this.selected) {
      if (!this.computeSelected.col.cell.format) {
        this.computeSelected.col.cell.format = {}
      }
      defaultsDeep(this.computeSelected.col.cell.format, defaultFormatConfig)
      this.isReady = true
    }
  }
}
</script>
<style scoped lang="scss">
  .pointer {
    cursor: pointer;
  }
</style>
