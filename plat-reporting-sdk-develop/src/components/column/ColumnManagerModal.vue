<template>
  <div>
    <!--Modal-->
    <modal
      :name="modalName"
      draggable=".drag-part"
      height="auto"
      :clickToClose="true"
      classes="cbpo-custom-modal"
    >
      <template>
        <span class="close-icon" @click.stop="closeColumnModal(modalName)">
          <i class="fa fa-times-circle" aria-hidden="true"></i>
        </span>
        <div class="drag-part"></div>
        <div :id="wrapperId" class="cbpo-column-manager">
          <div class="cbpo-column-content">
            <template v-for="(type, typeIndex) of columnData.sortedData.types">
              <div class="column-box" :key="typeIndex">
                <template v-for="(col, colIndex) of columnData.sortedData.columns[typeIndex]">
                  <div
                    v-cbpo-connector="{
                      position: {
                        //start: 'top-right', //top-left, bottom-left, top-right, bottom-right, center default: default: mouse position
                        //end: 'top-right'
                      }
                    }"
                    v-cbpo-draggable="{
                      scope: wrapperId,
                      column: col,
                      [EVENT.START_EVENT]: startEvent,
                      [EVENT.STOP_EVENT]: stopEvent
                    }"
                    :key="`${col.type}_${col.name}_${typeIndex}`" class="cell-box">
                    <span class="text  text-truncate">{{col.displayName || col.name}}</span>
                    <i :id="`${col.name}_${typeIndex}_${colIndex}`" class="card-info fa fa-info-circle"></i>
                    <small><b>({{col.type}})</b></small>
                  </div>
                  <b-tooltip custom-class="tooltip-float" triggers="hover" placement="top" :key="`${col.name}_${typeIndex}_${colIndex}_tooltip`" :target="`${col.name}_${typeIndex}_${colIndex}`">
                    {{ col.displayName || col.name }}
                  </b-tooltip>
                </template>
              </div>
            </template>
          </div>
        </div>
      </template>
    </modal>
    <!--/end modal-->
  </div>
</template>
<script>
import CBPO from '@/services/CBPO'
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import dragDirective from '@/directives/dragDirective'
import { EVENT } from '@/utils/dragAndDropUtil'
import $ from 'jquery'
import connectorDirective from '@/directives/connectorDirective'
import { BUS_EVENT } from '@/services/eventBusType'
import { cloneDeep, defaultsDeep, startCase } from 'lodash'
import { defaultColumnConfig } from '@/components/widgets/elements/table/TableConfig'

export default {
  name: 'ColumnManagerModal',
  props: {
    wrapperId: String,
    modalName: String,
    columns: Array
  },
  directives: {
    'cbpo-draggable': dragDirective,
    'cbpo-connector': connectorDirective
  },
  data() {
    return {
      EVENT: EVENT,
      columnData: {
        sortedData: {
          types: [],
          columns: []
        },
        isMaximize: true,
        isColumnMode: false
      }
    }
  },
  mixins: [WidgetBaseMixins],
  methods: {
    closeColumnModal (name) {
      this.$modal.hide(name)
      CBPO.$bus.$emit(`close-${this.modalName}`)
    },
    openColumnModal (name) {
      this.$modal.show(name)
    },
    startEvent({scope, index}, el) {
      $(el.target).addClass('_disable_cell_box')
      this.$emit('dragColumnChange', this[BUS_EVENT.DRAG_DATA_DIRECTIVE])
    },
    stopEvent({scope, index}, el) {
      $(el.target).removeClass('_disable_cell_box')
      this.$emit('dragColumnChange', null)
    },
    mappingColumns(columns) {
      return columns.map(column => {
        column = defaultsDeep(column, defaultColumnConfig)
        if (!column.displayName) {
          column.displayName = column.label || startCase([column.name])
        }
        return column
      })
    },
    sortColumnsByTypes(items) {
      const clonedData = cloneDeep(this.columnData.sortedData)
      const sortedData = items.reduce((data, item) => {
        let index = data.types.indexOf(item.type)
        if (index !== -1) {
          // find column in data.columns
          const findedItem = data.columns[index].findIndex(col => col.name === item.name)
          if (findedItem !== -1) {
            data.columns[index][findedItem] = item
          } else {
            data.columns[index] = [...data.columns[index], item]
          }
        } else {
          let newType = [item]
          data.types = [...data.types, item.type]
          data.columns = [...data.columns, newType]
        }
        return data
      }, clonedData)
      this.$set(this.columnData, 'sortedData', sortedData)
    },
    convertColumns (columns) {
      let cols = this.mappingColumns(columns)
      this.sortColumnsByTypes(cloneDeep(cols))
    }
  },
  mounted() {
    this.convertColumns(this.columns)
    CBPO.$bus.$on(`open-${this.modalName}`, () => {
      this.$modal.show(this.modalName)
    })
  },
  destroyed() {
    CBPO.$bus.$off(`open-${this.modalName}`)
  },
  watch: {
    columns: {
      deep: true,
      handler(newVal, oldVal) {
        if (newVal && newVal !== oldVal) {
          this.convertColumns(newVal)
        }
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "ColumnManager";
</style>
