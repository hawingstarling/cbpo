<template>
  <div class="cbpo-node tree-group"
       :class="{
        'cbpo-filter-group': filter.level > 0,
        'end-node': nodeConfig.index === nodeConfig.childNodes - 1
       }">
    <div v-if="filter && filter.conditions" class="d-flex cbpo-builder-action">
      <!-- Logic Button-->
      <template v-if="filter.conditions.length > 0">
        <button type="button" class="cbpo-btn btn-info btn-logic mr-2" @click="filter.type = SUPPORT_LOGIC.OR"
           v-if="filter.type === SUPPORT_LOGIC.AND">
          <span>AND</span>
        </button>
        <button  type="button" class="cbpo-btn btn-info btn-logic mr-2" @click="filter.type = SUPPORT_LOGIC.AND" v-else>
          <span>OR</span>
        </button>
      </template>
      <!-- End Logic Button-->
      <button type="button" @click="addNewNode" class="cbpo-btn btn-success mr-2">
          <span>
            + Rule
          </span>
      </button>
      <button  type="button" v-if="filter.level < maxlevel" @click="addNewGroup" class="cbpo-btn btn-success mr-auto">
          <span>
            + Group
          </span>
      </button>
      <button type="button" v-if="filter.level !== 0" @click="$emit('deleteGroup', builder)" :class="{'btn-delete-group' : filter.level === maxlevel}"
         class="cbpo-btn btn-danger btn-icon --outline">
        <i class="fa fa-times"></i>
      </button>
    </div>

    <!--Drop zone-->
    <div v-if="filter.level >= 1 ? nodeConfig.index === 0 : false"
         v-cbpo-droppable="{
            scope: scope,
            level: filter.level,
            node: filter,
            index: nodeConfig.index
         }"
         :key="`dropZone_${filter.id}_before`"
         :data-level="filter.level"
         :data-index="nodeConfig.index"
         class="first-group tree-group-droppable ">
      <i class="fa fa-arrow-circle-o-right"/>
    </div>

    <!--Drag node-->
    <i v-if="filter.level !== 0"
       v-cbpo-draggable="{
        scope: scope,
        level: filter.level,
        node: filter,
        index: nodeConfig.index,
        [EVENT.START_EVENT]: startEvent,
        [EVENT.STOP_EVENT]: stopEvent
       }"
       v-cbpo-connector="{
        position: {
          start: 'center',
          end: 'center'
        },
        scopeId: `connector-${scope}`
       }"
       :key="`dragNode_${filter.id}`"
       class="tree-group-draggable fa fa-arrows"/>

    <!--Drop zone-->
    <div v-if="filter.level !== 0"
         v-cbpo-droppable="{
            scope: scope,
            level: filter.level,
            node: filter,
            index: nodeConfig.index + 1
         }"
         :key="`dropZone_${filter.id}_after`"
         :data-level="filter.level"
         :data-index="nodeConfig.index + 1"
         :class="{'last-group': nodeConfig.index === nodeConfig.childNodes - 1 }"
         class="tree-group-droppable">
      <i class="fa fa-arrow-circle-o-right"/>
    </div>

    <template v-for="(element, i) in filter.conditions">
      <!--Group filter-->
      <FilterWrapper
        v-if="element.conditions"
        :key="`${i}_${filter.level}_${filter.id}_filter`"
        :scope="scope"
        :format="format"
        :fields="fields"
        :maxlevel="maxlevel"
        :operators="operators"
        :nodeConfig="getNodeConfig(filter.conditions.length, i)"
        :filter.sync="element"
        :form-columns="formColumns"
        @dropChange="dropEventChange($event)"
        @deleteGroup="deleteGroup($event)"
        @updateItems="updateItems($event)"
        :updateItemsObj="updateItemsObj"
      />
      <!--Node filter-->
      <cbpo-dynamic-node-filter
        v-else
        :key="`${i}_${filter.level}_${filter.id}_filter`"
        :format="format"
        :scope="scope"
        :node.sync="element"
        :nodeConfig="getNodeConfig(filter.conditions.length, i)"
        :fields="fields"
        :operators="operators"
        :form-columns="formColumns"
        @dropChange="dropEventChange($event)"
        @delete:node="deleteNode($event)"
        @updateItems="updateItems($event)"
        :updateItemsObj="updateItemsObj"
      />
    </template>
  </div>
</template>
<script>
import DynamicNodeFilter from './DynamicNodeFilter'
import dragDirective from '@/directives/dragDirective'
import dropDirective from '@/directives/dropDirective'
import connectorDirective from '@/directives/connectorDirective'
import CBPO from '@/services/CBPO'
import { getDefaultNode, getDefaultGroup } from './DynamicFilterConfig'
import { BUS_EVENT } from '@/services/eventBusType'
import { SUPPORT_LOGIC, findAndCreate, findAndRemove, changeFlag, updateLevel } from '@/utils/filterUtils'
import { moveElement } from '@/utils/arrayUtil'
import { cloneDeep } from 'lodash'
import { EVENT } from '@/utils/dragAndDropUtil'
import $ from 'jquery'

export default {
  name: 'FilterWrapper',
  data() {
    return {
      builder: this.filter,
      SUPPORT_LOGIC,
      EVENT
    }
  },
  props: {
    fields: Array,
    scope: String,
    operators: Array,
    format: Object,
    filter: Object,
    formColumns: Array,
    nodeConfig: {
      type: Object,
      default: function () {
        return {
          childNodes: 0,
          index: 0
        }
      }
    },
    maxlevel: Number,
    updateItemsObj: Object
  },
  directives: {
    'cbpo-draggable': dragDirective,
    'cbpo-droppable': dropDirective,
    'cbpo-connector': connectorDirective
  },
  components: {
    'cbpo-dynamic-node-filter': DynamicNodeFilter
  },
  methods: {
    startEvent(data, el) {
      let $body = $(el.target).closest('.modal-body')
      let $container = $(el.target).closest('.tree-group')

      $body
        .find('.tree-node-draggable, .tree-group-draggable')
        .addClass('hide')
      $body
        .find('.tree-node-droppable, .tree-group-droppable')
        .addClass('show')

      $container
        .find('.tree-group-droppable, .tree-node-droppable')
        .removeClass('show')
        .addClass('hide')

      $body
        .find(`.tree-node-droppable[data-level=${data.level}][data-index=${data.index}]`)
        .removeClass('show')
      $body
        .find(`.tree-node-droppable[data-level=${data.level}][data-index=${data.index + 1}]`)
        .removeClass('show')
      $body
        .find(`.tree-group-droppable[data-level=${data.level}][data-index=${data.index}]`)
        .removeClass('show')
      $body
        .find(`.tree-group-droppable[data-level=${data.level}][data-index=${data.index + 1}]`)
        .removeClass('show')

      CBPO.$bus.$emit(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_CHILD_INTERNAL}`, cloneDeep(this[BUS_EVENT.DRAG_DATA_DIRECTIVE]))
    },
    stopEvent(data, el) {
      let $body = $(el.target).closest('.modal-body')

      $body.find('.tree-node-draggable, .tree-group-draggable').removeClass('hide')
      $body.find('.tree-node-droppable, .tree-group-droppable').removeClass('show')

      CBPO.$bus.$emit(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_CHILD_INTERNAL}`, null)
    },
    dropEventChange(dragData) {
      let {data: {source, target}} = dragData
      if (source.level === target.level && source.node.parentId === target.node.parentId) {
        this.moveNodeToNewPosition(source, target)
      } else {
        CBPO.$bus.$emit(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_ROOT_INTERNAL}`, dragData)
      }
    },
    moveNodeToNewPosition(source, target) {
      this.filter.conditions = moveElement(this.filter.conditions, source.index, target.index)
    },
    modeNodeFromAnotherLevel({data: {target, source}}) {
      // reset flag
      changeFlag(false)
      findAndRemove(this.filter, source.node, target)
      updateLevel(source.node, target.node.level)
      findAndCreate(this.filter, source.node, target)
      this.$set(this.filter, 'conditions', this.filter.conditions)
    },
    addNewGroup() {
      const group = getDefaultGroup(this.filter.level)
      const node = getDefaultNode(this.filter.level + 1)
      group.conditions.push(node)
      group.parentId = this.filter.id
      node.parentId = group.id
      this.filter.conditions.push(group)
    },
    addNewNode() {
      const node = getDefaultNode(this.filter.level)
      node.parentId = this.filter.id
      this.filter.conditions.push(node)
    },
    deleteNode(node) {
      this.filter.conditions = this.filter.conditions.filter(e => e.id !== node.id)
    },
    deleteGroup(group) {
      this.filter.conditions = this.filter.conditions.filter(e => e.id !== group.id)
    },
    getNodeConfig(length, index) {
      return {childNodes: length, index: index}
    },
    updateItems(data) {
      this.$emit('updateItems', data)
    }
  },
  created() {
    if (!this.filter.conditions.length && this.level) {
      this.addNewNode()
    }
    if (this.filter.level === 0) {
      CBPO.$bus.$on(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_ROOT_INTERNAL}`, (dragData) => {
        this.modeNodeFromAnotherLevel(dragData)
      })
    }
    CBPO.$bus.$on(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_CHILD_INTERNAL}`, (dragData) => {
      this[BUS_EVENT.DRAG_DATA_DIRECTIVE] = dragData
    })
  },
  destroyed() {
    if (this.filter.level === 0) {
      CBPO.$bus.$off(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_CHILD_INTERNAL}`)
      CBPO.$bus.$off(`${this.scope}_${BUS_EVENT.NOTIFY_TO_THE_ROOT_INTERNAL}`)
    }
  },
  watch: {
    builder(val) {
      this.$emit('update:filter', val)
    },
    filter(val) {
      this.builder = val
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "FilterWrapper";
</style>
