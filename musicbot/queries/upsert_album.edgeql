select upsert_album(
    artist := <Artist>$artist,
    album := <str>$album
).id