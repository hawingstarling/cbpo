// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './assets/css/main.scss'
import './assets/css/base/jquery-ui.scss'
import './assets/icons/css/font-awesome.min.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import $ from 'jquery'

import { extend } from 'vee-validate'
import { required } from 'vee-validate/dist/rules'
import Vue from 'vue'
import CBPO from '@/services/CBPO'
import BootstrapVue from 'bootstrap-vue'
import VueSelect from 'vue-select'
import VModal from 'vue-js-modal'
import Toasted from 'vue-toasted'

extend('required', {
  ...required,
  message: 'This field is required'
})

Vue.config.productionTip = false

Vue.use(BootstrapVue)
Vue.use(VModal)
Vue.component('v-select', VueSelect)
Vue.use(Toasted)

if ($('#cbpo-root').length) {
  console.log('CBPO SDK auto init on #cbpo-root')
  CBPO.wgManager().init('#cbpo-root') // must run after instantiation of CBPO
}
