CREATE MIGRATION m1oy3zaoi4vykcutcfrianlcvpose52w7fdmesc6vcv3l73mlb5p4a
    ONTO initial
{
  CREATE EXTENSION edgeql_http VERSION '1.0';
  CREATE EXTENSION graphql VERSION '1.0';
  CREATE EXTENSION pg_trgm VERSION '1.6';
  CREATE FUNCTION default::bytes_to_human(size: std::int64, k: std::int64 = 1000, decimals: std::int64 = 2, units: array<std::str> = [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']) ->  std::str {
      CREATE ANNOTATION std::title := 'Convert a byte size to human readable string';
      USING (SELECT
          (('0' ++ (units)[0]) IF (size = 0) ELSE (WITH
              i := 
                  <std::int64>math::floor((math::ln(math::abs(size)) / math::ln(k)))
          SELECT
              (std::to_str(std::round(<std::decimal>(size / (k ^ i)), decimals)) ++ (units)[i])
          ))
      )
  ;};
  CREATE TYPE default::Album {
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
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
  };
  CREATE SCALAR TYPE default::Length EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE SCALAR TYPE default::Rating EXTENDING std::float64 {
      CREATE CONSTRAINT std::one_of(0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0);
  };
  CREATE SCALAR TYPE default::Size EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE SCALAR TYPE default::Track EXTENDING std::int64;
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
      CREATE CONSTRAINT std::exclusive ON ((.name, .album));
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          CREATE REWRITE
              INSERT 
              USING (std::datetime_of_statement());
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
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
      CREATE CONSTRAINT std::exclusive ON (.name);
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
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
      CREATE CONSTRAINT std::exclusive ON ((.name, .username, .ipv4));
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
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
  };
  ALTER TYPE default::Music {
      CREATE MULTI LINK folders: default::Folder {
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
      CREATE CONSTRAINT std::exclusive ON (.name);
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
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
  };
  ALTER TYPE default::Music {
      CREATE REQUIRED LINK genre: default::Genre {
          ON TARGET DELETE DELETE SOURCE;
      };
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
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
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
          <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
      );
  };
  CREATE SCALAR TYPE default::`Limit` EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
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
          <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
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
          <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
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
          <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
      );
  };
};
