<template>
  <div>
    <label class="mb-2">Name</label>
    <b-form-input class="mb-2" placeholder="Enter name" v-model="name" @keypress.enter="handleSaveItem"></b-form-input>
    <label class="mb-2">Review</label>
    <div
      class="d-flex p-1 pl-2 load-save-condition rounded border mb-2"
      v-if="$props.type=='save-column-set' || $props.type=='save-as-column-set'"
      v-b-popover.hover.bottom.html="getColumnSetExpr(sdkConfig.elements[0].config.columns)"
    >
      <template class="load-save-condition" v-if="($props.sdkConfig.elements[0].config.columns && $props.sdkConfig.elements[0].config.columns.length)">
        <span class="overflow-hidden">
          <span class='h-75 text-truncate' v-html="getColumnSetExpr($props.sdkConfig.elements[0].config.columns)"></span>
        </span>
      </template>
    </div>
    <div
      class="d-flex p-1 pl-2 load-save-condition mr-1 rounded border mb-2"
      v-if="$props.type!=='save-column-set' && $props.type!=='save-as-column-set'"
      v-b-popover.hover="{html: true, content: readableQueryString, customClass: 'customPopover', placement: 'bottom'}"
    >
      <template class="load-save-condition" v-if="hasQuery('builder') || hasQuery('base')">
        <span class="overflow-hidden">
          <span class="text-truncate" v-html="readableQueryString">
          </span>
        </span>
      </template>
      <template class="load-save-condition" v-else><span>All Data</span></template>
    </div>
    <div class="mb-2 d-flex">
      <label class="mr-1">Favorite</label>
      <b-form-checkbox switch v-model="featured" />
    </div>
  </div>
</template>

<script>
import _ from 'lodash'
import { mapActions, mapGetters } from 'vuex'
import toastMixin from '@/components/common/toastMixin'
import exprUtil from '@/services/exprUtil'

export default {
  name: 'SaveModal',
  props: {
    type: String,
    callback: Function,
    sdkConfig: Object
  },
  data() {
    return {
      name: '',
      id_item: '',
      featured: false
    }
  },
  mixins: [
    toastMixin
  ],
  computed: {
    ...mapGetters({
      view: `pf/analysis/view`,
      filter: `pf/analysis/filter`,
      columnSet: `pf/analysis/columnSet`,
      getUserId: `ps/userModule/GET_USER_ID`
    }),
    getColumnSetExpr() {
      return columns => exprUtil.buildColumnSetExpr(columns)
    },
    hasQuery() {
      return type =>
        _.get(this.sdkConfig, ['filter', type, 'config', 'query', 'conditions']) &&
        this.sdkConfig.filter[type].config.query.conditions.length
    },
    readableQueryString() {
      return exprUtil.buildFilterExpr(this.sdkConfig, this.sdkConfig.elements[0].config.columns)
    }
  },
  methods: {
    ...mapActions({
      createView: `pf/analysis/createView`,
      updateView: `pf/analysis/updateView`,
      createColumnSet: `pf/analysis/createColumnSet`,
      updateColumnSet: `pf/analysis/updateColumnSet`,
      createFilter: `pf/analysis/createFilter`,
      updateFilter: `pf/analysis/updateFilter`
    }),
    async handleSaveItem() {
      try {
        let data = this.callback()
        let payload = {
          name: this.name,
          client_id: this.$route.params.client_id,
          user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id_item: this.id_item,
          data: data,
          featured: this.featured
        }
        if (this.$props.type === 'save-view') {
          if (this.id_item) {
            await this.updateView(payload)
          } else {
            await this.createView(payload)
          }
        } else if (this.$props.type === 'save-as-view') {
          await this.createView(payload)
        } else if (this.$props.type === 'save-column-set') {
          if (this.id_item) {
            await this.updateColumnSet(payload)
          } else {
            await this.createColumnSet(payload)
          }
        } else if (this.$props.type === 'save-as-column-set') {
          await this.createColumnSet(payload)
        } else if (this.$props.type === 'save-filter') {
          payload.data.timezone = _.cloneDeep(this.sdkConfig.elements[0].config.timezone)
          if (this.id_item) {
            await this.updateFilter(payload)
          } else {
            await this.createFilter(payload)
          }
        } else if (this.$props.type === 'save-as-filter') {
          await this.createFilter(payload)
        }
        this.vueToast('success', 'Successfully saved.')
        this.$bvModal.hide(this.$props.type)
      } catch (err) {
        if (err.code === 1024) {
          this.vueToast('error', err.message)
        } else {
          this.vueToast('error', 'Saving failed. Please retry or contact administrator.')
        }
      }
    },
    handleCloseModal() {
      this.$bvModal.hide(this.$props.type)
    }
  },
  created() {
    if (this.$props.type === 'save-column-set' || this.$props.type === 'save-as-column-set') {
      this.id_item = _.get(this.columnSet, 'id', '')
      this.name = _.get(this.columnSet, 'name', '')
      this.featured = _.get(this.columnSet, 'featured', false)
    } if (this.$props.type === 'save-view' || this.$props.type === 'save-as-view') {
      this.id_item = _.get(this.view, 'id', '')
      this.name = _.get(this.view, 'name', '')
      this.featured = _.get(this.view, 'featured', false)
    } if (this.$props.type === 'save-filter' || this.$props.type === 'save-as-filter') {
      this.id_item = _.get(this.filter, 'id', '')
      this.name = _.get(this.filter, 'name', '')
      this.featured = _.get(this.filter, 'featured', false)
    }
  }
}
</script>

<style lang="scss" scoped>
  .load-save-condition {
    overflow: hidden;
    >span {
      height: 26px;
      display: flex;
      align-items: center;
    }
  }
  .customPopover {
    max-height: 90vh;
    overflow: auto;
  }
</style>
