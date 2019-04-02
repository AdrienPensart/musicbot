<template>
    <div>
        <p v-if="errors.length">
            <b>Please correct the following error(s):</b>
            <ul>
                <li v-for="error in errors" :key="error.id">{{ error }}</li>
            </ul>
        </p>
        <splitpanes horizontal class="default-theme">
            <span splitpanes-default="75">
                <splitpanes vertical>
                    <span splitpanes-default="25">
                        <ul v-if="filters.length">
                            <li v-for="filter in filters" :key="filter.id">{{ filter.name }}</li>
                        </ul>
                    </span>
                    <span splitpanes-default="25">
                        <ul v-if="genres.length">
                            <li v-for="genre in genres" :key="genre.id">{{ genre }}</li>
                        </ul>
                    </span>
                    <span splitpanes-default="25">
                        <ul v-if="keywords.length">
                            <li v-for="keyword in keywords" :key="keyword.id">{{ keyword }}</li>
                        </ul>
                    </span>
                    <span splitpanes-default="25">
                        <p v-if="artists.length" v-for="artist in artists" :key="artist.id">
                            {{ artist.name }}
                            <ul>
                                <li v-for="album in artist.albums" :key="album.id">{{ album }}</li>
                            </ul>
                        </p>
                    </span>
                </splitpanes>
            </span>
            <span splitpanes-default="25">
                Queue
            </span>
        </splitpanes>
    </div>
</template>

<script>
import gql from 'graphql-tag'
import { print } from 'graphql'
import Splitpanes from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

const MUSIC_QUERY = gql`
{
  keywordsList
  genresList
  allFiltersList {
    name
  }
  artistsList {
    name
    albums
  }
}
`
export default {
    components: {
        Splitpanes,
    },
    methods: {
    },
    data() {
        return {
            direction: '',
            errors: [],
            artists: [],
            keywords: [],
            genres: [],
            filters: [],
        };
    },
    mounted() {
        this.axios.post(this.graphql, {
            query: print(MUSIC_QUERY),
        }).then((result) => {
            this.artists = result.data.data.artistsList
            this.keywords = result.data.data.keywordsList
            this.genres = result.data.data.genresList
            this.filters = result.data.data.allFiltersList
        }).catch((err) => {
            this.errors = []
            this.artists = []
            this.keywords = []
            this.genres = []
            this.filters = []
            this.errors.push(err)
        })
    },
}
</script>
