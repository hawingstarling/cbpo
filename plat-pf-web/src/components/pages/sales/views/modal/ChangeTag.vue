<template>
  <b-modal ref="modal" variant="danger" dialog-class="tag-configuration-modal" hide-header centered>
    <div class="title">Change Tag</div>
    <!-- Search -->
    <b-form-group class="mb-0 d-flex flex-wrap w-100">
      <b-input-group class="search cancel-action form-search-custom w-100">
        <b-form-input class="input-search form-search-input" v-model="search" placeholder="Search">
        </b-form-input>
        <i v-if="search" @click="search=''" class="icon-close cancel-icon"></i>
        <div class="form-search-icon">
          <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
        </div>
      </b-input-group>
    </b-form-group>
    <!-- List tag option -->
    <div class="list-tag-suggest d-flex flex-wrap" v-if="filterTagList.length > 0">
      <b-form-group v-slot="{ ariaDescribedby }">
        <b-form-radio-group
          id="radio-tag-suggest"
          v-model="selectedTag"
          :aria-describedby="ariaDescribedby"
          name="tag-suggest"
        >
          <b-form-radio
            v-for="(tagItem, index) in filterTagList"
            :key="`${tagItem.tag_name}_${index}`"
            :value="tagItem"
          >
            {{ tagItem.tag_name }}
          </b-form-radio>
        </b-form-radio-group>
      </b-form-group>
    </div>
    <!-- Loading -->
    <div v-else-if="isLoading" class="w-100 d-flex justify-content-center align-items-center">
      <b-spinner label="Loading..."></b-spinner>
    </div>
    <!-- No Data -->
    <div v-else>
      <p class="text-center p-4">No data</p>
    </div>
    <!-- Footer -->
    <template v-slot:modal-footer>
      <b-button variant="primary" @click="applyTag()" :disabled="isLoading">
        Change
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'ChangeTagModal',
  data() {
    return {
      search: '',
      tagList: [],
      isLoading: false,
      selectedTag: null
    }
  },
  computed: {
    filterTagList() {
      return this.search
        ? this.tagList.filter(tag => tag.tag_name.includes(this.search))
        : this.tagList
    }
  },
  methods: {
    ...mapActions({
      getAllTags: `pf/compareTable/getAllTags`
    }),
    openModal() {
      this.$refs.modal.show()
    },
    hideModel() {
      this.$refs.modal.hide()
    },
    async fetchTagList() {
      try {
        this.isLoading = true
        this.tagList = await this.getAllTags({ client_id: this.$route.params.client_id })
        this.tagList.length && (this.selectedTag = this.tagList[0])
      } catch (error) {
        console.error('Failed with auto load tags. Error: ', error)
      } finally {
        this.isLoading = false
      }
    },
    applyTag() {
      this.$emit('change', this.selectedTag)
      this.hideModel()
    }
  },
  async created() {
    await this.fetchTagList()
    this.applyTag()
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';

::v-deep .form-group {
  margin-top: 8px;
}

::v-deep .list-tag-suggest {
  margin-top: 8px;

  .custom-control-label {
    padding: 4px 0 0 6px;
  }
}
</style>
