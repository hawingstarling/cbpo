<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="icon-screen-desktop"></i> Views</strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <div class="overflow-auto">
      <b-row class="justify-content-center align-items-center">
        <b-col md="3" class="mt-0 mb-4 px-1">
          <b-form-group class="mb-0">
            <b-input-group class="search cancel-action form-search-custom">
              <p class="d-flex align-items-center mr-1 font-weight-normal m-0 w-100 title-filter">Search</p>
              <b-form-input class="input-search form-search-input" v-model.trim="key" @keypress.enter="searchChange()" placeholder="Search for name">
              </b-form-input>
              <i v-if="key" @click="key='', searchChange()" class="icon-close cancel-icon form-cancel-icon"></i>
              <div class="form-search-icon" @click="searchChange()">
                <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
              </div>
            </b-input-group>
          </b-form-group>
        </b-col>
        <b-col md="2" class="mt-0 mb-4 px-1">
          <div class="d-flex flex-wrap">
            <span class="d-flex align-items-center mr-1 font-weight-normal title-filter">Filter by Tag</span>
            <b-form-select
              v-model="filterByTagValue"
              :options="tagOptionByClient"
              @change="searchChange()"
            />
          </div>
        </b-col>
        <b-col md="3" class="mt-0 px-1">
          <div class='d-flex'>
            <b-dropdown right variant="primary" class="manage-tag-dropdown dropdown-manage" text="Manage Tags">
              <b-dropdown-item @click="openCreateTagModal()">
                <img src="@/assets/img/icon/add-icon.svg" class="mr-2">Create New Tag
              </b-dropdown-item>
              <b-dropdown-divider></b-dropdown-divider>
              <b-dropdown-item @click="openEditTagModal()">
                <img src="@/assets/img/icon/edit-icon.svg" class="mr-2">Edit Tag
              </b-dropdown-item>
              <b-dropdown-divider></b-dropdown-divider>
              <b-dropdown-item @click="openApplyTagModal()">
                <img src="@/assets/img/icon/apply-tag.svg" class="mr-2">Apply Tag
              </b-dropdown-item>
            </b-dropdown>
          </div>
        </b-col>
      </b-row>
      <b-table class="view-table table-border" outlined striped head-variant="light" table-variant="secondary" :fields="filteredFields" :items="viewList.results" empty-text="There are no views to show" show-empty>
        <template v-slot:empty>
          <div class="align-middle d-flex justify-content-center align-items-center spinner-container" v-if="isLoading">
            <div class="spinner-border spinner-border-sm thin-spinner"></div>&nbsp;Loading...
          </div>
          <div class="align-middle d-flex justify-content-center" v-else>
            <div>There are no views to show</div>
          </div>
        </template>
        <template v-slot:row-details="row" class="px-0">
          <table class="w-100">
            <b-td colspan='1' class="pl-0 pb-0">
              <p class="title-preview">View Name</p>
              <b-form-input
                id="view-name"
                v-model="row.item.name"
                type="text"
                :disabled="true"
              ></b-form-input>
              <b-button
                size="sm"
                variant="secondary"
                class="mr-1 mt-2 text-truncate custom-btn"
                @click="openModal(row.item)"
              >
                Share View
              </b-button>
              <b-button
                size="sm"
                variant="primary"
                class="mr-1 mt-2 text-truncate custom-btn"
                @click="openEditModal(row.item)"
              >
                Edit View
              </b-button>
              <p class="btn-remove" @click="openConfirmModal(row.item)">Delete View</p>
            </b-td>
            <b-td colspan='2' class="pb-0">
              <p class="title-preview">Current Tags</p>
              <div class="tags">
                <b-badge
                  type="button"
                  v-for="tagItem in row.item.tags"
                  :key="`dataTag_${tagItem.tag_id}`"
                  :style="{ backgroundColor: tagItem && tagItem.tag_color || '' }"
                  @click="openComparableTableModal(row.item, tagItem)"
                  :class="{'mr-4': isEditTag, 'mr-1': !isEditTag}"
                  class="position-relative"
                >
                  {{tagItem.tag_name}} <img v-if="isEditTag" class="btn-delete-tag" @click.stop="openModalConfirmDeleteTag(row.item, tagItem)" src="@/assets/img/icon/delete-tag.svg">
                </b-badge>
              </div>
              <div class="mt-2">
                <b-button
                  size="xs"
                  variant="secondary"
                  class="mr-1 text-truncate custom-btn"
                  @click="openAddTagModal(row.item)"
                >
                  Add Tags
                </b-button>
                <b-button
                  v-if="row.item.tags.length > 0"
                  size="xs"
                  variant="secondary"
                  class="mr-1 text-truncate custom-btn"
                  @click="isEditTag = !isEditTag"
                >
                  Edit Tags
                </b-button>
              </div>
              <p class="btn-remove" v-if="row.item.tags.length > 0" @click="openModalConfirmDeleteAllTag(row.item)">Remove All Tags</p>
            </b-td>
            <b-td colspan='2' class="d-flex justify-content-end pr-0 pb-0">
              <span class="text-preview">Preview</span>
              <div
                class="expr-table"
                @click="openPreviewModal(row.item)"
              >
                <span class="overflow-hidden preview-content">
                  <div class="filter-expr-container" v-html="getFilterExpr(row.item.ds_filter)"></div>
                  <div class='h-75 text-truncate' v-html="getColumnSetExpr(row.item.ds_column.config.columns)"></div>
                </span>
              </div>
            </b-td>
          </table>
        </template>
        <template v-slot:cell(actions)="row">
          <div class="d-flex align-items-center">
            <b-button
              title="Manage"
              size="sm"
              class="mr-3 text-truncate custom-btn toggle-btn toggle-manage-btn"
              :variant="row.detailsShowing ? 'primary' : 'secondary'"
              @click="row.toggleDetails"
            >
              {{ row.detailsShowing ? 'Close' : 'Manage'}}
            </b-button>
            <b-button
              :title='`Create Alert for View "${row.item.name}"`'
              style="max-width:112px"
              class="mr-3 text-truncate btn-create-alert"
              v-if="Object.keys(row.item.alert_info).length === 0"
              @click="openCreateAlert(row.item)"
              variant="warning" text="Small" size="sm" >
              <img src="@/assets/img/icon/alert-triangle.svg" class="pagination-icon mr-1">Create Alert for View "{{row.item.name}}"
            </b-button>
            <b-button
              :title='`Alert details for View "${row.item.name}"`'
              class="mr-3 text-truncate"
              style="max-width:112px"
              v-else
              @click="openAlertDetails(row.item)"
              variant="primary" text="Small" size="sm" >
              <div style="height: 21px" class="d-flex align-items-center">
                <i class="fa fa-check-circle mr-1"></i>
                <span class="text-truncate">Alert details</span>
              </div>
            </b-button>
            <b-button
              v-if="Object.keys(row.item.alert_info).length > 0"
              :title='`Delete Alert for View "${row.item.name}"`'
              style="max-width:112px"
              class="mr-3"
              @click="openDeleteAlertModal(row.item)"
              variant="primary" text="Small" size="sm" >
              <div style="height: 21px" class="d-flex align-items-center">
                <i class="fa fa-check-circle mr-1"></i>
                <span class="text-truncate">Delete Alert for View "{{row.item.name}}"</span>
              </div>
            </b-button>
            <b-button
              style="min-width:64px"
              class="mr-3 d-flex btn-open justify-content-center align-items-center"
              v-if="hasPermission(permissions.sale.viewAll) || hasPermission(permissions.sale.view24h)"
              variant="primary" text="Small" size="sm" @click="$router.push({name: 'PFAnalysis', params: { selectedView: row.item }, query: { viewId: row.item.id }})">
              <img src="@/assets/img/icon/open-icon.svg" class="pagination-icon mr-1">Open
            </b-button>
          </div>
        </template>
        <template v-slot:cell(name)="row">
          <div class=" d-flex align-items-center col-start">
            <div><i class="fa fa-star" :class="row.item.featured ? 'text-warning' : 'text-secondary'" @click="toggleFavorite(row.item.id, row.item.featured, row.item.name)" /></div>
            <div>{{row.item.name}} {{showCreater(row.item)}}</div>
          </div>
        </template>
        <template v-slot:cell(created)="row">
          <span>{{row.item.created | moment("from", "now")}}</span>
        </template>
        <template v-slot:cell(tags)="row">
          <b-badge
            type="button" v-for="(dataItem, index) in row.item.tags"
            :key="`${index}_${dataItem.tag_name}`"
            :style="{ backgroundColor: dataItem && dataItem.tag_color || '' }"
            @click="openComparableTableModal(row.item, dataItem)"
            class="mr-1"
          >
            {{dataItem.tag_name}}
          </b-badge>
        </template>
        <template v-slot:cell(modified)="row">
          <span>{{row.item.modified | moment("from", "now")}}</span>
        </template>
      </b-table>
      <b-modal id="preview-modal" title="Preview" content-class="preview-modal" centered hide-footer>
        <template slot="modal-header-close">
          <img src="@/assets/img/icon/x.svg" @click="$bvModal.hide('preview-modal')" />
        </template>
        <div v-if="currentDsFilter" class="ml-3">
          <div v-html="getFilterExpr(currentDsFilter)"></div>
          <div v-html="getColumnSetExpr(currentColumn)"></div>
        </div>
      </b-modal>
      <b-modal size="xl" title="Comparable Table" hide-footer hide-header id="comparable-table-modal" centered>
        <div>
          <CompareTable
            :tag="currentTag"
            :actions="tableActions"
          />
        </div>
      </b-modal>
      <b-modal
        id="share-center"
        title="Confirmation"
        size="xl"
        centered
        hide-footer
      >
        <PFShareCenter :id_item="id_item" :share_mode="share_mode" type="view"></PFShareCenter>
      </b-modal>
      <b-modal id="delete-confirm" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to delete this view?</div>
        <template v-slot:modal-footer>
          <b-button variant="warning" @click="handleRemoveViewItem()" :disabled="deleting">
              <i class="icon-check"></i> Yes, I understand &amp; confirm!
          </b-button>
          <b-button variant @click="$bvModal.hide('delete-confirm')" :disabled="deleting">
              <i class="icon-close"></i> No
          </b-button>
        </template>
      </b-modal>
      <b-modal id="confirm-delete-tag-modal" variant="danger" dialog-class="alert-modal" hide-header centered>
        <div class="text-center py-3"><img src="@/assets/img/icon/alert.svg"></div>
        <div class="text-center">
          Are you sure you want to remove the tag
          <b-badge
            type="button"
            :style="{ backgroundColor: currentTag && currentTag.tag_color || '' }"
          >
            {{ currentTag && currentTag.tag_name}}
          </b-badge>
          <div class="mt-2">from <strong v-if="currentView">{{currentView.name}} {{showCreater(currentView)}}</strong></div>
        </div>
        <template v-slot:modal-footer>
          <b-button @click="$bvModal.hide('confirm-delete-tag-modal')" :disabled="deleting">
            Cancel
          </b-button>
          <b-button variant="primary" @click="handleRemoveTagItem()" :disabled="deleting">
            Remove
          </b-button>
        </template>
      </b-modal>
      <b-modal id="confirm-delete-all-tag-modal" variant="danger" dialog-class="alert-modal" hide-header centered>
        <div class="text-center py-3"><img src="@/assets/img/icon/alert.svg"></div>
        <div class="text-center">
          Are you sure you want to remove the tags
          <div class="my-2">
            <b-badge
              type="button"
              v-for="(tagItem, index) in listCurrentTag"
              :key="`${index}_${tagItem.tag_name}`"
              :style="{ backgroundColor: tagItem && tagItem.tag_color || '' }"
              class="position-relative mr-1"
            >
              {{tagItem.tag_name}}
            </b-badge>
          </div>
          from <strong v-if="currentView">{{currentView.name}} {{showCreater(currentView)}}</strong>
        </div>
        <template v-slot:modal-footer>
          <b-button @click="$bvModal.hide('confirm-delete-all-tag-modal')" :disabled="deleting">
            Cancel
          </b-button>
          <b-button variant="primary" @click="handleRemoveAllTagItem()" :disabled="deleting">
            Remove
          </b-button>
        </template>
      </b-modal>
      <b-modal id="edit-view-modal" title="Edit view" centered>
        <label class="mb-2">Name</label>
        <b-form-input class="mb-2" placeholder="Enter name" v-model="name" @keypress.enter="handleUpdateView"></b-form-input>
        <label class="mb-2">Review</label>
        <div
          v-if="currentColumn"
          class="d-flex p-1 pl-2 load-save-condition rounded border mb-2"
          v-b-popover.hover="{html: true, content: getFilterExpr(currentDsFilter) + '</br>' + getColumnSetExpr(currentColumn), customClass: 'customPopover', placement: 'right'}"
        >
          <span class="overflow-hidden">
            <span class='h-75 text-truncate' v-html="getFilterExpr(currentDsFilter)"></span>
            <!-- <span class='h-75 text-truncate' v-html="getColumnSetExpr(currentColumn)"></span> -->
          </span>
        </div>
        <div class="mb-2 d-flex">
          <label class="mr-1">Favorite</label>
          <b-form-checkbox switch v-model="currentFeatured" />
        </div>
        <div class="mb-2 d-flex flex-column">
          <label class="mr-1">Tags:</label>
          <div class="b-form-tags form-control h-auto pb-1 pt-0">
            <ul class="b-form-tags-list list-unstyled mb-0 d-flex flex-wrap align-items-center">
              <li class="badge mr-2 d-inline-flex align-items-baseline mw-100 badge-secondary label-tag" v-for="(item, index) in listTag" :key="index">
                {{ item }}
                <button class="close b-form-tag-remove" @click="removeTag(index)" type="button">×</button>
              </li>
              <li class="b-form-tag d-inline-flex align-items-baseline w-auto">
                <b-form-input
                  input-id="tags-pills"
                  v-model="tagValue"
                  @keypress.enter="addTag()"
                  class="close input-tag"
                  tag-variant="primary"
                  tag-pills
                  size="lg"
                  separator=" "
                  placeholder="Add tags by enter button"
                  list="tag-suggestion"
                  @input="getSuggestion()"
                ></b-form-input>
                <datalist id="tag-suggestion" v-if="tagValue">
                  <option v-for="itemTag in tagSuggestion" :key="itemTag">{{ itemTag }}</option>
                </datalist>
              </li>
            </ul>
          </div>
        </div>
        <template v-slot:modal-footer>
          <div class="w-100">
            <b-button
              class="float-right"
              variant="primary"
              @click="handleUpdateView"
              >Save</b-button
            >
            <b-button class="float-left" @click="$bvModal.hide('edit-view-modal')"
              >Cancel</b-button
            >
          </div>
        </template>
      </b-modal>
      <b-modal id="create-alert-modal" :title='`Create Alert for View "${name}"`' centered>
        <label class="mb-2">Refresh Rate</label>
        <b-form-select v-model="refreshRateSelected" :options="refreshRateOptions"></b-form-select>
        <div class="d-flex mt-3">
          <label class="mr-1">Throttle Alerts</label>
          <b-form-checkbox switch v-model="throttlingAlert" />
        </div>
        <span class="text-muted">(All alerts after the first, in an X hour-period, are grouped into the same message)</span>
        <b-form-group class="mt-5">
          <label class="mb-2 mt-2">Throttling Period</label>
          <b-form-select v-model="throttlingPeriodSelected" :options="throttlingPeriodOptions"></b-form-select>
        </b-form-group>
        <b-form-group>
          <label class="mb-2 mt-2">Users to send browser push notifications to:</label>
          <b-form-input disabled class="mb-2" placeholder="[User picker]" v-model="users"></b-form-input>
        </b-form-group>
        <b-form-group>
          <label class="mb-2 mt-2">Phone numbers to send alerts to (SMS):</label>
          <b-form-input class="mb-2" placeholder="Separate addresses with comma (,)" v-model="phones"></b-form-input>
        </b-form-group>
        <b-form-group>
          <label class="mb-2 mt-2">Emails Addresses to send alerts to:</label>
          <b-form-input class="mb-2" placeholder="Separate addresses with comma (,)" v-model="emails"></b-form-input>
        </b-form-group>
        <template v-slot:modal-footer>
          <div class="w-100">
            <b-button
              class="float-right"
              variant="primary"
              @click="handleCreateAlerts()"
              >Create Alert</b-button
            >
            <b-button class="float-left" @click="$bvModal.hide('create-alert-modal')"
              >Cancel</b-button
            >
          </div>
        </template>
      </b-modal>
      <b-modal id="alert-details-modal" :title='isEditAlert ? `Edit alert for View "${name}"` : `Alert details for View "${name}"`' centered>
        <label class="mb-2">Refresh Rate</label>
        <b-form-select :disabled='!isEditAlert' v-model="refreshRateSelected" :options="refreshRateOptions"></b-form-select>
        <div class="d-flex mt-3">
          <label class="mr-1">Throttle Alerts</label>
          <b-form-checkbox :disabled='!isEditAlert' switch v-model="throttlingAlert" />
        </div>
        <span class="text-muted">(All alerts after the first, in an X hour-period, are grouped into the same message)</span>
        <b-form-group class="mt-5">
          <label class="mb-2 mt-2">Throttling Period</label>
          <b-form-select :disabled='!isEditAlert' v-model="throttlingPeriodSelected" :options="throttlingPeriodOptions"></b-form-select>
        </b-form-group>
        <b-form-group>
          <label class="mb-2 mt-2">Users to send browser push notifications to:</label>
          <b-form-input readonly class="mb-2" placeholder="[User picker]" v-model="users"></b-form-input>
        </b-form-group>
        <b-form-group>
          <label class="mb-2 mt-2">Phone numbers to send alerts to (SMS):</label>
          <b-form-input :disabled='!isEditAlert' class="mb-2" placeholder="Separate addresses with comma (,)" v-model="phones"></b-form-input>
        </b-form-group>
        <b-form-group>
          <label class="mb-2 mt-2">Emails Addresses to send alerts to:</label>
          <b-form-input :disabled='!isEditAlert' class="mb-2" placeholder="Separate addresses with comma (,)" v-model="emails"></b-form-input>
        </b-form-group>
        <template v-slot:modal-footer>
          <div class="w-100">
            <b-button v-if="!isEditAlert" variant="primary" class="float-left" @click="editAlert()"
              >Edit</b-button
            >
            <b-button v-else :disabled="!isChangedAlertInfo" variant="primary" class="float-left" @click="handleUpdateAlert()"
              >Save</b-button
            >
            <b-button class="float-right" @click="$bvModal.hide('alert-details-modal')"
              >Close</b-button
            >
          </div>
        </template>
      </b-modal>
      <b-modal id="delete-confirm-alert-modal" variant="danger" centered title="Please confirm">
        <div>Are you sure you want to delete alert for this view?</div>
        <template v-slot:modal-footer>
          <b-button variant="warning" @click="handleDeleteAlert()">
              <i class="icon-check"></i> Yes, I understand &amp; confirm!
          </b-button>
          <b-button variant @click="$bvModal.hide('delete-confirm-alert-modal')">
              <i class="icon-close"></i> No
          </b-button>
        </template>
      </b-modal>
      <config-tag :title="titleModal" ref="refConfigTag" :handlerSubmit="handlerModal" :isMultiTag="isMultiTagModal"/>
      <create-tag title="Create Tag" ref="refAddTag" :handlerSubmit="nextStepConfirmCreateTagModal"/>
      <edit-tag title="Edit Tag" ref="refEditTag" :selectedTag="{...itemTag}" :handlerSubmit="handlerEditTag" :handlerExit="handlerExitModal" />
      <apply-tag title="Apply Tag to Multiple Views" ref="refApplyTag" :handlerSubmit="nextStepConfirmApplyTagModal"/>
      <confirm-tag :titleSubmit="titleSubmit" ref="refConfirmTag" :isMultiTag="isMultiTagModal" :handlerSubmit="handlerModal" :handlerExit="handlerExitModal" :itemTag="itemTag" :validate="modalValidate"/>
      <success-alert :title="titleSuccess" :content="contentSuccess"/>
    </div>
    <nav class="d-flex justify-content-center">
      <b-pagination @change="goToPage($event)" v-if="viewList && viewList.count > $route.query.limit" :total-rows="viewList.count || 0" :per-page="$route.query.limit" v-model="$route.query.page" hide-goto-end-buttons>
        <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
        <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
      </b-pagination>
    </nav>
  </b-card>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
import PFShareCenter from '@/components/common/ShareCenter'
import CompareTable from '@/components/pages/sales/compare-table/CompareTable'
import ConfigTag from '@/components/pages/sales/views/modal/ConfigTag'
import CreateTag from '@/components/pages/sales/views/modal/CreateTag'
import EditTag from '@/components/pages/sales/views/modal/EditTag'
import ConfirmTag from '@/components/pages/sales/views/modal/ConfirmTag'
import ApplyTag from '@/components/pages/sales/views/modal/ApplyTag'
import SuccessAlert from '@/components/pages/sales/views/modal/SuccessAlert'
import toastMixin from '@/components/common/toastMixin'
import exprUtil from '@/services/exprUtil'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import { convertedPermissions as permissions, showCreaterName } from '@/shared/utils'
import _ from 'lodash'
import _nav from '@/_nav'
import applyTagImg from '@/assets/img/icon/apply-tag.svg'
import removeTagImg from '@/assets/img/icon/add-icon.svg'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'

export default {
  name: 'PFViewList',
  data() {
    return {
      saveTableFields: [
        {key: 'name', lable: 'Name', tdClass: 'align-middle customName w-30 pl-0', thClass: 'th-name'},
        {key: 'tags', lable: 'Tags', tdClass: 'align-middle'},
        {key: 'created', lable: 'Created', tdClass: 'align-middle'},
        {key: 'modified', lable: 'Modified', tdClass: 'align-middle'},
        {key: 'actions', lable: 'Actions', tdClass: 'align-middle action-col'}
      ],
      id_item: '',
      share_mode: null,
      pagingViews: {
        page: 1,
        limit: 10
      },
      key: '',
      deleting: false,
      permissions,
      nav: _nav,
      isLoading: true,
      name: null,
      currentFeatured: false,
      currentDsFilter: null,
      currentColumn: null,
      currentTag: null,
      currentView: null,
      currentCustomViewId: null,
      throttlingAlert: false,
      refreshRateSelected: 'every_15_minute',
      refreshRateOptions: [
        { value: 'every_5_minute', text: 'Every 5 minutes' },
        { value: 'every_15_minute', text: 'Every 15 minutes' },
        { value: 'every_1_hour', text: 'Every 1 hour' },
        { value: 'every_24_hour', text: 'Every 24 hour' }
      ],
      throttlingPeriodSelected: 'every_6_hour',
      throttlingPeriodOptions: [
        { value: 'every_1_hour', text: 'Every 1 hour' },
        { value: 'every_2_hour', text: 'Every 2 hours' },
        { value: 'every_6_hour', text: 'Every 6 hours' },
        { value: 'every_12_hour', text: 'Every 12 hours' },
        { value: 'every_24_hour', text: 'Every 24 hours' }
      ],
      users: '',
      emails: '',
      phones: '',
      isEditAlert: false,
      alertInfoOrigin: {},
      listTag: [],
      tagValue: '',
      tagSuggestion: [],
      tagOptions: [
        { text: 'All', value: null }
      ],
      filterByTagValue: null,
      isEditTag: false,
      titleSuccess: '',
      titleModal: '',
      titleSubmit: () => {},
      handlerModal: () => {},
      handlerExitModal: () => {},
      contentSuccess: '',
      listCurrentTag: [],
      itemTag: {},
      isMultiTagModal: false,
      modalValidate: () => true,
      tableActions: [
        {
          img: applyTagImg,
          text: 'Apply Tag',
          handler: () => {
            this.$bvModal.hide('comparable-table-modal')
            this.openAddTagModal(this.currentView)
          }
        },
        {
          img: removeTagImg,
          text: 'Remove Tag',
          handler: () => {
            this.$bvModal.hide('comparable-table-modal')
            this.openModalConfirmDeleteTag(this.currentView, this.currentTag)
          }
        }
      ]
    }
  },
  mixins: [
    toastMixin,
    PermissionsMixin,
    spapiReconnectAlertMixin
  ],
  computed: {
    ...mapGetters({
      dsColumns: `pf/analysis/dsColumns`,
      viewList: `pf/analysis/viewList`,
      getUserId: `ps/userModule/GET_USER_ID`,
      listTagByClient: `pf/tags/listTagByClient`
    }),
    filteredFields() {
      if (!(this.hasPermission(this.permissions.sale.viewAll) ||
        this.hasPermission(this.permissions.sale.view24h) ||
        this.hasPermission(this.permissions.view.share) ||
        this.hasPermission(this.permissions.view.delete))
      ) {
        return this.saveTableFields.filter(f => f.key !== 'actions')
      } else {
        return this.saveTableFields
      }
    },
    showCreater() {
      return (qSelecter) => {
        let userId = this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
        return showCreaterName(qSelecter, userId)
      }
    },
    phoneNumbersFormat() {
      if (this.phones === '') return []
      const result = this.phones.split(',').map(phone => phone.trim())
      return result
    },
    emailsFormat() {
      if (this.emails === '') return []
      const result = this.emails.split(',').map(email => email.trim())
      return result
    },
    isChangedAlertInfo() {
      const alertInfoChanged = {
        throttlingAlert: this.throttlingAlert,
        refreshRateSelected: this.refreshRateSelected,
        throttlingPeriodSelected: this.throttlingPeriodSelected,
        users: this.users,
        emails: this.emails,
        phones: this.phones
      }
      return !_.isEqual(this.alertInfoOrigin, alertInfoChanged)
    },
    tagOptionByClient() {
      const options = [
        { text: 'All', value: null }
      ]
      if (this.listTagByClient && this.listTagByClient.length > 0) {
        for (const tagItem of this.listTagByClient) {
          options.push({text: tagItem.name, value: tagItem.name})
        }
      }
      return options
    }
  },
  components: {
    PFShareCenter,
    CompareTable,
    ConfigTag,
    CreateTag,
    EditTag,
    ApplyTag,
    ConfirmTag,
    SuccessAlert
  },
  methods: {
    ...mapActions({
      fetchDSColumns: `pf/analysis/fetchDSColumns`,
      fetchAllDataSourceIDs: `pf/analysis/fetchAllDataSourceIDs`,
      getViews: `pf/analysis/getViews`,
      updateCustomView: `pf/analysis/updateCustomView`,
      createAlertForView: `pf/analysis/createAlertForView`,
      editAlertForView: `pf/analysis/editAlertForView`,
      deleteAlertForView: `pf/analysis/deleteAlertForView`,
      removeView: `pf/analysis/removeView`,
      getTagSuggestions: `pf/analysis/getTagSuggestions`,
      getTagByClient: `pf/tags/getTagByClient`,
      createNewTag: `pf/tags/createNewTag`,
      addTagsToBulkView: `pf/tags/addTagsToBulkView`,
      editTagView: `pf/tags/editTagView`
    }),
    ...mapMutations({
      setViewList: `pf/analysis/setViewList`
    }),
    getSuggestion: _.debounce(
      async function() {
        const payload = {
          clientId: this.$route.params.client_id,
          keyword: this.tagValue
        }
        this.tagSuggestion = await this.getTagSuggestions(payload)
      }, 500
    ),
    getFilterExpr(filter) {
      return exprUtil.buildFilterExpr({ filter }, this.dsColumns)
    },
    getColumnSetExpr(columns) {
      return exprUtil.buildColumnSetExpr(columns)
    },
    async handleRemoveViewItem() {
      this.deleting = true
      try {
        let payload = {
          client_id: this.$route.params.client_id,
          user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id_item: this.id_item,
          search: this.key
        }
        payload.limit = this.pagingViews.limit
        payload.page = this.pagingViews.page
        await this.removeView(payload)
        await this.getViews(payload)
        this.$bvModal.hide('delete-confirm')
        this.vueToast('success', 'Removed successfully.')
      } catch {
        this.vueToast('error', 'Removing failed. Please retry or contact administrator.')
      }
      this.deleting = false
    },
    openModal(item) {
      this.id_item = item.id
      this.share_mode = item.share_mode
      this.$nextTick(() => {
        this.$bvModal.show(`share-center`)
      })
    },
    openConfirmModal(item) {
      this.id_item = item.id
      this.$nextTick(() => {
        this.$bvModal.show(`delete-confirm`)
      })
    },
    openEditModal(item) {
      this.currentFeatured = item.featured
      this.name = item.name
      this.id_item = item.id
      this.listTag = _.cloneDeep(item.tags)
      this.currentColumn = item.ds_column.config.columns
      this.currentDsFilter = item.ds_filter
      this.$nextTick(() => {
        this.$bvModal.show(`edit-view-modal`)
      })
    },
    openCreateAlert(item) {
      this.refreshRateSelected = 'every_15_minute'
      this.throttlingAlert = false
      this.throttlingPeriodSelected = 'every_6_hour'
      this.users = ''
      this.phones = ''
      this.emails = ''

      this.name = item.name
      this.currentCustomViewId = item.id
      this.$nextTick(() => {
        this.$bvModal.show(`create-alert-modal`)
      })
    },
    openAlertDetails(item) {
      this.isEditAlert = false
      this.currentAlertId = item.alert_info.id
      this.name = item.name
      this.users = item.alert_info.users.toString()
      this.phones = item.alert_info.phones.toString()
      this.emails = item.alert_info.emails.toString()
      this.currentCustomViewId = item.id
      this.throttlingAlert = item.alert_info.throttling_alert
      this.throttlingPeriodSelected = item.alert_info.throttling_period
      this.refreshRateSelected = item.alert_info.refresh_rate
      this.$nextTick(() => {
        this.$bvModal.show(`alert-details-modal`)
      })
    },
    async openDeleteAlertModal(item) {
      this.currentAlertId = item.alert_info.id
      this.$nextTick(() => {
        this.$bvModal.show(`delete-confirm-alert-modal`)
      })
    },
    async handleCreateAlerts() {
      try {
        const params = {
          clientId: this.$route.params.client_id,
          payload: {
            custom_view: this.currentCustomViewId,
            name: this.name,
            // users: [this.users],
            phones: this.phoneNumbersFormat,
            emails: this.emailsFormat,
            throttling_alert: this.throttlingAlert,
            throttling_period: this.throttlingPeriodSelected,
            refresh_rate: this.refreshRateSelected
          }
        }
        await this.createAlertForView(params)
        this.$bvModal.hide('create-alert-modal')
        this.handleQueryData()
        this.vueToast('success', 'The view has been created alerts successfully')
        this.handleAlertInfoDefault()
      } catch (err) {
        console.log(err)
        this.vueToast('error', 'Creating alert failed')
      }
    },
    handleAlertInfoDefault() {
      this.throttlingAlert = false
      this.refreshRateSelected = 'every_15_minute'
      this.throttlingPeriodSelected = 'every_6_hour'
      this.users = ''
      this.emails = ''
      this.phones = ''
    },
    editAlert() {
      this.alertInfoOrigin = {
        throttlingAlert: this.throttlingAlert,
        refreshRateSelected: this.refreshRateSelected,
        throttlingPeriodSelected: this.throttlingPeriodSelected,
        users: this.users,
        emails: this.emails,
        phones: this.phones
      }
      this.isEditAlert = !this.isEditAlert
    },
    async handleUpdateAlert() {
      try {
        const params = {
          clientId: this.$route.params.client_id,
          alertId: this.currentAlertId,
          payload: {
            custom_view: this.currentCustomViewId,
            name: this.name,
            // users: [this.users],
            phones: this.phoneNumbersFormat,
            emails: this.emailsFormat,
            throttling_alert: this.throttlingAlert,
            throttling_period: this.throttlingPeriodSelected,
            refresh_rate: this.refreshRateSelected
          }
        }
        await this.editAlertForView(params)
        this.$bvModal.hide('alert-details-modal')
        await this.handleQueryData()
        this.vueToast('success', 'The view has been edited alert successfully')
        this.handleAlertInfoDefault()
        this.isEditAlert = false
      } catch (error) {
        console.log(error)
        this.vueToast('error', 'Editing alert failed')
      }
    },
    async handleDeleteAlert() {
      try {
        this.$bvModal.hide(`delete-confirm-alert-modal`)
        const params = {
          clientId: this.$route.params.client_id,
          alertId: this.currentAlertId
        }
        await this.deleteAlertForView(params)
        this.setViewList([])
        this.handleQueryData()
        this.vueToast('success', 'The view has been deleted alert successfully')
      } catch (error) {
        console.log(error)
        this.vueToast('error', 'Deleting alert failed')
      }
    },
    async handleQueryData() {
      this.isLoading = true
      let payload = {
        search: this.key,
        tag: this.filterByTagValue,
        limit: this.$route.query.limit,
        page: this.$route.query.page,
        client_id: this.$route.params.client_id,
        user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
      }
      let data = _.pickBy({ ...payload }, _.identity)
      await this.getViews(data)
      this.isLoading = false
    },
    async goToPage(event) {
      if (this.$route.query.page !== event) {
        await this.$router.push({ query: { ...this.$route.query, page: event } })
      }
    },
    async searchChange() {
      this.setViewList([])
      this.$route.query.page = 1
      await this.$router.push({ query: { ...this.$route.query, search: this.key, tag: this.filterByTagValue, page: this.$route.query.page } })
      this.handleQueryData()
    },
    async handleUpdateView() {
      try {
        const params = {
          clientId: this.$route.params.client_id,
          userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id: this.id_item,
          data: {
            name: this.name,
            featured: this.currentFeatured,
            tags: this.listTag
          }
        }
        await this.updateCustomView(params)
        this.$bvModal.hide('edit-view-modal')
        this.vueToast('success', 'The view has been edited successfully')
        this.handleQueryData()
      } catch (error) {
        this.vueToast('error', error.response.data.message)
      }
    },
    openPreviewModal(item) {
      this.id_item = item.id
      this.currentColumn = item.ds_column.config.columns
      this.currentDsFilter = item.ds_filter
      this.$bvModal.show('preview-modal')
    },
    openModalConfirmDeleteTag(item, tag) {
      this.currentView = item
      this.name = item.name
      this.currentFeatured = item.featured
      this.id_item = item.id
      this.listCurrentTag = item.tags
      this.currentTag = tag
      this.$bvModal.show('confirm-delete-tag-modal')
    },
    async handleRemoveTagItem() {
      try {
        this.$bvModal.hide('confirm-delete-tag-modal')
        const listTag = _.filter(this.listCurrentTag, item => {
          return item.tag_id !== this.currentTag.tag_id
        })
        const params = {
          clientId: this.$route.params.client_id,
          userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id: this.id_item,
          data: {
            name: this.name,
            featured: this.currentFeatured,
            tags: _.map(listTag, 'tag_id')
          }
        }
        await this.updateCustomView(params)
        this.titleSuccess = 'Tags removed from view'
        this.contentSuccess = 'The tags have been removed from the view. Team members will be able to edit this tag and republish changes.'
        this.showSuccessAlert()
        this.handleQueryData()
      } catch (error) {
        this.vueToast('error', error.response.data.message)
      }
    },
    openModalConfirmDeleteAllTag(item) {
      this.currentView = item
      this.name = item.name
      this.currentFeatured = item.featured
      this.id_item = item.id
      this.listCurrentTag = item.tags
      this.$bvModal.show('confirm-delete-all-tag-modal')
    },
    async handleRemoveAllTagItem() {
      try {
        this.$bvModal.hide('confirm-delete-all-tag-modal')
        const params = {
          clientId: this.$route.params.client_id,
          userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id: this.id_item,
          data: {
            name: this.name,
            featured: this.currentFeatured,
            tags: []
          }
        }
        await this.updateCustomView(params)
        this.titleSuccess = 'Tags removed from view'
        this.contentSuccess = 'The tags have been removed from the view. Team members will be able to edit this tag and republish changes.'
        this.showSuccessAlert()
        this.handleQueryData()
      } catch (error) {
        this.vueToast('error', error.response.data.message)
      }
    },
    openAddTagModal(item) {
      this.id_item = item.id
      this.titleModal = 'Add Tag'
      this.handlerModal = this.handleAddTag
      this.isMultiTagModal = true
      this.$refs.refConfigTag.refresh()
      this.$bvModal.show('config-tag-modal')
    },
    async handleAddTag() {
      try {
        const customViewIds = []
        customViewIds.push(this.id_item)
        let payload = {
          tagIds: _.map(this.$refs.refConfigTag.itemTag, 'id'),
          clientId: this.$route.params.client_id,
          customViewIds
        }
        await this.addTagsToBulkView(payload)
        this.vueToast('success', 'Tags has been added.')
        this.$bvModal.hide('config-tag-modal')
        this.isLoading = true
        await this.handleQueryData()
        this.isLoading = false
      } catch (err) {
        this.vueToast('error', 'Add failed. Please retry or contact administrator.')
      }
    },
    openCreateTagModal() {
      this.$refs.refAddTag.refresh()
      this.$bvModal.show('create-tag-modal')
    },
    openEditTagModal() {
      this.titleModal = 'Edit Tag'
      this.handlerModal = this.openEditDetailTagModal
      this.isMultiTagModal = false
      this.$refs.refConfigTag.refresh()
      this.$refs.refEditTag.canApplyChange = false
      this.$bvModal.show('config-tag-modal')
    },
    openEditDetailTagModal() {
      this.$bvModal.hide('config-tag-modal')
      this.itemTag = this.$refs.refConfigTag.itemTag[0]
      this.handlerExitModal = () => {
        this.$bvModal.hide('edit-tag-modal')
        this.$bvModal.show('config-tag-modal')
      }
      this.$bvModal.show('edit-tag-modal')
    },
    async handlerEditTag() {
      let payload = {
        clientId: this.$route.params.client_id,
        tagId: this.$refs.refEditTag.selectedTag.id,
        name: this.$refs.refEditTag.selectedTag.name,
        color: this.$refs.refEditTag.selectedTag.color
      }
      await this.editTagView(payload)
      const filterByTag = this.listTagByClient.find(tag => tag.name === this.filterByTagValue)
      await this.getTagByClient({client_id: this.$route.params.client_id, user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID})
      // update filter by tag after editing itself
      if (filterByTag && this.$refs.refEditTag.selectedTag.id === filterByTag.id) {
        const currentTag = this.listTagByClient.find(tag => tag.id === filterByTag.id)
        this.filterByTagValue = currentTag.name
        await this.$router.push({ query: { ...this.$route.query, search: this.key, tag: currentTag.name, page: this.$route.query.page } })
      }
      this.handleQueryData()
      this.$bvModal.hide('edit-tag-modal')
    },
    openApplyTagModal() {
      this.$bvModal.show('apply-tag-modal')
    },
    nextStepConfirmCreateTagModal() {
      this.$bvModal.hide('create-tag-modal')
      this.itemTag = this.$refs.refAddTag.itemTag
      this.handlerModal = this.handlerAddTagModal
      this.handlerExitModal = () => {
        this.$bvModal.hide('confirm-tag-modal')
        this.$bvModal.show('create-tag-modal')
      }
      this.titleSubmit = selectedViewCount => selectedViewCount ? 'Create and Apply Tag' : 'Create Tag'
      this.isMultiTagModal = false
      this.modalValidate = this.$refs.refAddTag.validate
      this.$bvModal.show('confirm-tag-modal')
    },
    async handlerAddTagModal() {
      try {
        this.$bvModal.hide('confirm-tag-modal')
        let payload = {
          clientId: this.$route.params.client_id,
          name: this.$refs.refConfirmTag.itemTag.name,
          color: this.$refs.refConfirmTag.itemTag.color,
          custom_view_ids: this.$refs.refConfirmTag.itemTag.customViewIds
        }
        await this.createNewTag(payload)
        this.handleQueryData()
        this.titleSuccess = 'Tag created and applied'
        this.contentSuccess = 'Your tag has been created and applied to the views you chose. Team members will be able to edit this tag and republish changes.'
        this.showSuccessAlert()
      } catch (err) {
        if (err.response.data.non_field_errors) {
          this.vueToast('error', "The tag's name must be distinct.")
        }
      }
    },
    nextStepConfirmApplyTagModal() {
      this.$bvModal.hide('apply-tag-modal')
      this.itemTag = this.$refs.refApplyTag.itemSelected
      this.handlerModal = this.handlerApplyTagModal
      this.handlerExitModal = this.openAgainApplyTagModal
      this.titleSubmit = () => 'Confirm and Apply'
      this.isMultiTagModal = true
      this.modalValidate = this.$refs.refApplyTag.validate
      this.$bvModal.show('confirm-tag-modal')
    },
    openAgainApplyTagModal() {
      this.$bvModal.hide('confirm-tag-modal')
      this.$bvModal.show('apply-tag-modal')
    },
    async handlerApplyTagModal() {
      try {
        this.$bvModal.hide('confirm-tag-modal')
        this.itemTag = this.$refs.refApplyTag.itemSelected
        let payload = {
          tagIds: this.$refs.refConfirmTag.itemTag.tags,
          clientId: this.$route.params.client_id,
          customViewIds: this.$refs.refConfirmTag.itemTag.customViewIds
        }
        await this.addTagsToBulkView(payload)
        this.handleQueryData()
        // Show modal success
        this.titleSuccess = 'Tag applied to multiple views'
        this.contentSuccess = 'Your tag has been applied to the views you chose. Team members will be able to edit this tag and republish changes.'
        this.showSuccessAlert()
      } catch (err) {
        this.vueToast('error', 'Add failed. Please retry or contact administrator.')
      }
    },
    async showSuccessAlert() {
      this.$bvModal.show('success-alert-modal')
      setTimeout(() => this.$bvModal.hide('success-alert-modal'), 3000)
      let payload = {
        client_id: this.$route.params.client_id,
        user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
      }
      await this.getTagByClient(payload)
    },
    async openComparableTableModal(view, tag) {
      this.currentView = view
      this.currentTag = tag
      this.$bvModal.show('comparable-table-modal')
    },
    async toggleFavorite(viewId, currentFavorite, viewName) {
      try {
        const params = {
          clientId: this.$route.params.client_id,
          userId: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID,
          id: viewId,
          data: {
            name: viewName,
            featured: !currentFavorite
          }
        }
        await this.updateCustomView(params)
        if (!currentFavorite) {
          this.vueToast('success', `${viewName} favourite turned on`)
        } else {
          this.vueToast('success', `${viewName} favourite turned off`)
        }
        this.handleQueryData()
      } catch (error) {
        this.vueToast('error', error.response.data.message)
      }
    },
    addTag() {
      if (this.tagValue) {
        this.listTag.push(this.tagValue)
        this.tagValue = ''
      }
    },
    removeTag(index) {
      this.listTag.splice(index, 1)
    }
  },
  async created() {
    this.key = this.$route.query.search || ''
    this.filterByTagValue = this.$route.query.tag || null
    if (!this.$route.query.limit && !this.$route.query.page) {
      await this.$router.push({
        name: 'PFViewList',
        params: { client_id: this.nav.clientId },
        query: { page: this.$route.query.page || 1, limit: this.$route.query.limit || 10, search: this.$route.query.search, tag: this.filterByTagValue }
      })
    } else {
      this.handleQueryData()
    }
    let payload = {
      client_id: this.$route.params.client_id,
      user_id: this.getUserId || process.env.VUE_APP_PF_USER_ID || window.URL.VUE_APP_PF_USER_ID
    }
    await this.getTagByClient(payload)
    await this.fetchAllDataSourceIDs(payload)
    await this.fetchDSColumns(payload)
  },
  watch: {
    async $route(to, from) {
      this.key = this.$route.query.search
      if (to.fullPath !== from.fullPath) {
        await this.handleQueryData()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/listSaved.scss';
@import './modal/Modal.scss';

::v-deep .action-padding {
  padding-left: 25px;
}

::v-deep .table-border {
  overflow: hidden;
  border-top-left-radius: 5px;
  border-top-right-radius: 5px;
}

.view-table .b-table-has-details td {
  &:nth-child(2) .badge {
    background-color: #F1F1F1 !important;
  }

  &:nth-child(3),
  &:nth-child(4) {
    span {
      color: #D2D6DB;
    }
  }
}

.title-filter {
  min-height: 24px;
}

::v-deep .manage-tag-dropdown {
  height: 40px;

  .dropdown-item:active {
    color: $primary;
    background-color: #FFFFFF;
  }
}

.toggle-manage-btn {
  min-width: 88px;
  min-height: 31px;
}

::v-deep .btn.custom-btn {
  justify-content: space-between;
  font-weight: 600 !important;

  &.toggle-btn {
    @include button-icon(false, 'chevron-down.svg', 12px, 12px);

    &.btn-primary::after {
      transform: rotate(180deg);
    }
  }

  &.btn-xs {
    padding: 0.15rem 0.35rem;
    font-size: 0.76563rem;
    font-weight: 400 !important;
  }
}

.tags {
  min-height: 35px;
}

::v-deep .preview-modal.modal-content .modal-header {
  border: 0 !important;
  padding: 1rem 1rem 0;

  .close {
    margin: 0;
    padding: 0;

    img {
      width: 28px;
    }
  }
}
.form-search-custom {
  .form-search-input {
    padding-right: 30px !important;
  }
}
</style>
