CREATE MIGRATION m17u3ztutw3czku6xjpqpxrrwyd2j4puyfbnhvdr3pkea3l3hvicoq
    ONTO m1a27gu7rhhsforpuxthxocmca2d57v33pbhe4egxnbzsjgnzpdbva
{
  DROP FUNCTION default::upsert_music(NAMED ONLY title: std::str, NAMED ONLY size: default::Size, NAMED ONLY length: default::Length, NAMED ONLY artist: std::str, NAMED ONLY genre: std::str, NAMED ONLY album: std::str, NAMED ONLY keywords: array<std::str>, NAMED ONLY track: OPTIONAL default::Track, NAMED ONLY rating: default::Rating, NAMED ONLY path: std::str, NAMED ONLY folder: std::str, NAMED ONLY username: std::str, NAMED ONLY ipv4: std::str);
  CREATE FUNCTION default::upsert_music(NAMED ONLY title: std::str, NAMED ONLY size: default::Size, NAMED ONLY length: default::Length, NAMED ONLY genre: default::Genre, NAMED ONLY album: default::Album, NAMED ONLY keywords: array<std::uuid>, NAMED ONLY track: OPTIONAL default::Track, NAMED ONLY rating: default::Rating, NAMED ONLY folder: default::Folder, NAMED ONLY path: std::str) ->  default::Music {
      CREATE ANNOTATION std::title := 'Create a new music';
      USING (SELECT
          (INSERT
              default::Music
              {
                  name := title,
                  size := size,
                  length := length,
                  genre := genre,
                  album := album,
                  keywords := std::assert_distinct((SELECT
                      std::array_unpack(<array<default::Keyword>>keywords)
                  )),
                  track := track,
                  rating := rating,
                  folders := (SELECT
                      folder {
                          @path := path
                      }
                  )
              }UNLESS CONFLICT ON (.name, .album) ELSE (UPDATE
              default::Music
          SET {
              size := size,
              genre := genre,
              album := album,
              keywords := std::assert_distinct((SELECT
                  std::array_unpack(<array<default::Keyword>>keywords)
              )),
              length := length,
              track := track,
              rating := rating,
              folders += (SELECT
                  folder {
                      @path := path
                  }
              )
          }))
      )
  ;};
};
