<template>
    <div id="artists">
        <p v-if="artists.length">
            <ul>
                <li v-for="artist in artists" :key="artist.id">{{ artist }}</li>
            </ul>
        </p>
    </div>
</template>

<script>
import gql from 'graphql-tag'

const ARTISTS_QUERY = gql`
{
    artistsList
}
`
export default {
    data() {
        return {
            artists: []
        };
    },
}
</script>
