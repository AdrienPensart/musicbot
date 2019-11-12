<template>
  <div>
    <div v-if="isLoggedIn">
        <v-btn small color="info" @click.prevent="logout">Logout</v-btn>
    </div>
  </div>
</template>
<script>
export default {
  computed : {
    isLoggedIn: function(){ return this.$store.getters.isLoggedIn }
  },
  methods: {
    logout() {
      this.$store.dispatch('logout')
    },
  },
}
</script>
