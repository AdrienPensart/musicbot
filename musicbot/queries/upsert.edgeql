with
    upsert_artist := (
        insert Artist {
            name := <str>$artist
        }
        unless conflict on (.name) else (select Artist)
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
        unless conflict on (.name) else (select Genre)
    ),
    upsert_keywords := (
        for keyword in { array_unpack(<array<str>>$keywords) }
        union (
            insert Keyword {
                name := keyword
            }
            unless conflict on (.name)
            else (select Keyword)
        )
    ),
    upsert_folder := (
        insert Folder {
            name := <str>$folder,
            username := <str>$username,
            ipv4 := <str>$ipv4
        }
        unless conflict on (.name, .username, .ipv4) else (select Folder)
    )
    select (
        insert Music {
            name := <str>$title,
            size := <Size>$size,
            length := <Length>$length,
            genre := upsert_genre,
            album := upsert_album,
            keywords := upsert_keywords,
            track := <optional Track>$track,
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
                track := <optional Track>$track,
                rating := <Rating>$rating,
                folders += (
                    select upsert_folder {
                        @path := <str>$path
                    }
                )
            }
        )
    ) {
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
