const sdkDashboardVisualizePage = Vue.component('sdkDashboardVisualizePage', {
  template: `
    <div class="dashboard-visualization-demo">
    <div id="dashboard-visualization-demo">
    </div>
    <sdk-export-code :templates="getTemplate" />
    </div>
  `,
  data() {
    return {
      template: '<cbpo-dashboard class="p-0" config-ref="config"></cbpo-dashboard>',
      config: {
        'widgetLayout': {
          'widgets': [
            {
              'type': 'cbpo-widget',
              'config': {
                'grid': {
                  'x': 0,
                  'y': 207,
                  'w': 12,
                  'h': 39,
                  'i': 1,
                  'id': 'id-a8aa2178-215d-45a6-b1fd-f61bcd49bbce',
                  'moved': false
                },
                'autoHeight': false,
                'widget': {
                  'title': {
                    'text': 'Seller Buy-box Percentage (Updated Weekly)',
                    'enabled': true,
                    'edited': true
                  },
                  'style': {
                    'background_color': null,
                    'foreground_color': null,
                    'header_background_color': null,
                    'header_foreground_color': null,
                    'border_width': null,
                    'border_radius': null
                  },
                  'id': 'id-8a8d9657-4871-4ab4-b9ae-7d4815d28374',
                  'class': ''
                },
                'action': { 'elements': [] },
                'elements': [{
                  'type': 'cbpo-element-chart', 'config': {
                    'dataSource': '21c876b1-c58b-4dd2-89ae-fbfdee171b41',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Quantitation of [bb_winner] over [bb_winner]',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [{
                      'name': 'bb_winner',
                      'displayName': 'Count BB Winner',
                      'type': 'double',
                      'format': {
                        'common': {
                          'plain': { 'nil': 'NULL', 'empty': 'EMPTY', 'na': 'N/A' },
                          'html': {
                            'nil': '<span class="d-sdk-nil">null</span>',
                            'empty': '<span class="d-sdk-empty">empty</span>',
                            'na': '<span class="d-sdk-na">N/A</span>'
                          },
                          'prefix': null,
                          'suffix': null
                        }, 'type': 'numeric', 'config': { 'comma': true, 'precision': 0, 'siPrefix': false }
                      },
                      'aggrFormats': null
                    }],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [{
                      'axis': {
                        'x': [{
                          'id': 'x_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                          'type': 'category',
                          'display': true,
                          'format': null,
                          'scaleLabel': { 'display': false, 'labelString': '' },
                          'ticks': { 'fontSize': 11, 'fontStyle': 'bold' }
                        }],
                        'y': [{
                          'id': 'y_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                          'type': 'linear',
                          'format': null,
                          'position': 'left',
                          'stack': false,
                          'ticks': {
                            'beginAtZero': true,
                            'stepSize': '',
                            'maxTicksLimit': 5,
                            'fontSize': 11,
                            'fontStyle': 'bold'
                          },
                          'scaleLabel': { 'display': false, 'labelString': '' }
                        }]
                      },
                      'options': {
                        'legend': {
                          'enabled': true,
                          'position': 'right',
                          'widthPercent': 40,
                          'isHorizontal': false
                        }, 'pie': { 'type': 'doughnut' }, 'borderWidth': 0
                      },
                      'series': [{
                        'type': 'pie',
                        'name': 'Count BB Winner (Count)',
                        'axis': {
                          'x': 'x_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                          'y': 'y_id-e1a033a1-564a-4796-b1ad-acb62492a988'
                        },
                        'data': { 'x': 'bb_winner', 'y': 'bb_winner' },
                        'id': 'id-e1a033a1-564a-4796-b1ad-acb62492a988'
                      }]
                    }],
                    'sorting': [{
                      'column': 'bb_winner_count_id-e1a033a1-564a-4796-b1ad-acb62492a988',
                      'direction': 'desc'
                    }],
                    'grouping': {
                      'aggregations': [{
                        'column': 'bb_winner',
                        'aggregation': 'count',
                        'alias': 'bb_winner_count_id-e1a033a1-564a-4796-b1ad-acb62492a988'
                      }], 'columns': [{ 'name': 'bb_winner' }]
                    },
                    'bins': [],
                    'pagination': { 'limit': 1000, 'current': 1, 'type': 'buttons' },
                    'color_scheme': 'D3_30',
                    'messages': { 'no_data_at_all': 'No data', 'no_data_found': 'No data found' },
                    'timezone': { 'enabled': true, 'utc': 'America/Danmarkshavn', 'visible': false },
                    'id': '03f4ee81-fa40-48a2-9645-7ca5b939e962',
                    'filter': {
                      'type': 'AND',
                      'conditions': [{
                        'id': 'id-07f9af28-ea48-49ca-aa5e-cc65912c62fc',
                        'level': 1,
                        'column': 'bb_winner',
                        'value': 'null',
                        'operator': 'not_null',
                        'parentId': 'id-e825ec80-0b65-47b7-bfc3-da2db5eaa234'
                      }]
                    },
                    'drillDown': { 'enabled': false, 'config': {} },
                    'formats': { 'aggrs': {} }
                  }
                }],
                'filter': {
                  'form': { 'config': { 'controls': [], 'query': {} } },
                  'base': {
                    'config': {
                      'query': {
                        'id': 'id-e825ec80-0b65-47b7-bfc3-da2db5eaa234',
                        'level': 0,
                        'type': 'AND',
                        'conditions': [{
                          'id': 'id-07f9af28-ea48-49ca-aa5e-cc65912c62fc',
                          'level': 1,
                          'column': 'bb_winner',
                          'value': 'null',
                          'operator': 'not_null',
                          'parentId': 'id-e825ec80-0b65-47b7-bfc3-da2db5eaa234'
                        }],
                        'parentId': null
                      }
                    }
                  },
                  'builder': {
                    'enabled': false,
                    'config': {
                      'trigger': { 'label': 'Setting Filter' },
                      'modal': { 'title': 'Query Builder' },
                      'format': { 'temporal': { 'date': 'YYYY-MM-DD', 'datetime': 'YYYY-MM-DD hh:mm' } },
                      'threshold': { 'maxLevel': 5 },
                      'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] },
                      'ignore': {
                        'global': { 'visible': false, 'value': false },
                        'base': { 'visible': false, 'value': false }
                      },
                      'form': { 'columns': [] }
                    },
                    'readable': { 'enabled': false }
                  },
                  'globalFilter': { 'enabled': false },
                  'alignment': ''
                },
                'columnManager': {
                  'enabled': false,
                  'config': {
                    'trigger': { 'label': 'Manage Columns' },
                    'modal': { 'title': 'Manage Columns' },
                    'managedColumns': [],
                    'hiddenColumns': []
                  }
                },
                'menu': {
                  'enabled': true,
                  'config': {
                    'label': { 'text': '' },
                    'icons': { 'css': 'fa fa-ellipsis-h' },
                    'dataSource': null,
                    'selection': {
                      'options': [{
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      }, {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      }, {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      }, { 'type': 'divider' }, {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }, {
                        'label': 'Data Source',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'type': 'item'
                      }],
                      'dsUrl': ''
                    },
                    'id': 'id-8bb95fb4-612a-4ad5-9015-52bb26bb76d0',
                    'widget': { 'title': { 'enabled': true, 'text': '' }, 'class': '' }
                  }
                },
                'waitingForGlobalFilter': false,
                'id': 'id-4c49ee5c-3e80-40ba-ba90-3852f078ada1',
                'calculatedColumn': { 'enabled': false }
              },
              'id': 'id-b4042cfd-10c2-4322-8c70-cfe5db0db53b',
              'key': 'd8b131fd-70fd-4657-ac7f-0cbefe9d4891'
            },
            {
              'type': 'cbpo-widget', 'config': {
                'grid': {
                  'x': 0,
                  'y': 58,
                  'w': 12,
                  'h': 63,
                  'i': 3,
                  'moved': false,
                  'id': 'id-94b9ed6a-680b-4933-a44e-33d9f4b0c94a'
                },
                'autoHeight': true,
                'widget': {
                  'title': {
                    'text': '[format expression="TODAY()" type="temporal" format="YYYY" ][/format] Sales by Units (Updated Daily)',
                    'enabled': true,
                    'edited': true
                  },
                  'style': {
                    'background_color': null,
                    'foreground_color': null,
                    'header_background_color': null,
                    'header_foreground_color': null,
                    'border_width': null,
                    'border_radius': null
                  },
                  'id': 'id-914f6ce4-04c3-424c-ad18-8e889cda5d2f',
                  'class': ''
                },
                'action': { 'elements': [] },
                'elements': [{
                  'type': 'cbpo-element-html-editor', 'config': {
                    'dataSource': 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e',
                    'builder': { 'visualization': false },
                    'content': '<div style="margin-left: 0px; margin-right: 0px; display: flex; flex-wrap: wrap; justify-content: center; align-items: center"> <div style="min-width: 320px; flex-grow: 1"> <p class="mt-1 text-center"><strong>Inventory Sales YTD</strong></p><p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="320" height="300" current="{SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@fba_unit, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string=",d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18pt; color: #e67e23;">[format expression="SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',\'][/format]</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"&nbsp; format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t1" type="numeric" format=","][/format] ([format expression="DATE_LAST(1,\'years\')" type="temporal" format="YYYY"][/format])</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@fba_unit,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100" format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t2" type="numeric" format=","][/format] ([format expression="DATE_LAST(2,\'years\')" type="temporal" format="YYYY"][/format])</p></div><div style="min-width: 320px; flex-grow: 1"> <p class="mt-1 text-center"><strong>MFN Sales YTD</strong></p><p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="320" height="300" current="{SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@mfn_unit, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string=",d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18pt; color: #e67e23;">[format expression="SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',\'][/format]</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"&nbsp; format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t1" type="numeric" format=","][/format] ([format expression="DATE_LAST(1,\'years\')" type="temporal" format="YYYY"][/format])</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@mfn_unit,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100" format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t2" type="numeric" format=","][/format] ([format expression="DATE_LAST(2,\'years\')" type="temporal" format="YYYY"][/format])</p></div><div style="min-width: 320px; flex-grow: 1"> <p class="mt-1 text-center"><strong>Total Sales YTD</strong></p><p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="320" height="300" current="{SUMIF(@total_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@total_unit, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@total_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string=",d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18pt; color: #e67e23;">[format expression="SUMIF(@total_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',\'][/format]</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@total_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@total_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@total_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"&nbsp; format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t1" type="numeric" format=","][/format] ([format expression="DATE_LAST(1,\'years\')" type="temporal" format="YYYY"][/format])</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@total_unit,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100" format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t2" type="numeric" format=","][/format] ([format expression="DATE_LAST(2,\'years\')" type="temporal" format="YYYY"][/format])</p></div></div>',
                    'pagination': {
                      'limit': 50,
                      'current': 1,
                      'total': null,
                      'type': 'auto',
                      'buttons': {
                        'first': { 'visibility': true, 'label': 'First', 'style': {} },
                        'last': { 'visibility': true, 'label': 'Last', 'style': {} },
                        'prev': { 'visibility': true, 'label': 'Previous', 'style': {} },
                        'next': { 'visibility': true, 'label': 'Next', 'style': {} }
                      },
                      'numbers': { 'beforeCurrent': 2, 'afterCurrent': 2 },
                      'default': 'auto'
                    },
                    'sorting': [],
                    'columns': [],
                    'grouping': { 'columns': [], 'aggregations': [] },
                    'bins': [],
                    'options': {
                      'plugins': ['advlist autolink lists link image preview anchor', 'searchreplace visualblocks code', 'insertdatetime media table paste'],
                      'toolbar': 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | a11ycheck ltr rtl | showcomments addcomment'
                    },
                    'timezone': { 'enabled': true, 'utc': 'America/Danmarkshavn', 'visible': false },
                    'id': '56cad9ba-ce54-4887-827e-aff8b53fbdb8',
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    }
                  }
                }],
                'filter': {
                  'form': { 'config': { 'controls': [], 'query': {} } },
                  'builder': {
                    'enabled': false,
                    'config': {
                      'trigger': { 'label': 'Setting Filter' },
                      'modal': { 'title': 'Query Builder' },
                      'format': { 'temporal': { 'date': 'YYYY-MM-DD', 'datetime': 'YYYY-MM-DD hh:mm' } },
                      'threshold': { 'maxLevel': 5 },
                      'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] },
                      'ignore': {
                        'global': { 'visible': false, 'value': false },
                        'base': { 'visible': false, 'value': false }
                      },
                      'form': { 'columns': [] }
                    },
                    'readable': { 'enabled': false }
                  },
                  'globalFilter': { 'enabled': false },
                  'alignment': '',
                  'base': { 'config': { 'query': {} } }
                },
                'columnManager': {
                  'enabled': false,
                  'config': {
                    'trigger': { 'label': 'Manage Columns' },
                    'modal': { 'title': 'Manage Columns' },
                    'managedColumns': [],
                    'hiddenColumns': []
                  }
                },
                'menu': {
                  'enabled': false,
                  'config': {
                    'label': { 'text': '' },
                    'icons': { 'css': 'fa fa-ellipsis-h' },
                    'dataSource': null,
                    'selection': {
                      'options': [{
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      }, {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      }, {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      }, {
                        'label': 'Data Source',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'type': 'item'
                      }],
                      'dsUrl': ''
                    },
                    'id': 'id-9a29af45-c462-4926-acf4-f1cb03b053b9',
                    'widget': { 'title': { 'enabled': true, 'text': '' }, 'class': '' }
                  }
                },
                'waitingForGlobalFilter': false,
                'id': 'id-7c91c94b-8e33-4ed2-803f-e6ff35088ffe',
                'calculatedColumn': { 'enabled': false }
              }, 'id': 'id-f9af4747-6bcd-4cab-9d1b-8972e1c86fbc', 'key': 'c8c06d29-7a85-4732-9470-6cab0b5c7582'
            },
            {
              'type': 'cbpo-widget', 'config': {
                'grid': {
                  'x': 0,
                  'y': 246,
                  'w': 6,
                  'h': 36,
                  'i': 4,
                  'moved': false,
                  'id': 'id-e6e0ecad-b197-479b-8c53-49c789e19bda'
                },
                'autoHeight': false,
                'widget': {
                  'title': { 'text': '30 Day Sales (Updated Daily)', 'enabled': true, 'edited': true },
                  'style': {
                    'background_color': null,
                    'foreground_color': null,
                    'header_background_color': null,
                    'header_foreground_color': null,
                    'border_width': null,
                    'border_radius': null
                  },
                  'id': 'id-1057d771-9997-4660-8878-341e76187ca7',
                  'class': ''
                },
                'action': { 'elements': [] },
                'elements': [{
                  'type': 'cbpo-element-chart', 'config': {
                    'dataSource': 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Quantitation of [total_unit, fba_unit] over [date]',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [{
                      'name': 'date',
                      'displayName': 'Date',
                      'type': 'date',
                      'format': null,
                      'aggrFormats': null
                    }, {
                      'name': 'total_unit',
                      'displayName': 'TOTAL',
                      'type': 'int',
                      'format': null,
                      'aggrFormats': null
                    }, {
                      'name': 'fba_unit',
                      'displayName': 'INV',
                      'type': 'int',
                      'format': null,
                      'aggrFormats': null
                    }, {
                      'name': 'mfn_unit',
                      'displayName': 'MFN',
                      'type': 'int',
                      'format': null,
                      'aggrFormats': null
                    }],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [{
                      'axis': {
                        'x': [{
                          'id': 'x_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56',
                          'type': 'category',
                          'display': true,
                          'format': null,
                          'scaleLabel': { 'display': false, 'labelString': '' },
                          'ticks': { 'fontSize': 11, 'fontStyle': 'bold' }
                        }],
                        'y': [{
                          'id': 'y_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56',
                          'type': 'linear',
                          'format': null,
                          'position': 'left',
                          'stack': false,
                          'ticks': {
                            'beginAtZero': true,
                            'stepSize': '',
                            'maxTicksLimit': 5,
                            'fontSize': 11,
                            'fontStyle': 'bold'
                          },
                          'scaleLabel': { 'display': false, 'labelString': '' }
                        }]
                      },
                      'options': {
                        'legend': {
                          'enabled': true,
                          'position': 'top',
                          'widthPercent': 40,
                          'isHorizontal': true
                        }, 'stacking': '', 'isHorizontal': false
                      },
                      'series': [{
                        'type': 'bar',
                        'name': 'TOTAL',
                        'axis': {
                          'x': 'x_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56',
                          'y': 'y_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56'
                        },
                        'options': { 'stacking': '', 'isHorizontal': false },
                        'data': { 'x': 'date', 'y': 'total_unit' },
                        'id': 'id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56'
                      }, {
                        'type': 'line',
                        'name': 'INV',
                        'axis': {
                          'x': 'x_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56',
                          'y': 'y_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56'
                        },
                        'options': { 'stacking': '', 'isHorizontal': false, 'step': 'center' },
                        'data': { 'x': 'date', 'y': 'fba_unit' },
                        'id': 'id-5607848f-5905-4320-88ab-a0307b9b7587'
                      }, {
                        'type': 'line',
                        'name': 'MFN',
                        'axis': {
                          'x': 'x_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56',
                          'y': 'y_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56'
                        },
                        'options': { 'stacking': '', 'isHorizontal': false, 'step': 'center' },
                        'data': { 'x': 'date', 'y': 'fba_unit' },
                        'id': 'id-86932a30-453a-45e0-a11c-4d22d3ab74b3'
                      }]
                    }],
                    'sorting': [{ 'column': 'date', 'direction': 'asc' }],
                    'grouping': {
                      'aggregations': [{
                        'column': 'total_unit',
                        'alias': 'total_unit_sum_id-11e55f23-a3c9-4dab-862f-5ba6e40e6f56',
                        'aggregation': 'sum'
                      }, {
                        'column': 'fba_unit',
                        'aggregation': 'sum',
                        'alias': 'fba_unit_sum_id-5607848f-5905-4320-88ab-a0307b9b7587'
                      }, {
                        'column': 'mfn_unit',
                        'aggregation': 'sum',
                        'alias': 'mfn_unit_sum_id-86932a30-453a-45e0-a11c-4d22d3ab74b3'
                      }], 'columns': [{ 'name': 'date' }]
                    },
                    'bins': [],
                    'pagination': { 'limit': 1000, 'current': 1, 'type': 'buttons' },
                    'color_scheme': 'SC_1',
                    'messages': { 'no_data_at_all': 'No data', 'no_data_found': 'No data found' },
                    'timezone': { 'enabled': true, 'utc': 'America/Danmarkshavn', 'visible': false },
                    'id': '536a6f60-595b-41e2-935f-0108bb8b5157',
                    'filter': {
                      'type': 'AND',
                      'conditions': [{
                        'id': 'id-5ae32ba5-dd31-4d51-bf63-6f0976d35509',
                        'level': 1,
                        'column': 'date',
                        'value': ['DATE_LAST(30, "days")', 'TODAY()'],
                        'operator': 'in_range',
                        'parentId': 'id-562205d9-f70e-42cd-bb8c-51195ee9247d'
                      }]
                    },
                    'drillDown': { 'enabled': false, 'config': {} },
                    'formats': { 'aggrs': {} }
                  }
                }],
                'filter': {
                  'form': { 'config': { 'controls': [], 'query': {} } },
                  'base': {
                    'config': {
                      'query': {
                        'id': 'id-562205d9-f70e-42cd-bb8c-51195ee9247d',
                        'level': 0,
                        'type': 'AND',
                        'conditions': [{
                          'id': 'id-5ae32ba5-dd31-4d51-bf63-6f0976d35509',
                          'level': 1,
                          'column': 'date',
                          'value': ['DATE_LAST(30, "days")', 'TODAY()'],
                          'operator': 'in_range',
                          'parentId': 'id-562205d9-f70e-42cd-bb8c-51195ee9247d'
                        }],
                        'parentId': null
                      }
                    }
                  },
                  'builder': {
                    'enabled': false,
                    'config': {
                      'trigger': { 'label': 'Setting Filter' },
                      'modal': { 'title': 'Query Builder' },
                      'format': { 'temporal': { 'date': 'YYYY-MM-DD', 'datetime': 'YYYY-MM-DD hh:mm' } },
                      'threshold': { 'maxLevel': 5 },
                      'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] },
                      'ignore': {
                        'global': { 'visible': false, 'value': false },
                        'base': { 'visible': false, 'value': false }
                      },
                      'form': { 'columns': [] }
                    },
                    'readable': { 'enabled': false }
                  },
                  'globalFilter': { 'enabled': false },
                  'alignment': ''
                },
                'columnManager': {
                  'enabled': false,
                  'config': {
                    'trigger': { 'label': 'Manage Columns' },
                    'modal': { 'title': 'Manage Columns' },
                    'managedColumns': [],
                    'hiddenColumns': []
                  }
                },
                'menu': {
                  'enabled': true,
                  'config': {
                    'label': { 'text': '' },
                    'icons': { 'css': 'fa fa-ellipsis-h' },
                    'dataSource': null,
                    'selection': {
                      'options': [{
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      }, {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      }, {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      }, { 'type': 'divider' }, {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }, {
                        'label': 'Data Source',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'type': 'item'
                      }],
                      'dsUrl': ''
                    },
                    'id': 'id-1c433f6f-e05c-4133-ad68-6571adb7344a',
                    'widget': { 'title': { 'enabled': true, 'text': '' }, 'class': '' }
                  }
                },
                'waitingForGlobalFilter': false,
                'id': 'id-41b8fcb1-fafa-4f0e-a591-9b586d58f06f',
                'calculatedColumn': { 'enabled': false }
              }, 'id': 'id-9a5159cb-dfb6-4ad2-bfbb-265f08d312b5', 'key': '3c0e7778-3329-400c-b85b-8316adb0c4e1'
            },
            {
              'type': 'cbpo-widget', 'config': {
                'grid': {
                  'x': 6,
                  'y': 246,
                  'w': 6,
                  'h': 36,
                  'i': 5,
                  'moved': false,
                  'id': 'id-60aa1e81-1155-4078-a5b2-c63c023dbf50'
                },
                'autoHeight': false,
                'widget': {
                  'title': { 'text': 'Monthly Sales (Updated Monthly)', 'enabled': true, 'edited': true },
                  'style': {
                    'background_color': null,
                    'foreground_color': null,
                    'header_background_color': null,
                    'header_foreground_color': null,
                    'border_width': null,
                    'border_radius': null
                  },
                  'id': 'id-fa30ee60-ddbd-40e2-8bfa-afa21470d111',
                  'class': ''
                },
                'action': { 'elements': [] },
                'elements': [{
                  'type': 'cbpo-element-chart', 'config': {
                    'dataSource': 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e',
                    'widget': {
                      'title': {
                        'enabled': false,
                        'text': 'Quantitation of [total_amount, fba_amount] over [date] per 1 M uniform interval',
                        'edited': false
                      },
                      'style': {
                        'background_color': null,
                        'foreground_color': null,
                        'header_background_color': null,
                        'header_foreground_color': null,
                        'border_width': null,
                        'border_radius': null
                      }
                    },
                    'library': 'highcharts',
                    'columns': [{
                      'name': 'date',
                      'displayName': 'Date',
                      'type': 'date',
                      'format': null,
                      'aggrFormats': null
                    }, {
                      'name': 'total_amount',
                      'displayName': 'TOTAL',
                      'type': 'double',
                      'format': {
                        'common': {
                          'plain': { 'nil': 'NULL', 'empty': 'EMPTY', 'na': 'N/A' },
                          'html': {
                            'nil': '<span class="d-sdk-nil">null</span>',
                            'empty': '<span class="d-sdk-empty">empty</span>',
                            'na': '<span class="d-sdk-na">N/A</span>'
                          },
                          'prefix': null,
                          'suffix': null
                        }, 'type': 'numeric', 'config': { 'comma': true, 'precision': 0, 'siPrefix': false }
                      },
                      'aggrFormats': null
                    }, {
                      'name': 'fba_amount',
                      'displayName': 'INV',
                      'type': 'double',
                      'format': {
                        'common': {
                          'plain': { 'nil': 'NULL', 'empty': 'EMPTY', 'na': 'N/A' },
                          'html': {
                            'nil': '<span class="d-sdk-nil">null</span>',
                            'empty': '<span class="d-sdk-empty">empty</span>',
                            'na': '<span class="d-sdk-na">N/A</span>'
                          },
                          'prefix': null,
                          'suffix': null
                        }, 'type': 'numeric', 'config': { 'comma': true, 'precision': 0, 'siPrefix': false }
                      },
                      'aggrFormats': null
                    }, {
                      'name': 'mfn_amount',
                      'displayName': 'MFN',
                      'type': 'double',
                      'format': {
                        'common': {
                          'plain': { 'nil': 'NULL', 'empty': 'EMPTY', 'na': 'N/A' },
                          'html': {
                            'nil': '<span class="d-sdk-nil">null</span>',
                            'empty': '<span class="d-sdk-empty">empty</span>',
                            'na': '<span class="d-sdk-na">N/A</span>'
                          },
                          'prefix': null,
                          'suffix': null
                        }, 'type': 'numeric', 'config': { 'comma': true, 'precision': 0, 'siPrefix': false }
                      },
                      'aggrFormats': null
                    }],
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    },
                    'charts': [{
                      'axis': {
                        'x': [{
                          'id': 'x_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761',
                          'type': 'category',
                          'display': true,
                          'format': null,
                          'scaleLabel': { 'display': false, 'labelString': '' },
                          'ticks': { 'fontSize': 11, 'fontStyle': 'bold' }
                        }],
                        'y': [{
                          'id': 'y_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761',
                          'type': 'linear',
                          'format': null,
                          'position': 'left',
                          'stack': false,
                          'ticks': {
                            'beginAtZero': true,
                            'stepSize': '',
                            'maxTicksLimit': 5,
                            'fontSize': 11,
                            'fontStyle': 'bold'
                          },
                          'scaleLabel': { 'display': false, 'labelString': '' }
                        }]
                      },
                      'options': {
                        'legend': {
                          'enabled': true,
                          'position': 'top',
                          'widthPercent': 40,
                          'isHorizontal': true
                        }, 'stacking': '', 'isHorizontal': false
                      },
                      'series': [{
                        'type': 'bar',
                        'name': 'TOTAL',
                        'axis': {
                          'x': 'x_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761',
                          'y': 'y_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761'
                        },
                        'data': { 'x': 'date', 'y': 'total_amount' },
                        'id': 'id-ae2c4e17-fab1-4d63-8b30-acbbb8346761'
                      }, {
                        'type': 'line',
                        'name': 'INV',
                        'axis': {
                          'x': 'x_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761',
                          'y': 'y_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761'
                        },
                        'options': { 'stacking': '', 'isHorizontal': false, 'step': 'center' },
                        'data': { 'x': 'date', 'y': 'fba_amount' },
                        'id': 'id-72f3f69c-cbf4-45c9-b9a5-8e18f8c75169'
                      }, {
                        'type': 'line',
                        'name': 'MFN',
                        'axis': {
                          'x': 'x_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761',
                          'y': 'y_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761'
                        },
                        'options': { 'stacking': '', 'isHorizontal': false, 'step': 'center' },
                        'data': { 'x': 'date', 'y': 'mfn_amount' },
                        'id': 'id-a3af514b-4864-4130-94d6-29d1e2da4a13'
                      }]
                    }],
                    'sorting': [{ 'column': 'date_max_id-69013062-ea2c-4db8-bf4a-88cf460f1250', 'direction': 'asc' }],
                    'grouping': {
                      'aggregations': [{
                        'column': 'total_amount',
                        'aggregation': 'sum',
                        'alias': 'total_amount_sum_id-ae2c4e17-fab1-4d63-8b30-acbbb8346761'
                      }, {
                        'column': 'date',
                        'aggregation': 'max',
                        'alias': 'date_max_id-69013062-ea2c-4db8-bf4a-88cf460f1250'
                      }, {
                        'column': 'fba_amount',
                        'aggregation': 'sum',
                        'alias': 'fba_amount_sum_id-72f3f69c-cbf4-45c9-b9a5-8e18f8c75169'
                      }, {
                        'column': 'mfn_amount',
                        'aggregation': 'sum',
                        'alias': 'mfn_amount_sum_id-a3af514b-4864-4130-94d6-29d1e2da4a13'
                      }], 'columns': [{ 'name': 'date_bin' }]
                    },
                    'bins': [{
                      'column': { 'name': 'date', 'type': 'date' },
                      'alias': 'date_bin',
                      'options': { 'alg': 'uniform', 'uniform': { 'width': 1, 'unit': 'M' } }
                    }],
                    'pagination': { 'limit': 1000, 'current': 1, 'type': 'buttons' },
                    'color_scheme': 'SC_1',
                    'messages': { 'no_data_at_all': 'No data', 'no_data_found': 'No data found' },
                    'timezone': { 'enabled': true, 'utc': 'America/Danmarkshavn', 'visible': false },
                    'id': '9dae4d74-f020-48c9-9d29-44b6d7a3b37b',
                    'drillDown': { 'enabled': false, 'config': {} },
                    'formats': { 'aggrs': {} },
                    'filter': {}
                  }
                }],
                'filter': {
                  'form': { 'config': { 'controls': [], 'query': {} } },
                  'builder': {
                    'enabled': false,
                    'config': {
                      'trigger': { 'label': 'Setting Filter' },
                      'modal': { 'title': 'Query Builder' },
                      'format': { 'temporal': { 'date': 'YYYY-MM-DD', 'datetime': 'YYYY-MM-DD hh:mm' } },
                      'threshold': { 'maxLevel': 5 },
                      'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] },
                      'ignore': {
                        'global': { 'visible': false, 'value': false },
                        'base': { 'visible': false, 'value': false }
                      },
                      'form': { 'columns': [] }
                    },
                    'readable': { 'enabled': false }
                  },
                  'globalFilter': { 'enabled': false },
                  'alignment': '',
                  'base': { 'config': { 'query': {} } }
                },
                'columnManager': {
                  'enabled': false,
                  'config': {
                    'trigger': { 'label': 'Manage Columns' },
                    'modal': { 'title': 'Manage Columns' },
                    'managedColumns': [],
                    'hiddenColumns': []
                  }
                },
                'menu': {
                  'enabled': true,
                  'config': {
                    'label': { 'text': '' },
                    'icons': { 'css': 'fa fa-ellipsis-h' },
                    'dataSource': null,
                    'selection': {
                      'options': [{
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      }, {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      }, {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      }, { 'type': 'divider' }, {
                        'label': 'Download CSV',
                        'icon': 'fa fa-download',
                        'value': 'csv',
                        'type': 'item'
                      }, {
                        'label': 'Data Source',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'type': 'item'
                      }],
                      'dsUrl': ''
                    },
                    'id': 'id-3a7879dc-06a8-405c-b778-747dabf1efe7',
                    'widget': { 'title': { 'enabled': true, 'text': '' }, 'class': '' }
                  }
                },
                'waitingForGlobalFilter': false,
                'id': 'id-c0109e05-96e5-4417-91cf-839a8e0c250a',
                'calculatedColumn': { 'enabled': false }
              }, 'id': 'id-6e65e919-0a6a-465e-b450-d16e22a70771', 'key': '6ec2b714-d782-4d0f-933f-f6e08fc6cfd0'
            },
            {
              'type': 'cbpo-widget', 'config': {
                'grid': {
                  'x': 0,
                  'y': 0,
                  'w': 12,
                  'h': 58,
                  'i': 6,
                  'moved': false,
                  'id': 'id-8e7308d4-3a7c-4b07-b3a7-7fad7f176d91'
                },
                'autoHeight': true,
                'widget': {
                  'title': {
                    'text': '[format expression="TODAY()" type="temporal" format="YYYY" ][/format] Sales by Units (Updated Daily)',
                    'enabled': true,
                    'edited': true
                  },
                  'style': {
                    'background_color': null,
                    'foreground_color': null,
                    'header_background_color': null,
                    'header_foreground_color': null,
                    'border_width': null,
                    'border_radius': null
                  },
                  'id': 'id-914f6ce4-04c3-424c-ad18-8e889cda5d2f',
                  'class': ''
                },
                'action': { 'elements': [] },
                'elements': [{
                  'type': 'cbpo-element-html-editor', 'config': {
                    'dataSource': 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e',
                    'builder': { 'visualization': false },
                    'content': '<div style="margin-left: 0px; margin-right: 0px; display: flex; flex-wrap: wrap; justify-content: center; align-items: center"> <div style="min-width: 320px; flex-grow: 1"> <p class="mt-1 text-center"><strong>Inventory Sales YTD</strong></p><p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="320" height="300" current="{SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@fba_unit, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string=",d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18pt; color: #e67e23;">[format expression="SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',\'][/format]</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@fba_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"&nbsp; format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t1" type="numeric" format=","][/format] ([format expression="DATE_LAST(1,\'years\')" type="temporal" format="YYYY"][/format])</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@fba_unit,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100" format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@fba_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t2" type="numeric" format=","][/format] ([format expression="DATE_LAST(2,\'years\')" type="temporal" format="YYYY"][/format])</p></div><div style="min-width: 320px; flex-grow: 1"> <p class="mt-1 text-center"><strong>MFN Sales YTD</strong></p><p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="320" height="300" current="{SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@mfn_unit, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string=",d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18pt; color: #e67e23;">[format expression="SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',\'][/format]</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@mfn_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"&nbsp; format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t1" type="numeric" format=","][/format] ([format expression="DATE_LAST(1,\'years\')" type="temporal" format="YYYY"][/format])</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@mfn_unit,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100" format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@mfn_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t2" type="numeric" format=","][/format] ([format expression="DATE_LAST(2,\'years\')" type="temporal" format="YYYY"][/format])</p></div><div style="min-width: 320px; flex-grow: 1"> <p class="mt-1 text-center"><strong>Total Sales YTD</strong></p><p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="320" height="300" current="{SUMIF(@total_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@total_unit, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@total_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string=",d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18pt; color: #e67e23;">[format expression="SUMIF(@total_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',\'][/format]</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@total_unit,(@date &gt;=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@total_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@total_unit,(@date &gt;=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"&nbsp; format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t1" type="numeric" format=","][/format] ([format expression="DATE_LAST(1,\'years\')" type="temporal" format="YYYY"][/format])</p><p class="text-center" style="font-size: 18pt;">[format expression="(((SUMIF(@total_unit,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100" format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "#e14d58": "value &lt; 0"}\'][/format]</p><p class="text-center">vs [format expression="SUMIF(@total_unit,(@date >=DATE_START_OF(DATE_LAST(2,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(2,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as t2" type="numeric" format=","][/format] ([format expression="DATE_LAST(2,\'years\')" type="temporal" format="YYYY"][/format])</p></div></div>',
                    'pagination': {
                      'limit': 50,
                      'current': 1,
                      'total': null,
                      'type': 'auto',
                      'buttons': {
                        'first': { 'visibility': true, 'label': 'First', 'style': {} },
                        'last': { 'visibility': true, 'label': 'Last', 'style': {} },
                        'prev': { 'visibility': true, 'label': 'Previous', 'style': {} },
                        'next': { 'visibility': true, 'label': 'Next', 'style': {} }
                      },
                      'numbers': { 'beforeCurrent': 2, 'afterCurrent': 2 },
                      'default': 'auto'
                    },
                    'sorting': [],
                    'columns': [],
                    'grouping': { 'columns': [], 'aggregations': [] },
                    'bins': [],
                    'options': {
                      'plugins': ['advlist autolink lists link image preview anchor', 'searchreplace visualblocks code', 'insertdatetime media table paste'],
                      'toolbar': 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | a11ycheck ltr rtl | showcomments addcomment'
                    },
                    'timezone': { 'enabled': true, 'utc': 'America/Danmarkshavn', 'visible': false },
                    'id': '56cad9ba-ce54-4887-827e-aff8b53fbdb8',
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    }
                  }
                }],
                'filter': {
                  'form': { 'config': { 'controls': [], 'query': {} } },
                  'builder': {
                    'enabled': false,
                    'config': {
                      'trigger': { 'label': 'Setting Filter' },
                      'modal': { 'title': 'Query Builder' },
                      'format': { 'temporal': { 'date': 'YYYY-MM-DD', 'datetime': 'YYYY-MM-DD hh:mm' } },
                      'threshold': { 'maxLevel': 5 },
                      'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] },
                      'ignore': {
                        'global': { 'visible': false, 'value': false },
                        'base': { 'visible': false, 'value': false }
                      },
                      'form': { 'columns': [] }
                    },
                    'readable': { 'enabled': false }
                  },
                  'globalFilter': { 'enabled': false },
                  'alignment': '',
                  'base': { 'config': { 'query': {} } }
                },
                'columnManager': {
                  'enabled': false,
                  'config': {
                    'trigger': { 'label': 'Manage Columns' },
                    'modal': { 'title': 'Manage Columns' },
                    'managedColumns': [],
                    'hiddenColumns': []
                  }
                },
                'menu': {
                  'enabled': false,
                  'config': {
                    'label': { 'text': '' },
                    'icons': { 'css': 'fa fa-ellipsis-h' },
                    'dataSource': null,
                    'selection': {
                      'options': [{
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      }, {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      }, {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      }, {
                        'label': 'Data Source',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'type': 'item'
                      }],
                      'dsUrl': ''
                    },
                    'id': 'id-9a29af45-c462-4926-acf4-f1cb03b053b9',
                    'widget': { 'title': { 'enabled': true, 'text': '' }, 'class': '' }
                  }
                },
                'waitingForGlobalFilter': false,
                'id': 'id-7c91c94b-8e33-4ed2-803f-e6ff35088ffe',
                'calculatedColumn': { 'enabled': false }
              }, 'id': 'id-54eda008-cb6e-4f90-9b1d-562f63b651b8', 'key': '579a31e9-bf9e-476e-8593-4c232d61a7df'
            },
            {
              'type': 'cbpo-widget', 'config': {
                'grid': {
                  'x': 0,
                  'y': 121,
                  'w': 12,
                  'h': 49,
                  'i': 7,
                  'moved': false,
                  'id': 'id-b4ab22c1-5017-4394-8eb0-0dfa80eff333'
                },
                'autoHeight': true,
                'widget': {
                  'title': {
                    'text': '[format expression="TODAY()" type="temporal" format="YYYY" ][/format] Sales by Retail $ (Updated Weekly)',
                    'enabled': true,
                    'edited': true
                  },
                  'style': {
                    'background_color': null,
                    'foreground_color': null,
                    'header_background_color': null,
                    'header_foreground_color': null,
                    'border_width': null,
                    'border_radius': null
                  },
                  'id': 'id-a6d7bdd1-94c4-4933-957c-7c086dc71fd2',
                  'class': ''
                },
                'action': { 'elements': [] },
                'elements': [{
                  'type': 'cbpo-element-html-editor', 'config': {
                    'dataSource': 'c00d0693-9cc3-414e-8a51-2c07b0d5f24e',
                    'builder': { 'visualization': false, 'internalChangeAllowed': true },
                    'content': '<div class="row h-100" style="margin-left: 0px; margin-right: 0px;"> <div class="col-lg-6 col-md-12 col-sm-12"> <p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="400" height="300" current="{SUMIF(@total_amount, (@date &lt; TODAY()) &amp; (@date >=DATE_START_OF(TODAY(),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@total_amount, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@total_amount, (@date &lt; DATE_LAST(1,\'years\')) &amp; (@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string="$,d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18px;"><strong>[format expression="SUMIF(@total_amount,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',d\' prefix="$" color=\'{"green": "value >=0", "red": "value &lt; 0"}\'][/format]</strong></p><p class="text-center" style="font-size: 14px;">[format expression="(((SUMIF(@total_amount,(@date >=DATE_START_OF(TODAY(),\'years\')) &amp; (@date &lt; TODAY()), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@total_amount,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@total_amount,(@date >=DATE_START_OF(DATE_LAST(1,\'years\'),\'years\')) &amp; (@date &lt; DATE_LAST(1,\'years\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"  format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "red": "value &lt; 0"}\'][/format]</p><p class="text-center">YTD</p></div><div class="col-lg-6 col-md-12 col-sm-12"> <p class="text-center">[kpi chart-type="radial" class-css="m-auto" width="400" height="300" current="{SUMIF(@total_amount, (@date &lt;=DATE_END_OF(DATE_LAST(1,\'week\'),\'week\')) &amp; (@date >=DATE_START_OF(DATE_LAST(1,\'week\'), \'week\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" min="0" max="{SUMIF(@total_amount, (@date &lt;=DATE_END_OF(DATE_LAST(2,\'week\'),\'week\')) &amp; (@date >=DATE_START_OF(DATE_LAST(2,\'week\'), \'week\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" target="{SUMIF(@total_amount, (@date &lt;=DATE_END_OF(DATE_LAST(2,\'week\'),\'week\')) &amp; (@date >=DATE_START_OF(DATE_LAST(2,\'week\'),\'week\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\')}" format-string="$,d" format-tooltip=",d"][/kpi]</p><p class="text-center" style="font-size: 18px;"><strong>[format expression="SUMIF(@total_amount,(@date >=DATE_START_OF(DATE_LAST(1,\'week\'),\'week\')) &amp; (@date &lt;=DATE_END_OF(DATE_LAST(1,\'week\'),\'week\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as \'current\'" type="numeric" format=\',d\' prefix="$" color=\'{"green": "value >=0", "red": "value &lt; 0"}\'][/format]</strong></p><p class="text-center" style="font-size: 14px;">[format expression="(((SUMIF(@total_amount,(@date >=DATE_START_OF(DATE_LAST(1,\'week\'),\'week\')) &amp; (@date &lt;=DATE_END_OF(DATE_LAST(1,\'week\'),\'week\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c1 - SUMIF(@total_amount,(@date >=DATE_START_OF(DATE_LAST(2,\'week\'),\'week\')) &amp; (@date &lt;=DATE_END_OF(DATE_LAST(2,\'week\'),\'week\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c2)) / SUMIF(@total_amount,(@date >=DATE_START_OF(DATE_LAST(2,\'week\'),\'week\')) &amp; (@date &lt;=DATE_END_OF(DATE_LAST(2,\'week\'),\'week\')), \'c00d0693-9cc3-414e-8a51-2c07b0d5f24e\') as c3) as c4 * 100"  format=\'{"config":{"segmentType":"custom"}, "common":{"suffix":"%"}}\' type="segments" color=\'{"green": "value >=0", "red": "value &lt; 0"}\'][/format]</p><p class="text-center">Weekly Sales ([format expression="DATE_START_OF(DATE_LAST(1,\'week\'), \'week\')" type="temporal" format="MM/DD"][/format]-[format expression="DATE_END_OF(DATE_LAST(1, \'week\'), \'week\')" type="temporal" format="MM/DD"][/format] vs [format expression="DATE_START_OF(DATE_LAST(2, \'week\'), \'week\')" type="temporal" format="MM/DD"][/format]-[format expression="DATE_END_OF(DATE_LAST(2, \'week\'), \'week\')" type="temporal" format="MM/DD"][/format])</p></div></div>',
                    'pagination': {
                      'limit': 50,
                      'current': 1,
                      'total': null,
                      'type': 'auto',
                      'buttons': {
                        'first': { 'visibility': true, 'label': 'First', 'style': {} },
                        'last': { 'visibility': true, 'label': 'Last', 'style': {} },
                        'prev': { 'visibility': true, 'label': 'Previous', 'style': {} },
                        'next': { 'visibility': true, 'label': 'Next', 'style': {} }
                      },
                      'numbers': { 'beforeCurrent': 2, 'afterCurrent': 2 },
                      'default': 'auto'
                    },
                    'sorting': [],
                    'columns': [],
                    'grouping': { 'columns': [], 'aggregations': [] },
                    'bins': [],
                    'options': {
                      'plugins': ['advlist autolink lists link image preview anchor', 'searchreplace visualblocks code', 'insertdatetime media table paste'],
                      'toolbar': 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | a11ycheck ltr rtl | showcomments addcomment'
                    },
                    'timezone': { 'enabled': true, 'utc': 'America/Danmarkshavn', 'visible': false },
                    'id': '12773170-d687-4ea1-9326-fa51a5f4bcc6',
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    }
                  }
                }],
                'filter': {
                  'form': { 'config': { 'controls': [], 'query': {} } },
                  'builder': {
                    'enabled': false,
                    'config': {
                      'trigger': { 'label': 'Setting Filter' },
                      'modal': { 'title': 'Query Builder' },
                      'format': { 'temporal': { 'date': 'YYYY-MM-DD', 'datetime': 'YYYY-MM-DD hh:mm' } },
                      'threshold': { 'maxLevel': 5 },
                      'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] },
                      'ignore': {
                        'global': { 'visible': false, 'value': false },
                        'base': { 'visible': false, 'value': false }
                      },
                      'form': { 'columns': [] }
                    },
                    'readable': { 'enabled': false }
                  },
                  'globalFilter': { 'enabled': false },
                  'alignment': '',
                  'base': { 'config': { 'query': {} } }
                },
                'columnManager': {
                  'enabled': false,
                  'config': {
                    'trigger': { 'label': 'Manage Columns' },
                    'modal': { 'title': 'Manage Columns' },
                    'managedColumns': [],
                    'hiddenColumns': []
                  }
                },
                'menu': {
                  'enabled': false,
                  'config': {
                    'label': { 'text': '' },
                    'icons': { 'css': 'fa fa-ellipsis-h' },
                    'dataSource': null,
                    'selection': {
                      'options': [{
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      }, {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      }, {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      }, {
                        'label': 'Data Source',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'type': 'item'
                      }],
                      'dsUrl': ''
                    },
                    'id': 'id-ac0bab3d-d068-47dd-98e8-78971031a9c4',
                    'widget': { 'title': { 'enabled': true, 'text': '' }, 'class': '' }
                  }
                },
                'waitingForGlobalFilter': false,
                'id': 'id-1d743c49-a09b-4c0c-bf32-9f1c567909e5',
                'calculatedColumn': { 'enabled': false }
              }, 'id': 'id-c1044eb3-0d18-47dc-887c-ca1c39d9c8e3', 'key': 'ad1cd4ef-dcbb-4381-be8b-a4d03ccc1a2d'
            },
            {
              'type': 'cbpo-widget', 'config': {
                'grid': {
                  'x': 0,
                  'y': 170,
                  'w': 12,
                  'h': 37,
                  'i': 8,
                  'moved': false,
                  'id': 'id-30c85be2-be52-4a3b-bce5-f6368655e346'
                },
                'autoHeight': false,
                'widget': {
                  'title': { 'text': 'YTD Goal (Updated Weekly)', 'enabled': true, 'edited': true },
                  'style': {
                    'background_color': null,
                    'foreground_color': null,
                    'header_background_color': null,
                    'header_foreground_color': null,
                    'border_width': null,
                    'border_radius': null
                  },
                  'id': 'id-c3c91bc5-451c-4862-94ab-44bb181784cc',
                  'class': ''
                },
                'action': { 'elements': [] },
                'elements': [{
                  'type': 'cbpo-element-html-editor', 'config': {
                    'dataSource': '7316c006-98d4-47c7-9213-7784cbc7d196',
                    'builder': {},
                    'content': '<p>[kpi chart-type="bar" class-css="m-auto" width="1000" height="150" current="{SUM(@sales, \'7316c006-98d4-47c7-9213-7784cbc7d196\')}" min="0" max="{SUMIF(@sale_goal, LAST_BIN_OF(@year, 1, M), \'c5a5034b-8939-4b8c-b645-176db1c0f552\')}" target="{((SUMIF(@sale_goal, LAST_BIN_OF(@year, 1, M), \'c5a5034b-8939-4b8c-b645-176db1c0f552\')) / DAYS_IN(\'year\') * DATE_OF(\'y\'))}" format-string=",d" format-tooltip=",d" goal-legend="2020 Goal" target-legend="2019 Sales"][/kpi]</p>',
                    'pagination': {
                      'limit': 50,
                      'current': 1,
                      'total': null,
                      'type': 'auto',
                      'buttons': {
                        'first': { 'visibility': true, 'label': 'First', 'style': {} },
                        'last': { 'visibility': true, 'label': 'Last', 'style': {} },
                        'prev': { 'visibility': true, 'label': 'Previous', 'style': {} },
                        'next': { 'visibility': true, 'label': 'Next', 'style': {} }
                      },
                      'numbers': { 'beforeCurrent': 2, 'afterCurrent': 2 },
                      'default': 'auto'
                    },
                    'sorting': [],
                    'columns': [],
                    'grouping': { 'columns': [], 'aggregations': [] },
                    'bins': [],
                    'options': {
                      'plugins': ['advlist autolink lists link image preview anchor', 'searchreplace visualblocks code', 'insertdatetime media table paste'],
                      'toolbar': 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | a11ycheck ltr rtl | showcomments addcomment'
                    },
                    'timezone': { 'enabled': true, 'utc': 'America/Danmarkshavn', 'visible': false },
                    'id': '3ba520bc-cd6e-411b-8fa1-2e444c328c37',
                    'sizeSettings': {
                      'defaultMinSize': 250,
                      'warningText': 'The area is too small for this visualization.'
                    }
                  }
                }],
                'filter': {
                  'form': { 'config': { 'controls': [], 'query': {} } },
                  'builder': {
                    'enabled': false,
                    'readable': { 'enabled': false },
                    'config': {
                      'trigger': { 'label': 'Setting Filter' },
                      'modal': { 'title': 'Query Builder' },
                      'format': { 'temporal': { 'date': 'YYYY-MM-DD', 'datetime': 'YYYY-MM-DD hh:mm' } },
                      'threshold': { 'maxLevel': 5 },
                      'query': { 'id': null, 'level': 0, 'type': 'AND', 'conditions': [] },
                      'ignore': {
                        'global': { 'visible': false, 'value': false },
                        'base': { 'visible': false, 'value': false }
                      },
                      'form': { 'columns': [] }
                    }
                  },
                  'globalFilter': { 'enabled': false },
                  'alignment': '',
                  'base': { 'config': { 'query': {} } }
                },
                'columnManager': {
                  'enabled': false,
                  'config': {
                    'trigger': { 'label': 'Manage Columns' },
                    'modal': { 'title': 'Manage Columns' },
                    'managedColumns': [],
                    'hiddenColumns': []
                  }
                },
                'calculatedColumn': { 'enabled': false },
                'menu': {
                  'enabled': true,
                  'config': {
                    'label': { 'text': '' },
                    'icons': { 'css': 'fa fa-ellipsis-h' },
                    'dataSource': null,
                    'selection': {
                      'options': [{
                        'label': 'Widget Settings',
                        'icon': 'fa fa-cog',
                        'value': 'widget-settings',
                        'type': 'item'
                      }, {
                        'label': 'Element Settings',
                        'icon': 'fa fa-cog',
                        'value': 'element-settings',
                        'type': 'item'
                      }, {
                        'label': 'Remove',
                        'icon': 'fa fa-times',
                        'value': 'remove',
                        'type': 'item'
                      }, {
                        'label': 'Data Source 1',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'type': 'item'
                      }, {
                        'label': 'Data Source 2',
                        'icon': 'fa fa-database',
                        'value': '',
                        'link': true,
                        'optional': true,
                        'type': 'item'
                      }], 'dsUrl': ''
                    },
                    'id': 'id-8369c003-c928-43e2-a2b0-0a97c2b49453',
                    'widget': { 'title': { 'enabled': true, 'text': '' }, 'class': '' }
                  }
                },
                'waitingForGlobalFilter': false,
                'id': 'id-211fcdb7-0fbb-465f-a434-698e720f2401',
                'editMode': true
              }, 'id': 'id-f98fe147-242a-45fc-b94e-cb2f99972e6d', 'key': 'fa9c88e2-f60c-4f36-adca-ed947161d4f4'
            }
          ],
          'layout': [],
          'id': 'id-c78afc62-e1cb-4f7e-a084-9f0c0e0d42de',
          'gridConfig': {
            'colNum': 12,
            'rowHeight': 1,
            'margin': [8, 8],
            'defaultHeight': 50,
            'minHeight': 10,
            'responsive': {
              'enabled': false,
              'breakpoints': { 'lg': 1200, 'md': 996, 'sm': 768, 'xs': 480, 'xxs': 0 },
              'cols': { 'lg': 12, 'md': 10, 'sm': 6, 'xs': 4, 'xxs': 2 }
            }
          }
        },
        'id': 'id-f2f6fc81-ee63-4379-b529-85eb80f88f9e',
        'style': {
          'background_color': null,
          'foreground_color': null,
          'header_background_color': null,
          'header_foreground_color': null,
          'border_width': null,
          'border_radius': null
        },
        'widget': { 'title': { 'enabled': true, 'text': 'Dashboard Builder' } },
        'menu': {
          'enabled': true,
          'config': {
            'label': { 'text': '' },
            'icons': { 'css': 'fa fa-ellipsis-h' },
            'dataSource': null,
            'selection': {
              'options': [{
                'label': 'Dashboard Settings',
                'icon': 'fa fa-cog',
                'value': 'widget-settings',
                'type': 'item'
              }]
            }
          }
        }
      }
    }
  },
  components: {
    'sdk-export-code': sdkExportCodeComponent
  },
  mixins: [configMixins, renderMixins],
  computed: {
    getTemplate() {
      return [
        {
          name: 'Dashboard Container with Visualization',
          tag: this.template,
          config: this.config
        }
      ]
    }
  },
  mounted() {
    this.render('#dashboard-visualization-demo', this.template, 'http://ds-api.qa.channelprecision.com/v1/', '652cce4a-7190-475f-8e4d-d73b02173ab5')
    this.$nextTick(() => {
      window.CBPO.$bus.$emit('CBPO_TOGGLE_BUILDER_MODE', this.isBuilder)
    })
  },
  created() {
    window.config = this.config
  }
})
