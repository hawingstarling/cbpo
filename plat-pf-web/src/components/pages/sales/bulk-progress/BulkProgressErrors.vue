<template>
  <b-row>
    <b-col>
      <b-card>
        <template v-slot:header>
          <div
            class="d-flex justify-content-between align-items-center text-uppercase"
          >
            <div>
              <b>{{ title }}</b>
            </div>
          </div>
        </template>

        <b-row class="mb-3">
          <b-col md="4" class="mx-auto">
            <b-form @submit.prevent="handleKeywordChange()">
              <b-input-group class="mt-3">
                <template v-slot:append>
                  <b-input-group-text
                    class="cursor-pointer"
                    @click="handleKeywordChange()"
                  >
                    <i class="fa fa-search"></i>
                  </b-input-group-text>
                </template>
                <b-form-input
                  id="input-valid"
                  placeholder="Search for Item ID"
                  type="text"
                  v-model="keyword"
                  @input=" value.page = 1"
                >
                </b-form-input>
                <i
                  class="fa fa-times-circle clear-keyword"
                  v-if="keyword"
                  @click="clearKeyword()"
                ></i>
              </b-input-group>
            </b-form>
          </b-col>
        </b-row>

        <b-table
          v-if="listItems"
          :fields="fields"
          :items="listItems.items"
          bordered
          class="error-table overflow-auto height"
          thead-class="text-nowrap text-uppercase"
          tbody-class="text-nowrap"
          responsive="sm"
          show-empty
          small
        >
          <template
            v-slot:cell(_meta)="row"
            v-if="
              listItems.items && listItems.items[0] && listItems.items[0]._meta
            "
          >
            <ul
              class="mb-0 w-100 p-0"
              v-for="(item, index) in row.item._meta.processing_errors"
              :key="index"
              style="list-style-position: inside;"
            >
              <li
                class="text-danger text-truncate max-width-300"
                :title="item.message"
              >
                {{ item.code | filterColumnName }}: {{ item.message }}
              </li>
            </ul>
            <div
              class="text-left d-flex justify-content-center align-items-center"
            >
              <span
                v-if="!row.item._meta.processing_errors.length > 0"
                class="badge badge-success"
                ><i class="fa fa-check-circle"></i> OK</span
              >
            </div>
          </template>
          <template slot="empty">
            <div
              class="d-flex justify-content-center align-item-center text-secondary p-5"
            >
              No data
            </div>
          </template>
        </b-table>
        <nav class="d-flex justify-content-center" v-if="listItems">
          <b-pagination
            v-model="value.page"
            v-if="listItems.page_count && listItems.page_count > 1"
            :total-rows="listItems.total || 0"
            first-text="First"
            prev-text="Prev"
            next-text="Next"
            last-text="Last"
          >
            <template #prev-text><img src="@/assets/img/icon/arrow-right.svg" class="rotate-icon pagination-icon"><span class="pl-2"> Previous</span></template>
            <template #next-text><span class="pr-2">Next </span><img src="@/assets/img/icon/arrow-right.svg" class="pagination-icon"></template>
          </b-pagination>
        </nav>
      </b-card>
    </b-col>
  </b-row>
</template>

<script>
import { filterColumnName } from '@/shared/filters'

export default {
  name: 'BulkProgressErrors',
  props: {
    title: String,
    value: Object, // { search, page }
    listItems: Object
  },
  data() {
    return {
      fields: [
        { key: 'id', label: 'Sale Item ID', class: 'sale-item-id-td w-50' },
        { key: '_meta', label: 'Status', class: 'errors-td w-50' }
      ],
      keyword: ''
    }
  },
  filters: {
    filterColumnName
  },
  methods: {
    handleKeywordChange() {
      this.value.search = this.keyword
    },
    clearKeyword() {
      this.keyword = ''
      this.value.search = ''
    }
  }
}
</script>

<style lang="scss" scoped>
#input-valid {
  padding-right: 30px;
}
.clear-keyword {
  position: absolute;
  cursor: pointer;
  right: 50px;
  top: 50%;
  z-index: 20;
  transform: translateY(-50%);
}
::v-deep .error-table {
  thead th {
    padding-left: 20px;
    padding-right: 20px;
  }
  .table td {
    padding-left: 20px;
    padding-right: 20px;
  }
}

::v-deep .pagination {
  .page-item:nth-child(2),
  .page-item:nth-last-child(2) {
    .page-link {
      width: auto !important;
    }
  }
}
</style>
