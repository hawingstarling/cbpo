<template>
  <b-modal id="create-tag-modal" variant="danger" dialog-class="tag-configuration-modal" hide-header centered>
    <div class="title">{{title}}</div>
    <!-- Name -->
    <p class="sub-title">Tag Name</p>
    <b-form-input class="input-search form-search-input tag-name-input" v-model="itemTag.name" placeholder="Type the name of your tag here"></b-form-input>
    <!-- Select Color -->
    <p class="sub-title">Select Tag Color</p>
    <ul class="list-color">
      <li v-for="(colorItem, index) in listColor" :key="index" class="color-item" @click="applyColorToTag(colorItem)" :class="{ 'active': itemTag.color === colorItem}" :style="{ backgroundColor: colorItem }"></li>
    </ul>
    <!-- Search -->
    <p class="sub-title select-view" @click="showViewsToApplyNewTag()">Select Views to Apply New Tag  <img src="" class="ml-1 chevron-down-img" :class="{'rotate-icon': isShowReviewer}"/></p>
    <template v-if="isShowReviewer">
      <b-form-group class="mb-0 d-flex flex-wrap w-100">
        <b-input-group class="search cancel-action form-search-custom w-100">
          <b-form-input class="input-search form-search-input" v-model="key" @keypress.enter="getSuggestion()"  @input="getSuggestion()" placeholder="Search">
          </b-form-input>
          <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon"></i>
          <div class="form-search-icon" @click="searchChange()">
            <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
          </div>
        </b-input-group>
      </b-form-group>
      <!-- List tag option -->
      <div class="list-tag-suggest checkbox-list d-flex flex-wrap" v-if="viewsByClient.length > 0">
        <b-form-group v-slot="{ ariaDescribedby }">
          <b-form-checkbox-group
            id="checkbox-view-suggest"
            v-model="itemTag.customViewIds"
            :aria-describedby="ariaDescribedby"
            value-field="item"
            text-field="name"
            name="tag-suggest"
          >
            <b-form-checkbox
              v-for="viewItem in viewsByClient"
              :key="`dataOption-${viewItem.id}`"
              :id="`dataOption-${viewItem.id}`"
              :value="viewItem.id"
              @change="selectedView(viewItem)"
              size="lg"
            >
              {{ viewItem.name }} : {{ viewItem.user_info.first_name }} {{ viewItem.user_info.last_name }} ({{ viewItem.user_info.username }})
            </b-form-checkbox>
          </b-form-checkbox-group>
        </b-form-group>
      </div>
      <div v-else-if="!isLoading" class="w-100">
        <p class="text-center p-4">No data</p>
      </div>
    </template>
    <template v-slot:modal-footer>
      <b-button variant="primary" @click="handlerSubmit()" :disabled="!validate(itemTag)">
        Next
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import debounce from 'lodash/debounce'
export default {
  name: 'CreateTag',
  props: {
    title: {
      type: String,
      required: true
    },
    handlerSubmit: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      itemTag: {
        name: '',
        color: '',
        customViewIds: [],
        viewSelected: []
      },
      listColor: ['#91E4AB', '#205FDC', '#D30B53', '#F4B400', '#303651'],
      key: '',
      tagsSelected: [],
      isLoading: false,
      isShowReviewer: false
    }
  },
  async created() {
    await this.searchChange()
  },
  methods: {
    ...mapActions({
      fetchViewsByClient: `pf/tags/fetchViewsByClient`
    }),
    async searchChange() {
      this.isLoading = true
      const payload = {
        clientId: this.$route.params.client_id,
        keyword: this.key
      }
      await this.fetchViewsByClient(payload)
      this.isLoading = false
    },
    getSuggestion: debounce(
      async function() {
        const payload = {
          clientId: this.$route.params.client_id,
          keyword: this.key
        }
        await this.fetchViewsByClient(payload)
      }, 500
    ),
    showViewsToApplyNewTag() {
      this.isShowReviewer = !this.isShowReviewer
    },
    applyColorToTag(color) {
      this.itemTag.color = color
    },
    selectedView(viewItem) {
      const savedViews = this.itemTag.viewSelected.find(item => {
        return item.id === viewItem.id
      })
      if (!savedViews) {
        this.itemTag.viewSelected.push(viewItem)
      } else {
        for (let i = 0; i < this.itemTag.viewSelected.length; i++) {
          if (this.itemTag.viewSelected[i].id === viewItem.id) {
            this.itemTag.viewSelected.splice(i, 1)
          }
        }
      }
    },
    refresh() {
      this.itemTag.name = ''
      this.itemTag.color = ''
      this.itemTag.viewSelected = []
      this.itemTag.customViewIds = []
      this.isShowReviewer = false
    }
  },
  computed: {
    ...mapGetters({
      viewsByClient: `pf/tags/viewsByClient`
    }),
    validate() {
      return tagItem => tagItem.name.trim() !== '' && tagItem.color !== ''
    }
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';

.tag-name-input {
  border-color: #F2F4F7;
}

.select-view {
  box-shadow: 0px 2px 1px #F5F5F6;
  cursor: pointer;
}
.chevron-down-img {
  background: url('~@/assets/img/icon/chevron-down.svg') no-repeat;
  background-size: 100%;
  width: 14px;
  height: 8px;
}
</style>
