import Chart from '@/components/widgets/elements/chart/Chart'
import HeatMap from '@/components/widgets/elements/heat-map/HeatMap'
import Table from '@/components/widgets/elements/table/Table'
import BulletGauge from '@/components/widgets/elements/gauge/Gauge'
import HtmlEditor from '@/components/widgets/elements/htmlEditor/HtmlEditor'
import Widget from '@/components/widgets/Widget'
import Layout from '@/components/widgetLayout/WidgetLayout'
import Dashboard from '@/components/dashboard/Dashboard'
import VisualizationWrapper from '@/components/visualizationBuilder/VisualizationBuilder'
import WidgetContainer from '@/components/widgetsContainer/WidgetContainer'
import DropLayoutContainer from '@/components/dropLayoutContainer/DropLayoutContainer'
import CrosstabTable from '@/components/widgets/elements/crosstab-table/CrosstabTable'
import ReadableFilter from '@/components/widgets/builder/ReadableFilter'
import BuilderFilter from '@/components/widgets/builder/BuilderFilter'
import ManageColumns from '@/components/widgets/columns/ManageColumns'
import MultipleExport from '@/components/widgets/exports/MultipleExport'
import CompactMode from '@/components/widgets/elements/table/compact-mode/CompactMode'
import VueSelect from 'vue-select'
import WidgetLoader from '@/components/widgets/loader/WidgetLoader'
import CrosstabChart from '@/components/widgets/elements/crosstab-chart/CrosstabChart'
import FilterForm from '@/components/widgets/form/FilterForm'
import WidgetMenuControl from '@/components/widgets/menu/MenuControlSelect'
import ComparableTable from '@/components/widgets/elements/comparable-table/ComparableTable'
import LazyLoad from '@/components/common/LazyLoad'
import ManageWidgets from '@/components/widgets/setting/ManageWidgets'

const components = {
  'cbpo-element-table': Table,
  'cbpo-element-chart': Chart,
  'cbpo-element-crosstab-chart': CrosstabChart,
  'cbpo-element-html-editor': HtmlEditor,
  'cbpo-element-crosstab-table': CrosstabTable,
  'cbpo-element-heat-map': HeatMap,
  'cbpo-element-comparable-table': ComparableTable,
  'cbpo-widget': Widget,
  'cbpo-layout': Layout,
  'cbpo-dashboard': Dashboard,
  'cbpo-visualization': VisualizationWrapper,
  'cbpo-widget-container': WidgetContainer,
  'cbpo-drop-layout-container': DropLayoutContainer,
  'cbpo-element-gauge': BulletGauge,
  'cbpo-readable-builder-filter': ReadableFilter,
  'cbpo-builder-filter': BuilderFilter,
  'cbpo-manage-columns': ManageColumns,
  'cbpo-compact-mode': CompactMode,
  'v-select': VueSelect,
  'cbpo-widget-loader': WidgetLoader,
  'cbpo-filter-form': FilterForm,
  'cbpo-multiple-export': MultipleExport,
  'cbpo-widget-menu-control': WidgetMenuControl,
  'cbpo-lazy-load': LazyLoad,
  'cbpo-manage-widgets': ManageWidgets
}

export default components
