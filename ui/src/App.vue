<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline">
        MusicBot
      </v-toolbar-title>
      <v-toolbar-items class="hidden-sm-and-down">
        <v-btn href="https://github.com/AdrienPensart/musicbot" target="_blank" flat>GitHub</v-btn>
        <v-btn href="http://127.0.0.1:5000/graphiql" target="_blank" flat>GraphiQL</v-btn>
      </v-toolbar-items>
      <v-spacer></v-spacer>
      <Player v-if='isLoggedIn' />
      <Login  v-if='notLoggedIn' />
      <Logout v-if='isLoggedIn' />
    </v-toolbar>
    <v-content>
      <Errors />
      <splitpanes v-if='isLoggedIn' watch-slots vertical class="default-theme">
        <span splitpanes-default="5">
          <Queue />
        </span>
        <Music />
      </splitpanes>
    </v-content>
  </v-app>
</template>
<script>
import Music from './components/Music.vue'
import Login from './components/Login.vue'
import Logout from './components/Logout.vue'
import Errors from './components/Errors.vue'
import Queue from './components/Queue.vue'
import Player from './components/Player.vue'
import splitpanes from 'splitpanes'

export default {
  name: 'App',
  components: {
    splitpanes,
    Login,
    Logout,
    Errors,
    Music,
    Queue,
    Player,
  },
  computed : {
    notLoggedIn: function(){ return !this.$store.getters.isLoggedIn },
    isLoggedIn: function(){ return this.$store.getters.isLoggedIn },
  },
}
</script>
