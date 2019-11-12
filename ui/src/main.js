import Vue from 'vue'
import VueAxios from 'vue-axios'
import Vuetify from 'vuetify/lib'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import store from './store'
import 'vuetify/src/stylus/app.styl'

Vue.config.productionTip = false

Vue.use(Vuetify, {iconfont: 'md',})
Vue.use(VueAxios, axios)

axios.defaults.baseURL = `http://${location.hostname}:5000/graphql`;
axios.defaults.timeout = 2000;
axios.defaults.headers.common['Content-Type'] = 'application/json';
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
