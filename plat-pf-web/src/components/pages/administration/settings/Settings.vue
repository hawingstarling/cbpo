<template>
  <b-card>
    <div slot="header">
      <b-row align-v="center">
        <b-col class="col-6">
          <span>
            <strong><i class="fa fa-cog"></i> Settings</strong>
          </span>
        </b-col>
      </b-row>
    </div>
    <div class="align-items-center d-flex justify-content-center" v-if="isLoadingSetting">
      <div class="spinner-border thin-spinner spinner-border-sm cls-loading-setting"></div>&nbsp;Loading...
    </div>
    <div class="settings-body" v-else>
      <div class="d-flex align-items-center cls-sale-date">
        <span class="label-style mr-2">Allow Sale Data Update After</span>
        <Datepicker
          format="MM-DD-YYYY"
          v-model="currentData.allow_sale_data_update_from"
          :disabled="!hasPermission(permissions.admin.settingsChange)"
          class="flex-grow-1"
        />
      </div>
      <div class="d-flex py-3 pr-3">
        <b-form-checkbox
          v-model="currentData.is_remove_cogs_refunded"
          name="isRemoveCogsRefunded"
        >Remove COGs for partially refunded items
        </b-form-checkbox>
      </div>
      <div class="mt-3 mb-3 cls-alert">
        <b-alert show variant="primary">Please select your integration method</b-alert>
      </div>
      <div class="d-flex">
        <div class="cls-seller-integration">
          <h4 class="mt-3 mb-3">Seller Central Integration - MWS API</h4>
          <div class="d-flex align-items-center mt-3 mx-2">
            <span class="label-style">MWS Access Key</span>
            <b-form-input
              v-model="currentData.ac_mws_access_key"
              :disabled="!hasPermission(permissions.admin.settingsChange)||!currentData.ac_mws_enabled"
              type="password"
            >
            </b-form-input>
          </div>
          <div v-show="!$v.currentData.ac_mws_access_key.required && currentData.ac_mws_enabled" style="margin-left:194px" class="mt-1 text-danger">The MWS Access Key is required</div>
          <div class="d-flex align-items-center mt-3 mx-2">
            <span class="label-style">MWS Secret Key</span>
            <b-form-input
              v-model="currentData.ac_mws_secret_key"
              :disabled="!hasPermission(permissions.admin.settingsChange)||!currentData.ac_mws_enabled"
              type="password"
            >
            </b-form-input>
          </div>
          <div v-show="!$v.currentData.ac_mws_secret_key.required && currentData.ac_mws_enabled" style="margin-left:194px" class="mt-1 text-danger">The MWS Secret Key is required</div>
          <div class="d-flex align-items-center mt-3 mx-2">
            <span class="label-style">MWS Merchant ID</span>
            <b-form-input
              v-model="currentData.ac_mws_merchant_id"
              :disabled="!hasPermission(permissions.admin.settingsChange)||!currentData.ac_mws_enabled"
            >
            </b-form-input>
          </div>
          <div v-show="!$v.currentData.ac_mws_merchant_id.required && currentData.ac_mws_enabled" style="margin-left:194px" class="mt-1 text-danger">The MWS Merchant ID is required</div>
          <div class="d-flex align-items-center mt-3 mx-2">
            <span class="label-style">MWS Merchant Name</span>
            <b-form-input
              v-model="currentData.ac_mws_merchant_name"
              :disabled="!hasPermission(permissions.admin.settingsChange)||!currentData.ac_mws_enabled"
            >
            </b-form-input>
          </div>
          <div v-show="!$v.currentData.ac_mws_merchant_name.required && currentData.ac_mws_enabled" style="margin-left:194px" class="mt-1 text-danger">The MWS Merchant Name is required</div>
          <div class="d-flex align-items-center mt-3 mx-2">
            <span class="label-style">MWS Enabled</span>
            <b-form-checkbox switch v-model="currentData.ac_mws_enabled" />
          </div>
        </div>
      <div class="connect">
        <div class="d-flex">
          <div class="mt-3 mx-2">
            <div>
              <h4>Seller Central Integration - Connect</h4>
              <b-button @click="openConfirmModal" v-if="!currentData.ac_spapi_enabled">Connect to your Seller
                Central
              </b-button>
            </div>
            <div class="cls-btn-revoke" v-if="currentData.ac_spapi_enabled">
              <span class="label-style mt-2">You have already connected to your Seller Central</span><br>
              <b-button class="mt-2" @click="openConfirmModal">Revoke Access</b-button>
            </div>
          </div>
        </div>
        <div class="d-flex w-100">
          <div class="mt-3 mx-2 w-100">
            <h4>Shopify Integration - Connect</h4>
            <div v-if="!isShopifyPartnerConnected" class="d-flex p-3">
              <b-form-checkbox
                v-model="acceptConnectFromShopifyAdmin"
                name="acceptConnectFromShopifyAdmin"
                value="accepted"
                unchecked-value="not_accepted"
              >Shopify Public App Store
              </b-form-checkbox>
            </div>
            <div v-if="acceptConnectFromShopifyAdmin === 'accepted'" class="p-3">
              <span>Register your merchant here and then install Precise Financial App in Shopify Public App Store!</span>
              <div class="shopify-app d-flex justify-content-center p-3">
                <b-button type="button" class="col-5" @click="registerShopUrl" :disabled="!register_shop_url">Register merchant </b-button>
                <b-form-input class="col"
                  placeholder="SHOP_NAME.myshopify.com"
                  v-model="register_shop_url"
                  :disabled=isShopifyPartnerConnected
                >
                </b-form-input>
              </div>
            </div>
            <div v-else class="d-flex input-group">
              <b-button @click="connectShopifyPartner" v-if="!isShopifyPartnerConnected">Connect to your Shopify
              </b-button>
              <div div class="cls-btn-revoke col-sm" v-else>
                <div class="container">
                  <span class="label-style row text-center">You have already connected to your Shopify Partner</span>
                  <div class="row mt-2" style="display: flex; justify-content: center">
                    <b-button @click="revokeShopifyPartner">Revoke Access</b-button>
                  </div>
                </div>
              </div>
              <b-form-input
                placeholder="SHOP_NAME.myshopify.com"
                v-model="shop_url"
                :disabled=isShopifyPartnerConnected
              >
              </b-form-input>
            </div>
          </div>
        </div>
      </div>
      </div>
      </div>
      <hr style="margin: 30px 0;">
      <h4 class="mt-3 mb-3">COGS</h4>
      <div class="d-flex flex-row">
        <fieldset class="p-3 width-50">
          <div class="input-group d-inline-block">
            <span class="label-style mb-1">
              <h5>Source</h5>
            </span>
            <fieldset class="pt-2 rounded">
              <b-form-checkbox v-model="currentData.cog_use_extensiv" name="useExtensiv">
                Use Extensiv
              </b-form-checkbox>

              <div class="d-flex align-items-center mt-2 ml-4">
                <span class="label-style mb-1">Access Token</span>
                <b-form-input
                  v-model="currentData.cog_extensiv_token"
                  :disabled="!hasPermission(permissions.admin.settingsChange)||!currentData.cog_use_extensiv"
                  placeholder="Enter Extensiv Access Token"
                  type="password"
                  @input="$v.currentData.cog_extensiv_token.$touch()"
                >
                </b-form-input>
              </div>
              <div v-show="!$v.currentData.cog_extensiv_token.requiredWhenExtensiv && currentData.cog_use_extensiv" class="mt-1 text-danger">
                The Extensiv Access Token is required
              </div>
            </fieldset>
            <fieldset class="pt-2 rounded">
              <div class="input-group d-inline-block">
                <b-form-checkbox v-model="currentData.cog_use_dc" name="useDC">
                  Use Data Central (DC)
                </b-form-checkbox>
              </div>
            </fieldset>
            <fieldset class="pt-2 rounded">
              <div class="input-group d-inline-block">
                <b-form-checkbox v-model="currentData.cog_use_pf" name="useItem">
                  Use Internal Precise Financial COGS
                </b-form-checkbox>
              </div>
              <div class="text-danger mt-2" v-show="showNoCOGSEnableError && noCOGSEnable">
                At least one COGS source must be enabled
              </div>
            </fieldset>
          </div>
        </fieldset>
        <fieldset class="width-50 p-3">
          <div class="input-group d-flex flex-column">
            <div class="d-flex align-items-center mb-2 mr-2">
              <span class="mb-0">
                <h5 class="mb-0 mr-2">Priority Source</h5>
              </span>
              <div>
                <span id="question-tooltip-priority-source" class="ml-1">
                  <i class="fa fa-question-circle-o"></i>
                </span>
                <b-popover target="question-tooltip-priority-source" triggers="hover" placement="top">
                  <div>{{ prioritySourceTooltip }}</div>
                </b-popover>
              </div>
            </div>
            <Container
              @drop="onDrop"
              :get-child-payload="getChildPayload"
              class="pt-2"
            >
              <Draggable v-for="(option, index) in prioritySourceItems" :key="option.value">
                <div class="draggable-item">
                  <label class="priority-number">{{ index + 1 }}.</label>
                  <div class="drag-handle">
                    <i class="fa fa-bars"></i>
                  </div>
                  <label class="priority-text">
                    {{ option.displayName }}
                  </label>
                </div>
              </Draggable>
            </Container>
          </div>
        </fieldset>
      </div>

      <!-- <div v-if="!isLoadingSetting" class="d-flex mt-3">
        <div class="cls-seller-integration d-flex align-items-center">
          <h4 class="mt-3 mb-3">CartRover Integration</h4>
          <div class="add-cartRover" @click="addCartRover">
            <img src="@/assets/img/icon/add-icon.svg" class="ml-2">
          </div>
        </div>
      </div>
    <b-row v-if="!isLoadingSetting">
      <b-col v-for="(item, index) in currentData.ac_cart_rover" :key="index" class="col-3">
        <div class="cartRover-item">
          <div class="d-flex align-items-center position-relative">
            <span class="cartRover-label">Merchant Name</span>
            <b-form-input
              v-model="item.merchant_name"
              disabled
              type="text"
            >
            </b-form-input>
          </div>
          <div class="d-flex align-items-center position-relative mt-4">
            <span class="cartRover-label">API User</span>
            <b-form-input
              v-model="item.api_user"
              disabled
              type="text"
            >
            </b-form-input>
          </div>
          <div class="d-flex align-items-center position-relative my-4">
            <span class="cartRover-label">API Key</span>
            <b-form-input
              v-model="item.api_key"
              disabled
              type="password"
            >
            </b-form-input>
          </div>
          <div class="text-right mt-3">
            <b-button @click="deleteCartRover(index)">Delete</b-button>
          </div>
        </div>
      </b-col>
    </b-row>
    <b-row v-if="!isLoadingSetting">
      <b-col class="col-3">
        <div class="d-flex align-items-center">
          <span class="cartRover-label mr-3">Enabled</span>
          <b-form-checkbox switch v-model="currentData.ac_cart_rover_enabled" />
        </div>
      </b-col>
    </b-row>
    <div v-if="!isLoadingSetting && isChangeData" class="d-flex align-items-center mt-3">
      <span class="label-style text-warning">*The cartRover Integration must be saved by the Save button at the bottom</span>
    </div> -->
    <div slot="footer">
      <b-row v-if="!isLoadingSetting" align-v="center">
        <b-col>
          <span class="pull-right">
            <b-button
              class="btn-save"
              @click="saveSetting"
              :disabled="isSaveDisabled"
            >
              <i class="fa fa-save"></i> Save
            </b-button>
          </span>
        </b-col>
      </b-row>
    </div>
    <b-modal
        id="add-cartRover-modal"
        title="Add CartRover"
        centered
    >
      <div>
        <div class="d-flex align-items-center position-relative" style="padding-right: 22px;">
          <span class="cartRover-label">Merchant Name</span>
          <b-form-input
            v-model.trim="addCartRoverInfo.merchant_name"
            type="text"
            @input="$v.addCartRoverInfo.merchant_name.$touch()"
          >
          </b-form-input>
          <div v-show="$v.addCartRoverInfo.merchant_name.$dirty && !$v.addCartRoverInfo.merchant_name.required" class="validate-msg text-danger">The Merchant Name is required</div>
          <div v-show="$v.addCartRoverInfo.merchant_name.$dirty && isMerchantNameAlreadyExists" class="validate-msg text-danger">This merchant name already exists</div>
        </div>
        <div class="d-flex align-items-center position-relative mt-4" style="padding-right: 22px;">
          <span class="cartRover-label">API User</span>
          <b-form-input
            v-model="addCartRoverInfo.api_user"
            type="text"
            @input="$v.addCartRoverInfo.api_user.$touch()"
          >
          </b-form-input>
          <div v-show="$v.addCartRoverInfo.api_user.$dirty && !$v.addCartRoverInfo.api_user.required" class="validate-msg text-danger">The API User is required</div>
          <div v-show="$v.addCartRoverInfo.api_user.$dirty && !$v.addCartRoverInfo.api_user.validApiKey" class="validate-msg text-danger">The API User is invalid</div>
          <div v-show="$v.addCartRoverInfo.api_user.$dirty && isApiUserAlreadyExists" class="validate-msg text-danger">This api user already exists</div>
        </div>
        <div class="d-flex align-items-center position-relative my-4">
          <span class="cartRover-label">API Key</span>
          <b-form-input
            v-model="addCartRoverInfo.api_key"
            :type="apiKeyInputType"
            @input="$v.addCartRoverInfo.api_key.$touch()"
          >
          </b-form-input>
          <div style="cursor: pointer;" @click="toggleApiKeyInputType" class="ml-2">
            <i v-if="apiKeyInputType === 'password'" class="fa fa-eye-slash"></i>
            <i v-else class="fa fa-eye" aria-hidden="true"></i>
          </div>
          <div v-show="$v.addCartRoverInfo.api_key.$dirty && !$v.addCartRoverInfo.api_key.required" class="validate-msg text-danger">The API Key is required</div>
          <div v-show="$v.addCartRoverInfo.api_key.$dirty && !$v.addCartRoverInfo.api_key.validApiKey" class="validate-msg text-danger">The API Key is invalid</div>
        </div>
      </div>
      <template v-slot:modal-footer>
        <div class="w-100">
            <b-button class="float-right" variant="primary" @click="handleAddCartRover" :disabled="$v.addCartRoverInfo.$invalid || isMerchantNameAlreadyExists || isApiUserAlreadyExists">Add</b-button>
            <b-button class="float-left" @click="cancelAddCartRover">Cancel</b-button>
        </div>
      </template>
    </b-modal>
    <b-modal id="delete-cartRover-modal" variant="danger" centered title="Please confirm">
      <div>Are you sure you want to delete this {{merchantNameSelected}} integration?</div>
      <template v-slot:modal-footer>
        <b-button variant="warning" @click="handleDeleteCartRover()">
            <i class="icon-check"></i> Yes, I understand &amp; confirm!
        </b-button>
        <b-button variant @click="$bvModal.hide('delete-cartRover-modal')">
            <i class="icon-close"></i> No
        </b-button>
      </template>
    </b-modal>
    <ConfirmationAccessModal id="confirm-modal" :isConnect="!currentData.ac_spapi_enabled" @confirm="handleConfirm"/>
  </b-card>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { convertedPermissions as permissions } from '@/shared/utils'
import Datepicker from 'vue2-datepicker'
import ConfirmationAccessModal from '@/components/common/ActionModals/ConfirmationAccessModal.vue'
import toastMixin from '@/components/common/toastMixin'
import PermissionsMixin from '@/components/common/PermissionsMixin'
import { required } from 'vuelidate/lib/validators'
import cloneDeep from 'lodash/cloneDeep'
import isEqual from 'lodash/isEqual'
import isEmpty from 'lodash/isEmpty'
import spapiReconnectAlertMixin from '@/mixins/spapiReconnectAlertMixin'
import { Container, Draggable } from 'vue-smooth-dnd'

const validApiKey = (text) => {
  const regex = /\s/
  return !text.match(regex)
}

const DEFAULT_PRIORITY_ITEMS = [
  { value: 'Extensiv', displayName: 'Extensiv' },
  { value: 'PF', displayName: 'Use Internal Precise Financial COGS' },
  { value: 'Data Central', displayName: 'Data Central (DC)' }
]

export default {
  name: 'Settings',
  components: {
    Datepicker,
    ConfirmationAccessModal,
    Container,
    Draggable
  },
  data() {
    return {
      permissions,
      showNoCOGSEnableError: false,
      prioritySourceItems: DEFAULT_PRIORITY_ITEMS,
      prioritySourceTooltip: 'Drag and drop the sources to set their priority order, from highest (1) at the top to lowest (3) at the bottom. The system will use the highest-ranked source first when calculating COGS, and only fall back to lower-priority sources if others are unavailable.',
      currentData: {
        allow_sale_data_update_from: '',
        is_remove_cogs_refunded: false,
        ac_mws_access_key: '',
        ac_mws_secret_key: '',
        ac_mws_merchant_id: '',
        ac_mws_merchant_name: '',
        ac_mws_enabled: false,
        ac_spapi_enabled: false,
        // CartRover
        ac_cart_rover: [],
        ac_cart_rover_enabled: false,
        // COGS
        cog_use_extensiv: false,
        cog_extensiv_token: '',
        cog_use_dc: false,
        cog_use_pf: false,
        cog_priority_source: {}
      },
      originData: {
        allow_sale_data_update_from: '',
        is_remove_cogs_refunded: false,
        ac_mws_access_key: '',
        ac_mws_secret_key: '',
        ac_mws_merchant_id: '',
        ac_mws_merchant_name: '',
        ac_mws_enabled: false,
        ac_spapi_enabled: false,
        // CartRover
        ac_cart_rover: [],
        ac_cart_rover_enabled: false,
        // COGS
        cog_use_extensiv: false,
        cog_extensiv_token: '',
        cog_use_dc: false,
        cog_use_pf: false,
        cog_priority_source: {}
      },
      acceptConnectFromShopifyAdmin: 'not_accepted',
      shop_url: null,
      register_shop_url: null,
      addCartRoverInfo: {
        merchant_name: '',
        api_user: '',
        api_key: ''
      },
      cartRoverIndexSelected: null,
      apiKeyInputType: 'password'
    }
  },
  mixins: [ toastMixin, PermissionsMixin, spapiReconnectAlertMixin ],
  validations: {
    currentData: {
      ac_mws_access_key: {
        required
      },
      ac_mws_secret_key: {
        required
      },
      ac_mws_merchant_id: {
        required
      },
      ac_mws_merchant_name: {
        required
      },
      cog_extensiv_token: {
        requiredWhenExtensiv(value) {
          if (!this.currentData.cog_use_extensiv) {
            return true
          }
          return value != null && String(value).trim() !== ''
        }
      }
    },
    addCartRoverInfo: {
      merchant_name: {required},
      api_user: {required, validApiKey},
      api_key: {required, validApiKey}
    }
  },
  computed: {
    ...mapGetters({
      settingOption: `pf/settings/settingOption`,
      spapiSetting: `pf/settings/spapiSetting`,
      shopifyPartnerSetting: `pf/settings/shopifyPartnerSetting`,
      isLoadingSetting: `pf/settings/isLoadingSetting`
    }),
    isChangeData() {
      let currentData = cloneDeep(this.currentData)
      currentData.allow_sale_data_update_from = this.$moment(currentData.allow_sale_data_update_from).format('YYYY-MM-DD')
      return !isEqual(this.originData, currentData)
    },
    isShopifyPartnerConnected() {
      return isEqual(this.shopifyPartnerSetting.enabled, true)
    },
    merchantNameSelected() {
      return this.cartRoverIndexSelected !== null ? this.currentData.ac_cart_rover[this.cartRoverIndexSelected].merchant_name : ''
    },
    isMerchantNameAlreadyExists() {
      return this.currentData.ac_cart_rover.some(item => item.merchant_name === this.addCartRoverInfo.merchant_name)
    },
    isApiUserAlreadyExists() {
      return this.currentData.ac_cart_rover.some(item => item.api_user === this.addCartRoverInfo.api_user)
    },
    noCOGSEnable() {
      return (!this.currentData.cog_use_extensiv &&
          !this.currentData.cog_use_dc &&
          !this.currentData.cog_use_pf)
    },
    isSaveDisabled() {
      if (!this.hasPermission(this.permissions.admin.settingsChange)) {
        return true
      }
      if (!this.isChangeData) {
        return true
      }
      if (this.showNoCOGSEnableError && this.noCOGSEnable) {
        return true
      }
      if (this.currentData.cog_use_extensiv && (!this.currentData.cog_extensiv_token || this.currentData.cog_extensiv_token.trim() === '')) {
        return true
      }
      if (this.currentData.ac_mws_enabled) {
        return this.$v.currentData.$invalid
      }
      return false
    }
  },
  watch: {
    'shopifyPartnerSetting': {
      immediate: true,
      deep: true,
      handler (val) {
        val && (this.shop_url = val.shop_url)
      }
    },
    'currentData': {
      deep: true,
      handler(val) {
        if (!val.ac_cart_rover.length) this.currentData.ac_cart_rover_enabled = false
        if (!this.originData.ac_cart_rover.length && val.ac_cart_rover.length) this.currentData.ac_cart_rover_enabled = true
      }
    },
    'currentData.cog_use_extensiv': function(val) {
      if (val) {
        this.showNoCOGSEnableError = false
        this.$v.currentData.cog_extensiv_token.$touch()
      }
      this.updatePrioritySourceItems()
    },
    'currentData.cog_use_dc': function(val) {
      if (val) this.showNoCOGSEnableError = false
      this.updatePrioritySourceItems()
    },
    'currentData.cog_use_pf': function(val) {
      if (val) this.showNoCOGSEnableError = false
      this.updatePrioritySourceItems()
    },
    'currentData.cog_extensiv_token': function(val) {
      if (this.currentData.cog_use_extensiv) {
        this.$v.currentData.cog_extensiv_token.$touch()
      }
    }
  },
  methods: {
    ...mapActions({
      getSettingOption: `pf/settings/getSettingOption`,
      putSettingOption: `pf/settings/putSettingOption`,
      getSpapiSetting: `pf/settings/getSpapiSetting`,
      getShopifyPartnerSetting: 'pf/settings/getShopifyPartnerSetting',
      getOauthUrlShopifyPartner: 'pf/settings/getOauthUrlShopifyPartner',
      serviceRevokeShopifyPartner: 'pf/settings/revokeShopifyPartner',
      registerMerchantShopUrl: 'pf/settings/registerMerchantShopUrl',
      patchSettingOption: `pf/settings/patchSettingOption`,
      revokeAccountConnection: 'pf/settings/revokeAccountConnection'
    }),
    async saveSetting() {
      if (this.noCOGSEnable) {
        this.showNoCOGSEnableError = true
        return
      }

      if (this.currentData.cog_use_extensiv &&
        (!this.currentData.cog_extensiv_token || this.currentData.cog_extensiv_token.trim() === '')) {
        return
      }

      try {
        let currentDataClone = Object.assign({}, this.currentData)
        currentDataClone.allow_sale_data_update_from = this.$moment(currentDataClone.allow_sale_data_update_from).format('YYYY-MM-DD')
        let payload = {
          client_id: this.$route.params.client_id,
          ...currentDataClone
        }
        await this.putSettingOption(payload)
        await this.getSettingOption({client_id: this.$route.params.client_id})
        this.setOriginData()
        this.vueToast('success', 'Updated successfully.')
      } catch {
        this.vueToast('error', 'Updating failed. Please retry or contact administrator.')
      }
    },
    bin2hex (bin) {
      var i = 0
      var l = bin.length
      var chr
      var hex = ''
      for (i; i < l; ++i) {
        chr = bin.charCodeAt(i).toString(16)
        hex += chr.length < 2 ? '0' + chr : chr
      }
      return hex
    },
    random_bytes(length) {
      var result = ''
      var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
      var charactersLength = characters.length
      for (let i = 0; i < length; i++) result += characters.charAt(Math.floor(Math.random() * charactersLength))
      return result
    },
    connectSellerCentral() {
      let applicationId = this.spapiSetting.spapi_app_id
      let redirectUri = this.spapiSetting.api_aws_oauth_redirect
      let state = `${this.bin2hex(this.random_bytes(8))}_${this.$route.params.client_id}`
      var version = ''
      if (process.env.VUE_APP_PF_IS_BETA === 'true' || window.URL.VUE_APP_PF_IS_BETA === 'true') {
        version = '&version=beta'
      }
      window.location.href = `https://sellercentral.amazon.com/apps/authorize/consent?application_id=${applicationId}&state=${state}&redirect_uri=${redirectUri}` + version
    },
    async revokeToken() {
      try {
        let payload = {
          client_id: this.$route.params.client_id
        }
        await this.revokeAccountConnection(payload)
        await this.getSettingOption(payload)
        this.originData = Object.assign(this.originData, this.settingOption)
        this.currentData = Object.assign(this.currentData, this.settingOption)
        this.currentData.allow_sale_data_update_from = this.settingOption.allow_sale_data_update_from ? new Date(this.settingOption.allow_sale_data_update_from) : new Date()
      } catch {
        this.vueToast('error', 'Revoking failed. Please retry or contact administrator.')
      }
    },
    async connectShopifyPartner() {
      if (!this.shop_url) {
        this.vueToast('error', 'Your shopify url is required!')
        return
      }
      try {
        const res = await this.getOauthUrlShopifyPartner({
          client_id: this.$route.params.client_id,
          shop_url: this.shop_url
        })
        window.location.href = res.data.auth_url
      } catch (err) {
        if (err.response) {
          const dataValidation = err.response.data
          const clientValidation = isEmpty(dataValidation.client_id) ? [] : dataValidation.client_id
          clientValidation.forEach(msg => {
            this.vueToast('error', msg)
          })
        }
      }
    },
    async revokeShopifyPartner() {
      try {
        const res = await this.serviceRevokeShopifyPartner(
          {
            client_id: this.$route.params.client_id,
            shop_url: this.shop_url
          })
        if (res.status === 200) {
          this.vueToast('success', `Revoke ${this.shop_url} successfully`)
          await this.getShopifyPartnerSetting({client_id: this.$route.params.client_id})
        }
      } catch (err) {
        console.log(err)
      }
    },
    async registerShopUrl() {
      try {
        const data = await this.registerMerchantShopUrl({
          shop_url: this.register_shop_url,
          client_id: this.$route.params.client_id
        })
        this.vueToast('success', data.message)
        this.register_shop_url = null
      } catch (err) {
        this.vueToast('error', 'Oops! Something went wrong!')
      }
    },
    deleteCartRover(index) {
      this.cartRoverIndexSelected = index
      this.$bvModal.show('delete-cartRover-modal')
    },
    async handleDeleteCartRover() {
      this.currentData.ac_cart_rover.splice(this.cartRoverIndexSelected, 1)
      this.cartRoverIndexSelected = null
      this.$bvModal.hide('delete-cartRover-modal')
    },
    addCartRover() {
      this.addCartRoverInfo = {
        merchant_name: '',
        api_user: '',
        api_key: ''
      }
      this.apiKeyInputType = 'password'
      this.$v.$reset()
      this.$bvModal.show('add-cartRover-modal')
    },
    async handleAddCartRover() {
      this.currentData.ac_cart_rover.push(this.addCartRoverInfo)
      this.$bvModal.hide('add-cartRover-modal')
    },
    cancelAddCartRover() {
      this.$bvModal.hide('add-cartRover-modal')
      this.addCartRoverInfo = {
        merchant_name: '',
        api_user: '',
        api_key: ''
      }
    },
    setOriginData() {
      this.originData = cloneDeep(Object.assign(this.originData, this.settingOption))
      this.currentData = Object.assign(this.currentData, this.settingOption)
      this.currentData.allow_sale_data_update_from = this.settingOption.allow_sale_data_update_from ? new Date(this.settingOption.allow_sale_data_update_from) : new Date()

      // Ensure cog_extensiv_token is never null, always string
      if (this.currentData.cog_extensiv_token === null) {
        this.currentData.cog_extensiv_token = ''
      }

      if (this.currentData.cog_priority_source) {
        const sortedItems = Object.entries(this.currentData.cog_priority_source)
          .sort((a, b) => a[1] - b[1])
          .map(([name]) => DEFAULT_PRIORITY_ITEMS.find(item => item.value === name))
          .filter(Boolean)
        this.prioritySourceItems = sortedItems
      } else {
        // set default priority source if not defined
        this.currentData.cog_priority_source = {
          'Extensiv': 1,
          'PF': 2,
          'Data Central': 3
        }
      }
    },
    toggleApiKeyInputType() {
      this.apiKeyInputType = this.apiKeyInputType === 'password' ? 'text' : 'password'
    },
    openConfirmModal() {
      this.$bvModal.show('confirm-modal')
    },
    handleConfirm(isConnect) {
      if (isConnect) this.connectSellerCentral()
      else this.revokeToken()
    },
    getChildPayload(index) {
      return this.prioritySourceItems[index]
    },
    onDrop(dropResult) {
      if (dropResult.removedIndex !== null && dropResult.addedIndex !== null) {
        const itemsClone = [...this.prioritySourceItems]
        const [movedItem] = itemsClone.splice(dropResult.removedIndex, 1)
        itemsClone.splice(dropResult.addedIndex, 0, movedItem)
        this.prioritySourceItems = itemsClone

        // Update priority values in cog_priority_source directly
        this.prioritySourceItems.forEach((item, index) => {
          this.currentData.cog_priority_source[item.value] = index + 1
        })
      }
    },
    updatePrioritySourceItems() {
      if (this.currentData.cog_priority_source) {
        const sortedItems = Object.entries(this.currentData.cog_priority_source)
          .sort((a, b) => a[1] - b[1])
          .map(([name]) => DEFAULT_PRIORITY_ITEMS.find(item => item.value === name))
          .filter(Boolean)
        this.prioritySourceItems = sortedItems
      }
    }
  },
  async created() {
    let payload = {
      client_id: this.$route.params.client_id
    }
    await Promise.all([
      this.getSettingOption(payload),
      this.getSpapiSetting(payload),
      this.getShopifyPartnerSetting(payload)
    ])
    this.setOriginData()
    this.updatePrioritySourceItems()
  }
}
</script>
<style lang="scss" scoped>
.settings-body {
  .cls-sale-date {
    width: 50vw;
  }
  .cls-seller-integration {
    width: 50%;
  }
  .connect {
    width: 40%;
  }
}

.cls-loading-setting {
  border-width: 0.1em !important
}

.label-style {
  min-width: 186px;
}

.shopify-app {
  button, input {
    height: 40px;
  }
  button {
    color: #254164;
    background-color: #FFFFFF;
    border-color: #254164;
    padding: 8px 14px;
    font-size: 14px;
    font-weight: 600;
  }
}
//multi cartRover
.add-cartRover {
  cursor: pointer;
}
.cartRover-item {
  border: 1px solid rgb(228,231,234);
  padding: 1rem;
  margin-bottom: 30px;
}
.cartRover-label {
  min-width: 110px;
}
.validate-msg {
  position: absolute;
  left: 110px;
  bottom: -2px;
  transform: translateY(100%);
}
.custom-cartRover-msg {
  right: 0;
  left: unset;
}
.width-50 {
  width: 50%;
}
.btn-save.disabled {
  pointer-events: none;
}

.draggable-item {
  display: flex;
  align-items: center;
  border: 1px solid #ced4da;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  margin-bottom: 5px;
  cursor: grab;
}

.priority-number, .drag-handle {
  width: 20px;
}
.drag-handle, .priority-number, .priority-text {
  margin-bottom: 0;
  cursor: grab;
}

.smooth-dnd-container.vertical > .smooth-dnd-draggable-wrapper {
  overflow: visible;
}

.smooth-dnd-draggable-wrapper.is-dragging .priority-item {
  background-color: #f8f9fa;
  box-shadow: 0 5px 10px rgba(0,0,0,0.15);
}

::v-deep .tooltip-inner {
  max-width: 500px;
  text-align: center;
  background-color: #f8f9fa;
  color: #23282c;
}

::v-deep .icon-tooltips {
  background: #fff;
  color: #23282c;
  border-radius: 50%;
  padding: 2px 4px;
  border: 1px solid #ced4da;
  font-size: 18px;
}

@media (min-width: 1200px) {
  .draggable-item {
    max-width: 50%;
  }
}
</style>
