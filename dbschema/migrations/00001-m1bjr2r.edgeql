CREATE MIGRATION m1bjr2rffoclpevx4fwtloztxwzoamuwaebupjguz3hxxjnu6lywdq
    ONTO initial
{
  CREATE EXTENSION edgeql_http VERSION '1.0';
  CREATE EXTENSION graphql VERSION '1.0';
  CREATE EXTENSION pg_trgm VERSION '1.6';
  CREATE SCALAR TYPE default::Length EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE SCALAR TYPE default::`Limit` EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE SCALAR TYPE default::Rating EXTENDING std::float64 {
      CREATE CONSTRAINT std::one_of(0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0);
  };
  CREATE SCALAR TYPE default::Size EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE SCALAR TYPE default::Track EXTENDING std::int64;
  CREATE FUNCTION default::bytes_to_human(size: std::int64, k: std::int64 = 1000, decimals: std::int64 = 2, units: array<std::str> = [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']) ->  std::str {
      CREATE ANNOTATION std::title := 'Convert a byte size to human readable string';
      USING (SELECT
          (('0' ++ (units)[0]) IF (size = 0) ELSE (WITH
              i := 
                  <std::int64>std::math::floor((std::math::ln(std::math::abs(size)) / std::math::ln(k)))
          SELECT
              (std::to_str(std::round(<std::decimal>(size / (k ^ i)), decimals)) ++ (units)[i])
          ))
      )
  ;};
  CREATE TYPE default::Album {
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          CREATE REWRITE
              INSERT 
              USING (std::datetime_of_statement());
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
      CREATE INDEX fts::index ON (std::fts::with_options(.name, language := std::fts::Language.eng));
  };
  CREATE TYPE default::Music {
      CREATE REQUIRED LINK album: default::Album {
          ON TARGET DELETE DELETE SOURCE;
      };
      CREATE REQUIRED PROPERTY size: default::Size;
      CREATE REQUIRED PROPERTY length: default::Length;
      CREATE REQUIRED PROPERTY rating: default::Rating {
          SET default := 0.0;
      };
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE PROPERTY track: default::Track;
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          CREATE REWRITE
              INSERT 
              USING (std::datetime_of_statement());
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE CONSTRAINT std::exclusive ON ((.name, .album));
      CREATE INDEX fts::index ON (std::fts::with_options(.name, language := std::fts::Language.eng));
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
  };
  ALTER TYPE default::Album {
      CREATE MULTI LINK musics := (.<album[IS default::Music]);
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
  };
  CREATE TYPE default::Artist {
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          CREATE REWRITE
              INSERT 
              USING (std::datetime_of_statement());
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
      CREATE CONSTRAINT std::exclusive ON (.name);
      CREATE INDEX fts::index ON (std::fts::with_options(.name, language := std::fts::Language.eng));
  };
  ALTER TYPE default::Album {
      CREATE REQUIRED LINK artist: default::Artist {
          ON TARGET DELETE DELETE SOURCE;
      };
      CREATE PROPERTY title := (SELECT
          ((.artist.name ++ ' - ') ++ .name)
      );
      CREATE CONSTRAINT std::exclusive ON ((.name, .artist));
  };
  ALTER TYPE default::Artist {
      CREATE MULTI LINK albums := (.<artist[IS default::Album]);
      CREATE LINK musics := (SELECT
          .albums.musics
      );
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
  };
  ALTER TYPE default::Music {
      CREATE LINK artist := (SELECT
          .album.artist
      );
  };
  CREATE TYPE default::Folder {
      CREATE REQUIRED PROPERTY ipv4: std::str;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY username: std::str;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          CREATE REWRITE
              INSERT 
              USING (std::datetime_of_statement());
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
      CREATE CONSTRAINT std::exclusive ON ((.name, .username, .ipv4));
      CREATE INDEX fts::index ON (std::fts::with_options(.name, language := std::fts::Language.eng));
  };
  ALTER TYPE default::Music {
      CREATE REQUIRED MULTI LINK folders: default::Folder {
          CREATE PROPERTY path: std::str;
      };
  };
  ALTER TYPE default::Folder {
      CREATE MULTI LINK musics := (.<folders[IS default::Music]);
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
      CREATE LINK artists := (SELECT
          .musics.artist
      );
      CREATE PROPERTY all_artists := (SELECT
          std::to_str(std::array_agg(.musics.artist.name), ' ')
      );
  };
  CREATE TYPE default::Genre {
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          CREATE REWRITE
              INSERT 
              USING (std::datetime_of_statement());
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
      CREATE CONSTRAINT std::exclusive ON (.name);
      CREATE INDEX fts::index ON (std::fts::with_options(.name, language := std::fts::Language.eng));
  };
  ALTER TYPE default::Music {
      CREATE REQUIRED LINK genre: default::Genre;
  };
  ALTER TYPE default::Genre {
      CREATE MULTI LINK musics := (.<genre[IS default::Music]);
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
      CREATE LINK artists := (SELECT
          .musics.artist
      );
      CREATE PROPERTY all_artists := (SELECT
          std::to_str(std::array_agg(.musics.artist.name), ' ')
      );
      CREATE PROPERTY n_artists := (SELECT
          std::count(.artists)
      );
      CREATE LINK albums := (SELECT
          .musics.album
      );
      CREATE PROPERTY n_albums := (SELECT
          std::count(.albums)
      );
  };
  CREATE TYPE default::Keyword {
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE CONSTRAINT std::exclusive ON (.name);
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          CREATE REWRITE
              INSERT 
              USING (std::datetime_of_statement());
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
      CREATE INDEX fts::index ON (std::fts::with_options(.name, language := std::fts::Language.eng));
  };
  ALTER TYPE default::Music {
      CREATE MULTI LINK keywords: default::Keyword;
      CREATE PROPERTY title := (SELECT
          ((.album.title ++ ' - ') ++ .name)
      );
      CREATE PROPERTY paths := (SELECT
          .folders@path
      );
  };
  ALTER TYPE default::Keyword {
      CREATE MULTI LINK musics := (.<keywords[IS default::Music]);
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
      CREATE LINK artists := (SELECT
          .musics.artist
      );
      CREATE PROPERTY all_artists := (SELECT
          std::to_str(std::array_agg(.musics.artist.name), ' ')
      );
      CREATE PROPERTY n_artists := (SELECT
          std::count(.artists)
      );
      CREATE LINK albums := (SELECT
          .musics.album
      );
      CREATE PROPERTY n_albums := (SELECT
          std::count(.albums)
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>std::math::mean((.musics.rating ?? {0.0})), 2)
      );
  };
  CREATE FUNCTION default::gen_playlist(NAMED ONLY min_length: default::Length = 0, NAMED ONLY max_length: default::Length = 2147483647, NAMED ONLY min_size: default::Size = 0, NAMED ONLY max_size: default::Size = 2147483647, NAMED ONLY min_rating: default::Rating = 0.0, NAMED ONLY max_rating: default::Rating = 5.0, NAMED ONLY artist: std::str = '(.*?)', NAMED ONLY album: std::str = '(.*?)', NAMED ONLY genre: std::str = '(.*?)', NAMED ONLY title: std::str = '(.*?)', NAMED ONLY keyword: std::str = '(.*?)', NAMED ONLY `limit`: default::`Limit` = 2147483647, NAMED ONLY pattern: std::str = '') -> SET OF default::Music {
      CREATE ANNOTATION std::title := 'Generate a playlist from parameters';
      USING (SELECT
          default::Music FILTER
              ((((((((((((.length >= min_length) AND (.length <= max_length)) AND (.size >= min_size)) AND (.size <= max_size)) AND (.rating >= min_rating)) AND (.rating <= max_rating)) AND std::re_test(artist, .artist.name)) AND std::re_test(album, .album.name)) AND std::re_test(genre, .genre.name)) AND std::re_test(title, .name)) AND std::re_test(keyword, std::array_join(std::array_agg((SELECT
                  .keywords.name
              )), ' '))) AND ((pattern = '') OR ext::pg_trgm::word_similar(pattern, .title)))
          ORDER BY
              .artist.name ASC THEN
              .album.name ASC THEN
              .track ASC THEN
              .name ASC
      LIMIT
          `limit`
      )
  ;};
  CREATE FUNCTION default::gen_bests(NAMED ONLY min_length: default::Length = 0, NAMED ONLY max_length: default::Length = 2147483647, NAMED ONLY min_size: default::Size = 0, NAMED ONLY max_size: default::Size = 2147483647, NAMED ONLY min_rating: default::Rating = 0.0, NAMED ONLY max_rating: default::Rating = 5.0, NAMED ONLY artist: std::str = '(.*?)', NAMED ONLY album: std::str = '(.*?)', NAMED ONLY genre: std::str = '(.*?)', NAMED ONLY title: std::str = '(.*?)', NAMED ONLY keyword: std::str = '(.*?)', NAMED ONLY `limit`: default::`Limit` = 2147483647, NAMED ONLY pattern: std::str = '') ->  std::json {
      CREATE ANNOTATION std::title := 'Generate a playlist from parameters';
      USING (WITH
          musics := 
              (SELECT
                  default::gen_playlist(min_length := min_length, max_length := max_length, min_size := min_size, max_size := max_size, min_rating := min_rating, max_rating := max_rating, artist := artist, album := album, genre := genre, title := title, keyword := keyword, pattern := pattern, `limit` := `limit`)
              )
          ,
          unique_keywords := 
              (SELECT
                  DISTINCT ((FOR music IN musics
                  UNION 
                      music.keywords))
              )
      SELECT
          <std::json>{
              genres := (GROUP
                  musics {
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
              BY .genre),
              keywords := (FOR unique_keyword IN unique_keywords
              UNION 
                  (SELECT
                      default::Keyword {
                          name,
                          musics := (SELECT
                              DISTINCT (musics {
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
                              })
                          FILTER
                              (unique_keyword.name IN .keywords.name)
                          )
                      }
                  FILTER
                      (.name = unique_keyword.name)
                  )),
              ratings := (GROUP
                  musics {
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
              BY .rating),
              keywords_for_artist := (FOR artist IN (SELECT
                  DISTINCT (musics.artist)
              )
              UNION 
                  (SELECT
                      {
                          artist := artist.name,
                          keywords := (WITH
                              artist_musics := 
                                  (SELECT
                                      musics
                                  FILTER
                                      (.artist = artist)
                                  )
                              ,
                              artist_keywords := 
                                  (SELECT
                                      DISTINCT ((FOR music IN artist_musics
                                      UNION 
                                          music.keywords))
                                  )
                          FOR artist_keyword IN (SELECT
                              artist_keywords
                          )
                          UNION 
                              (SELECT
                                  {
                                      keyword := artist_keyword.name,
                                      musics := (SELECT
                                          DISTINCT (artist_musics {
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
                                          })
                                      FILTER
                                          (artist_keyword IN .keywords)
                                      )
                                  }
                              ))
                      }
                  )),
              ratings_for_artist := (GROUP
                  musics {
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
              BY .artist,
              .rating)
          }
      )
  ;};
  CREATE FUNCTION default::remove_musics_path(NAMED ONLY path: std::str) -> SET OF default::Music {
      CREATE ANNOTATION std::title := 'Remove path from musics';
      USING (UPDATE
          default::Music
      FILTER
          std::contains(.paths, path)
      SET {
          folders := (SELECT
              .folders
          FILTER
              (@path != path)
          )
      })
  ;};
  CREATE FUNCTION default::upsert_album(NAMED ONLY artist: default::Artist, NAMED ONLY album: std::str) ->  default::Album {
      CREATE ANNOTATION std::title := 'Create a new album';
      USING (SELECT
          (INSERT
              default::Album
              {
                  name := album,
                  artist := artist
              }UNLESS CONFLICT ON (.name, .artist) ELSE (SELECT
              default::Album
          ))
      )
  ;};
  CREATE FUNCTION default::upsert_artist(NAMED ONLY artist: std::str) ->  default::Artist {
      CREATE ANNOTATION std::title := 'Create a new artist';
      USING (SELECT
          (INSERT
              default::Artist
              {
                  name := artist
              }UNLESS CONFLICT ON .name ELSE (SELECT
              default::Artist
          ))
      )
  ;};
  CREATE FUNCTION default::upsert_folder(NAMED ONLY folder: std::str, NAMED ONLY username: std::str, NAMED ONLY ipv4: std::str) ->  default::Folder {
      CREATE ANNOTATION std::title := 'Create a new folder';
      USING (SELECT
          (INSERT
              default::Folder
              {
                  name := folder,
                  username := username,
                  ipv4 := ipv4
              }UNLESS CONFLICT ON (.name, .username, .ipv4) ELSE (SELECT
              default::Folder
          ))
      )
  ;};
  CREATE FUNCTION default::upsert_genre(NAMED ONLY genre: std::str) ->  default::Genre {
      CREATE ANNOTATION std::title := 'Create a new genre';
      USING (SELECT
          (INSERT
              default::Genre
              {
                  name := genre
              }UNLESS CONFLICT ON .name ELSE (SELECT
              default::Genre
          ))
      )
  ;};
  CREATE FUNCTION default::upsert_keyword(NAMED ONLY keyword: std::str) ->  default::Keyword {
      CREATE ANNOTATION std::title := 'Create a new keyword';
      USING (SELECT
          (INSERT
              default::Keyword
              {
                  name := keyword
              }UNLESS CONFLICT ON .name ELSE (SELECT
              default::Keyword
          ))
      )
  ;};
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
  ALTER TYPE default::Artist {
      CREATE LINK genres := (SELECT
          .musics.genre
      );
      CREATE LINK keywords := (SELECT
          .musics.keywords
      );
      CREATE PROPERTY all_genres := (SELECT
          std::to_str(std::array_agg(.musics.genre.name), ' ')
      );
      CREATE PROPERTY all_keywords := (SELECT
          std::to_str(std::array_agg((SELECT
              default::Artist.keywords.name
          ORDER BY
              default::Artist.keywords.name ASC
          )), ' ')
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY n_albums := (SELECT
          std::count(.albums)
      );
      CREATE PROPERTY n_genres := (SELECT
          std::count(.genres)
      );
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>std::math::mean((.musics.rating ?? {0.0})), 2)
      );
  };
  ALTER TYPE default::Album {
      CREATE PROPERTY all_keywords := (SELECT
          std::to_str(std::array_agg((SELECT
              default::Artist.keywords.name
          ORDER BY
              default::Artist.keywords.name ASC
          )), ' ')
      );
      CREATE LINK genres := (SELECT
          .musics.genre
      );
      CREATE PROPERTY n_genres := (SELECT
          std::count(.genres)
      );
      CREATE LINK keywords := (SELECT
          .musics.keywords
      );
      CREATE PROPERTY all_genres := (SELECT
          std::to_str(std::array_agg(.musics.genre.name), ' ')
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>std::math::mean((.musics.rating ?? {0.0})), 2)
      );
  };
  ALTER TYPE default::Folder {
      CREATE PROPERTY all_keywords := (SELECT
          std::to_str(std::array_agg((SELECT
              default::Artist.keywords.name
          ORDER BY
              default::Artist.keywords.name ASC
          )), ' ')
      );
      CREATE PROPERTY n_artists := (SELECT
          std::count(.artists)
      );
      CREATE LINK albums := (SELECT
          .musics.album
      );
      CREATE PROPERTY n_albums := (SELECT
          std::count(.albums)
      );
      CREATE LINK genres := (SELECT
          .musics.genre
      );
      CREATE PROPERTY n_genres := (SELECT
          std::count(.genres)
      );
      CREATE LINK keywords := (SELECT
          .musics.keywords
      );
      CREATE PROPERTY n_keywords := (SELECT
          std::count(.keywords)
      );
      CREATE PROPERTY all_genres := (SELECT
          std::to_str(std::array_agg(.musics.genre.name), ' ')
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
  };
  ALTER TYPE default::Genre {
      CREATE LINK keywords := (SELECT
          .musics.keywords
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>std::math::mean((.musics.rating ?? {0.0})), 2)
      );
  };
  CREATE TYPE default::Playlist {
      CREATE MULTI LINK musics: default::Music;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE INDEX fts::index ON (std::fts::with_options(.name, language := std::fts::Language.eng));
  };
};
