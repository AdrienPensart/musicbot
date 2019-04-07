import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import VueAxios from 'vue-axios'

Vue.use(Vuex)
Vue.use(VueAxios, axios)

axios.defaults.baseURL = `http://${location.hostname}:5000/graphql`;
axios.defaults.timeout = 2000;
axios.defaults.headers.common['Content-Type'] = 'application/json';

export default new Vuex.Store({
  state: {
  },
  mutations: {
  },
  actions: {
  },
  getters: {
  }
})
