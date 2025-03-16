select upsert_music(
    title := <str>$title,
    size := <Size>$size,
    length := <Length>$length,
    genre := <Genre>$genre,
    album := <Album>$album,
    keywords := <array<uuid>>$keywords,
    track := <optional Track>$track,
    rating := <Rating>$rating,
    folder := <Folder>$folder,
    path := <str>$path
){
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

# select upsert_music(
#     title := <str>$title,
#     size := <Size>$size,
#     length := <Length>$length,
#     artist := <str>$artist,
#     genre := <str>$genre,
#     album := <str>$album,
#     keywords := <array<str>>$keywords,
#     track := <optional Track>$track,
#     rating := <Rating>$rating,
#     path := <str>$path,
#     folder := <str>$folder,
#     username := <str>$username,
#     ipv4 := <str>$ipv4
# ) 
# {
#     name,
#     size,
#     genre: {name},
#     album: {name},
#     artist: {name},
#     keywords: {name},
#     length,
#     track,
#     rating,
#     folders: {
#         name,
#         ipv4,
#         username,
#         path := @path
#     }
# }