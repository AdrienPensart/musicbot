import Vue from 'vue'
import Vuex from 'vuex'
import App from './App.vue'
import axios from 'axios'

Vue.use(Vuex)
Vue.config.productionTip = false

const GRAPHQL = `http://${location.hostname}:5000/graphql`


const store = new Vuex.Store({
    state: {
        client: axios.create(
        {
            baseURL: GRAPHQL,
            timeout: 1000,
            headers: {'Content-Type': 'application/json'}
        }),
    },
    mutations: {
        addtoken(state, token) {
            if (token) {
                localStorage.setItem('token', token)
                state.client.defaults.headers['Authorization'] = `Bearer ${token}`
            }
        }
    }
})

new Vue({
  render: h => h(App),
  store,
}).$mount('#app')
