<template>
  <div class="w-100">
    <template v-if="elementData.config.widget && elementData.config.widget.title">
      <b-form-group label="Use data source">
        <div class="row">
          <div v-if="selectedElement.elementType !== ELEMENT.HTML_EDITOR" class="col-4">
            <b-form-checkbox switch v-model="elementData.config.widget.title.enabled">Title</b-form-checkbox>
          </div>
          <div v-if="selectedElement.chartType === TYPES.BAR || selectedElement.chartType === TYPES.PIE || shouldShow([ELEMENT.TABLE, ELEMENT.HEAT_MAP])" class="col-4">
            <b-form-checkbox switch v-model="elementData.config.drillDown.enabled" @change="defaultDrillDown()">Drill Down</b-form-checkbox>
          </div>
        </div>
      </b-form-group>
      <!--Widget Setting-->
      <b-card v-if="elementData.config.widget.title.enabled" no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.widgetTitleCollapse>Widget Title</span>
        </b-card-header>
        <b-collapse id="widgetTitleCollapse">
          <b-card-body>
            <b-form-group
              id="widgetTitle"
              label="Title"
              label-for="widgetTitle">
              <b-form-input type="text" v-model="elementData.config.widget.title.text" @input="changeTitle($event)">
              </b-form-input>
            </b-form-group>
          </b-card-body>
        </b-collapse>
      </b-card>
    </template>
    <!-- Drill down builder -->
    <b-card
      v-if="
        (
          (shouldShow([ELEMENT.CHART]) && [TYPES.PIE, TYPES.BAR].includes(selectedElement.chartType)) ||
          shouldShow([ELEMENT.TABLE]) ||
          shouldShow([ELEMENT.HEAT_MAP])
        ) && elementData.config.drillDown.enabled"
      no-body
      class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.drillDownCollapse>Drill Down Config</span>
      </b-card-header>
      <b-collapse id="drillDownCollapse">
        <b-card-body class="cbpo-form-control">
          <template v-if="!shouldShow([ELEMENT.HEAT_MAP])">
            <b-form-checkbox class="mb-3" switch v-model="elementData.config.drillDown.config.path.enabled">Path</b-form-checkbox>
            <template v-if="elementData.config.drillDown.config.path && elementData.config.drillDown.config.path.enabled && shouldShow([ELEMENT.CHART])">
              <cbpo-drill-down-builder
                :existedColumns="getExistedColumns()"
                :dsId="elementData.config.dataSource"
                :settings.sync="elementData.config.drillDown.config.path.settings">
              </cbpo-drill-down-builder>
            </template>
          </template>
          <template v-else>
            <cbpo-drill-down-builder
              :dsId="elementData.config.dataSource"
              :limit="1"
              :settings.sync="elementData.config.drillDown.path.settings">
            </cbpo-drill-down-builder>
          </template>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!-- End drill down builder -->

    <!--Chart options-->
    <b-card v-if="shouldShow([ELEMENT.HEAT_MAP])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.chartOptionsCollapse>Chart Options</span>
      </b-card-header>
      <b-collapse id="chartOptionsCollapse">
        <b-card-body class="cbpo-form-control">
          <div class="row">
            <div class="col-6">
              <b-form-group label="Label of Dataset">
                <b-form-input
                  :key="index"
                  v-for="(item, index) of elementData.config.charts[0].series"
                  v-model="item.name"
                  type="text" class="mb-2"/>
              </b-form-group>
            </div>
            <div class="col-6">
              <b-form-group label="Text back button (Drilldown only)">
                <b-form-input
                  :key="index"
                  v-for="(item, index) of elementData.config.charts[0].series"
                  v-model="elementData.config.charts[0].options.labelDrillUpButton"
                  type="text" class="mb-2"/>
              </b-form-group>
            </div>
            <div class="col-6">
              <b-form-group label="Color of grid line">
                <color-picker :color="elementData.config.charts[0].options.gridBorderColor" v-model="elementData.config.charts[0].options.gridBorderColor" />
              </b-form-group>
            </div>
            <div class="col-6">
              <b-form-group label="Color of data label">
                <color-picker :color="elementData.config.charts[0].options.dataLabelColor" v-model="elementData.config.charts[0].options.dataLabelColor" />
              </b-form-group>
            </div>
          </div>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End chart options-->

    <!--Chart options-->
    <b-card v-if="shouldShow([ELEMENT.CHART, ELEMENT.GAUGE])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.chartOptionsCollapse>Chart Options</span>
      </b-card-header>
      <b-collapse id="chartOptionsCollapse">
        <b-card-body class="cbpo-form-control">

          <!--Library-->
          <b-form-group v-if="shouldShow([ELEMENT.CHART,  ELEMENT.GAUGE])" label="Library">
            <b-form-select  size="sm" class="mb-2" v-model="elementData.config.library">
              <option :value="CHART_LIBRARY.CHART_JS">Chartjs</option>
              <option :value="CHART_LIBRARY.HIGH_CHART">Highcharts</option>
            </b-form-select>
          </b-form-group>
          <b-form-group v-if="shouldShow([ELEMENT.CHART])" label="Background scheme">
            <b-form-select  size="sm" class="mb-2" v-model="elementData.config.color_scheme">
              <option :value="colorSchemes.D3_10">Color type D3 1</option>
              <option :value="colorSchemes.D3_20">Color type D3 2</option>
              <option :value="colorSchemes.D3_30">Color type D3 3</option>
              <option :value="colorSchemes.Google">Color type Google</option>
              <option v-if="isChartType([TYPES.BAR]) || isChartType([TYPES.PARETO])" :value="colorSchemes.SC_1">Color type gradient 1</option>
            </b-form-select>
          </b-form-group>

          <!--Label-->
          <b-form-group label="Label of Dataset">
            <b-form-input
              :key="index"
              v-for="(item, index) of elementData.config.charts[0].series"
              v-model="item.name"
              type="text" class="mb-2"/>
          </b-form-group>

          <!--Title-->
          <b-form-group v-if="isChartType([TYPES.SOLIDGAUGE])" label="Title">
            <b-form-input
              :key="index"
              v-for="(item, index) of elementData.config.charts[0].series"
              v-model="elementData.config.charts[0].axis.y[index].title"
              type="text" class="mb-2"/>
          </b-form-group>

          <!--Title-->
          <b-form-group v-if="isChartType([TYPES.SOLIDGAUGE])" label="Label Size">
            <b-form-input
              :key="index"
              v-for="(item, index) of elementData.config.charts[0].series"
              v-model="item.options.size"
              type="text" class="mb-2"/>
          </b-form-group>

          <!--Title-->
          <b-form-group v-if="isChartType([TYPES.BULLETGAUGE])" label="Title">
            <b-form-input
              :key="index"
              v-for="(item, index) of elementData.config.charts[0].series"
              v-model="item.options.title"
              type="text" class="mb-2"/>
          </b-form-group>

          <!--Subtitle-->
          <b-form-group v-if="isChartType([TYPES.BULLETGAUGE, TYPES.SOLIDGAUGE])" label="Subtitle">
            <b-form-input
              :key="index"
              v-for="(item, index) of elementData.config.charts[0].series"
              v-model="item.options.subtitle"
              type="text" class="mb-2"/>
          </b-form-group>

          <!--Max-->
          <b-form-group v-if="isChartType([TYPES.SOLIDGAUGE])" label="Max">
            <b-form-input
              :key="index"
              v-for="(item, index) of elementData.config.charts[0].series"
              v-model="elementData.config.charts[0].axis.y[index].max"
              type="text" class="mb-2"/>
          </b-form-group>

          <!--Target-->
          <b-form-group v-if="isChartType([TYPES.BULLETGAUGE])" label="Target">
            <b-form-input
              :key="index"
              v-for="(item, index) of elementData.config.charts[0].series"
              v-model="item.options.target"
              type="number" class="mb-2"/>
          </b-form-group>

          <!-- Border Color -->
          <b-form-group v-if="isChartType([TYPES.BAR])" label="Border Color">
            <ColorPicker :color="elementData.config.charts[0].options.borderColor" v-model="elementData.config.charts[0].options.borderColor" />
          </b-form-group>

          <!--stacking mode-->
          <b-form-group v-if="isChartType([TYPES.BAR, TYPES.AREA])" label="Stacking">
            <b-form-select size="sm" v-model="elementData.config.charts[0].options.stacking">
              <option v-if="isChartType([TYPES.BAR])" value="">None</option>
              <option value="normal">Normal</option>
              <option value="percent">Percentage</option>
            </b-form-select>
          </b-form-group>

          <!-- padding between column -->
          <b-form-group v-if="isChartType([TYPES.BAR, TYPES.LINE])" label="Spacing">
            <b-form-input v-model="elementData.config.charts[0].options.pointPadding" type="number" />
          </b-form-group>

          <!--Border width-->
          <b-form-group v-if="isChartType([TYPES.PIE])" label="Border width">
            <b-form-input type="number" class="mb-2" v-model="elementData.config.charts[0].options.borderWidth"/>
          </b-form-group>

          <!--Doughnut chart-->
          <b-form-group v-if="isChartType([TYPES.PIE])" label="Type">
            <b-form-select size="sm" v-model="elementData.config.charts[0].options.pie.type">
              <option value="pie">Pie</option>
              <option value="doughnut">Doughnut</option>
            </b-form-select>
          </b-form-group>

          <!--Horizontal bar chart-->
          <b-form-group label="Orientation" v-if="isChartType([TYPES.BAR, TYPES.BULLETGAUGE])">
            <b-row>
              <b-col sm="6">
                <b-form-radio
                  v-model="elementData.config.charts[0].options.isHorizontal"
                  name="chart-orientation"
                  :value="false">
                  Vertical
                </b-form-radio>
              </b-col>
              <b-col sm="6">
                <b-form-radio
                  v-model="elementData.config.charts[0].options.isHorizontal"
                  name="chart-orientation"
                  :value="true">
                  Horizontal
                </b-form-radio>
              </b-col>
            </b-row>
          </b-form-group>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Chart options-->

    <!--Table options-->
    <b-card v-if="shouldShow([ELEMENT.TABLE])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.chartOptionsCollapse>Global Control Options</span>
      </b-card-header>
      <b-collapse id="chartOptionsCollapse">
        <b-card-body class="cbpo-form-control">
          <b-form-checkbox switch v-model="elementData.config.globalControlOptions.globalGrouping.enabled">Global Grouping</b-form-checkbox>
          <b-form-checkbox switch v-model="elementData.config.globalControlOptions.editColumn.enabled">Edit Column</b-form-checkbox>
          <b-form-checkbox switch v-model="elementData.config.globalControlOptions.editColumnLabel.enabled">Edit Column Label</b-form-checkbox>
          <b-form-checkbox switch v-model="elementData.config.globalControlOptions.grouping.enabled">Grouping</b-form-checkbox>
          <b-form-checkbox switch v-model="elementData.config.globalControlOptions.aggregation.enabled">Change Aggregation</b-form-checkbox>
          <b-form-checkbox switch v-model="elementData.config.globalControlOptions.editBin.enabled">Edit Bin</b-form-checkbox>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Table options-->

    <!--Legend Options-->
    <b-card v-if="shouldShow([ELEMENT.CHART, ELEMENT.HEAT_MAP])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.legendOptionsCollapse>Legend Options</span>
      </b-card-header>
      <b-collapse id="legendOptionsCollapse">
        <b-card-body class="cbpo-form-control">
          <!--Enable-->
          <b-form-group label="Enable">
            <b-form-checkbox switch v-model="elementData.config.charts[0].options.legend.enabled"/>
          </b-form-group>

          <!--Position-->
          <b-form-group label="Position" v-if="shouldShow([ELEMENT.HEAT_MAP])">
            <b-form-select  size="sm" class="mb-2" v-model="elementData.config.charts[0].options.legend.position">
              <option value="left">Left</option>
              <option value="right">Right</option>
              <option value="center">Center</option>
            </b-form-select>
          </b-form-group>

          <b-form-group label="Position" v-else>
            <b-form-select  size="sm" class="mb-2" v-model="elementData.config.charts[0].options.legend.position">
              <option value="top">Top</option>
              <option value="right">Right</option>
              <option value="bottom">Bottom</option>
              <option value="left">Left</option>
            </b-form-select>
          </b-form-group>

          <!--Width-->
          <b-form-group label="Width" v-if="shouldShow([ELEMENT.CHART])">
            <b-row>
              <b-col class="col-sm-11 col-xs-10">
                <b-form-input class="custom-ranger"
                  v-model="elementData.config.charts[0].options.legend.widthPercent"
                  type="range" step="1" min="30" max="70">
                </b-form-input>
              </b-col>
              <b-col class="col-sm-1 col-xs-2">
                {{ elementData.config.charts[0].options.legend.widthPercent }} %
              </b-col>
            </b-row>
          </b-form-group>

          <!--Orientation-->
          <b-form-group label="Orientation">
            <b-row>
              <b-col sm="6">
                <b-form-radio
                  v-model="elementData.config.charts[0].options.legend.isHorizontal"
                  name="legend-orientation"
                  :value="false">
                  Vertical
                </b-form-radio>
              </b-col>
              <b-col sm="6">
                <b-form-radio
                  v-model="elementData.config.charts[0].options.legend.isHorizontal"
                  name="legend-orientation"
                  :value="true">
                  Horizontal
                </b-form-radio>
              </b-col>
            </b-row>
          </b-form-group>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Legend Options-->

    <!--Map navigator Options-->
    <b-card v-if="shouldShow([ELEMENT.HEAT_MAP])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.mapNavigationOptionsCollapse>Map Navigator</span>
      </b-card-header>
      <b-collapse id="mapNavigationOptionsCollapse">
        <b-card-body class="cbpo-form-control">
          <b-form-checkbox switch v-model="elementData.config.charts[0].options.mapNavigation.enabled">Enabled Navigator</b-form-checkbox>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Legend Options-->

    <!--Plot Bands options-->
    <b-card v-if="isChartType([TYPES.BULLETGAUGE])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.plotBandsOptionsCollapse>Band Options</span>
      </b-card-header>
      <b-collapse id="plotBandsOptionsCollapse">
        <b-card-body
          :key="index"
          v-for="(item, index) of elementData.config.charts[0].series"
          class="cbpo-form-control">
          <!--Label-->
          <b-form-group :label="item.name">
            <b-card no-body class="mb-1">
              <b-card-header header-tag="header" class="p-1" role="tab">
                <span v-b-toggle="`plotBands_${index}`">Options</span>
              </b-card-header>
              <b-collapse :id="`plotBands_${index}`">
                <b-card-body class="cbpo-form-control">
                  <div :key="key" class="card card-padding mb-1" v-for="(item, key) of elementData.config.charts[0].axis.y[index].plotBands">
                    <b-form-group label="From">
                      <b-form-input switch size="sm" class="mb-2" v-model="item.from"/>
                    </b-form-group>
                    <b-form-group label="To">
                      <b-form-input switch size="sm" class="mb-2" v-model="item.to"/>
                    </b-form-group>
                    <b-form-group label="Color">
                      <ColorPicker :color="item.color" v-model="item.color" defaultColor="#000000" />
                    </b-form-group>
                    <div class="d-flex ml-0 control-box justify-content-center">
                      <button
                        :disabled="!(elementData.config.charts[0].axis.y[index].plotBands.length > 3)"
                        @click="deletePlotBands(index, key)"
                        class="cbpo-btn btn-danger btn-icon">
                        <i class="fa fa-times"></i>
                      </button>
                    </div>
                  </div>
                  <div class="control-box mb-2">
                    <button
                      @click="createNewPlotBands(index)"
                      class="cbpo-btn btn-success btn-icon">
                      <i class="fa fa-plus"></i>
                    </button>
                  </div>
                </b-card-body>
              </b-collapse>
            </b-card>
          </b-form-group>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Plot Bands options-->

    <!--Stops options-->
    <b-card v-if="isChartType([TYPES.SOLIDGAUGE])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.stopsOptionsCollapse>Stops Options</span>
      </b-card-header>
      <b-collapse id="stopsOptionsCollapse">
        <b-card-body
          :key="index"
          v-for="(item, index) of elementData.config.charts[0].series"
          class="cbpo-form-control">
          <!--Label-->
          <b-form-group :label="item.name">
            <b-card no-body class="mb-1">
              <b-card-header header-tag="header" class="p-1" role="tab">
                <span v-b-toggle="`plotBands_${index}`">Options</span>
              </b-card-header>
              <b-collapse :id="`plotBands_${index}`">
                <b-card-body class="cbpo-form-control">
                  <div :key="key" class="card card-padding mb-1" v-for="(item, key) of elementData.config.charts[0].axis.y[index].stops">
                    <b-form-group label="Percent">
                      <b-form-input switch size="sm" class="mb-2" v-model="item[0]"/>
                    </b-form-group>
                    <b-form-group label="Color">
                      <ColorPicker :color="item[1]" v-model="item[1]" defaultColor="#000000" />
                    </b-form-group>
                    <div class="d-flex ml-0 control-box justify-content-center">
                      <button
                        :disabled="!(elementData.config.charts[0].axis.y[index].stops.length > 3)"
                        @click="deleteStops(index, key)"
                        class="control-button cbpo-danger icon-only">
                        <i class="fa fa-times"></i>
                      </button>
                    </div>
                  </div>
                  <div class="control-box mb-2">
                    <button
                      @click="createNewStops(index)"
                      class="control-button icon-only">
                      <i class="fa fa-plus"></i>
                    </button>
                  </div>
                </b-card-body>
              </b-collapse>
            </b-card>
          </b-form-group>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Stops options-->

    <!--Global Summary Settings-->
    <b-card v-if="shouldShow([ELEMENT.TABLE])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.globalSummaryOptionsCollapse>Global Summary Settings</span>
      </b-card-header>
      <b-collapse id="globalSummaryOptionsCollapse">
        <b-card-body>
          <b-form-group
            id="enableGlobalSummary"
            class="mb-2"
            label="Enabled"
            label-for="enableGlobalSummary">
            <b-form-checkbox switch v-model="elementData.config.globalSummary.enabled"/>
          </b-form-group>

          <template v-if="elementData.config.globalSummary.enabled">
            <!-- summary builder -->
            <fieldset class="custom-fieldset" :key="index" v-for="(summary, index) of elementData.config.globalSummary.summaries">
              <i class="fa fa-times remove-btn" @click="removeGlobalSummary(index)"></i>
              <legend>Summary {{ summary.label || (index + 1) }}</legend>
              <b-form-group
                :id="`gLabel_${index}`"
                class="mb-2"
                label="Label"
                :label-for="`gLabel_${index}`">
                <b-form-input switch v-model="summary.label"/>
              </b-form-group>
              <b-form-group
                :id="`gExpression_${index}`"
                class="mb-2"
                label="Expression"
                :label-for="`gExpression_${index}`">
                <b-form-input switch v-model="summary.expr"/>
              </b-form-group>
              <b-form-group
                :id="`gPosition_${index}`"
                class="mb-2"
                label="Position"
                :label-for="`gPosition_${index}`">
                <b-form-select v-model="summary.position">
                  <option value="left">Left</option>
                  <option value="right">Right</option>
                </b-form-select>
              </b-form-group>
              <format-config-builder :format-config.sync="summary.format"/>
            </fieldset>

            <!-- add button -->
            <button class="cbpo-btn btn-success mt-2" @click="addGlobalSummary">Add new summary</button>
          </template>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Summary Settings-->

    <!--Table Summary Settings-->
    <b-card v-if="shouldShow([ELEMENT.TABLE])" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.tableSummaryOptionsCollapse>Table Summary Settings</span>
      </b-card-header>
      <b-collapse id="tableSummaryOptionsCollapse">
        <b-card-body>
          <b-form-group
            id="enableTableSummary"
            class="mb-2"
            label="Enabled"
            label-for="enableTableSummary">
            <b-form-checkbox switch v-model="elementData.config.tableSummary.enabled"/>
          </b-form-group>

          <template v-if="elementData.config.tableSummary.enabled">
            <b-form-group
              :id="`tPosition`"
              class="mb-2"
              label="Position"
              :label-for="`tPosition`">
              <b-form-select v-model="elementData.config.tableSummary.position">
                <option value="header">Header</option>
                <option value="footer">Footer</option>
                <option value="both">Both</option>
              </b-form-select>
            </b-form-group>
            <!-- summary builder -->
            <fieldset class="custom-fieldset" :key="index" v-for="(summary, index) of elementData.config.tableSummary.summaries">
              <i class="fa fa-times remove-btn" @click="removeTableSummary(index)"></i>
              <legend>Summary {{ summary.label || (index + 1) }}</legend>
<!--              <b-form-group-->
<!--                :id="`tLabel_${index}`"-->
<!--                class="mb-2"-->
<!--                label="Label"-->
<!--                :label-for="`tLabel_${index}`">-->
<!--                <b-form-input switch v-model="summary.label"/>-->
<!--              </b-form-group>-->
              <b-form-group
                :id="`tExpression_${index}`"
                class="mb-2"
                label="Expression"
                :label-for="`tExpression_${index}`">
                <b-form-input switch v-model="summary.expr"/>
              </b-form-group>
              <b-form-group
                :id="`tColumn_${index}`"
                class="mb-2"
                label="Column"
                :label-for="`tColumn_${index}`">
                <b-form-select v-model="summary.column" :options="columns.data"/>
              </b-form-group>

              <format-config-builder :format-config.sync="summary.format"/>
            </fieldset>
            <!-- add button -->
            <button class="cbpo-btn btn-success mt-2" @click="addTableSummary">Add new summary</button>
          </template>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Table Summary Settings-->

    <!--Timezone Settings-->
    <b-card v-if="hasTimezone" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <span v-b-toggle.timezoneOptionsCollapse>Timezone Settings</span>
      </b-card-header>
      <b-collapse id="timezoneOptionsCollapse">
        <b-card-body>
          <b-form-group
            id="enableTimezone"
            label="Enabled"
            label-for="enableTimezone">
            <b-form-checkbox switch v-model="elementData.config.timezone.enabled"/>
          </b-form-group>
          <template v-if="elementData.config.timezone.enabled">
            <b-form-group
              id="visibleTimezone"
              label="Visible"
              label-for="visibleTimezone">
              <b-form-checkbox switch v-model="elementData.config.timezone.visible"/>
            </b-form-group>
            <b-form-group
              id="visibleTimezone"
              label="Visible"
              label-for="visibleTimezone">
              <b-form-select v-model="elementData.config.timezone.utc"
                             :options="timezoneData"/>
            </b-form-group>
          </template>
        </b-card-body>
      </b-collapse>
    </b-card>
    <!--End Timezone Settings-->

    <!--HTML Editor only-->
    <!--<div v-if="shouldShow([ELEMENT.HTML_EDITOR])">
      <b-form-group label="Enable Editor">
        <b-form-checkbox switch v-model="elementData.config.builder.enabled">
        </b-form-checkbox>
      </b-form-group>

      <editor
        v-if="show"
        :api-key="apiKey"
        :init="{
           menubar: true,
           plugins: options.plugins,
           toolbar: options.toolbar
        }"
        :initial-value="elementData.config.content"
        v-model="elementData.config.content"
      />
    </div> -->
    <!--END HTML Editor-->

    <!--GLOBAL FILTER only-->
    <div v-if="shouldShow([ELEMENT.GLOBAL_FILTER])">
      <b-form-group label="Alignment ">
        <b-form-select  size="sm" class="mb-2" v-model="alignment">
          <option value="">Left</option>
          <option value="center">Center</option>
          <option value="right">Right</option>
        </b-form-select>
      </b-form-group>
    </div>
    <!--GLOBAL FILTER Editor-->

    <!--Pagination Config-->
    <b-card no-body class="mb-1">
        <b-card-header header-tag="header" class="p-1" role="tab">
          <span v-b-toggle.formatTypeCollapse>Pagination Options</span>
        </b-card-header>
        <b-collapse id="formatTypeCollapse">
          <b-card-body class="cbpo-form-control">
            <b-form-group v-if="shouldShow([ELEMENT.TABLE, ELEMENT.CROSSTAB_TABLE])" label="Type">
              <b-form-select size="sm" v-model="elementData.config.pagination.type">
                <option :key="type" v-for="type in paginationTypes" :value="type">{{type}}</option>
              </b-form-select>
            </b-form-group>
            <div class="row">
              <div class="col-md-6 col-12">
                <b-form-group label="Limit">
                  <b-form-input type="text" v-model="elementData.config.pagination.limit">
                  </b-form-input>
                </b-form-group>
              </div>
              <div class="col-md-6 col-12" v-if="shouldShow([ELEMENT.TABLE, ELEMENT.CROSSTAB_TABLE])">
                <b-form-group label="Current">
                  <b-form-input type="text" pattern="[0-9]" min="1" step="1" v-model="elementData.config.pagination.current">
                  </b-form-input>
                </b-form-group>
              </div>
            </div>
          </b-card-body>
        </b-collapse>
    </b-card>
    <!--End Pagination Config-->
  </div>
</template>
<script>
import { cloneDeep, isEmpty, get, startCase } from 'lodash'
import { ELEMENT, PAGINATION_TYPES, CHART_LIBRARY } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { TYPES, colorSchemes } from '@/components/widgets/elements/chart/ChartConfig'
import { defaultHtmlEditorConfig } from '@/components/widgets/elements/htmlEditor/HtmlEditorConfig'
import { makeDefaultDrillDownConfig } from '@/components/widgets/drillDown/DrillDownConfig'
import DrillDownPathBuilder from '@/components/widgets/drillDown/DrillDownPathBuilder'
import ColorPicker from '@/components/colorPicker/ColorPicker'
import FormatConfigBuilder from '@/components/formatBuilder/FormatConfigBuilder'
import CBPO from '@/services/CBPO'

export default {
  name: 'ElementSettings',
  data() {
    const timezoneData = (require('../elements/timezone-selector/timezoneData') || [])
      .map(timezone => ({text: timezone.text, value: timezone.utc[0]}))
    return {
      ELEMENT,
      TYPES,
      colorSchemes,
      CHART_LIBRARY,
      elementData: null,
      paginationTypes: [],
      options: cloneDeep(defaultHtmlEditorConfig).options,
      show: false,
      apiKey: '',
      alignment: '',
      timezoneData: [{text: 'Select a timezone', value: null}, ...timezoneData],
      columns: {
        data: [],
        isLoading: false
      }
    }
  },
  components: {
    FormatConfigBuilder,
    ColorPicker,
    'cbpo-drill-down-builder': DrillDownPathBuilder
  },
  methods: {
    getConfig() {
      return cloneDeep(this.elementData)
    },
    getExistedColumns() {
      const clone = cloneDeep(this.element.config.charts[0].series)
      const existedColumn = clone.reduce((prev, cur) => prev.concat(Object.values(cur.data)), [])
      return [...new Set(existedColumn)]
    },
    getFilterAlignment() {
      return cloneDeep(this.alignment)
    },
    createPaginationTypes() {
      this.paginationTypes = Object.keys(PAGINATION_TYPES).map(name => PAGINATION_TYPES[name])
    },
    createNewPlotBands(index) {
      this.elementData.config.charts[0].axis.y[index].plotBands.push({from: '', to: '', color: ''})
    },
    deletePlotBands(index, key) {
      this.elementData.config.charts[0].axis.y[index].plotBands.splice(key, 1)
    },
    createNewStops(index) {
      this.elementData.config.charts[0].axis.y[index].stops.push([])
    },
    deleteStops(index, key) {
      this.elementData.config.charts[0].axis.y[index].stops.splice(key, 1)
    },
    defaultDrillDown() {
      let current = this.elementData.config.drillDown.enabled
      if (!current && isEmpty(this.elementData.config.drillDown.config)) {
        this.elementData.config.drillDown.config = Object.assign({}, cloneDeep(makeDefaultDrillDownConfig(this.elementData.config.drillDown.config)))
      }
    },
    async fetchColumns(dataSource) {
      try {
        this.columns.isLoading = true
        const columns = await CBPO
          .dsManager()
          .getDataSource(dataSource)
          .columns()

        this.columns.data = [
          { text: 'Select a column', value: '' },
          ...columns.map(column => {
            return { text: column.name, value: (column.label || startCase(column.name)) }
          })
        ]
      } catch (e) {
        console.log(e)
        this.columns.data = []
      } finally {
        this.columns.isLoading = false
      }
    },
    changeTitle (data) {
      if (data) this.elementData.config.widget.title.edited = true
    },
    addGlobalSummary() {
      this.elementData.config.globalSummary.summaries.push({
        label: '', // label of summary info
        position: 'left', // left or right
        format: null,
        expr: ''
      })
    },
    removeGlobalSummary(index) {
      this.elementData.config.globalSummary.summaries.splice(index, 1)
    },
    addTableSummary() {
      this.elementData.config.tableSummary.summaries.push({
        label: '', // label of summary info
        position: 'header', // header or footer or both
        format: null,
        expr: '',
        style: {}
      })
    },
    removeTableSummary(index) {
      this.elementData.config.tableSummary.summaries.splice(index, 1)
    }
  },
  props: {
    element: Object,
    selectedElement: Object,
    filterAlignment: String
  },
  created() {
    this.apiKey = get(window, 'API_KEY_EDITOR') || process.env.VUE_APP_API_KEY_EDITOR
    this.show = true
    if (this.elementData.type !== ELEMENT.HTML_EDITOR) {
      this.createPaginationTypes()
    }
    if (this.filterAlignment) {
      this.alignment = this.filterAlignment
    }
  },
  beforeDestroy() {
    this.show = false
  },
  computed: {
    shouldShow() {
      return (arrayTypes) => {
        if (!this.elementData) {
          return false
        }
        return arrayTypes.includes(this.elementData.type)
      }
    },
    isChartType() {
      return (chartTypes) => {
        return chartTypes.includes(this.selectedElement.chartType)
      }
    },
    hasTimezone() {
      return !!this.elementData.config.timezone
    }
  },
  watch: {
    element: {
      deep: true,
      immediate: true,
      handler: function(val) {
        this.elementData = cloneDeep(val)

        if (val.config.dataSource) this.fetchColumns(val.config.dataSource)
      }
    },
    'elementData.config.pagination.limit'(val) {
      if (isEmpty(val)) {
        return
      }
      this.elementData.config.pagination.limit = parseInt(val)
    },
    'elementData.config.pagination.current'(val) {
      if (isEmpty(val)) {
        return
      }
      this.elementData.config.pagination.current = parseInt(val)
    }
  }
}
</script>
<style scoped lang="scss">
  .cbpo-editor /deep/ .ql-editor {
    max-height: 400px;
  }
  .card-padding {
  padding: 0.5rem;
  }
  .option-label {
    line-height: 30px;
  }
  .custom-ranger {
    &::after {
      content: '70';
      position: absolute;
      bottom: -10px;
      right: 15px;
    }
    &::before {
      content: '30';
      position: absolute;
      bottom: -10px;
    }
  }
  .custom-fieldset {
    padding: .5rem;
    position: relative;
    legend {
      padding: 0 .5rem;
      width: auto;
      font-size: 0.9rem;
      font-weight: bold;
    }
    .remove-btn {
      cursor: pointer;
      color: red;
      position: absolute;
      right: 9px;
      top: 15px;
    }
  }
</style>
