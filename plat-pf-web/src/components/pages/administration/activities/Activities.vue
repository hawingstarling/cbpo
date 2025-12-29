<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="icon-clock"></i> Activities</strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <b-row class="justify-content-center">
      <b-col md="4" class="mt-0 mb-4">
        <b-form-group class="mb-0">
          <b-input-group class="search cancel-action form-search-custom">
            <!-- <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p> -->
            <b-form-input class="form-search-input" v-model="params.key" @keypress.enter="searchChange()" placeholder="Search for user, action and data">
            </b-form-input>
            <i v-show="params.key" @click="params.key = '';searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
            <div class="form-search-icon" @click="searchChange()">
              <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
            </div>
          </b-input-group>
        </b-form-group>
      </b-col>
    </b-row>
    <b-row>
      <b-col class="table-responsive col-12">
        <b-table
          show-empty
          hover
          outlined
          striped
          responsive="sm"
          :fields="fields"
          :items="activitiesList.results"
          id="activity-table"
          class="tb-activity"
        >
          <template v-slot:empty>
            <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="isLoading">
              <div class="spinner-border thin-spinner spinner-border-sm thin-spinner"></div>&nbsp;Loading...
            </div>
            <div class="align-middle d-flex justify-content-center" v-else>
              <div>There is no activity to show.</div>
            </div>
          </template>
          <template v-slot:cell(user)="row">
            <div class="d-flex justify-content-center">
              <div class="text-center">
                <div v-if="row.item.user_info.first_name && row.item.user_info.last_name">{{row.item.user_info.first_name}} {{row.item.user_info.last_name}}</div>
                <div>{{row.item.user_info.email}}</div>
              </div>
            </div>
          </template>
          <template v-slot:cell(action)="row">
            <div>{{row.item.action.split('_').join(' ')}}</div>
          </template>
          <template v-slot:cell(data)="row">
            <div
              v-b-popover.hover.right.html="showData(row.item.data)"
              class="text-center"
            >
              {...}
            </div>
          </template>
          <template v-slot:cell(time)="row">
            <div class="text-center">{{row.item.created | moment('from')}}</div>
          </template>
        </b-table>
        <nav class="d-flex justify-content-center">
          <b-pagination @click.native="goToPage" v-if="activitiesList.count && activitiesList.count > params.limit" :total-rows="activitiesList.count || 0" :per-page="params.limit" v-model="params.page" prev-text="Prev" next-text="Next" hide-goto-end-buttons>
            <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
            <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
          </b-pagination>
        </nav>
      </b-col>
    </b-row>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import placeholderURL from '@/assets/img/profile-placeholder.png'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import _ from 'lodash'
export default {
  name: 'PFActivities',
  mixins: [PermissionsMixin],
  data: () => {
    return {
      fields: [
        { key: 'user', label: 'User', class: 'vertical-content user-td', thClass: 'w-25 text-center align-middle', tdClass: 'justify-content-center align-middle' },
        { key: 'action', label: 'Action', class: 'vertical-content action-td', thClass: 'w-25 text-center align-middle', tdClass: 'justify-content-center text-center align-middle' },
        { key: 'data', label: 'Data', class: 'vertical-content data-td', thClass: 'w-25 text-center align-middle', tdClass: 'justify-content-center align-middle' },
        { key: 'time', label: 'Time', class: 'vertical-content time-td', thClass: 'w-25 text-center align-middle', tdClass: 'justify-content-center align-middle' }
      ],
      params: {
        page: 1,
        limit: 10,
        id: '',
        key: '',
        action: null
      },
      isLoading: false
    }
  },
  computed: {
    ...mapGetters({
      activitiesList: `pf/activities/activitiesList`
    }),
    placeholderURL () {
      const temp = placeholderURL.split('/')
      const imgName = temp[temp.length - 1]
      return `/img/${imgName}`
    }
  },
  methods: {
    ...mapActions({
      getActivitiesList: `pf/activities/getActivitiesList`
    }),
    ...mapMutations({
      setActivitiesList: `pf/activities/setActivitiesList`
    }),
    searchChange() {
      this.setActivitiesList([])
      this.params.page = 1
      this.getActivitiesList(this.params)
      this.handleQueryData()
    },
    goToPage () {
      this.getActivitiesList(this.params)
    },
    showData (data) {
      let content = '<div style="overflow: auto; max-height: 500px;">{'
      if ((typeof data) === 'object') {
        for (let key in data) {
          content += `<div style="margin-left: 15px;">${key} : ${data[key]}</div>`
        }
      }
      content += '}</div>'
      return content
    },
    async handleQueryData() {
      let payload = {
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        key: this.key
      }
      let data = _.pickBy({ ...payload }, _.identity)
      await this.loadingListActivity(data)
    },
    async loadingListActivity(payload) {
      this.isLoading = true
      try {
        await this.getActivitiesList(payload)
      } catch (err) {
        console.log('error', err)
      }
      this.isLoading = false
    }
  },
  created() {
    this.params.client_id = this.$route.params.client_id
    this.getActivitiesList(this.params)
    this.handleQueryData()
  }
}
</script>

<style lang="scss" scoped>
  .table-responsive {
    overflow-x: visible;
    margin-bottom: 0;
  }
  /deep/ #activity-table {
    thead {
      th {
        &.action-td {
          width: 400px;
        }
        &.data-td {
          width: 70px;
        }
        &.time-td {
          width: 150px;
        }
      }
    }
  }
  .cancel-icon {
    position: absolute;
    cursor: pointer;
    right: 50px;
    top: 50%;
    z-index: 20;
    transform: translateY(-50%);
  }
  .form-control {
    padding-right: 35px
  }
  .spinner-container {
    height: 50px;

    .thin-spinner {
      border-width: 1px;
    }
  }

  .tb-activity {
    border-radius: 4px;
    overflow: hidden;

    ::v-deep thead {
      height: 56px;
    }
  }
  .form-search-custom {
    .form-cancel-icon {
      top: 50% !important;
    }
  }
  .card-body {
    padding-bottom: 0;
  }
</style>
