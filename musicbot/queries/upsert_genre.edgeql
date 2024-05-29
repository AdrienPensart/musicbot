select (
    insert Genre {
        name := <str>$genre
    }
    unless conflict on (.name) else (select Genre)
) {id}
