<template>
  <v-list id="playlist">
    <template v-for="music in musics">
      <v-list-tile :key="music.id">
        <v-list-tile-content @click="play(music.path)" class="queue_entry">
          {{ music.folder }} - {{ music.artist }} - {{ music.album }} - {{ music.title }} - {{ music.path }}
        </v-list-tile-content>
      </v-list-tile>
    </template>
  </v-list>
</template>
<style>

#playlist .v-list__tile {
  height: 24px;
}

#playlist .v-list__tile__content {
  height: 24px;
}

.queue_entry {
  font-size: 0.8em;
  cursor: pointer;
}

.queue_entry:hover {
}

.queue_active_entry {
  color:#000000;
  text-decoration:none;
}
</style>
<script>
import gql from 'graphql-tag'
import { print } from 'graphql'

const MUSIC_QUERY = gql`
{
  allRawMusicsList(first: 10) {
    artist
    album
    title
    path
    folder
  }
}
`
export default {
  components: {
  },
  methods: {
    init() {
      this.axios.post(this.graphql, {
        query: print(MUSIC_QUERY),
      }).then((result) => {
        this.musics = result.data.data.allRawMusicsList
      }).catch((err) => {
        window.console.log(err)
        this.musics = []
      })
    },
    play(music) {
      alert(music)
    }
  },
  data() {
    return {
      musics: [],
    };
  },
  mounted() {
    this.init()
  },
}
</script>
