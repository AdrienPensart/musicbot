select gen_playlist(
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