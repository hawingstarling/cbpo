<template>
  <b-modal :id="id" size="mdx" centered hide-footer headerClass="text-center">
    <template v-slot:modal-title>
      Sale item audit log
      <span v-if="dataForApi && dataForApi.asin">of {{ dataForApi.asin }}</span>
      <span v-if="dataForApi && dataForApi.sale_channel_id">
        in {{ dataForApi.sale_channel_id }}</span>
    </template>
    <b-container v-if="isLoading">
      <div class="align-middle d-flex justify-content-center">
        <div class="spinner-border thin-spinner spinner-border-sm"></div>&nbsp;Loading...
      </div>
    </b-container>
    <b-container fluid class="changelog-modal" v-else>
      <b-row>
        <b-col md="6" class="mx-auto">
          <b-form @submit="handleKeywordChange($event)">
            <b-input-group class="mt-3 history-search">
              <template v-slot:append>
                <b-input-group-text class="cursor-pointer" @click="handleKeywordChange($event)">
                  <i class="fa fa-search"></i>
                </b-input-group-text>
              </template>
              <b-form-input id="input-valid" placeholder="Search keyword" type="text" v-model="keyword">
              </b-form-input>
              <i class="fa fa-times-circle clear-keyword" v-if="keyword" @click="clearKeyword()"></i>
            </b-input-group>
          </b-form>
        </b-col>
      </b-row>
      <b-row>
        <b-col>
          <b-table outlined responsive striped hover show-empty empty-text="There are no logs to show" :fields="fields"
            :items="tableItems" class="mt-4">
            <template v-slot:cell(timestamp)="data">
              <div>{{ formattedByTimeZone(data.item.timestamp, 'MM/DD/YYYY') }}</div>
              <div>{{ formattedByTimeZone(data.item.timestamp) }}</div>
            </template>
            <template v-slot:head(timestamp)>
              <i class="fa fa-clock-o" /> Date
            </template>
            <template v-slot:cell(changes)="data">
              <div class="d-flex mb-1" v-for="(change, key, index) in data.item.changes" :key="`change-${index}`">
                <span class="changelog-modal__key">{{ key | filterColumnName }}:
                </span>
                <div class="changelog-modal__value">
                  <span>{{ formatDataChange(change[0]) | formatText }}</span>
                  <span>
                    <img src="@/assets/img/icon/arrow-right.png" />
                    <span>{{ formatDataChange(change[1]) | formatText }}</span>
                  </span>
                </div>
                <span v-if="data.item.model_name === 'sale' && key === 'sale_status'">(Sale)</span>
              </div>
            </template>
            <template v-slot:cell(additional_data)="data">
              <div v-if="
                data.item.additional_data &&
                data.item.additional_data.actor_info
              ">
                <div>
                  {{ data.item.additional_data.actor_info.first_name }}
                  {{ data.item.additional_data.actor_info.last_name }}
                </div>
                <div>{{ data.item.additional_data.actor_info.email }}</div>
              </div>
              <div v-if="
                data.item.additional_data &&
                !data.item.additional_data.actor_info &&
                data.item.additional_data.actor
              ">
                <div class="text-capitalize">{{ data.item.additional_data.actor }}</div>
              </div>
            </template>
          </b-table>
        </b-col>
      </b-row>
      <b-row v-if="perPage < totalRows">
        <b-col md="6" class="mx-auto mb-5">
          <b-pagination v-model="currentPage" :total-rows="totalRows" :per-page="perPage" first-text="First"
            prev-text="Prev" next-text="Next" last-text="Last" align="fill" size="md" class="my-0"></b-pagination>
        </b-col>
      </b-row>
    </b-container>
  </b-modal>
</template>

<script>
import { mapActions } from 'vuex'
import { UNIQUE_KEY_BE } from '@/shared/constants/column.constant'
import editSaleItemMixins from '@/mixins/editMixins/editSaleItemMixins'
import moment from 'moment-timezone'

export default {
  name: 'ChangeLogModal',
  props: {
    id: {
      type: String,
      required: true
    },
    dataRow: {
      type: [Object, Array]
    },
    columns: {
      type: Array
    },
    timezone: {
      type: String
    }
  },
  data() {
    return {
      fields: [
        {
          key: 'timestamp',
          label: 'Date',
          class: 'timestamp-field',
          sortable: true
        },
        { key: 'changes', label: 'Change', class: 'changes-field' },
        { key: 'additional_data', label: 'User', class: 'actor-field' }
      ],
      tableItems: [],
      totalRows: 0,
      currentPage: 1,
      perPage: 5,
      keyword: '',
      timer: null,
      isLoading: false
    }
  },
  mixins: [editSaleItemMixins],
  methods: {
    ...mapActions({
      getAuditLogs: `pf/analysis/getAuditLogs`
    }),
    async handleGetAuditLogs() {
      this.isLoading = true
      const data = {
        client_id: this.clientID,
        id: this.internalData.data[UNIQUE_KEY_BE].base,
        page: this.currentPage,
        keyword: this.keyword
      }
      try {
        await this.getAuditLogs(data).then(resp => {
          if (resp.data) {
            const usefulProperty = ['timestamp', 'changes', 'additional_data', 'model_name']
            this.totalRows = resp.data.count
            this.tableItems = this.filterDataByProps(
              resp.data.results,
              usefulProperty
            )
          }
        })
      } catch (err) {
        console.log('error', err)
      }
      this.isLoading = false
    },
    filterDataByProps(data, props) {
      return data.reduce((acc, current) => {
        const newItem = props.reduce((item, prop) => {
          if (prop === 'changes') {
            const result = {}
            for (const change in current[prop]) {
              switch (change) {
                case 'created':
                  break
                case 'modified':
                  result[change] = current[prop][change].map(item =>
                    this.$moment(item).format('MM/DD/YYYY h:mm A')
                  )
                  break
                case 'brand':
                case 'client':
                case 'sale':
                case 'size':
                case 'style':
                  result[change] = current[prop][change].map(item => {
                    return item ? item.split(' - ', 1).toString() : 'None'
                  })
                  break
                default:
                  result[change] = current[prop][change]
              }
            }
            item[prop] = result
          } else {
            item[prop] = current[prop]
          }
          return item
        }, {})
        acc.push(newItem)
        return acc
      }, [])
    },
    handleKeywordChange(e) {
      e.preventDefault()
      if (this.keyword) {
        this.currentPage = 1
        this.handleGetAuditLogs()
      }
    },
    clearKeyword() {
      this.keyword = ''
      this.handleGetAuditLogs()
    },
    formatDataChange(data) {
      let dataAfterFormat = null
      this.$moment(data, this.$moment.ISO_8601, true).isValid() ? dataAfterFormat = this.$moment(data).format('MM/DD/YYYY h:mm A') : dataAfterFormat = data
      return dataAfterFormat
    },
    formattedByTimeZone(timeStamp, format = 'h:mm A z') {
      return moment(timeStamp).tz(this.timezone).format(format)
    }
  },
  mounted() {
    this.totalRows = this.tableItems.length
  },
  watch: {
    dataRow() {
      this.currentPage = 1
      this.keyword = ''
      this.handleGetAuditLogs()
    },
    currentPage() {
      this.handleGetAuditLogs()
    }
  },
  filters: {
    formatText: function (string) {
      if (string) return string
      else if (string === null) return 'None'
      else if (string === '') return 'Empty'
      else return 'N/A'
    }
  }
}
</script>

<style lang="scss" scoped>
::v-deep .modal-mdx {
  max-width: 700px;
}

::v-deep .modal-title {
  width: 100%;
}

::v-deep .cursor-pointer {
  cursor: pointer;
}

::v-deep .timestamp-field {
  width: 20%;
  vertical-align: middle;
}

::v-deep .changes-field {
  width: 60%;
}

::v-deep .actor-field {
  vertical-align: middle;
}

.thin-spinner {
  border-width: .14em;
}

.changelog-modal {
  .clear-keyword {
    position: absolute;
    cursor: pointer;
    right: 50px;
    top: 50%;
    z-index: 20;
    transform: translateY(-50%);
  }

  &__key {
    display: inline-block;
    margin-right: 5px;
  }

  &__value {
    img {
      height: 16px;
      width: 16px;
    }

    span {
      display: inline-block;

      &:first-child {
        max-width: 700px;
        padding: 0 4px;
        background-color: #ffebe6;
        text-decoration: line-through;
        text-decoration-color: red;
      }

      &:last-child {
        span {
          display: inline;
          max-width: 700px;
          padding: 0 4px;
          background-color: #e3fcef;
        }
      }
    }
  }
}

::v-deep .history-search input {
  padding-right: 35px;
}
</style>
