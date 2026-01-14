const sdkliveDataSource = Vue.component('sdkliveDataSource', {
  template: `
    <div class="sdk-live-datasource">
      <b-form-checkbox size="sm" switch @change="useClientID()">
        Use Client ID
      </b-form-checkbox>
      <div class="d-flex align-items-center">
        <b-form-group class="flex-grow-1 mr-2" label="Token">
          <b-form-input id="baseUrl" v-model="stateInstance.token" trim/>
        </b-form-group>
        <b-form-group class="flex-grow-1 mr-2" label="Client Id" v-if="isActiveInputClientId">
          <b-form-input id="dataSource" v-model="stateInstance.clientId" trim/>
        </b-form-group>
      </div>
      <div class="d-flex align-items-center">
        <b-form-group class="flex-grow-1 mr-2" label="Base URL">
          <b-form-input id="baseUrl" v-model="stateInstance.baseURL" trim/>
        </b-form-group>
        <b-form-group class="flex-grow-1 mr-2" label="Datasource Id">
          <b-form-input id="dataSource" v-model="stateInstance.dataSource" trim/>
        </b-form-group>
        <div>
        <b-button v-if="getButton" :disabled="(needValidation && (!stateInstance.baseURL || !stateInstance.dataSource)) || isLoading"
        style="margin-top: 14px"
        :class="{'mr-2': saveButton}"
        variant="primary"
        @click="fireEvent('get')">
Get
</b-button>
<b-button v-if="saveButton" :disabled="(needValidation && (!stateInstance.baseURL || !stateInstance.dataSource)) || isLoading"
        style="margin-top: 14px"
        :class="{'ml-2': !getButton}"
        variant="success"
        @click="fireEvent('save')">
Save
</b-button>
        </div>
      </div>
      <b-row v-if="needValidation && ( !stateInstance.baseURL || !stateInstance.dataSource )">
        <span class="text-danger">Base URL or DataSource cannot be empty alo</span>
      </b-row>
    </div>
  `,
  props: {
    isLoading: {
      type: Boolean,
      default: false
    },
    needValidation: {
      type: Boolean,
      default: true
    },
    getButton: {
      type: Boolean,
      default: true
    },
    saveButton: {
      type: Boolean,
      default: false
    },
    state: {
      type: Object,
      default: () => {}
    }
  },
  methods: {
    fireEvent(type) {
      this.$emit(type, this.stateInstance)
    },
    useClientID() {
      this.isActiveInputClientId = !this.isActiveInputClientId
      this.stateInstance.clientId = ''
      if (!this.isActiveInputClientId) {
        this.stateInstance.token = this.VUE_DEMO_TOKEN
      } else {
        this.stateInstance.token = ''
      }
    }
  },
  data() {
    return {
      stateInstance: {
        baseURL: '',
        dataSource: '',
        clientId: '',
        token: this.VUE_DEMO_TOKEN
      },
      isActiveInputClientId: false
    }
  },
  created() {
    if (this.state) {
      let {baseURL, dataSource, clientId, token } = this.state
      this.stateInstance = {baseURL, dataSource, clientId, token }
    }
  }
})
