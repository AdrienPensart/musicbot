CREATE MIGRATION m1b5dzcdji5x6rdan6nq3zmkffqg4exk5v3kukztu4wfagn3abpgcq
    ONTO m1iwthp6hboshutri7li5ycqxlx5kkzexzicasvfk6darlnnewspvq
{
  ALTER FUNCTION default::upsert_music(NAMED ONLY title: std::str, NAMED ONLY size: default::Size, NAMED ONLY length: default::Length, NAMED ONLY artist: std::str, NAMED ONLY genre: std::str, NAMED ONLY album: std::str, NAMED ONLY keywords: array<std::str>, NAMED ONLY track: OPTIONAL default::Track, NAMED ONLY rating: default::Rating, NAMED ONLY path: std::str, NAMED ONLY folder: std::str, NAMED ONLY username: std::str, NAMED ONLY ipv4: std::str) USING (WITH
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
      (INSERT
          default::Music
          {
              name := title,
              size := size,
              length := length,
              genre := std::assert_single(upsert_genre),
              album := std::assert_single(upsert_album),
              keywords := std::assert_single(upsert_keywords),
              track := track,
              rating := rating,
              folders := (SELECT
                  upsert_folder {
                      @path := path
                  }
              )
          }UNLESS CONFLICT ON (.name, .album) ELSE (UPDATE
          default::Music
      SET {
          size := size,
          genre := std::assert_single(upsert_genre),
          album := std::assert_single(upsert_album),
          keywords := upsert_keywords,
          length := length,
          track := track,
          rating := rating,
          folders += (SELECT
              upsert_folder {
                  @path := path
              }
          )
      })) {
          name,
          size,
          genre: {
              name
          },
          album: {
              name
          },
          artist: {
              name
          },
          keywords: {
              name
          },
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
  );
};
