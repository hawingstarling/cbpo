import getters from './_getters'
import mutations from './_mutations'
import actions from './_actions'
import analysis from './analysis'
import bulk from './bulk'
import share from './share'
import activities from './activities'
import tools from './tools'
import items from './items'
import brands from './brands'
import tags from './tags'
import settings from './settings'
import fedex from './fedex'
import overview from './overview'
import advertising from './advertising'
import appEagleProfile from './app-eagle-profile'
import reports from './reports'
import compareTable from './compare-table'
import saleWidget from './sale-widget'
import manageWidgetDashboard from './manage-widget-dashboard'
import topAsins from './top-asins'
import cogsConflicts from './cogs-conflicts'

export default {
  pf: {
    namespaced: true,
    modules: {
      analysis,
      share,
      activities,
      bulk,
      tools,
      items,
      brands,
      tags,
      settings,
      fedex,
      overview,
      advertising,
      appEagleProfile,
      reports,
      compareTable,
      saleWidget,
      manageWidgetDashboard,
      topAsins,
      cogsConflicts
    },
    state: {
      permissions: {}
    },
    getters,
    mutations,
    actions
  }
}
