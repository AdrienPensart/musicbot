from typing import Final

SOFT_CLEAN_QUERY: Final[str] = """
delete Keyword filter not exists .musics;
delete Album filter not exists .musics;
delete Artist filter not exists .musics;
delete Genre filter not exists .musics;
"""

SEARCH_QUERY: Final[str] = """
select Music {{
    name,
    links,
    size,
    genre: {{name}},
    album: {{name}},
    artist: {{name}},
    keywords: {{name}},
    length,
    track,
    rating
}}
filter
.name ilike "{pattern}" or
.genre.name ilike "{pattern}" or
.album.name ilike "{pattern}" or
.artist.name ilike "{pattern}" or
.keywords.name ilike "{pattern}"
"""

DELETE_QUERY: Final[str] = """
delete Music filter contains(.links, <str>$path)
"""

UPSERT_QUERY: Final[str] = """
with
    upsert_artist := (
        insert Artist {
            name := <str>$artist
        }
        unless conflict on .name else (select Artist)
    ),
    upsert_album := (
        insert Album {
            name := <str>$album,
            artist := upsert_artist
        }
        unless conflict on (.name, .artist) else (select Album)
    ),
    upsert_genre := (
        insert Genre {
            name := <str>$genre
        }
        unless conflict on .name else (select Genre)
    ),
    upsert_keywords := (
        for keyword in { array_unpack(<array<str>>$keywords) }
        union (
            insert Keyword {
                name := keyword
            }
            unless conflict on .name
            else (select Keyword)
        )
    ),
    select (
        insert Music {
            name := <str>$title,
            links := array_unpack(<array<str>>$links),
            size := <Size>$size,
            length := <Length>$length,
            genre := upsert_genre,
            album := upsert_album,
            keywords := upsert_keywords,
            track := <int16>$track,
            rating := <Rating>$rating
        }
        unless conflict on (.name, .album)
        else (
            update Music
            set {
                links := array_unpack(<array<str>>$links),
                size := <Size>$size,
                genre := upsert_genre,
                album := upsert_album,
                keywords := upsert_keywords,
                length := <Length>$length,
                track := <int16>$track,
                rating := <Rating>$rating
            }
        )
    ) {
        name,
        links,
        size,
        genre: {name},
        album: {name},
        artist: {name},
        keywords: {name},
        length,
        track,
        rating
    }
"""

BESTS_QUERY: Final[str] = """
with
    musics := ({filtered_playlist}),
    unique_keywords := (select distinct (for music in musics union (music.keywords)))
select {{
    genres := (
        group musics {{ name, links, size, genre: {{name}}, album: {{name}}, artist: {{name}}, keywords: {{name}}, length, track, rating }}
        by .genre
    ),
    keywords := (
        for unique_keyword in unique_keywords
        union (
            select Keyword {{
                name,
                musics := (
                    select musics {{ name, links, size, genre: {{name}}, album: {{name}}, artist: {{name}}, keywords: {{name}}, length, track, rating }}
                    filter unique_keyword.name in .keywords.name
                )
            }}
            filter .name = unique_keyword.name
        )
    ),
    ratings := (
        group musics {{ name, links, size, genre: {{name}}, album: {{name}}, artist: {{name}}, keywords: {{name}}, length, track, rating }}
        by .rating
    ),
    keywords_for_artist := (
        for artist in (select distinct musics.artist)
        union (
            select {{
                artist := artist.name,
                keywords := (
                    with
                    artist_musics := (select musics filter .artist = artist),
                    artist_keywords := (select distinct (for music in artist_musics union (music.keywords)))
                    for artist_keyword in (select artist_keywords)
                    union (
                        select {{
                            keyword := artist_keyword.name,
                            musics := (
                                select artist_musics {{ name, links, size, genre: {{name}}, album: {{name}}, artist: {{name}}, keywords: {{name}}, length, track, rating }}
                                filter artist_keyword in .keywords
                            )
                        }}
                    )
                )
            }}
        )
    ),
    ratings_for_artist := (
        group musics {{ name, links, size, genre: {{name}}, album: {{name}}, artist: {{name}}, keywords: {{name}}, length, track, rating }}
        by .artist, .rating
    )
}}
"""


PLAYLIST_QUERY: Final[str] = """
with
    artists := (
        select Artist
        filter
            (len(<array<str>>$artists) = 0 or contains(<array<str>>$artists, .name)) and
            (len(<array<str>>$no_artists) = 0 or not contains(<array<str>>$no_artists, .name))
    ),
    albums := (
        select Album
        filter
            (len(<array<str>>$albums) = 0 or contains(<array<str>>$albums, .name)) and
            (len(<array<str>>$no_albums) = 0 or not contains(<array<str>>$no_albums, .name)) and
            .artist in artists
    ),
    genres := (
        select Genre
        filter
            (len(<array<str>>$genres) = 0 or contains(<array<str>>$genres, .name)) and
            (len(<array<str>>$no_genres) = 0 or not contains(<array<str>>$no_genres, .name))
    ),
    select Music {
        id,
        name,
        links,
        size,
        genre: {name},
        album: {name},
        artist: {name},
        keywords: {name},
        length,
        track,
        rating
    }
    filter
        .length >= <int64>$min_length and .length <= <int64>$max_length
        and .size >= <int64>$min_size and .size <= <int64>$max_size
        and .rating >= <Rating>$min_rating and .rating <= <Rating>$max_rating
        and (len(<array<str>>$titles) = 0 or contains(<array<str>>$titles, .name))
        and (len(<array<str>>$no_titles) = 0 or not contains(<array<str>>$no_titles, .name))
        and .genre in genres
        and .album in albums
        and (len(<array<str>>$no_keywords) = 0 or all((
            for no_keyword in array_unpack(<array<str>>$no_keywords)
            union (
                not contains(.keywords.name, no_keyword)
            )
        )))
        and (len(<array<str>>$keywords) = 0 or all((
            for yes_keyword in array_unpack(<array<str>>$keywords)
            union (
                contains(.keywords.name, yes_keyword)
            )
        )))
    order by max({<float64>$shuffle, random()})
    limit <int64>$limit
"""
