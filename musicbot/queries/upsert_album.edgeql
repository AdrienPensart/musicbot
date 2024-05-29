select (
    insert Album {
        name := <str>$album,
        artist := <Artist>$artist
    }
    unless conflict on (.name, .artist) else (select Album)
) {id}
