import Vue from 'vue'
import Vuex from 'vuex'
import VueAxios from 'vue-axios'
import Vuetify from 'vuetify/lib'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import 'vuetify/src/stylus/app.styl'

Vue.config.productionTip = false

Vue.use(Vuetify, {iconfont: 'md',})
Vue.use(Vuex)
Vue.use(VueAxios, axios)

axios.defaults.baseURL = `http://${location.hostname}:5000/graphql`;
axios.defaults.timeout = 2000;
axios.defaults.headers.common['Content-Type'] = 'application/json';

var store = new Vuex.Store({
  state: {
  },
  mutations: {
  },
  actions: {
  },
  getters: {
  }
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
