<template>
  <div>
    <div v-if="notLoggedIn">
        <input id="email" required name="email" v-model.lazy="email" type="email" placeholder="Your email" size="25">
        <input id="password" required name="password" v-model.lazy="password" type="password" placeholder="Your password" size="25">
        <v-btn small color="success" @click.prevent="login">Login</v-btn>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      email: '',
      password: '',
    }
  },
  computed : {
    notLoggedIn: function(){ return !this.$store.getters.isLoggedIn }
  },
  methods: {
    login() {
      let email = this.email
      let password = this.password
      this.$store.dispatch('login', { email, password })
    },
  },
}
</script>
