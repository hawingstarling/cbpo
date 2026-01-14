<template>
  <div class="cbpo-list position-relative" >
    <div class="px-3">
      <div class="cbpo-list__search-wrapper">
        <b-form class="cbpo-list__search-wrapper__form">
          <b-input-group class="my-1">
            <template v-slot:prepend>
              <b-input-group-text class="cursor-pointer">
                <i class="fa fa-search"></i>
              </b-input-group-text>
            </template>
            <i
              class="fa fa-times-circle clear-keyword"
              v-if="keyword"
              @click="clearKeyword()"
            ></i>
            <b-form-input
              id="input-valid"
              placeholder="Search Column"
              type="text"
              v-model="keyword"
            >
            </b-form-input>
          </b-input-group>
        </b-form>
      </div>
    </div>
    <template v-if="leftColumns.length">
      <div class="cbpo-list-element__wrapper position-relative">
        <div class="cbpo__element row no-gutters position-relative">
          <div class="p-0 cbpo__element__column__wrapper" :class="{'--diff': leftColumns.length !== rightColumns.length}">
            <!-- left column -->
            <div class="position-relative cbpo__element__column --left">
              <template v-for="(col, colIndex) in leftColumns">
                <div
                  v-if="col && !col.disable"
                  class="wrapper-row"
                  :key="`element-column-${colIndex}`"
                >
                  <div class="cbpo__row" :id="col.name">
                    <div class="cbpo__index">
                      {{colIndex + 1}}
                    </div>
                    <div class="cbpo__name" :title="col.displayName || col.name">
                      {{ col.displayName || col.name }}
                    </div>
                    <div class="cbpo__switch">
                      <b-form-checkbox
                        :id="`element-checkbox-twin-${col.alias ? col.alias : col.name}`"
                        ref="columnsList"
                        v-model="col.visible"
                        switch
                      />
                    </div>
                  </div>
                </div>
              </template>
            </div>
            <!-- right column -->
            <div class="position-relative cbpo__element__column --right">
              <template v-for="(col, colIndex) in rightColumns">
                <div
                  v-if="col && !col.disable"
                  class="wrapper-row"
                  :key="`element-column-${colIndex + middleLength + 1}`"
                >
                  <div class="cbpo__row" :id="col.name">
                    <div class="cbpo__index">
                      {{colIndex + middleLength + 1}}
                    </div>
                    <div class="cbpo__name" :title="col.displayName || col.name">
                      {{ col.displayName || col.name }}
                    </div>
                    <div class="cbpo__switch">
                      <b-form-checkbox
                        :id="`element-checkbox-twin-${col.alias ? col.alias : col.name}`"
                        ref="columnsList"
                        v-model="col.visible"
                        switch
                      />
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template v-else>
      <div class="cbpo__element--not-found">
        No column found.
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'ListColumnsSingleMode',
  props: {
    columnsInElements: Array,
    hiddenColumns: Array
  },
  data() {
    return {
      keyword: ''
    }
  },
  computed: {
    columns: {
      get() {
        const columns = this.hiddenColumns.length
          ? this.columnsInElements[0].columns
            .filter(c => !this.hiddenColumns.find(col => col.name === c.name))
          : this.columnsInElements[0].columns
        return this.keyword
          ? columns.filter(col => col.name.includes(this.keyword.toLowerCase().trim()))
          : columns
      },
      set(columnsInElements) {
        this.$emit('update:columnsInElements', columnsInElements)
      }
    },
    middleLength() {
      return Math.ceil(this.columns.length / 2)
    },
    leftColumns() {
      return this.columns.filter((_c, index) => index >= 0 && index < this.middleLength)
    },
    rightColumns() {
      return this.columns.filter((_c, index) => index >= this.middleLength && index < this.columns.length)
    }
  },
  methods: {
    switchColumn(col) {
      const enabledColumns = this.$refs.columnsList.filter((col) => col.checked)
      if (enabledColumns.length === 0) {
        col.visible = true
      }
    },
    clearKeyword() {
      this.keyword = ''
    }
  }
}
</script>

<style lang="scss" scoped>
@import "@/components/widgets/columns/ListColumnsSingleMode.scss";
</style>
