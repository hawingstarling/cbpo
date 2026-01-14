const sdkToolBar = Vue.component('sdkToolBar', {
  template: `
    <b-navbar type='dark' variant='dark'>
    <b-navbar-nav>
      <template v-for='(route, index) of routes'>
        <sdk-menu-item :key='index + route.name' :root='true' :routeItem='route' />
      </template>
    </b-navbar-nav>
    </b-navbar>
  `,
  components: {
    'sdk-menu-item': sdkMenuItem
  },
  data() {
    return {
      routes: [
        {
          name: 'Live Docs',
          path: '/live-docs'
        },
        {
          name: 'Dashboard',
          children: [
            {
              name: 'Dashboard Container',
              path: '/dashboard-container'
            },
            {
              name: 'Dashboard Builder',
              path: '/dashboard-builder'
            },
            {
              name: 'Dashboard Global Filter',
              path: '/dashboard-global-filter'
            },
            {
              name: 'Dashboard with new Visualization',
              path: '/dashboard-visualization'
            }
          ]
        },
        {
          name: 'Table',
          children: [
            {
              name: 'Normal Table',
              path: '/table'
            },
            {
              name: 'Group Table',
              path: '/group-table'
            }
          ]
        },
        {
          name: 'Chartjs',
          children: [
            {
              name: 'Pie Chart',
              path: '/chartJS-pie'
            },
            {
              name: 'Donut Chart',
              path: '/chartJS-donut'
            },
            {
              name: 'Bar Chart',
              path: '/chartJS-bar'
            },
            {
              name: 'Line Chart',
              path: '/chartJS-line'
            },
            {
              name: 'Pareto Chart',
              path: '/chartJS-pareto'
            },
            {
              name: 'Area Chart',
              path: '/chartJS-area'
            },
            {
              name: 'Scatter Chart',
              path: '/chartJS-scatter'
            },
            {
              name: 'Bubble Chart',
              path: '/chartJS-bubble'
            }
          ]
        },
        {
          name: 'Highcharts',
          children: [
            {
              name: 'Pie Chart',
              path: '/hc-pie'
            },
            {
              name: 'Donut Chart',
              path: '/hc-donut'
            },
            {
              name: 'Bar Chart',
              path: '/hc-bar'
            },
            {
              name: 'Line Chart',
              path: '/hc-line'
            },
            {
              name: 'Pareto Chart',
              path: '/hc-pareto'
            },
            {
              name: 'Area Chart',
              path: '/hc-area'
            },
            {
              name: 'Scatter Chart',
              path: '/hc-scatter'
            },
            {
              name: 'Bubble Chart',
              path: '/hc-bubble'
            },
            {
              name: 'Solid Gauge',
              path: '/hc-solidgauge'
            },
            {
              name: 'Bullet Gauge',
              path: '/hc-bulletgauge'
            },
            {
              name: 'Heat Map',
              path: '/hc-heat-map'
            }
          ]
        },
        {
          name: 'Crosstab',
          children: [
            {
              name: 'Crosstab Table',
              path: '/crosstab-table'
            },
            {
              name: 'Crosstab Chart',
              path: '/crosstab-chart'
            }
          ]
        },
        {
          name: 'Html Editor',
          path: '/html-editor'
        },
        {
          name: 'Drill Down',
          children: [
            {
              name: 'Chart',
              path: '/drill-down-chart'
            },
            {
              name: 'Table',
              path: '/drill-down-table'
            }
          ]
        },
        {
          name: 'Widgets',
          children: [
            {
              name: 'Widget Performance Table',
              path: '/widget-performance'
            },
            {
              name: 'Save config to Server',
              path: '/widget-save-config'
            },
            {
              name: 'Full Features Table',
              path: '/widget-full-features'
            },
            {
              name: 'Widget Table With Filter Form',
              path: '/widget-filter-form'
            },
            {
              name: 'Widget Loader',
              path: '/widget-loader'
            },
            {
              name: 'Comparable Table',
              path: '/widget-comparable-table'
            }
          ]
        },
        {
          name: 'Visualization',
          children: [
            {
              name: 'Visualization Builder',
              path: '/visualization-builder'
            }
          ]
        }
      ]
    }
  }
})
