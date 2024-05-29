select (
    insert Music {
        name := <str>$title,
        size := <Size>$size,
        length := <Length>$length,
        genre := <Genre><uuid>$genre,
        album := <Album><uuid>$album,
        keywords := assert_distinct((select array_unpack(<array<Keyword>><array<uuid>>$keywords))),
        track := <optional Track>$track,
        rating := <Rating>$rating,
        folders := (
            (<Folder><uuid>$folder) {
                @path := <str>$path
            }
        )
    }
    unless conflict on (.name, .album)
    else (
        update Music
        set {
            size := <Size>$size,
            genre := <Genre><uuid>$genre,
            album := <Album><uuid>$album,
            keywords := assert_distinct((select array_unpack(<array<Keyword>><array<uuid>>$keywords))),
            length := <Length>$length,
            track := <optional Track>$track,
            rating := <Rating>$rating,
            folders += (
                (<Folder><uuid>$folder) {
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
