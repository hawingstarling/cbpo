<template>
  <div ref="wrapper" class="total-sales-tracker">
    <div class="total-sales-tracker-header">
      <span>Total Sales Tracker</span>
      <cbpo-widget-menu-control class="custom-menu"
        :config-obj="this.mixinsWidgetMenuConfig" @click="menuEventHandler" />
    </div>
    <div class="total-sales-tracker-body">
      <cbpo-widget :key="count" :config-obj="config" />
    </div>
    <setting-goal :default="widgetData.goal" :is-open.sync="isModelOpened" @updateSettingsGoal="updateSettingsGoal"/>
  </div>
</template>

<script>
import WidgetMenu from '@/components/pages/sales/overview/common/widget-menu'
import SettingGoal from '@/components/pages/sales/views/modal/SettingGoal'

export default {
  name: 'TotalSalesTracker',
  components: { SettingGoal },
  mixins: [WidgetMenu],
  props: {
    config: Object,
    dsId: Object,
    settingGoal: Number
  },
  data: () => ({
    count: 0,
    isModelOpened: false,
    widgetData: {
      id: '',
      goal: 0
    }
  }),
  methods: {
    menuEventHandler() {
      this.isModelOpened = true
    },
    replaceExpressionAndReRender(id, goalValue) {
      const content = '[kpi chart-type="bar" version="precise" class-css="m-auto" width="WIDTH" height="160" min="EXPRESSION_MIN" max="EXPRESSION_MAX" target="EXPRESSION_TARGET" current="EXPRESSION_CURRENT" format-string="$,d" format-tooltip="$,.f" current-legend="Current" goal-legend="Goal" target-legend="Target" percent-number="on"][/kpi]'
      const baseConditions = [
        "(@item_sale_status in ['Pending','Unshipped','Shipped','Partially Refunded'])",
        "(@channel_name $eq 'amazon.com')"
      ].join(' & ')
      this.config.elements[0].config.dataSource = id
      this.config.elements[0].config.content = content
        .replace('WIDTH', this.$refs.wrapper ? Math.max(this.$refs.wrapper.clientWidth * 0.9, 500) : 1000)
        .replace('EXPRESSION_MIN', 0)
        .replace('EXPRESSION_MAX', goalValue)
        .replace('EXPRESSION_CURRENT', `{SUMIF(@item_sale_charged,(@sale_date >=DATE_START_OF(TODAY(),'years')) & (@sale_date <= YESTERDAY()) & ${baseConditions}, '${id}')}`)
        .replace('EXPRESSION_TARGET', `{SUMIF(@item_sale_charged, (@sale_date >=DATE_START_OF(DATE_LAST(1,'years'),'years')) & (@sale_date <= DATE_END_OF(DATE_LAST(1,'year'), 'year')) & ${baseConditions}, '${id}')}`)
      this.count++
    },
    updateSettingsGoal(value) {
      if (value === this.widgetData.goal) return
      this.widgetData.goal = value
      this.replaceExpressionAndReRender(this.widgetData.id, this.widgetData.goal)
    }
  },
  created() {
    this.mixinsWidgetMenuConfig.selection = {
      options: [
        {
          label: 'Edit Goal Value',
          icon: 'fa fa-pencil',
          value: 'edit-goal',
          type: 'item'
        }
      ]
    }
  },
  mounted() {
    this.widgetData = {
      id: this.dsId.data_source_id,
      goal: this.settingGoal
    }
    this.replaceExpressionAndReRender(this.widgetData.id, this.widgetData.goal)
  }
}
</script>

<style lang="scss" scoped>
.total-sales-tracker {
  display: flex;
  flex-direction: column;
  border: solid 1px #d9d9d9;
  height: 100%;
  background-color: #fff;

  .total-sales-tracker-header {
    position: relative;
    text-align: left;
    padding-top: 16px;
    padding-left: 1.5rem;

    span {
      margin: 0.7rem 0;
      font-size: 14px;
      font-weight: 500;
      font-stretch: normal;
      font-style: normal;
      line-height: 1.14;
      letter-spacing: 0.07px;
      color: #080e2c;
    }

    ::v-deep .menu-control-select {
      position: absolute;
      right: calc(25px + 0.5rem);
      top: 17px;
    }
  }

  .total-sales-tracker-body {
    height: 100%;

    &::v-deep {
      .cbpo-widget {
        border: none;
      }

      .cbpo-container-html-editor,
      .cbpo-control-features {
        padding: 0 !important;
      }

      .cbpo-container-html-editor {
        g.group-bar {
          circle {
            display: none;
          }

          &.Current_Value rect {
            fill: #52C0E1;
          }

          &.Target_Value rect {
            fill: #91E4AB;
          }

          &.Max_Value rect {
            fill: #D0DDE7;
          }
        }

        g.group-points text {
          font-family: 'Inter';
          font-style: normal;
          font-weight: 400;
          line-height: 20px;
          fill: #080E2C;
          font-size: 14px;
        }
      }
    }
  }
}

::v-deep .dropdown-item {
  font-size: 0.875rem;

  &:hover {
    color: #fff;
    background: #5897fb;
    border-radius: 0;
  }
}
</style>
