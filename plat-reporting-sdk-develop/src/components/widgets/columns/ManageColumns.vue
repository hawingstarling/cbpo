<template>
  <div v-if="configReady" class="cbpo-manage-column">
    <slot :openModal="openModal" name="button">
      <button @click="openModal()" class="cbpo-btn btn-primary">
        <span>{{config.trigger.label}}</span>
      </button>
    </slot>
    <!--Modal column manager-->
    <b-modal dialog-class="cbpo-custom-modal" :modal-class="config.modal.modalClass" :contentClass="config.modal.contentClass" :id="modalId" size="md" :no-close-on-backdrop="modalButtonsConfig.cancel.visible" @close="cancel()" @hide="cancel()">
      <template v-slot:modal-title>
        <span>{{config.modal.title}}</span>
      </template>
      <ListColumnsSingleMode v-if="config.mode  === 'single'" :columnsInElements.sync="config.managedColumns" :hiddenColumns="config.hiddenColumns" />
      <ListColumnsTwinMode v-else-if="config.mode  === 'twin'" :columnsInElements.sync="config.managedColumns" :hiddenColumns="config.hiddenColumns" @dropChange="dropChange" />
      <template v-else>
        Mode "{{config.mode}}" is not supported
      </template>
      <template v-slot:modal-footer>
        <button v-if="modalButtonsConfig.reset.visible" @click="reset()" class="cbpo-btn btn-warning mr-auto btn-reset">
          <span>{{ modalButtonsConfig.reset.text }}</span>
        </button>
        <!-- Emulate built in modal footer ok and cancel button actions -->
        <button v-if="modalButtonsConfig.apply.visible" @click="apply()" class="cbpo-btn btn-primary btn-apply">
          <span>{{ modalButtonsConfig.apply.text }}</span>
        </button>
        <button v-if="modalButtonsConfig.cancel.visible" @click="cancel()" class="cbpo-btn btn-cancel">
          <span>{{ modalButtonsConfig.cancel.text }}</span>
        </button>
      </template>
    </b-modal>
  </div>
</template>
<script>
import 'jquery-ui/ui/widgets/sortable'
import 'jquery-ui/ui/widgets/draggable'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '@/components/WidgetBase'
import ListColumnsTwinMode from './ListColumnsTwinMode'
import ListColumnsSingleMode from './ListColumnsSingleMode'
import { makeColumnManagerDefaultConfig } from '@/components/widgets/columns/ManageColumnConfig'
import { moveElement } from '@/utils/arrayUtil'

export default {
  name: 'ColumnManager',
  extends: WidgetBase,
  mixins: [WidgetBaseMixins],
  components: {
    ListColumnsTwinMode,
    ListColumnsSingleMode
  },
  props: {
    columns: {
      type: Array,
      default: function() {
        return []
      }
    }
  },
  data() {
    return {
      defaultState: null,
      rootState: null
    }
  },
  computed: {
    modalId() {
      return 'column-manager-modal-' + this.config.id
    },
    modalButtonsConfig() {
      return this.config.modal.buttons
    }
  },
  methods: {
    widgetConfig(config) {
      makeColumnManagerDefaultConfig(config)
      this.$set(config, 'id', config.id)
    },
    cloneDeep (value) {
      return JSON.parse(JSON.stringify(value))
    },
    apply() {
      let columns = this.cloneDeep(this.config.managedColumns)
      this.$emit('input', columns)
      this.defaultState = this.cloneDeep(columns)
      this.toggleModal()
    },
    applyDefaultState() {
      let defaultState = this.cloneDeep(this.defaultState)
      this.config.managedColumns.forEach((mc, index) => {
        this.$set(mc, 'columns', defaultState[index].columns)
      })
    },
    cancel() {
      this.applyDefaultState()
      this.toggleModal()
    },
    openModal() {
      this.toggleModal(true)
    },
    dropChange(e) {
      let {data: {source, target}, scope} = {...e}
      this.config.managedColumns.forEach((mc, index) => {
        if (mc.id === scope) {
          mc.columns = moveElement(mc.columns, source.index, target.index)
          this.$set(this.config.managedColumns, index, mc)
        }
      })
    },
    toggleModal (isOpen = false) {
      isOpen
        ? this.$bvModal.show(this.modalId)
        : this.$bvModal.hide(this.modalId)
    },
    reset() {
      let defaultState = this.cloneDeep(this.rootState)
      this.config.managedColumns.forEach((mc, index) => {
        this.$set(mc, 'columns', defaultState[index].columns)
      })
    }
  },
  created() {
    this.config.managedColumns = this.columns
    this.defaultState = this.cloneDeep(this.columns)
    this.rootState = this.cloneDeep(this.columns)
  }
}
</script>
<style scoped lang="scss">
::v-deep .modal-dialog {
  @media (min-width: 576px) {
    min-width: 500px;
    max-width: 750px;
    width: 50%;
  }
}
</style>
