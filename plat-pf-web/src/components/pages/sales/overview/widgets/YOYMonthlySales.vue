<template>
  <div class="widget-monthly-sales d-flex flex-column position-relative h-100 overflow-hidden">
    <span v-if="lastUpdated" class="last-updated">
      Last updated: {{ formatLastTime(lastUpdated) }}
    </span>
    <div class="select-wrapper w-50">
      <v-select
        class="custom-v-select"
        :options="options"
        :clearable="false"
        v-model="selected"
      >
        <template #open-indicator="{ attributes }">
          <i class="fa fa-angle-down" v-bind="attributes"></i>
        </template>
      </v-select>
    </div>
    <cbpo-widget
      ref="widget"
      class="border-0"
      :config-obj="config"
      @getLastUpdated="lastUpdated = $event"
    />
    <cbpo-widget-menu-control
      class="custom-menu"
      :config-obj="this.mixinsWidgetMenuConfig"
      @click="menuEventHandler"/>
  </div>
</template>

<script>
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import { formatLastTime } from '@/shared/utils'

export default {
  name: 'YOYMonthlySales',
  mixins: [WidgetMenu],
  data() {
    const options = [{label: 'YOY Monthly Sales', value: null}]
    return {
      options,
      selected: options[0],
      lastUpdated: null
    }
  },
  props: {
    config: Object
  },
  methods: {
    formatLastTime,
    menuEventHandler(type) {
      if (type !== 'csv' || !this.$refs.widget) return
      this.$refs.widget.widgetExport(type)
    },
    getLastUpdated(lastUpdated) {
      this.lastUpdated = this.lastUpdated || lastUpdated
    }
  }
}
</script>

<style scoped lang="scss">
.widget-monthly-sales {
  border: 1px solid #d9d9d9;
  padding: 0.5rem;
  background-color: #fff;
  border-radius: 6px;
}

.custom-menu {
  position: absolute;
  right: calc(25px + 0.5rem);
  top: 17px;
}

.select-wrapper {
  margin: calc(50px - 0.5rem) auto 33px auto;
}
// custom v-select
::v-deep .custom-v-select .vs__dropdown-toggle {
  font-size: 0.85em;
  background-color: white;
  height: 100%;
  padding-bottom: unset;
  font-weight: 400;
  line-height: 1.5;
  color: rgb(92, 104, 115);
  border-radius: 4px;
  border: 1px solid #c8ced3;
}
::v-deep .custom-v-select .vs__search {
  color: rgb(130,139,147);
  padding-bottom: 4px;
}
::v-deep .custom-v-select .vs__dropdown-menu {
  font-size: 14px;
  li {
    font-size: 14px;
  }
}
::v-deep .custom-v-select .vs__open-indicator {
  color: rgb(35,40,44);
  cursor: pointer;
  font-size: 16px;
}
::v-deep .custom-v-select .vs__clear, ::v-deep .custom-v-select .vs__open-indicator {
  margin-bottom: 4px;
}

.last-updated {
  position: absolute;
  z-index: 9;
  right: calc(25px + 2.5rem);
  font-weight: 500;
  color: #C8CBD0;
  margin: 0.7rem 0;
  font-size: 14px;
  font-stretch: normal;
  font-style: normal;
  line-height: 16px;
  letter-spacing: 0.07px;
}
</style>
