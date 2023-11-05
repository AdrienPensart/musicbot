import string


class CustomStringTemplate(string.Template):
    delimiter = "#"


FOLDERS_QUERY: str = "select Folder {*} order by .name"
ARTISTS_QUERY: str = """select Artist {*} order by .name"""

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

PLAYLIST_QUERY: str = CustomStringTemplate(
    """
    select Music {
        #music_fields
    }
    filter
        .length >= <Length>$min_length and .length <= <Length>$max_length
        and .size >= <Size>$min_size and .size <= <Size>$max_size
        and .rating >= <Rating>$min_rating and .rating <= <Rating>$max_rating
        and re_test(<str>$artist, .artist.name)
        and re_test(<str>$album, .album.name)
        and re_test(<str>$genre, .genre.name)
        and re_test(<str>$title, .name)
        and re_test(<str>$keyword, array_join(array_agg((select .keywords.name)), " "))
    order by
        .artist.name then
        .album.name then
        .track then
        .name
    limit <`Limit`>$limit
"""
).substitute(music_fields=MUSIC_FIELDS)

SOFT_CLEAN_QUERY: str = """
select {
    musics_deleted := count((delete Music filter not exists .folders)),
    albums_deleted := count((delete Album filter not exists .musics)),
    artists_deleted := count((delete Artist filter not exists .musics)),
    genres_deleted := count((delete Genre filter not exists .musics)),
    keywords_deleted := count((delete Keyword filter not exists .musics))
};
"""

SEARCH_QUERY: str = """
with res := (select fts::search(Music, <str>$pattern))
select res.object {**}
order by res.score desc;
"""

REMOVE_PATH_QUERY: str = """
update Music
filter contains(.paths, <str>$path)
set {folders := (select .folders filter @path != <str>$path)};
"""

UPSERT_QUERY: str = CustomStringTemplate(
    """
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
            track := <Track>$track,
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
                track := <Track>$track,
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
"""
).substitute(music_fields=MUSIC_FIELDS)

BESTS_QUERY: str = CustomStringTemplate(
    """
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
"""
).substitute(music_fields=MUSIC_FIELDS, filtered_playlist=PLAYLIST_QUERY)
