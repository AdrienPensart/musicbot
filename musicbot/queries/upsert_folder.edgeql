select upsert_folder(
    folder := <str>$folder,
    username := <str>$username,
    ipv4 := <str>$ipv4
).id