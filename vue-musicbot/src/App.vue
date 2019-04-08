<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>MusicBot</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <div v-if="token">
          <v-btn small color="info" @click.prevent="logout">Logout</v-btn>
      </div>
      <div v-else>
          <input id="email" required name="email" v-model.lazy="email" type="email" placeholder="Your email" size="25">
          <input id="password" required name="password" v-model.lazy="password" type="password" placeholder="Your password" size="25">
          <v-btn small color="success" @click.prevent="login">Login</v-btn>
      </div>
    </v-toolbar>
    <v-content>
      <p v-if="errors.length">
          <b>Please correct the following error(s):</b>
          <ul>
              <li v-for="error in errors" :key="error.id">{{ error }}</li>
          </ul>
      </p>
      <Music v-if="token"/>
    </v-content>
  </v-app>
</template>

<script>
import { print } from 'graphql'
import gql from 'graphql-tag'
import Music from './components/Music.vue'

const AUTH_MUTATION = gql`
    mutation Authentication($email:String!, $password:String!) {
        authenticate(input: {email:$email, password:$password}) {
            clientMutationId
            jwtToken
        }
    }
`

export default {
    name: 'App',
    components: {
        Music,
    },
    data() {
        return {
            errors: [],
            email: '',
            password: '',
            token: '',
        }
    },
    mounted() {
        if (localStorage.getItem('token')) {
            this.token = localStorage.getItem('token');
        }
    },
    watch: {
        token(newToken) {
            if (newToken) {
                localStorage.setItem('token', newToken)
                this.axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
            } else {
                delete this.axios.defaults.headers.common['Authorization']
                localStorage.clear()
            }
        }
    },
    methods: {
        logout() {
            this.token = null;
        },
        login(e) {
            if (!this.email || !this.password) {
                this.errors = []
                if (!this.email) {
                    this.errors.push('Email required.')
                }
                if (!this.password) {
                    this.errors.push('Password required.')
                }
                e.preventDefault()
                return
            }
            this.axios.post(this.graphql, {
                query: print(AUTH_MUTATION),
                variables: {
                    email: this.email,
                    password: this.password
                }
            }).then((result) => {
                var tempToken = result.data.data.authenticate.jwtToken
                if (tempToken) {
                    this.token = tempToken
                    this.errors = []
                } else {
                    this.errors.push('Authentication failed')
                }
            }).catch((err) => {
                this.errors = []
                this.token = null
                this.errors.push(err)
            })
        },
    },
}
</script>
