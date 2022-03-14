from typing import Final

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
    upsert_music := (
        insert Music {
            name := <str>$title,
            links := array_unpack(<array<str>>$links),
            size := <Size>$size,
            genre := upsert_genre,
            album := upsert_album,
            keywords := upsert_keywords,
            duration := to_duration(seconds := <float64>$length),
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
                duration := to_duration(seconds := <float64>$length),
                track := <int16>$track,
                rating := <Rating>$rating
            }
        )
    )
    select Music {
        name,
        links,
        size,
        genre_name := .genre.name,
        album_name := .album.name,
        artist_name := .album.artist.name,
        all_keywords := array_agg(.keywords.name),
        length := <int64>duration_to_seconds(.duration),
        track,
        rating
    }
    filter .id = upsert_music.id;
"""

PLAYLIST_QUERY = """
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
        name,
        links,
        size,
        genre_name := .genre.name,
        album_name := .album.name,
        artist_name := .album.artist.name,
        all_keywords := array_agg(.keywords.name),
        length := <int64>duration_to_seconds(.duration),
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
                not contains(.all_keywords, no_keyword)
            )
        )))
        and (len(<array<str>>$keywords) = 0 or all((
            for yes_keyword in array_unpack(<array<str>>$keywords)
            union (
                contains(.all_keywords, yes_keyword)
            )
        )))
    ;
"""
