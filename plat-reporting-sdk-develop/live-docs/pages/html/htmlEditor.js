const htmlEditorPage = Vue.component('htmlEditorPage', {
  template: `
  <div class="html-editor-demo">
    <p class="text-description"></p>
    <div class="d-block">
      <input id="auto" type="checkbox" v-model="auto">
      <label for="auto">Auto Change Data <span class="text-danger">(Support only Bullet Gauge and Solid Gauge ShortCode)</span></label>
    </div>
    <div id="html-editor-demo"></div>
  </div>
  `,
  data() {
    return {
      auto: false,
      builder: true,
      dataInterval: null
    }
  },
  mixins: [configMixins, renderMixins],
  mounted() {
    $('.text-description').html('You can add value of columns into html editor by follow this syntax: {{:column-name}} then toggle builder mode too see value change')
    this.builder = true
  },
  methods: {
    initSDK() {
      let min = 0
      let max = Math.floor(Math.random() * Math.floor(5000000))
      let current = Math.floor(Math.random() * Math.floor(max * 2 / 3))
      let value1 = Math.floor(Math.random() * Math.floor(max * 2 / 3))
      let config = this.getConfig(min, max, current, value1)
      config.builder.enabled = this.builder
      window.dataSource = this.dataSource
      window.config = config
      this.render('#html-editor-demo', this.getTemplate(), 'http://ds-api.qa.channelprecision.com/v1/', this.VUE_DEMO_TOKEN)
    },
    getConfig(min = 0, max = 0, current = 0, value1 = 0) {
      return {
        dataSource: 'dataSource',
        builder: {
          enabled: false
        },
        // content: `[kpi chart-type="bar" class-css="m-auto" width="1000" height="150" current="{SUM(@sales, '7316c006-98d4-47c7-9213-7784cbc7d196')}" min="0" max="{SUMIF(@sale_goal, LAST_BIN_OF(@year, 1, M), 'c5a5034b-8939-4b8c-b645-176db1c0f552')}" target="{((SUMIF(@sale_goal, LAST_BIN_OF(@year, 1, M), 'c5a5034b-8939-4b8c-b645-176db1c0f552')) / DAYS_IN('year') * DATE_OF('y'))}" format-string=",d" format-tooltip=",d" goal-legend="2020 Goal" target-legend="2019 Sales"][/kpi]`
        // content: `[kpi chart-type="radial" class-css="m-auto" width="400" height="300" current="{SUMIF(@total_amount, (@date <=DATE_END_OF(DATE_LAST(1,'week'),'week')) & (@date >=DATE_START_OF(DATE_LAST(1,'week'), 'week')), 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e')}" min="0" max="{SUMIF(@total_amount, (@date <=DATE_END_OF(DATE_LAST(2,'week'),'week')) & (@date >=DATE_START_OF(DATE_LAST(2,'week'), 'week')), 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e')}" target="{SUMIF(@total_amount, (@date <=DATE_END_OF(DATE_LAST(2,'week'),'week')) & (@date >=DATE_START_OF(DATE_LAST(2,'week'),'week')), 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e')}" format-string="$,d" format-tooltip=",d"][/kpi]`
        // content: `[format expression="COUNT('543a4f7a-cfde-444f-8239-aee48222c566') as count1 + COUNT('633d2c53-fe34-4029-9f00-b5b768e46917') as count2"][/format]`
        content: `[kpi chart-type="bar" class-css="m-auto" width="1000" height="150" current="{SUM(@sales, '7316c006-98d4-47c7-9213-7784cbc7d196')}" min="0" max="{SUMIF(@sale_goal, LAST_BIN_OF(@year, 1, M), 'c5a5034b-8939-4b8c-b645-176db1c0f552')}" target="{((SUMIF(@sale_goal, LAST_BIN_OF(@year, 1, M), 'c5a5034b-8939-4b8c-b645-176db1c0f552')) / DAYS_IN('year') * DATE_OF('y'))}" format-string="$,d" format-tooltip="$,d" goal-legend="2020 Goal" target-legend="2019 Sales" percent-number="off"][/kpi]`
      }
    },
    getTemplate() {
      return `<cbpo-element-html-editor :builder="${this.builder}" config-ref="config"></cbpo-element-html-editor>`
    }
  },
  destroyed() {
    if (this.dataInterval) {
      clearInterval(this.dataInterval)
    }
  },
  watch: {
    enabled: {
      immediate: true,
      handler(val) {
        this.$nextTick(() => {
          this.initSDK(val)
        })
      }
    },
    auto: {
      immediate: true,
      handler(val) {
        if (!val) {
          if (this.dataInterval) {
            this.builder = true
            clearInterval(this.dataInterval)
            this.initSDK()
          }
        } else {
          this.builder = false
          this.initSDK()
          this.dataInterval = setInterval(() => {
            this.initSDK()
          }, 5000)
        }
      }
    }
  }
})
