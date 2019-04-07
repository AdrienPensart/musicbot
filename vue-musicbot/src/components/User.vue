<template>
    <div id="logout" v-if="token">
        <button class="btn btn-primary" @click.prevent="logout">Logout</button>
        <Music />
    </div>
    <div id="login" v-else>
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
</template>

<script>
import Music from './Music.vue'
import { print } from 'graphql'
import gql from 'graphql-tag'

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
