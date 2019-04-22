import Vuex from 'vuex'
import Vue from 'vue'
import axios from 'axios'
import { print } from 'graphql'
import gql from 'graphql-tag'

Vue.use(Vuex)

const AUTH_MUTATION = gql`
mutation Authentication($email:String!, $password:String!) {
  authenticate(input: {email:$email, password:$password}) {
    jwtToken
  }
}
`

export default new Vuex.Store({
  state: {
    token: localStorage.getItem('token') || '',
    status: '',
    errors: [],
    musics: [],
  },
  mutations: {
    auth_request(state){
      state.status = 'loading'
    },
    auth_success(state, token, user){
      state.status = 'success'
      state.token = token
      state.user = user
      state.errors = []
    },
    graphql_error(state, errors){
      errors.forEach((error) => {
        state.errors.push(error.message)
      })
    },
    auth_error(state, errors){
      state.status = 'error'
      state.errors = errors
    },
    logout(state){
      state.status = ''
      state.token = ''
      state.errors = []
    },
  },
  actions: {
    login({commit}, {email, password}){
      commit('auth_request')
      axios.post(this.graphql, {
        query: print(AUTH_MUTATION),
        variables: {
            email: email,
            password: password
        }
      })
      .then((resp) => {
        console.log(resp.data.errors)
        if ( resp.errors ) {
          commit('graphql_error', resp.errors)
          return
        }
        if ( resp.data.errors ) {
          commit('graphql_error', resp.data.errors)
          return
        }
        const token = resp.data.data.authenticate.jwtToken
        localStorage.setItem('token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        commit('auth_success', token)
      }).catch(err => {
          commit('auth_error', err)
          localStorage.removeItem('token')
          delete axios.defaults.headers.common['Authorization']
      })
    },
    logout({commit}){
      return new Promise((resolve) => {
        commit('logout')
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        resolve()
      })
    }
  },
  getters: {
    isLoggedIn: state => !!state.token,
    authStatus: state => state.status,
    errors: state => state.errors,
  }
})
