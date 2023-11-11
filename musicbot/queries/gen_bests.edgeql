with
    musics := (select gen_playlist(
        min_length := <Length>$min_length,
        max_length := <Length>$max_length,
        min_size := <Size>$min_size,
        max_size := <Size>$max_size,
        min_rating := <Rating>$min_rating,
        max_rating := <Rating>$max_rating,
        artist := <str>$artist,
        album := <str>$album,
        genre := <str>$genre,
        title := <str>$title,
        keyword := <str>$keyword,
        pattern := <str>$pattern,
        `limit` := <`Limit`>$limit,
    )),
    unique_keywords := (select distinct (for music in musics union (music.keywords)))
select {
    genres := (
        group musics {
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
                username,
                path := @path
            }
        }
        by .genre
    ),
    keywords := (
        for unique_keyword in unique_keywords
        union (
            select Keyword {
                name,
                musics := (
                    select distinct musics {
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
                            username,
                            path := @path
                        }
                    }
                    filter unique_keyword.name in .keywords.name
                )
            }
            filter .name = unique_keyword.name
        )
    ),
    ratings := (
        group musics {
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
                username,
                path := @path
            }
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
                                select distinct artist_musics {
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
                                        username,
                                        path := @path
                                    }
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
                username,
                path := @path
            }
        }
        by .artist, .rating
    )
}
