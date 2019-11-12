<template>
  <splitpanes watch-slots vertical class="default-theme">
    <span splitpanes-default="20">
      <v-treeview :items="artists" activatable hoverable></v-treeview>
    </span>
    <span splitpanes-default="15">
      <v-treeview :items="genres" activatable hoverable></v-treeview>
      <v-treeview :items="keywords" activatable hoverable></v-treeview>
    </span>
  </splitpanes>
</template>
<style>
.splitpanes__pane {
    overflow: scroll;
}
.splitpanes--vertical > .splitpanes__splitter {
  min-width: 6px;
  background: linear-gradient(90deg, #ccc, #111);
}
</style>
<script>
import gql from 'graphql-tag'
import { print } from 'graphql'
import splitpanes from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

const MUSIC_QUERY = gql`
{
  keywordsTreeList {
    name
  }
  genresTreeList {
    name
  }
  allFiltersList {
    name
  }
  artistsTreeList {
    id
    name
    children: albums {
      id
      name
      children: musics {
        id
        name
        folder
        path
      }
    }
  }
  allRawMusicsList(first: 10) {
    artist
    album
    title
    path
  }
}
`
export default {
  components: {
    splitpanes,
  },
  methods: {
    init() {
      this.axios.post(this.graphql, {
        query: print(MUSIC_QUERY),
      }).then((result) => {
        this.artists = result.data.data.artistsTreeList
        this.keywords = result.data.data.keywordsTreeList
        this.genres = result.data.data.genresTreeList
        this.filters = result.data.data.allFiltersList
      }).catch((err) => {
        console.log(err)
        this.artists = []
        this.keywords = []
        this.genres = []
        this.filters = []
      })
    }
  },
  data() {
    return {
      artists: [],
      keywords: [],
      genres: [],
      filters: [],
    };
  },
  mounted() {
    this.init()
  },
}
</script>
