<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col lg="12">
        <transition name="fade">
          <b-card no-body class="mb-0">
            <template v-slot:header>
              <div class="w-100 d-flex align-items-center">
                <i class="mr-1 icon icon-people"></i>
                <strong>Share permission </strong>
              </div>
            </template>
            <b-card-body>
              <b-row class="mb-4">
                <b-col md="2">
                  <label>Mode</label>
                  <b-form-select v-model="data_access.share_mode" :options="mode_options">
                  </b-form-select>
                </b-col>
              </b-row>
              <b-row class="mb-3">
                <b-col md="3">
                  <label>These users</label>
                  <vue-tags-input
                    v-model="new_user.tag"
                    :tags="new_user.tags"
                    placeholder="New Email"
                    @tags-changed="newTags => {new_user.tags = newTags; this.hasOneOrMoreInvalidEmail = false}"
                    class="ra-vue-tags-custom"
                  />
                  <div class="position-absolute invalid-feedback" v-if="hasOneOrMoreInvalidEmail">One or more invalid email.</div>
                </b-col>
                <b-col md="3">
                  <label>Can</label>
                  <b-form-select v-model="new_user.permission" :options="permission_options">
                  </b-form-select>
                </b-col>
                <b-col md="3" class="mb-1 d-flex align-items-end" >
                  <b-button size="sm" variant="secondary" @click="addUser" :disabled="!$v.new_user.tags.required"><i class="fa fa-plus"></i></b-button>
                </b-col>
              </b-row>
              <b-row>
                <b-col md="6">
                  <b-table
                    outlined
                    hover
                    striped
                    responsive="sm"
                    thead-class="thead-light"
                    :items="listUserShared"
                    :fields="fieldAccessUser"
                    no-local-sorting
                    show-empty
                  >
                    <template v-slot:cell(actions)="row">
                      <button class="mr-1 btn btn-danger btn-sm" @click="removeUser(row.item)">
                        <i class="fa fa-remove"></i> Remove
                      </button>
                    </template>
                    <template v-slot:cell(permission)="row">
                      <b-form-select v-model="row.item.permission" :options="permission_options"></b-form-select>
                    </template>
                  </b-table>
                </b-col>
              </b-row>
            </b-card-body>
            <template v-slot:footer>
              <b-button :disabled="!isModified" @click="$bvModal.show('share-confirm')" variant="primary" size="sm">
                Apply
              </b-button>
            </template>
          </b-card>
        </transition>
      </b-col>
      <b-modal id="share-confirm" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to share this item?</div>
        <template v-slot:modal-footer>
          <b-button variant="warning" @click="apply()">
              <i class="icon-check"></i> Yes, I understand &amp; confirm!
          </b-button>
          <b-button variant @click="$bvModal.hide('share-confirm')">
              <i class="icon-close"></i> No
          </b-button>
        </template>
      </b-modal>
    </b-row>
  </div>
</template>

<script>
import * as _ from 'lodash'
import { mapActions, mapGetters } from 'vuex'
import VueTagsInput from '@johmun/vue-tags-input'
import toastMixin from '@/components/common/toastMixin'
import { required } from 'vuelidate/lib/validators'

export default {
  name: 'PFShareCenter',
  data () {
    return {
      new_user: {
        tag: '',
        tags: [],
        permission: 'view'
      },
      mode_options: [
        {
          text: 'Private',
          value: 0
        },
        {
          text: 'Public',
          value: 1
        }
      ],
      permission_options: [
        {
          text: 'View',
          value: 'view'
        },
        {
          text: 'Edit',
          value: 'edit'
        }
      ],
      fieldAccessUser: [
        { key: 'user_email', label: 'User' },
        { key: 'permission', label: 'Can', tdClass: 'col-can w-25' },
        { key: 'actions', label: 'Actions', tdClass: 'col-action' }
      ],
      data_access: {
        share_mode: '0',
        shared_users: []
      },
      listUserShared: [],
      originalShareStatus: {},
      hasOneOrMoreInvalidEmail: false
    }
  },
  validations: {
    new_user: {
      tags: {
        required
      }
    }
  },
  props: {
    id_item: String,
    share_mode: Number,
    type: String
  },
  components: {
    VueTagsInput
  },
  mixins: [
    toastMixin
  ],
  computed: {
    ...mapGetters({
      listIdSharedFilter: `pf/share/listIdSharedFilter`,
      listIdSharedColumns: `pf/share/listIdSharedColumns`,
      listIdSharedViews: `pf/share/listIdSharedViews`,
      getUserId: `ps/userModule/GET_USER_ID`
    }),
    isModified() {
      return !_.isEqual(this.originalShareStatus, this.data_access)
    }
  },
  methods: {
    ...mapActions({
      getFilters: `pf/analysis/getFilters`,
      getListIdSharedFilter: `pf/share/getListIdSharedFilter`,
      postFilterShareMode: `pf/share/postFilterShareMode`,
      getColumnSets: `pf/analysis/getColumnSets`,
      getListIdSharedColumns: `pf/share/getListIdSharedColumns`,
      postColumnsShareMode: `pf/share/postColumnsShareMode`,
      getViews: `pf/analysis/getViews`,
      getListIdSharedViews: `pf/share/getListIdSharedViews`,
      postViewsShareMode: `pf/share/postViewsShareMode`
    }),
    addUser() {
      const EMAIL_REGREX = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/g
      this.new_user.tags.forEach((item, index) => {
        if (item.text.match(EMAIL_REGREX) && _.findIndex(this.listUserShared, { 'user_email': item.text }) === -1) {
          this.listUserShared.push({user_email: item.text, permission: this.new_user.permission})
          this.data_access.shared_users = this.listUserShared
          this.listUserShared[this.listUserShared.length - 1]._rowVariant = 'success'
          this.new_user.tags.splice(index, 1)
        }
      })
      if (this.new_user.tags.length > 0) {
        this.hasOneOrMoreInvalidEmail = true
      } else {
        this.hasOneOrMoreInvalidEmail = false
      }
    },
    removeUser(item) {
      this.listUserShared.splice(this.listUserShared.indexOf(item), 1)
      this.data_access.shared_users = this.listUserShared
      // this.data_access.shared_users = _.remove(this.data_access.shared_users, user => user.user_email !== userEmail)
      // this.listUserShared = _.remove(this.listUserShared, user => user.user_email !== userEmail)
    },
    async apply() {
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id_item: this.$props.id_item,
          share_mode: this.data_access.share_mode,
          shared_users: this.data_access.shared_users
        }
        if (this.$props.type === 'filter') {
          await this.postFilterShareMode(payload)
          this.getFilters(payload)
        }
        if (this.$props.type === 'column-set') {
          await this.postColumnsShareMode(payload)
          this.getColumnSets(payload)
        }
        if (this.$props.type === 'view') {
          await this.postViewsShareMode(payload)
          this.getViews({
            ...payload,
            page: this.$route.query.page || 1,
            limit: this.$route.query.limit || 10,
            search: this.$route.query.search || '',
            tag: this.$route.query.tag || ''
          })
        }
        this.listUserShared.forEach((item, index) => {
          item._rowVariant = ''
        })
        this.vueToast('success', 'Shared successfully.')
        this.$bvModal.hide('share-center')
      } catch (err) {
        this.vueToast('error', 'Sharing failed. Please retry or contact administrator.')
      }
    }
  },
  async created () {
    let payload = {
      client_id: this.$route.params.client_id,
      user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
      id_item: this.$props.id_item
    }
    if (this.$props.type === 'filter') {
      await this.getListIdSharedFilter(payload)
      this.listUserShared = this.listIdSharedFilter.results
      this.data_access.shared_users = this.listUserShared
      this.data_access.share_mode = this.$props.share_mode
    }
    if (this.$props.type === 'column-set') {
      await this.getListIdSharedColumns(payload)
      this.listUserShared = this.listIdSharedColumns.results
      this.data_access.shared_users = this.listUserShared
      this.data_access.share_mode = this.$props.share_mode
    }
    if (this.$props.type === 'view') {
      await this.getListIdSharedViews(payload)
      this.listUserShared = this.listIdSharedViews.results
      this.data_access.shared_users = this.listUserShared
      this.data_access.share_mode = this.$props.share_mode
    }
    this.originalShareStatus = {
      shared_users: _.cloneDeep(this.listUserShared),
      share_mode: _.cloneDeep(this.data_access.share_mode)
    }
  }
}
</script>

<style lang="scss" scoped>
  .custom-pagination {
    >.b-pagination{
      margin-bottom: 0;
    }
  }
  ::v-deep .ra-vue-tags-custom .ti-input{
    border-radius: 5px;
    border-color: #e4e7ea;
  }
  ::v-deep .col-action {
    width: 130px;
  }
  ::v-deep .col-can {
    width: 70px;
  }
  .invalid-feedback {
    display: block;
    margin-top: 0
  }
  ::v-deep .ra-vue-tags-custom .ti-input {
    overflow: hidden;
    white-space: nowrap;
  }
  ::v-deep .ra-vue-tags-custom .ti-content .ti-tag-center {
    max-width: 85px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
