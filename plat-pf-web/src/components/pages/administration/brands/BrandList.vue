<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="fa fa-tags"></i> Brands</strong>
          </span>
        </b-col>
        <b-col class="d-flex justify-content-end">
          <b-button @click="handleExportBrands()" class="mr-1" size="sm" variant="primary"><i class="icon-cloud-download mr-1"/>Export</b-button>
          <b-button size="sm" variant="primary" @click="goImport()"><i class="icon-cloud-upload mr-1"/>Import</b-button>
        </b-col>
      </b-row>
    </div>
    <div>
      <b-row class="justify-content-center align-items-center">
        <b-col md="6" class="mt-0 mb-4 d-flex justify-content-center">
          <b-form-group class="mb-0 w-100">
            <b-input-group class="search cancel-action">
              <b-form-input class="input-search" v-model="key" @keypress.enter="searchChange()" placeholder="Search for Brand">
              </b-form-input>
              <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon"></i>
              <b-input-group-append>
                <b-button @click="searchChange()">
                  <i class="icons icon-magnifier"></i>
                </b-button>
              </b-input-group-append>
            </b-input-group>
          </b-form-group>
        </b-col>
      </b-row>
      <b-table outlined striped head-variant="light" :items="brandList.results" :fields="listOfBrandFields" show-empty>
        <template v-slot:empty>
          <div class="align-items-center d-flex justify-content-center" v-if="isLoading">
            <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
          </div>
          <div class="align-items-center d-flex justify-content-center" v-else>
            <div>There are no brands to show.</div>
          </div>
        </template>
        <template v-slot:cell(is_obsolete)="row">
            <b-badge :variant="getBadgeColor(row.item.is_obsolete)">{{ upperCaseFirstLetter(row.item.is_obsolete) }}</b-badge>
        </template>
        <template v-slot:cell(actions)=row>
          <div class='d-flex'>
            <b-dropdown right variant="secondary" size="sm">
              <template v-slot:button-content>
                <i class="fa fa-cog"/>&nbsp;Manage
              </template>
              <b-dropdown-item @click="openEditBrandModal(row.item)">
                <i class="fa fa-pencil"></i>Edit
              </b-dropdown-item>
              <b-dropdown-item @click="openDeleteBrandModal(row.item)">
                <i class="fa fa-trash"></i>Delete
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </template>
      </b-table>
      <nav class="d-flex justify-content-center">
        <b-pagination @change="goToPage($event)" v-if="brandList && brandList.count > $route.query.limit" :total-rows="brandList.count || 0" :per-page="$route.query.limit" v-model="$route.query.page" prev-text="Prev" next-text="Next" hide-goto-end-buttons>
          <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
          <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
        </b-pagination>
      </nav>
    </div>
    <b-modal
        id="edit-brand"
        title="Edit Brand"
        centered
    >
        <div>
            <label class="mb-2">Name</label>
            <b-form-input class="mb-2" placeholder="Enter name" v-model="editName" @keypress.enter="handleEditBrand"></b-form-input>
        </div>
        <div>
            <label class="">Obsolete</label>
            <b-form-select v-model="selectedObsolete" :options="[{value: true, text: 'True'},{value: false, text: 'False'}]"></b-form-select>
        </div>
        <template v-slot:modal-footer>
        <div class="w-100">
            <b-button class="float-right" variant="primary" @click="handleEditBrand" :disabled="editName ? false : true">Save</b-button>
            <b-button class="float-left" @click="$bvModal.hide('edit-brand')">Cancel</b-button>
        </div>
        </template>
    </b-modal>
    <b-modal id="delete-brand-confirm-modal" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to delete this brand?</div>
        <template v-slot:modal-footer>
        <b-button variant="warning" @click="handleDeleteBrand()">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
        </b-button>
        <b-button variant @click="$bvModal.hide('delete-brand-confirm-modal')" >
            <i class="icon-close"></i> No
        </b-button>
        </template>
    </b-modal>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import { convertedPermissions as permissions } from '@/shared/utils'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import toastMixin from '@/components/common/toastMixin'
import _ from 'lodash'

export default {
  name: 'BrandsList',
  data() {
    return {
      permissions,
      listOfBrandFields: [
        {key: 'name', label: 'Name', tdClass: 'align-middle', thClass: 'align-middle w-50'},
        {key: 'is_obsolete', label: 'Obsolete', tdClass: 'align-middle', thClass: 'align-middle w-50'},
        {key: 'actions', label: 'Actions', tdClass: 'align-middle', thClass: 'align-middle'}
      ],
      key: '',
      isLoading: true,
      page: 1,
      limit: 10,
      currentBrandId: null,
      editName: '',
      selectedObsolete: null
    }
  },
  mixins: [ PermissionsMixin, toastMixin ],
  computed: {
    ...mapGetters({
      brandList: `pf/brands/brandList`
    })
  },
  methods: {
    ...mapActions({
      getBrandList: `pf/brands/getBrandList`,
      exportBrands: `pf/brands/exportBrands`,
      deleteBrand: `pf/brands/deleteBrand`,
      editBrand: `pf/brands/editBrand`
    }),
    ...mapMutations({
      setBrandList: `pf/brands/setBrandList`
    }),
    async searchChange() {
      this.setBrandList([])
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.key } })
      this.handleQueryData()
    },
    async goToPage(event) {
      this.isLoading = true
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
      this.isLoading = false
    },
    goImport() {
      this.$router.push({name: 'PFStep1ImportBrand', params: {module: 'BrandModule'}})
    },
    async handleQueryData() {
      this.isLoading = true
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        key: this.key
      }
      let data = _.pickBy({ ...payload }, _.identity)
      await this.getBrandList(data)
      this.isLoading = false
    },
    handleExportBrands() {
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          query: {
            search: this.$route.query.search
          }
        }
        this.exportBrands(payload).then(res => {
          window.location.href = res.data.file_url
        })
      } catch {
        this.vueToast('error', 'Export failed. Please retry or contact administrator.')
      }
    },
    openDeleteBrandModal(data) {
      this.currentBrandId = data.id
      this.$bvModal.show('delete-brand-confirm-modal')
    },
    handleDeleteBrand() {
      this.deleteBrand({client_id: this.$route.params.client_id, id: this.currentBrandId}).then(() => {
        this.vueToast('success', 'Brand has been deleted successfully.')
        this.handleQueryData()
      })
        .catch(() => {
          this.vueToast('error', 'You cannot delete this brand because it has items in the analysis table.')
        })
        .finally(() => {
          this.$bvModal.hide('delete-brand-confirm-modal')
        })
    },
    openEditBrandModal(data) {
      this.currentBrandId = data.id
      this.editName = data.name
      this.selectedObsolete = data.is_obsolete
      this.$bvModal.show('edit-brand')
    },
    handleEditBrand() {
      const payload = {
        client_id: this.$route.params.client_id,
        id: this.currentBrandId,
        name: this.editName,
        is_obsolete: this.selectedObsolete
      }
      this.editBrand(payload)
        .then(() => {
          this.editName = null
          this.handleQueryData()
          this.vueToast('success', 'Brand has been edited successfully.')
        })
        .catch(err => {
          this.vueToast('error', err.response.data.message)
        })
        .finally(() => {
          this.$bvModal.hide('edit-brand')
        })
    },
    upperCaseFirstLetter(word) {
      switch (word) {
        case false:
          return 'False'
        case true:
          return 'True'
        default:
          break
      }
    },
    getBadgeColor(isObsolete) {
      switch (isObsolete) {
        case false:
          return 'secondary'
        default:
          return 'primary'
      }
    }
  },
  async created() {
    await this.$router.push({
      name: 'PFBrandList',
      params: { client_id: this.$route.params.client_id },
      query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search || this.key }
    })
    this.key = this.$route.query.search || this.key
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
.thin-spinner {
  border-width: .14em;
}
</style>
