<template>
  <div class="view-comparison-card" v-cbpo-loading="{ loading: (initial || isLoading) && !isEmptyTag }">
    <cbpo-widget-menu-control class="custom-menu" :config-obj="this.mixinsWidgetMenuConfig" @click="menuEventHandler" />
    <change-tag-modal ref="changeTagModal" @change="tagChanged" />
    <pf-compare-table ref="table" class="h-100" :class="{ 'd-none': isEmptyTag }" :tag="tag" :show-tag="false"
      :actions="actions">
      <template v-slot:loader>
        <div></div>
      </template>
    </pf-compare-table>
    <div v-if="isEmptyTag" class="h-100 w-100 d-flex justify-content-center align-items-center">
      There is no tag to show
    </div>
  </div>
</template>

<script>
import PfCompareTable from '@/components/pages/sales/compare-table/CompareTable'
import ChangeTagModal from '@/components/pages/sales/views/modal/ChangeTag'
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import applyTagImg from '@/assets/img/icon/apply-tag.svg'

export default {
  components: { ChangeTagModal, PfCompareTable },
  mixins: [WidgetMenu],
  data() {
    return {
      initial: true,
      isEmptyTag: false,
      isLoading: true,
      tag: null,
      actions: [
        {
          img: applyTagImg,
          text: 'Apply Tag',
          handler: () => {
            this.$refs.changeTagModal.openModal()
          }
        }
      ]
    }
  },
  mounted() {
    this.$watch('$refs.table.isReady', function (isReady) {
      this.isLoading = !isReady
    })
  },
  methods: {
    tagChanged(tag) {
      this.tag = tag
      this.isEmptyTag = !tag && this.initial
      this.initial = false
    },
    menuEventHandler() {
      this.$refs.table.exportData()
    }
  }
}
</script>

<style lang="scss" scoped>
.view-comparison-card {
  border: 1px solid #d9d9d9;
  height: 100%;
  min-height: 150px;

  ::v-deep {
    .analysis[data-v-ab706320] .cbpo-widget-wrapper .cbpo-widget .cbpo-table-element-container .cbpo-table {
      min-height: 90px;
      border-bottom: none !important;
    }

    .cbpo-widget-wrapper {
      margin-bottom: 0 !important;
    }

    .cbpo-table-reporting {
      padding-bottom: 0 !important;
    }

    .cbpo-table-body .vue-recycle-scroller__item-view .cbpo-table-cell:not(:first-child) .tbl-cell-body {
      text-align: center !important;
    }

    .cbpo-table-body .vue-recycle-scroller__item-wrapper .vue-recycle-scroller__item-view:last-child .cbpo-table-cell {
      border-bottom: 0 !important;
    }

    .cbpo-table {
      border-left: 0 !important;
      border-right: 0 !important;
    }

    .menu-control-select {
      position: absolute;
      right: calc(25px + 0.5rem);
      top: 28px;
      z-index: 200;
    }

    .column {
      &.column-4 {
        margin-right: 60px !important;
      }

      &.column-5 {
        display: none;
      }
    }

    .table-title {
      margin-left: 1.5rem !important;

      h5 {
        font-family: Inter, sans-serif;
        font-size: 14px;
        line-height: 16px;
        transform: translateY(0.25rem);
      }
    }

    .manage-tag-dropdown {
      button.dropdown-toggle {
        font-family: Inter, sans-serif !important;
        line-height: 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;

        &::after {
          width: 10px !important;
        }
      }

      .dropdown-menu {
        min-width: unset !important;
        border-radius: 0 !important;
        transform: translate3d(0, 36px, 0) !important;
        right: 0 !important;
        left: 0 !important;
        margin-top: 0 !important;
        box-shadow: 0 0 10px #c8ced3 !important;
        border: 0 !important;

        .dropdown-item {
          padding: 5px 10px;
        }
      }
    }

    .analysis>.row>.d-flex>div {
      &:first-child {
        padding-left: 0.5rem;
      }

      &:last-child {
        padding-right: 0.5rem;
      }
    }
  }
}

::v-deep .cbpo-control-features {
  background-color: #f9fbfb !important;
}

::v-deep .cbpo-table {
  background-color: unset !important;
}
</style>
