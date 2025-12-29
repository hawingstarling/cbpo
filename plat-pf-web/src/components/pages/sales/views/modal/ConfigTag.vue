<template>
  <b-modal id="config-tag-modal" variant="danger" dialog-class="tag-configuration-modal" hide-header centered>
    <div class="title">{{title}}</div>
    <!-- Search -->
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
    <div class="list-tag-suggest d-flex flex-wrap" v-if="tagOptionByClient.length > 0">
      <b-form-group v-slot="{ ariaDescribedby }">
        <b-form-checkbox-group
          id="checkbox-tag-suggest"
          v-model="tagsSelected"
          :aria-describedby="ariaDescribedby"
          name="tag-suggest"
        >
          <b-form-checkbox
            v-for="(tagItem, index) in tagOptionByClient"
            :key="`${tagItem.name}_${index}`"
            :value="tagItem.name"
            @change="selectedTag(tagItem)"
          >
            {{ tagItem.name }}
          </b-form-checkbox>
          <b-form-invalid-feedback class="error-select-tag" :state="state" v-if="tagsSelected.length !== 0 && !isMultiTag">Please pick just one tag</b-form-invalid-feedback>
        </b-form-checkbox-group>
      </b-form-group>
    </div>
    <div v-else-if="isLoading" class="w-100 d-flex justify-content-center align-items-center">
      <b-spinner label="Loading..."></b-spinner>
    </div>
    <div v-else>
      <p class="text-center p-4">No data</p>
    </div>
    <template v-slot:modal-footer>
      <b-button variant="primary" @click="handlerSubmit()" :disabled="tagsSelected.length !== 1">
        Next
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import debounce from 'lodash/debounce'
export default {
  name: 'ConfigTag',
  props: {
    title: {
      type: String,
      required: true
    },
    handlerSubmit: {
      type: Function,
      required: true
    },
    isMultiTag: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      itemTag: [],
      tagsSelected: [],
      tagSuggestion: [],
      key: '',
      isLoading: false
    }
  },
  methods: {
    ...mapActions({
      getTagByClient: `pf/tags/getTagByClient`,
      getTagSuggestions: `pf/analysis/getTagSuggestions`
    }),
    async searchChange() {
      this.isLoading = true
      const payload = {
        client_id: this.$route.params.client_id,
        keyword: this.key
      }
      await this.getTagByClient(payload)
      this.isLoading = false
    },
    getSuggestion: debounce(
      async function() {
        this.isLoading = true
        const payload = {
          client_id: this.$route.params.client_id,
          keyword: this.key
        }
        await this.getTagByClient(payload)
        this.isLoading = false
      }, 500
    ),
    selectedTag(tagItem) {
      const savedViews = this.itemTag.find(item => {
        return item.id === tagItem.id
      })
      if (!savedViews) {
        this.itemTag.push(tagItem)
      } else {
        for (let i = 0; i < this.itemTag.length; i++) {
          if (this.itemTag[i].id === tagItem.id) {
            this.itemTag.splice(i, 1)
          }
        }
      }
    },
    refresh() {
      this.itemTag = []
      this.tagsSelected = []
      this.tagSuggestion = []
      this.key = ''
      this.isLoading = false
    }
  },
  computed: {
    ...mapGetters({
      listTagByClient: `pf/tags/listTagByClient`
    }),
    state() {
      return this.tagsSelected.length === 1
    },
    tagOptionByClient() {
      return this.listTagByClient
    }
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

.error-select-tag {
  width: 100%;
  margin: 0;
  padding: 8px 0;
  font-size: 12px;
  text-align: center;
}
</style>
