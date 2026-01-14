const widgetLoader = Vue.component('widgetLoader', {
  template: `
    <div class="widget-save-config">
    <div class="d-flex" style="flex-wrap: nowrap;">
      <b-row class="w-100">
        <b-col col="4">
          <b-form-group label="Datasource Id">
            <b-input v-model="dataSource"></b-input>
          </b-form-group>
        </b-col>
        <b-col col="4">
          <b-form-group label="Widget Id">
            <b-input v-model="widgetId"></b-input>
          </b-form-group>
        </b-col>
        <b-col col="4">
          <b-form-group label="Client Id">
            <b-input v-model="clientId"></b-input>
          </b-form-group>
        </b-col>
      </b-row>

      <b-button @click="initSDK" style="height: 38px; margin-top: 30px; margin-left: 30px" variant="primary">Change
      </b-button>
    </div>

    <b-form-group>
      <label for="">Widget Loader </label>
      <div id="widget-save-config" class="mt-4 w-100">
      </div>
    </b-form-group>

    </div>
  `,
  data() {
    return {
      token: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiY2UwYmU1ODEtNDlkZi00Mjg4LThiNzItZTk2MWRkMzBhMTA1IiwidXNlcm5hbWUiOiJjYnBvX3FhQG1haWxpbmF0b3IuY29tIiwiZXhwIjoxNTk3OTA2NDU5LCJlbWFpbCI6ImNicG9fcWFAbWFpbGluYXRvci5jb20iLCJvcmlnX2lhdCI6MTU5NzczMzY1OSwiYXBwIjoibWF0cml4IiwiZm5hbWUiOiJDQlBPIiwibG5hbWUiOiJRQSJ9.LpjfAkthTQkEPgNSPYiLzpW8VIn1f_W9IBNpodVfRF6ONvXcfUENmEiXz2rWsBbYhk3QUUSdYJDGWIylrTqVeRzZNEdHAcTaFoH04wRpV1NID62tZ77PUoBD1CNukHkyzdSQHa07fqYmQZIjveqN4H2xQ4z7rSKoqj19yDqiwTXGuAquPMKFZe9KaohvOFKhC3Ljzge7CwZsxaE48uOmb49BYyV-JjM5wG2jTGVtnjxIxIsCNV281WGCjQZfsPi5LKEKmjTI5G8u3_R7tkVPJ9nz7V4HnQJYwAXuiCqsEtCmPKE2m-uceJzTpfzgCXyCUfrYZjKGQa5NE6Ro1vurag',
      clientId: '11153189-c451-43db-84aa-8de6dcef3484',
      widgetId: 'ab8ca9b9-2074-4049-9704-28c993587836',
      dataSource: null,
      template: '<cbpo-widget-loader class="p-0" config-ref="config"></cbpo-widget-loader>',
      raAxios: null,
      widgetName: null
    }
  },
  mixins: [configMixins, renderMixins],
  methods: {
    getConfig() {
      return {
        widgetId: this.widgetId,
        dataSource: this.dataSource,
        load: async (promise, widgetId, dataSource) => {
          // call RA service here, after that promise.resolve(config) to pass config to sdk
          let response = await this.raAxios.get(`/v1/clients/${this.clientId}/visualizations/${widgetId}`)
          // console.log(promise, widgetId, dataSource)
          promise.resolve(
            response.data
          )
        },
        save: async (promise, widgetInfo, saveAs) => {
          console.log('saving', widgetInfo)
          let payload = {
            ds_id: widgetInfo.ds_id,
            cf_object: widgetInfo.cf_object,
            name: `${widgetInfo.name}`
          }
          if (saveAs || widgetInfo.is_programmed) {
            let response = await this.raAxios.post(`/v1/clients/${widgetInfo.client_id}/visualizations`, payload)
            promise.resolve(
              response.data
            )
          } else {
            let response = await this.raAxios.put(`/v1/clients/${widgetInfo.client_id}/visualizations/${widgetInfo.id}`, payload)
            promise.resolve(
              response.data
            )
          }
        }
      }
    },
    initSDK() {
      window.config = this.getConfig()
      this.render('#widget-save-config', this.template, 'http://ds-api.qa.channelprecision.com/v1/', this.VUE_DEMO_TOKEN)
    }
  },
  mounted() {
    this.initSDK()
  },
  created() {
    this.raAxios = axios.create({
      // need check avoid hardcode
      baseURL: 'http://ra-api.qa.channelprecision.com',
      timeout: 60000
    })
    this.raAxios.interceptors.request.use(
      config => {
        // config.headers['ra-api-token'] = `87f6e425-4810-4897-a81d-1581a43fc829`
        let apiToken = JSON.parse(localStorage.getItem('auth')).ps.userModule.userToken
        if (apiToken) {
          config.headers.Authorization = `Bearer ${apiToken}`
        } else {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      err => Promise.reject(err)
    )
    this.raAxios.interceptors.response.use((response) => {
      return response
    }, (error) => {
      if (error.response && error.response.data) {
        let handler = `handle`
        if (!handler) {
          console.log('No remove API error handler.')
        } else {
          handler(error.response.data.statusCode)
        }
        return Promise.reject(error.response.data)
      }
      return Promise.reject(error.message)
    })
  }
})
