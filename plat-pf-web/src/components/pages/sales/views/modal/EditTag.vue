<template>
  <b-modal id="edit-tag-modal" variant="danger" dialog-class="tag-configuration-modal" hide-header centered>
    <div class="title">{{title}}</div>
    <!-- Name -->
    <p class="sub-title">Tag Name</p>
    <b-form-input @input="handlerApplyChange" class="input-search form-search-input" v-model="selectedTag.name" placeholder="Type the name of your tag here"></b-form-input>
    <!-- Select Color -->
    <p class="sub-title">Select Tag Color</p>
    <ul class="list-color">
      <li v-for="(colorItem, index) in listColor" :key="index" class="color-item" @click="applyColorToTag(colorItem)" :class="{ 'active': selectedTag.color === colorItem}" :style="{ backgroundColor: colorItem }"></li>
    </ul>
    <template v-slot:modal-footer>
      <b-button variant="secondary" @click="handlerExit()">
        Edit
      </b-button>
      <b-button variant="primary" @click="handlerSubmit()" :disabled="!canApplyChange">
        Apply Changes
      </b-button>
    </template>
  </b-modal>
</template>

<script>

export default {
  name: 'EditTag',
  props: {
    title: {
      type: String,
      required: true
    },
    handlerExit: {
      type: Function,
      required: true
    },
    handlerSubmit: {
      type: Function,
      required: true
    },
    selectedTag: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      itemTag: {
        name: this.selectedTag.name,
        color: this.selectedTag.color,
        customViewIds: [],
        viewSelected: []
      },
      listColor: ['#91E4AB', '#205FDC', '#D30B53', '#F4B400', '#303651'],
      key: '',
      tagsSelected: [],
      isLoading: false,
      isShowReviewer: true,
      canApplyChange: false
    }
  },
  methods: {
    showViewsToApplyNewTag() {
      this.isShowReviewer = !this.isShowReviewer
    },
    handlerApplyChange() {
      this.canApplyChange = this.selectedTag.name.length && this.selectedTag.color !== ''
    },
    applyColorToTag(color) {
      this.selectedTag.color = color
      this.handlerApplyChange()
      this.$forceUpdate()
    }
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';
</style>
