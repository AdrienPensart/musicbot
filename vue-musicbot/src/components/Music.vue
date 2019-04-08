<template>
    <div>
        <p v-if="errors.length">
            <b>Please correct the following error(s):</b>
            <ul>
                <li v-for="error in errors" :key="error.id">{{ error }}</li>
            </ul>
        </p>
        <splitpanes watch-slots horizontal class="default-theme" :push-other-panes="false">
            <span v-if="queue.length" style="height:500px">
            </span>
            <span v-else>
                Empty queue
            </span>
            <span>
                <splitpanes watch-slots vertical style="height:500px">
                    <span v-if="filters.length" splitpanes-default="25">
                        <ul>
                            <li v-for="filter in filters" :key="filter.id">{{ filter.name }}</li>
                        </ul>
                    </span>
                    <span v-else>
                        No filters
                    </span>
                    <span v-if="genres.length" splitpanes-default="25">
                        <ul>
                            <li v-for="genre in genres" :key="genre.id">{{ genre }}</li>
                        </ul>
                    </span>
                    <span v-else>
                        No genres
                    </span>
                    <span v-if="keywords.length" splitpanes-default="25">
                        <ul>
                            <li v-for="keyword in keywords" :key="keyword.id">{{ keyword }}</li>
                        </ul>
                    </span>
                    <span v-else>
                        No keywords
                    </span>
                    <span v-if="artists.length" splitpanes-default="25">
                        <v-treeview :items="artists"></v-treeview>
                    </span>
                    <span v-else>
                        No artists
                    </span>
                </splitpanes>
            </span>
        </splitpanes>
    </div>
</template>
<style>
.splitpanes__pane {
    overflow: scroll;
}
</style>
<script>
import gql from 'graphql-tag'
import { print } from 'graphql'
import splitpanes from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

const MUSIC_QUERY = gql`
{
  keywordsList
  genresTreeList
  allFiltersList {
    name
  }
  artistsTreeList {
    children: albums {
      name
      children: musics {
        name
      }
    }
    name
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
                this.keywords = result.data.data.keywordsList
                this.genres = result.data.data.genresTreeList
                this.filters = result.data.data.allFiltersList
            }).catch((err) => {
                this.errors = []
                this.artists = []
                this.keywords = []
                this.genres = []
                this.filters = []
                this.errors.push(err)
            })
        }
    },
    data: function() {
        return {
            errors: [],
            queue: [],
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
