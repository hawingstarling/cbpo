<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="fa fa-users"></i> Repricing</strong>
          </span>
        </b-col>
        <b-col class="d-flex justify-content-end">
          <b-button class="mr-1" size="sm" variant="primary" @click="handelExportProfile()"><i class="icon-cloud-download mr-1"/>Export</b-button>
          <b-button size="sm" variant="primary" @click="goImport()"><i class="icon-cloud-upload mr-1"/>Import</b-button>
        </b-col>
      </b-row>
    </div>
    <div>
      <b-row class="justify-content-center align-items-center">
        <b-col md="6" class="mt-0 mb-4 d-flex justify-content-center">
          <b-form-group class="mb-0 w-75">
            <b-input-group class="search cancel-action form-search-custom">
               <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
              <b-form-input class="input-search form-search-input" v-model="key" @keypress.enter="searchChange()" placeholder="Search for keyword">
              </b-form-input>
              <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
              <div class="form-search-icon" @click="searchChange()">
                <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
              </div>
            </b-input-group>
          </b-form-group>
        </b-col>
      </b-row>
      <b-table outlined striped head-variant="light" :items="appEagleProfileList.results" :fields="itemsFields" show-empty>
        <template v-slot:empty>
          <div class="align-middle d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
          </div>
          <div class="align-middle d-flex justify-content-center" v-else>
            <div>There are no profiles to show.</div>
          </div>
        </template>
        <template v-slot:cell(profile_id_link)="row">
          <a target='_blank' :href="row.item.profile_id_link">{{ row.item.profile_id_link }}</a>
        </template>
        <template v-slot:cell(actions)="row">
          <div class='d-flex'>
            <b-dropdown right variant="secondary" class="dropdown-manage" text="Manage">
              <b-dropdown-item :disabled="!hasPermission(permissions.repricing.edit)" @click="openEditProfileModal(row.item)">
                <i class="fa fa-pencil"></i>Edit
              </b-dropdown-item>
              <b-dropdown-item :disabled="!hasPermission(permissions.repricing.delete)" @click="openRemoveModal(row.item)">
                <i class="fa fa-trash"></i>Delete
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </template>
      </b-table>
      <nav class="d-flex justify-content-center">
        <b-pagination @change="goToPage($event)" v-if="appEagleProfileList && appEagleProfileList.count > $route.query.limit" :total-rows="appEagleProfileList.count || 0" :per-page="$route.query.limit" v-model="$route.query.page" prev-text="Prev" next-text="Next" hide-goto-end-buttons>
          <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
          <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
        </b-pagination>
      </nav>
    </div>
    <b-modal id="remove-profile-confirm-modal" variant="danger" centered title="Please confirm">
      <div>Are you sure you want to remove this profile?</div>
      <template v-slot:modal-footer>
        <b-button variant="warning" @click="handleRemoveItem()" :disabled="deleting">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
        </b-button>
        <b-button variant @click="$bvModal.hide('remove-profile-confirm-modal')" :disabled="deleting">
            <i class="icon-close"></i> No
        </b-button>
      </template>
    </b-modal>
    <b-modal
      id="edit-profile-modal"
      centered
      size="lg">
      <EditProfileModal :item="itemOfEditModal" ref="editProfile"/>
      <template v-slot:modal-header>
        <div class="d-flex justify-content-center w-100">
          <h4 class="mb-0">Edit Repricing</h4>
        </div>
      </template>
      <template v-slot:modal-footer>
        <b-button @click="handleEditProfile" variant="primary">Update</b-button>
      </template>
    </b-modal>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import toastMixin from '@/components/common/toastMixin'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import EditProfileModal from '@/components/pages/administration/repricing/EditProfileModal.vue'
import _ from 'lodash'

export default {
  name: 'Repricing',
  components: {
    EditProfileModal
  },
  data() {
    return {
      key: '',
      itemsFields: [
        {key: 'profile_id', label: 'Profile ID', tdClass: 'align-middle profile-id-col w-25'},
        {key: 'profile_name', label: 'Profile Name', tdClass: 'align-middle text-nowrap w-100'},
        // {key: 'profile_id_link', label: 'Profile Link', tdClass: 'align-middle w-50'},
        {key: 'actions', label: 'Actions', tdClass: 'align-middle'}
      ],
      page: 1,
      limit: 10,
      itemToRemove: null,
      deleting: false,
      editData: {},
      permissions,
      isLoading: false,
      itemOfEditModal: {}
    }
  },
  mixins: [
    toastMixin,
    PermissionsMixin
  ],
  computed: {
    ...mapGetters({
      appEagleProfileList: `pf/appEagleProfile/appEagleProfileList`
    })
  },
  methods: {
    ...mapActions({
      getAppEagleProfileList: `pf/appEagleProfile/getAppEagleProfileList`,
      removeProfile: `pf/appEagleProfile/removeProfile`,
      editProfile: `pf/appEagleProfile/editProfile`,
      exporProfile: `pf/appEagleProfile/exporProfile`
    }),
    ...mapMutations({
      setAppEagleProfileList: 'pf/appEagleProfile/setAppEagleProfileList'
    }),
    openRemoveModal(item) {
      this.itemToRemove = item
      this.$bvModal.show('remove-profile-confirm-modal')
    },
    async handleRemoveItem() {
      this.deleting = true
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          profile_id: this.itemToRemove.id,
          page: this.page,
          limit: this.limit,
          key: this.key
        }
        await this.removeProfile(payload)
        this.$bvModal.hide('remove-profile-confirm-modal')
        this.vueToast('success', 'Removed successfully.')
      } catch {
        this.vueToast('error', 'Removing failed. Please retry or contact administrator.')
      }
      this.deleting = false
    },
    openEditProfileModal(item) {
      this.itemOfEditModal = item
      this.$nextTick(() => {
        this.$bvModal.show('edit-profile-modal')
      })
    },
    async handleEditProfile() {
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          profile_id: this.$refs.editProfile.itemEdit.id,
          profile_edit: this.$refs.editProfile.itemEdit
        }
        await this.editProfile(payload)
        this.vueToast('success', 'Repricing has been saved.')
        this.$bvModal.hide('edit-profile-modal')
        this.isLoading = true
        await this.handleQueryData()
        this.isLoading = false
      } catch (err) {
        this.vueToast('error', 'Saving failed. Please retry or contact administrator.')
      }
    },
    async handleQueryData() {
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        key: this.key
      }
      let data = _.pickBy({ ...payload }, _.identity)
      await this.loadingListAppEagleProfile(data)
    },
    async goToPage(event) {
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
    },
    goImport() {
      this.$router.push({name: 'PFStep1ImportRepricing', params: {module: 'AppEagleProfileModule'}})
    },
    async loadingListAppEagleProfile(payload) {
      this.isLoading = true
      try {
        await this.getAppEagleProfileList(payload)
      } catch (err) {
        console.log('error', err)
      }
      this.isLoading = false
    },
    async searchChange() {
      this.setAppEagleProfileList([])
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.key } })
      this.handleQueryData()
    },
    async handelExportProfile() {
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          query: {}
        }
        if (this.$route.query.search) {
          payload.query.keyword = this.$route.query.search
        }
        this.exporProfile(payload).then(res => {
          window.location.href = res.data.file_url
        })
      } catch {
        this.vueToast('error', 'Export failed. Please retry or contact administrator.')
      }
    }
  },
  async created() {
    this.key = this.$route.query.search || ''
    await this.$router.push({
      params: { client_id: this.$route.params.client_id },
      query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.key }
    })
    this.handleQueryData()
  },
  watch: {
    async $route(to, from) {
      this.key = this.$route.query.search || ''
      await this.handleQueryData()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/button.scss';

::v-deep .profile-id-col {
  width: 10%
}
.thin-spinner {
  border-width: .14em;
}
.card-body {
  padding-bottom: 0;
}
</style>
