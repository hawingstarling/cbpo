<template>
  <b-modal id="apply-tag-modal" variant="danger" dialog-class="tag-configuration-modal" hide-header centered>
    <div class="title">{{title}}</div>
    <!-- Select Tag -->
    <p class="sub-title">Select Tag (s)</p>
    <!-- List tag option -->
      <div class="list-tag-suggest d-flex flex-wrap" v-if="listTagByClient.length > 0">
        <b-form-group v-slot="{ ariaDescribedby }">
          <b-form-checkbox-group
            id="checkbox-tag-current"
            v-model="itemSelected.tags"
            :aria-describedby="ariaDescribedby"
            value-field="item"
            text-field="name"
            name="tag-suggest"
            switches
          >
            <b-form-checkbox
              v-for="tagItem in listTagByClient"
              :key="`dataOption-${tagItem.id}`"
              :id="`dataOption-${tagItem.id}`"
              :value="tagItem.id"
              @change="selectedTag(tagItem)"
            >
              {{ tagItem.name }}
            </b-form-checkbox>
          </b-form-checkbox-group>
        </b-form-group>
      </div>
      <div v-else-if="!isLoading" class="w-100">
        <p class="text-center p-4">No data</p>
      </div>
    <!-- Search View -->
    <p class="sub-title">Select Views to Apply Tag (s)</p>
    <template>
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
            v-model="itemSelected.customViewIds"
            :aria-describedby="ariaDescribedby"
            value-field="item"
            text-field="name"
            name="tag-suggest"
          >
            <b-form-checkbox
              v-for="(viewItem, index) in viewsByClient"
              :key="`${viewItem.name}_${index}`"
              :value="viewItem.id"
              @change="selectedView(viewItem)"
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
      <b-button variant="primary" @click="handlerSubmit()" :disabled="!validate(itemSelected)">
        Next
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import debounce from 'lodash/debounce'
export default {
  name: 'ApplyTag',
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
      itemSelected: {
        tags: [],
        tagSelected: [],
        customViewIds: [],
        viewSelected: []
      },
      key: '',
      tagsSelected: [],
      isLoading: false
    }
  },
  methods: {
    ...mapActions({
      getTagByClient: `pf/tags/getTagByClient`,
      fetchViewsByClient: `pf/tags/fetchViewsByClient`
    }),
    ...mapMutations({
    }),
    async searchChange() {
      try {
        this.isLoading = true
        const payload = {
          clientId: this.$route.params.client_id,
          keyword: this.key
        }
        await this.fetchViewsByClient(payload)
        this.isLoading = false
      } catch (err) {
        this.vueToast('error', 'Progress failed. Please retry or contact administrator.')
      }
    },
    getSuggestion: debounce(
      async function() {
        try {
          const payload = {
            clientId: this.$route.params.client_id,
            keyword: this.key
          }
          await this.fetchViewsByClient(payload)
        } catch (err) {
          this.vueToast('error', 'Progress failed. Please retry or contact administrator.')
        }
      }, 500
    ),
    selectedView(viewItem) {
      const savedViews = this.itemSelected.viewSelected.find(item => {
        return item.id === viewItem.id
      })
      if (!savedViews) {
        this.itemSelected.viewSelected.push(viewItem)
      } else {
        for (let i = 0; i < this.itemSelected.viewSelected.length; i++) {
          if (this.itemSelected.viewSelected[i].id === viewItem.id) {
            this.itemSelected.viewSelected.splice(i, 1)
          }
        }
      }
    },
    selectedTag(tag) {
      const savedTag = this.itemSelected.tagSelected.find(item => {
        return item.id === tag.id
      })
      if (!savedTag) {
        this.itemSelected.tagSelected.push(tag)
      } else {
        for (let i = 0; i < this.itemSelected.tagSelected.length; i++) {
          if (this.itemSelected.tagSelected[i].id === tag.id) {
            this.itemSelected.tagSelected.splice(i, 1)
          }
        }
      }
    }
  },
  computed: {
    ...mapGetters({
      listTagByClient: `pf/tags/listTagByClient`,
      viewsByClient: `pf/tags/viewsByClient`
    }),
    validate() {
      return tagItem => tagItem.tags && tagItem.tags.length && tagItem.customViewIds && tagItem.customViewIds.length
    }
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';
</style>
