select (
    insert Artist {
        name := <str>$artist
    }
    unless conflict on (.name) else (select Artist)
) {id}
