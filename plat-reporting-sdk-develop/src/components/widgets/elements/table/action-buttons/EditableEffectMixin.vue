<script>
import $ from 'jquery'
import CBPO from '@/services/CBPO'
import uniq from 'lodash/uniq'
import cloneDeep from 'lodash/cloneDeep'
import isObject from 'lodash/isObject'
import get from 'lodash/get'
import { BUS_EVENT } from '@/services/eventBusType'
import { BULK_ACTION_MODE } from '@/components/widgets/elements/table/TableConfig'

export default {
  data() {
    return {
      event: {
        shift: false,
        ctrl: false
      },
      isSelectedAllMatchedItems: false,
      cursor: null,
      uniqueKeyIndex: null,
      selectedItems: [],
      updatedItems: []
    }
  },
  computed: {
    checkedState() {
      if (!this.selectedItems.length) return 'unchecked'
      return this.dataTable.items.length === this.selectedItems.length
        ? 'checked'
        : 'partial-checked'
    },
    isSelected() {
      return (item) => this.selectedItems.includes(item.pk_id_sdk)
    },
    isUpdated() {
      return (item) => this.updatedItems.includes(item.pk_id_sdk)
    }
  },
  methods: {
    findItemIndexByKey(array, id) {
      return array.findIndex(data => id === (isObject(data) ? data.pk_id_sdk : data))
    },
    generateArray(first, second) {
      let newArray = []
      if (first < second) {
        for (let i = first; i <= second; i++) {
          newArray.push(i)
        }
      } else {
        for (let i = second; i <= first; i++) {
          newArray.push(i)
        }
      }
      return newArray
    },
    triggerEventHandler(item) {
      if (!this.config.rowActions.enabled || !this.config.bulkActions.enabled) return
      if (this.config.bulkActions.mode === BULK_ACTION_MODE.CHECKBOX) return

      this.config.rowActions.eventHandler('dblClick', item)
    },
    deactiveAndSelect(event, column, item, index) {
      if (get(this.config, 'globalControlOptions.globalGrouping.config.value')) return
      if (column.grouped && item.group.level === 0) return
      if (!this.config.rowActions.enabled || !this.config.bulkActions.enabled) return
      if (this.config.bulkActions.mode === BULK_ACTION_MODE.CHECKBOX) return

      if (this.event.ctrl || this.event.shift) {
        this.selectItem(event, index, item)
      } else {
        this.resetAndSelect(item)
      }
    },
    resetAndSelect(item) {
      this.selectedItems.includes(item.pk_id_sdk)
        ? this.selectedItems = []
        : (this.selectedItems = [item.pk_id_sdk])

      this.cursor = item.pk_id_sdk
    },
    selectItem(event, indexRow, item) {
      if (!this.config.rowActions.enabled || !this.config.bulkActions.enabled) return

      const indexItem = this.findItemIndexByKey(this.selectedItems, item.pk_id_sdk)
      const isExisted = indexItem !== -1

      // Case 1: Multi Select
      if (
        this.event.shift &&
        !this.event.ctrl &&
        this.cursor !== null &&
        this.cursor !== item.pk_id_sdk
      ) {
        const indexNewCursor = this.dataTable.items.findIndex(item => item.pk_id_sdk === this.cursor)
        const indexOldCursor = this.dataTable.items.findIndex(item => item.pk_id_sdk === this.selectedItems[indexItem])
        const rangeIndexes = this.generateArray(
          indexNewCursor,
          isExisted
            ? (indexNewCursor > indexOldCursor ? indexRow + 1 : indexRow - 1)
            : indexRow
        )
        // if all index already is selected then remove it
        const isSlide = rangeIndexes.every((index) =>
          this.selectedItems.includes(this.dataTable.items[index].pk_id_sdk)
        )
        rangeIndexes.forEach((index) => {
          isSlide
            ? (this.selectedItems = this.selectedItems.filter(
              (id) => id !== this.dataTable.items[index].pk_id_sdk
            ))
            : (this.selectedItems = uniq([
              ...this.selectedItems,
              this.dataTable.items[index].pk_id_sdk
            ]))
        })
      } else {
        // Case 2: Single Select
        !isExisted
          ? this.selectedItems.push(item.pk_id_sdk)
          : this.selectedItems.splice(indexItem, 1)
      }
      this.cursor = item.pk_id_sdk
      this.isSelectedAllMatchedItems = false
    },
    toggleSelect() {
      if (this.selectedItems.length > 0) {
        this.selectedItems = []
        this.isSelectedAllMatchedItems = false
      } else {
        this.selectedItems = this.dataTable.items.map((item) => item.pk_id_sdk)
      }
    },
    deselectItems() {
      this.selectedItems = []
      this.cursor = null
    },
    allItemsSelected() {
      this.isSelectedAllMatchedItems = true
    }
  },
  mounted() {
    this.$nextTick(() => {
      $(window).on('keydown.analysis-table', (event) => {
        if (event.key === 'Shift') this.event.shift = true
        if ((event.key === 'Control' || event.key === 'Meta') && this.config.bulkActions.mode !== BULK_ACTION_MODE.CHECKBOX) this.event.ctrl = true
      })
      $(window).on('keyup.analysis-table', (event) => {
        if (event.key === 'Shift') this.event.shift = false
        if ((event.key === 'Control' || event.key === 'Meta') && this.config.bulkActions.mode !== BULK_ACTION_MODE.CHECKBOX) this.event.ctrl = false
      })
    })
  },
  watch: {
    'dataTable.items'() {
      const isNotChanged = this.selectedItems.every((selectItem) =>
        this.dataTable.items.some(item => item.pk_id_sdk === selectItem)
      )
      if (!isNotChanged) this.deselectItems()
    },
    'dataTable.items.length'() {
      this.isSelectedAllMatchedItems = false
    },
    isSelectedAllMatchedItems(newValue) {
      this.config.bulkActions.filterMode = newValue
    },
    dataTable: {
      deep: true,
      handler() {
        this.config.bulkActions.total = this.dataTable.total
      }
    },
    configReady() {
      this.$nextTick(() => {
        if (this.configReady) {
          this.uniqueKeyIndex =
            this.config.columns.findIndex((column) => column.isUniqueKey) ||
            null

          CBPO.$bus.$on(
            BUS_EVENT.SINGLE_EDIT_UPDATE(this.config.id),
            data => {
              const { id, updatedData } = data
              const rowIndex = this.findItemIndexByKey(
                this.dataTable.items,
                id
              )
              if (rowIndex !== -1) {
                Object.keys(updatedData.data).forEach(key => {
                  if (updatedData.data[key].formatFn) {
                    // apply format to new item
                    updatedData.data[key].format = updatedData.data[key].formatFn(updatedData.data[key].base)
                  } else {
                    // set format as base
                    updatedData.data[key].format = updatedData.data[key].base
                  }
                })

                // update new data
                this.$set(this.dataTable.items, rowIndex, cloneDeep(updatedData))
                // reload change for current row
                this.dataTable.items[rowIndex].key++

                // highlight item after update 3s
                this.updatedItems.push(updatedData.pk_id_sdk)
                setTimeout(() => (this.updatedItems = []), 3000)
              }
            }
          )
          CBPO.$bus.$on(
            BUS_EVENT.BULK_EDIT_UPDATE(this.config.id), () => {
              // Do nothing
            }
          )
          CBPO.$bus.$on(BUS_EVENT.SINGLE_DELETE(this.config.id), id => {
            const rowIndex = this.findItemIndexByKey(
              this.dataTable.items,
              id
            )
            if (rowIndex !== -1) {
              this.dataTable.items.splice(rowIndex, 1)
            }
          })
          CBPO.$bus.$on(BUS_EVENT.BULK_DELETE(this.config.id), () => {
            // Do nothing
          })
        }
      })
    },
    selectedItems() {
      document.getSelection().removeAllRanges()
    }
  },
  beforeDestroy() {
    $(window).off('.analysis-table')
    CBPO.$bus.$off(BUS_EVENT.SINGLE_EDIT_UPDATE(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.BULK_EDIT_UPDATE(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.SINGLE_DELETE(this.config.id))
    CBPO.$bus.$off(BUS_EVENT.BULK_DELETE(this.config.id))
  }
}
</script>
