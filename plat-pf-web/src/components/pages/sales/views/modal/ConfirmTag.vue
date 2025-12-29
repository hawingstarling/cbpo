<template>
  <b-modal id="confirm-tag-modal" variant="danger" dialog-class="tag-configuration-modal" hide-header centered>
    <div class="title">Confirm</div>
    <template v-if="isMultiTag">
      <p class="sub-title">Tag</p>
      <b-badge type="button" v-for="(tagItem, index) in itemTag.tagSelected" :key="`${index}_${tagItem.name}`" :style="{ backgroundColor: tagItem && tagItem.color || '' }" class="position-relative mr-1">{{tagItem.name}}</b-badge>
    </template>
    <template v-else>
      <!-- Name -->
      <p class="sub-title">Tag Name</p>
      <b-form-input class="input-search form-search-input" v-model="itemTag.name" placeholder="Type the name of your tag here"></b-form-input>
      <!-- Select Color -->
      <p class="sub-title">Tag Color</p>
      <ul class="list-color">
        <li class="color-item active" :style="{ backgroundColor: itemTag.color }"></li>
      </ul>
    </template>
    <!-- List view selected -->
    <p v-if="itemTag.viewSelected && itemTag.viewSelected.length" class="sub-title" @click="showViewsToApplyNewTag()">Applying to</p>
    <ul v-if="itemTag.viewSelected && itemTag.viewSelected.length" class="list-view" >
      <li class="view-item"
        v-for="(tagItem, index) in itemTag.viewSelected"
        :key="`${tagItem.name}_${index}`"
        :value="tagItem.name"
      >
        <div class="view-name">{{ tagItem.name }} : {{ tagItem.user_info.first_name }} {{ tagItem.user_info.last_name }} ({{ tagItem.user_info.username }})</div>
        <img src="@/assets/img/icon/x.svg" @click="clearItemToListView(tagItem)" class="clear-icon" alt="remove-icon"/>
      </li>
    </ul>
    <template v-slot:modal-footer>
      <b-button variant="secondary" @click="handlerExit()">
        Edit
      </b-button>
      <b-button variant="primary" @click="handlerSubmit()" :disabled="!validate(itemTag)">
        {{ titleSubmit(itemTag.viewSelected.length) }}
      </b-button>
    </template>
  </b-modal>
</template>

<script>
import { mapActions } from 'vuex'
export default {
  name: 'confirmTag',
  props: {
    titleSubmit: {
      type: Function,
      required: true
    },
    itemTag: {
      type: Object,
      required: true
    },
    handlerSubmit: {
      type: Function,
      required: true
    },
    handlerExit: {
      type: Function,
      required: false
    },
    isMultiTag: {
      type: Boolean,
      required: true
    },
    validate: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      listColor: ['#91E4AB', '#205FDC', '#D30B53', '#F4B400', '#303651'],
      tagsSelected: [],
      isLoading: false,
      isShowReviewer: true
    }
  },
  async created() {
    let payload = {
      client_id: this.$route.params.client_id
    }
    await this.getTagByClient(payload)
  },
  methods: {
    ...mapActions({
      getTagByClient: `pf/tags/getTagByClient`
    }),
    showViewsToApplyNewTag() {
      this.isShowReviewer = !this.isShowReviewer
    },
    applyColorToTag(color) {
      this.itemTag.color = color
    },
    clearItemToListView(item) {
      for (let i = 0; i < this.itemTag.viewSelected.length; i++) {
        if (this.itemTag.viewSelected[i].id === item.id) {
          this.itemTag.viewSelected.splice(i, 1)
        }
      }
      for (let i = 0; i < this.itemTag.customViewIds.length; i++) {
        if (this.itemTag.customViewIds[i] === item.id) {
          this.itemTag.customViewIds.splice(i, 1)
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import './Modal.scss';

.list-color .color-item {
  cursor: default;
}

.list-view {
  display: flex;
  flex-direction: column;
  list-style-type: none;
  padding: 0;
  border: 0.5px solid #E6E8F0;

  .view-item {
    width: 100%;
    display: flex;
    padding: 0 0 0 8px;

    &:not(:last-child) {
      border-bottom: 1px solid #E6E8F0;
    }

    .view-name {
      flex: 1 1 auto;
      padding: 8px 0;
      border-right: 1px solid #E6E8F0;
    }

    .clear-icon {
      padding: 8px;
      cursor: pointer;
    }
  }
}

.badge {
  margin-bottom: 4px;
  padding: 4px 8px;
  border-radius: 1px;
  font-size: 12px;
  color: #FFFFFF;
}
</style>
