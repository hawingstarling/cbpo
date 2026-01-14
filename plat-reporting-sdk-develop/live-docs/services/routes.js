const routes = [
  // ELEMENT
  {
    path: '/table',
    name: 'Table',
    meta: {
      title: 'Demo Table'
    },
    component: sdkTablePage
  },
  {
    path: '/group-table',
    name: 'TableGroup',
    meta: {
      title: 'Demo Group Table'
    },
    component: sdkGroupTablePage
  },
  {
    path: '/widget-save-config',
    name: 'WidgetSaveConfig',
    meta: {
      title: 'Demo Widget Save Config'
    },
    component: saveConfigPage
  },
  {
    path: '/html-editor',
    name: 'HtmlEditor',
    meta: {
      title: 'Demo HTML Editor'
    },
    component: htmlEditorPage
  },
  {
    path: '/chartJS-pie',
    name: 'ChartJSPieChart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/chartJS-donut',
    name: 'ChartJSDonutChart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/chartJS-area',
    name: 'ChartJSAreaChart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/chartJS-bar',
    name: 'ChartJSBarChart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/chartJS-line',
    name: 'ChartJSLineChart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/chartJS-pareto',
    name: 'ChartJSPareto Chart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/chartJS-scatter',
    name: 'ChartJSScatterChart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/chartJS-bubble',
    name: 'ChartJSBubbleChart',
    component: sdkChartjsDemoPage
  },
  {
    path: '/hc-pie',
    name: 'HighChartPie',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-donut',
    name: 'HighChartScatter',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-bar',
    name: 'HighChartBar',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-line',
    name: 'HighChartLine',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-pareto',
    name: 'HighChartPareto',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-area',
    name: 'HighChartArea',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-scatter',
    name: 'HighChartScatter',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-bubble',
    name: 'HighChartBubble',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-solidgauge',
    name: 'HighChartSolid',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-bulletgauge',
    name: 'HighChartBullet',
    component: sdkHighChartDemoPage
  },
  {
    path: '/hc-heat-map',
    name: 'HighChart Heat Map',
    component: sdkHighChartDemoPage
  },
  {
    path: '/visualization-builder',
    name: 'Visualization',
    meta: {
      title: 'Demo Visualization'
    },
    component: sdkVisualizationPage
  },
  {
    path: '/dashboard-container',
    name: 'DashboardContainer',
    meta: {
      title: 'Demo Dashboard Container'
    },
    component: sdkDashboardContainerPage
  },
  {
    path: '/dashboard-builder',
    name: 'DashboardDropLayout',
    meta: {
      title: 'Demo Dashboard Builder With Widgets'
    },
    component: sdkDashBoardBuilderPage
  },
  {
    path: '/dashboard-visualization',
    name: 'DashboardVisualization',
    meta: {
      title: 'Demo Dashboard with new Visualization'
    },
    component: sdkDashboardVisualizePage
  },
  {
    path: '/widget-full-features',
    name: 'WidgetFullFeatures',
    meta: {
      title: 'Demo Widget Table With All Features'
    },
    component: sdkFeatureTablePage
  },
  {
    path: '/widget-comparable-table',
    name: 'WidgetComparableTable',
    meta: {
      title: 'Demo Widget Comparable Table'
    },
    component: sdkComparableTablePage
  },
  {
    path: '/widget-filter-form',
    name: 'WidgetFilterForm',
    meta: {
      title: 'Demo Widget Table With Filter Form'
    },
    component: sdkFilterFormTablePage
  },
  {
    path: '/widget-loader',
    name: 'WidgetLoader',
    meta: {
      title: 'Demo Widget Loader'
    },
    component: widgetLoader
  },
  {
    path: '/crosstab-table',
    name: 'CrosstabTable',
    meta: {
      title: 'Demo Crosstab Table'
    },
    component: sdkCrosstabTablePage
  },
  {
    path: '/crosstab-chart',
    name: 'CrosstabChart',
    meta: {
      title: 'Demo Crosstab Chart'
    },
    component: sdkCrosstabChartPage
  },
  {
    path: '/dashboard-global-filter',
    name: 'DashboardGlobalFilter',
    meta: {
      title: 'Demo Dashboard Global Filter'
    },
    component: sdkDashboardGlobalFilterPage
  },
  {
    path: '/drill-down-chart',
    name: 'DrillDownChart',
    meta: {
      title: 'Drill down for chart'
    },
    component: sdkDrillDownChart
  },
  {
    path: '/drill-down-table',
    name: 'DrillDownTable',
    meta: {
      title: 'Drill down for Table'
    },
    component: sdkDrillDownTablePage
  },
  {
    path: '/widget-performance',
    name: 'WidgetPerformance',
    meta: {
      title: '1k row data in widget'
    },
    component: sdkPerformanceWidget
  }
]
