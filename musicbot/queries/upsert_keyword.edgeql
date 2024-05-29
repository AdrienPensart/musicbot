select (
    insert Keyword {
        name := <str>$keyword
    }
    unless conflict on (.name)
    else (select Keyword)
) {id}
