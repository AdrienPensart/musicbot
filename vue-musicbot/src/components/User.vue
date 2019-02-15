<template>
    <div id="login" v-if="!token">
        <p v-if="errors.length">
            <b>Please correct the following error(s):</b>
            <ul>
                <li v-for="error in errors" :key="error.id">{{ error }}</li>
            </ul>
        </p>
        <input id="email" required name="email" v-model.lazy="email" type="email" placeholder="Your email" size="25">
        <input id="password" required name="password" v-model.lazy="password" type="password" placeholder="Your password" size="25">
        <button class="btn btn-primary" @click.prevent="login">Login</button>
    </div>
    <div v-else>
        <Artists :client="client" />
        <button class="btn btn-primary" @click.prevent="logout">Logout</button>
    </div>
</template>

<script>
import { print } from 'graphql'
import gql from 'graphql-tag'

import Artists from './Artists.vue'

const AUTH_MUTATION = gql`
    mutation Authentication($email:String!, $password:String!) {
        authenticate(input: {email:$email, password:$password}) {
            clientMutationId
            jwtToken
        }
    }
`

export default {
    components: {
        Artists,
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
            this.token = localStorage.getItem('token')
        }
    },
    watch: {
        token(newToken) {
            if (newToken) {
                localStorage.setItem('token', newToken)
                this.client.defaults.headers['Authorization'] = `Bearer ${newToken}`
            }
        }
    },
    methods: {
        logout() {
            this.token = null
            delete this.client.defaults.headers['Authorization']
            localStorage.clear()
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
            this.client.post(this.graphql, {
                query: print(AUTH_MUTATION),
                variables: {
                    email: this.email,
                    password: this.password
                }
            }).then((result) => {
                this.token = result.data.data.authenticate.jwtToken
                if (this.token) {
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
