CREATE MIGRATION m1pxtlmzs26ywdoe5u3pfx5m3h2nh76q34bmktpckcauasvwno7n5a
    ONTO m1b5dzcdji5x6rdan6nq3zmkffqg4exk5v3kukztu4wfagn3abpgcq
{
  DROP FUNCTION default::upsert_music(NAMED ONLY title: std::str, NAMED ONLY size: default::Size, NAMED ONLY length: default::Length, NAMED ONLY artist: std::str, NAMED ONLY genre: std::str, NAMED ONLY album: std::str, NAMED ONLY keywords: array<std::str>, NAMED ONLY track: OPTIONAL default::Track, NAMED ONLY rating: default::Rating, NAMED ONLY path: std::str, NAMED ONLY folder: std::str, NAMED ONLY username: std::str, NAMED ONLY ipv4: std::str);
  CREATE FUNCTION default::upsert_music(NAMED ONLY title: std::str, NAMED ONLY size: default::Size, NAMED ONLY length: default::Length, NAMED ONLY artist: std::str, NAMED ONLY genre: std::str, NAMED ONLY album: std::str, NAMED ONLY keywords: array<std::str>, NAMED ONLY track: OPTIONAL default::Track, NAMED ONLY rating: default::Rating, NAMED ONLY path: std::str, NAMED ONLY folder: std::str, NAMED ONLY username: std::str, NAMED ONLY ipv4: std::str) ->  std::int64 {
      CREATE ANNOTATION std::title := 'Create a new music';
      USING (WITH
          upsert_artist := 
              (INSERT
                  default::Artist
                  {
                      name := <std::str>artist
                  }UNLESS CONFLICT ON .name ELSE (SELECT
                  default::Artist
              ))
          ,
          upsert_album := 
              (INSERT
                  default::Album
                  {
                      name := <std::str>album,
                      artist := std::assert_single(upsert_artist)
                  }UNLESS CONFLICT ON (.name, .artist) ELSE (SELECT
                  default::Album
              ))
          ,
          upsert_genre := 
              (INSERT
                  default::Genre
                  {
                      name := <std::str>genre
                  }UNLESS CONFLICT ON .name ELSE (SELECT
                  default::Genre
              ))
          ,
          upsert_keywords := 
              (FOR keyword IN {std::array_unpack(keywords)}
              UNION 
                  (INSERT
                      default::Keyword
                      {
                          name := keyword
                      }UNLESS CONFLICT ON .name ELSE (SELECT
                      default::Keyword
                  )))
          ,
          upsert_folder := 
              (INSERT
                  default::Folder
                  {
                      name := folder,
                      username := username,
                      ipv4 := ipv4
                  }UNLESS CONFLICT ON (.name, .username, .ipv4) ELSE (SELECT
                  default::Folder
              ))
      SELECT
          1
      )
  ;};
};
