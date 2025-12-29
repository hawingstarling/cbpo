import Vue from 'vue'
import Router from 'vue-router'
import routes from './routes'

Vue.use(Router)

const router = new Router({
  routes
})

router.beforeEach(async (to, from, next) => {
  // get nearest title
  const nearestWithTitle = to.matched.slice().reverse().find(r => r.meta && r.meta.title)
  // update title to document.title
  if (nearestWithTitle) document.title = nearestWithTitle.meta.title
  return next()
})

export default router
