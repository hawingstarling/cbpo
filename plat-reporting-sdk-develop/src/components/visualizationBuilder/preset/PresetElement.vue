<template>
  <div class="cbpo-visualization-preset">
    <div class="cbpo-element-content widget-list">
      <div class="cbpo-grid-row">
        <div
          v-for="(template, index) in listTemplates"
          :key="index"
          :class="{'active': isTemplate(template)}"
          class="cbpo-grid-item"
          @click="selectedTemplate(template.config)">
            <slot :item="template" :selectedTemplate="selectedTemplate">
              <img class="img-template" v-bind:src="template.screenshot">
            </slot>
        </div>
        <div v-if="listTemplates.length === 0" class="text-center w-100">
          <span>No Data.</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import {cloneDeep} from 'lodash'
import { makeWidgetDefaultConfig } from '@/components/widgets/WidgetConfig'

export default {
  name: 'PresetElement',
  props: {
    templates: Array,
    templateData: Object
  },
  data() {
    return {
      listTemplates: []
    }
  },
  computed: {
    isTemplate() {
      return id => {
        if (!this.templateData || !this.templateData.id) {
          return false
        }
        return this.templateData.id === id
      }
    }
  },
  methods: {
    selectedTemplate(config) {
      this.$emit('input', cloneDeep(config))
    }
  },
  created() {
    // default config when old config was added
    this.listTemplates = this.templates.map(temp => {
      temp.config = makeWidgetDefaultConfig(temp.config)
      return temp
    })
  },
  watch: {
    templates (val) {
      this.listTemplates = this.templates.map(temp => {
        temp.config = makeWidgetDefaultConfig(temp.config)
        return temp
      })
    }
  }
}
</script>
<style scoped lang="scss">
  @import "PresetElement";
</style>
