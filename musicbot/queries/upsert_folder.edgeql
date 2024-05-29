select (
    insert Folder {
        name := <str>$folder,
        username := <str>$username,
        ipv4 := <str>$ipv4
    }
    unless conflict on (.name, .username, .ipv4) else (select Folder)
) {id}
