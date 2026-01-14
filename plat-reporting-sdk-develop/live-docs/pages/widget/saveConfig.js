const saveConfigPage = Vue.component('saveConfigPage', {
  template: `
    <div class="widget-save-config">
      <sdkliveDataSource :state="state"
                         :save-button="true"
                         :isLoading="isLoading"
                         @get="getData"
                         @save="saveData"/>
      <b-row>
        <div id="widget-save-config" class="mt-4 w-100">
        </div>
      </b-row>
    </div>
  `,
  data() {
    return {
      isLoading: false,
      template: '<cbpo-widget class="p-0" config-ref="config"></cbpo-widget>',
      state: {
        baseURL: 'http://ds-api.qa.channelprecision.com/v1/',
        dataSource: 'idreportingsdk',
        token: this.VUE_DEMO_TOKEN,
        clientId: '',
        configId: null
      },
      config: {
        filter: {
          builder: {
            enabled: true
          }
        },
        columnManager: {
          enabled: true,
          config: {}
        },
        elements: [
          {
            type: 'cbpo-element-table',
            config: {
              widget: {
                title: {
                  enabled: false
                }
              },
              pagination: {
                limit: 10
              },
              globalControlOptions: {
                aggregation: {
                  enabled: true
                },
                grouping: {
                  enabled: true
                },
                editColumn: {
                  enabled: true
                },
                editColumnLabel: {
                  enabled: true
                },
                editColumnFormat: {
                  enabled: true
                },
                editBin: {
                  enabled: true
                }
              },
              dataSource: '',
              columns: []
            }
          }
        ]
      }
    }
  },
  mixins: [configMixins, renderMixins],
  methods: {
    async createNewConfig(state, config) {
      let {baseURL, token, clientId} = state
      try {
        return await configService.createConfig(baseURL, token, clientId, {
          data: {
            name: 'Save Config',
            description: 'dsc',
            config
          }
        })
      } catch (e) {
        console.error(e)
        this.$bvToast.toast('Cannot create config', {
          solid: true,
          variant: 'danger',
          headerClass: 'd-none'
        })
      }
    },
    async getData(state) {
      this.reset()
      this.state = state
      let config
      let configInLocal = configService.findConfig(state.baseURL, state.dataSource)
      if (configInLocal) {
        this.state.configId = configInLocal.configId
        config = await this.getConfigFromServer(state, {id: configInLocal.configId})
      } else {
        let columns = await this.getMappingColumns()
        let payloadConfig = _.cloneDeep(this.config)
        this.mappingColumnsToConfig(payloadConfig, columns)
        this.mappingDataSourceToConfig(payloadConfig, state.dataSource)
        let data = await this.createNewConfig(state, payloadConfig)
        configService.addNewLocalConfig(state.baseURL, state.dataSource, data._id)
        this.state.configId = data._id
        config = data.config
      }
      this.initSDK(state, config)
    },
    async saveData() {
      let configId = this.state.configId
      this.isLoading = true
      try {
        await configService.updateConfig(this.state.baseURL, this.state.token, this.state.clientId, {
          id: configId,
          data: {
            name: 'SDK',
            description: 'SDK',
            config: window.config
          }
        })
        this.$bvToast.toast('Save to server successfully', {
          solid: true,
          variant: 'success',
          headerClass: 'd-none'
        })
        this.isLoading = false
      } catch (e) {
        this.isLoading = false
        this.$bvToast.toast('Cannot save config!!! Please try again', {
          solid: true,
          variant: 'danger',
          headerClass: 'd-none'
        })
      }
    },
    async getConfigFromServer(state, id) {
      let {baseURL} = state
      try {
        let {config} = await configService.getConfig(baseURL, state.token, state.clientId, id)
        return config
      } catch (e) {
        console.error(e)
        this.$bvToast.toast('Cannot get columns', {
          solid: true,
          variant: 'danger',
          headerClass: 'd-none'
        })
      }
    },
    getDataColumns(baseURL, token, clientId, dataSource) {
      return columnService.getColumns(baseURL, token, clientId, {dataSource})
    },
    async getMappingColumns () {
      this.isLoading = true
      let {baseURL, token, clientId, dataSource} = this.state
      try {
        let {columns} = await this.getDataColumns(baseURL, token, clientId, dataSource)
        this.isLoading = false
        return columns.map(col => {
          col.displayName = _.startCase(col.name)
          if (col.type === 'date' || col.type === 'datetime') {
            col.cell = {
              format: {
                type: 'temporal'
              }
            }
          }
          if (col.type === 'float') {
            col.cell = {
              format: {
                type: 'numeric'
              }
            }
          }
          return col
        })
      } catch (e) {
        this.isLoading = false
        console.error(e)
        this.$bvToast.toast('Cannot get columns', {
          solid: true,
          variant: 'danger',
          headerClass: 'd-none'
        })
      }
    },
    mappingColumnsToConfig(config, columns) {
      config.elements[0].config.columns = _.cloneDeep(columns)
    },
    mappingDataSourceToConfig(config, dataSource) {
      config.elements[0].config.dataSource = dataSource
    },
    initSDK(state, config) {
      window.config = config
      this.render('#widget-save-config', this.template, state.baseURL, state.token, state.clientId)
    }
  },
  created() {
    let {baseURL, dataSource} = this.state
    let config = configService.findConfig(baseURL, dataSource)
    if (config) {
      this.state.configId = config.configId
    }
  }
})
