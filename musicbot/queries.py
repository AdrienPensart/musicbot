import string
from typing import Final


class CustomStringTemplate(string.Template):
    delimiter = "#"


MUSIC_FIELDS = """
name,
size,
genre: {name},
album: {name},
artist: {name},
keywords: {name},
length,
track,
rating,
folders: {
    name,
    ipv4,
    user,
    path := @path
}
"""

PLAYLIST_QUERY: Final[str] = CustomStringTemplate("""
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
        #music_fields
    }
    filter
        .length >= <int64>$min_length and .length <= <int64>$max_length
        and .size >= <int64>$min_size and .size <= <int64>$max_size
        and .rating >= <Rating>$min_rating and .rating <= <Rating>$max_rating
        and (len(<array<str>>$titles) = 0 or contains(<array<str>>$titles, .name))
        and (len(<array<str>>$no_titles) = 0 or not contains(<array<str>>$no_titles, .name))
        and .genre in genres
        and .album in albums
        and (len(<array<str>>$no_keywords) = 0 or not any(array_unpack(<array<str>>$no_keywords) in .keywords.name))
        and (len(<array<str>>$keywords) = 0 or all(array_unpack(<array<str>>$keywords) in .keywords.name))
    order by max({<float64>$shuffle, random()})
    limit <int64>$limit
""").substitute(music_fields=MUSIC_FIELDS)

SOFT_CLEAN_QUERY: Final[str] = """
delete Music filter not exists .folders;
delete Album filter not exists .musics;
delete Artist filter not exists .musics;
delete Genre filter not exists .musics;
delete Keyword filter not exists .musics;
"""

SEARCH_QUERY: Final[str] = CustomStringTemplate("""
select Music {
    #music_fields
}
filter
.name ilike <str>$pattern or
.genre.name ilike <str>$pattern or
.album.name ilike <str>$pattern or
.artist.name ilike <str>$pattern or
.keywords.name ilike <str>$pattern
""").substitute(music_fields=MUSIC_FIELDS)

REMOVE_PATH_QUERY: Final[str] = """
update Music filter contains(.folders@path, <str>$path) set {folders := (select .folders filter @path != <str>$path)};
"""

UPSERT_QUERY: Final[str] = CustomStringTemplate("""
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
    upsert_folder := (
        insert Folder {
            name := <str>$folder,
            user := <str>$user,
            ipv4 := <str>$ipv4
        }
        unless conflict on (.name, .ipv4) else (select Folder)
    )
    select (
        insert Music {
            name := <str>$title,
            size := <Size>$size,
            length := <Length>$length,
            genre := upsert_genre,
            album := upsert_album,
            keywords := upsert_keywords,
            track := <int16>$track,
            rating := <Rating>$rating,
            folders := (
                select upsert_folder {
                    @path := <str>$path
                }
            )
        }
        unless conflict on (.name, .album)
        else (
            update Music
            set {
                size := <Size>$size,
                genre := upsert_genre,
                album := upsert_album,
                keywords := upsert_keywords,
                length := <Length>$length,
                track := <int16>$track,
                rating := <Rating>$rating,
                folders += (
                    select upsert_folder {
                        @path := <str>$path
                    }
                )
            }
        )
    ) {
        #music_fields
    }
""").substitute(music_fields=MUSIC_FIELDS)

BESTS_QUERY: Final[str] = CustomStringTemplate("""
with
    musics := (#filtered_playlist),
    unique_keywords := (select distinct (for music in musics union (music.keywords)))
select {
    genres := (
        group musics {
            #music_fields
        }
        by .genre
    ),
    keywords := (
        for unique_keyword in unique_keywords
        union (
            select Keyword {
                name,
                musics := (
                    select musics {
                        #music_fields
                    }
                    filter unique_keyword.name in .keywords.name
                )
            }
            filter .name = unique_keyword.name
        )
    ),
    ratings := (
        group musics {
            #music_fields
        }
        by .rating
    ),
    keywords_for_artist := (
        for artist in (select distinct musics.artist)
        union (
            select {
                artist := artist.name,
                keywords := (
                    with
                    artist_musics := (select musics filter .artist = artist),
                    artist_keywords := (select distinct (for music in artist_musics union (music.keywords)))
                    for artist_keyword in (select artist_keywords)
                    union (
                        select {
                            keyword := artist_keyword.name,
                            musics := (
                                select artist_musics {
                                    #music_fields
                                }
                                filter artist_keyword in .keywords
                            )
                        }
                    )
                )
            }
        )
    ),
    ratings_for_artist := (
        group musics {
            #music_fields
        }
        by .artist, .rating
    )
}
""").substitute(music_fields=MUSIC_FIELDS, filtered_playlist=PLAYLIST_QUERY)
