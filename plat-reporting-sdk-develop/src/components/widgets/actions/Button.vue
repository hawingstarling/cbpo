<template>
  <button :disabled="isLoad" class="cbpo-btn btn-primary" @click="handleButtonClick">
    <div class="mr-1" v-if="config.icons && config.icons.css">
      <i :class="config.icons.css" aria-hidden="true">
      </i>
    </div>
    <span v-if="config.label && config.label.text">
      {{config.label.text}}
    </span>
    <div v-if="isLoad" class="ml-1">
      <span role="status" class="spinner-border">
      </span>
    </div>
  </button>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import CBPO from '@/services/CBPO'
import _ from 'lodash'
import { BUS_EVENT } from '@/services/eventBusType'

export default {
  name: 'Button',
  extends: WidgetBase,
  data() {
    return {
      state: false
    }
  },
  mixins: [
    WidgetBaseMixins
  ],
  computed: {
    isLoad: {
      get() {
        return this.state
      },
      set(e) {
        this.state = e
      }
    }
  },
  methods: {
    handleButtonClick  () {
      if (!this.isLoad) {
        const { id, events } = this.config
        if (_.isObject(events) && _.isFunction(events.click)) {
          events.click()
        }
        if (id) {
          return CBPO.$bus.$emit('click_' + id)
        }
      }
    }
  },
  created() {
    const {id} = this.config
    CBPO.$bus.$on(id + BUS_EVENT.STAGE_CHANGE, (e) => {
      this.isLoad = e
    })
  },
  beforeDestroy() {
    const {id} = this.config
    CBPO.$bus.$off(id + BUS_EVENT.STAGE_CHANGE)
  }
}
</script>
