CREATE MIGRATION m1n46zkg4ec75ff6drbbztljf3svo4hvnmby2h5u2akmqnmhtpzjiq
    ONTO initial
{
  CREATE EXTENSION pgcrypto VERSION '1.3';
  CREATE EXTENSION auth VERSION '1.0';
  CREATE EXTENSION edgeql_http VERSION '1.0';
  CREATE EXTENSION graphql VERSION '1.0';
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
  CREATE TYPE default::User {
      CREATE REQUIRED LINK identity: ext::auth::Identity;
      CREATE REQUIRED PROPERTY name: std::str;
  };
  CREATE TYPE default::Album {
      CREATE REQUIRED LINK user: default::User;
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
      CREATE REQUIRED LINK user: default::User;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE CONSTRAINT std::exclusive ON ((.name, .user, .album));
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
      CREATE PROPERTY track: default::Track;
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
      CREATE REQUIRED LINK user: default::User;
      CREATE CONSTRAINT std::exclusive ON ((.name, .user));
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
      CREATE CONSTRAINT std::exclusive ON ((.name, .user, .artist));
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
      CREATE REQUIRED LINK user: default::User;
      CREATE REQUIRED PROPERTY ipv4: std::str;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY username: std::str;
      CREATE CONSTRAINT std::exclusive ON ((.name, .user, .username, .ipv4));
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
      CREATE REQUIRED LINK user: default::User;
      CREATE CONSTRAINT std::exclusive ON ((.name, .user));
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
      CREATE REQUIRED LINK user: default::User;
      CREATE CONSTRAINT std::exclusive ON ((.name, .user));
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
  CREATE GLOBAL default::current_user := (std::assert_single((SELECT
      default::User {
          id,
          name
      }
  FILTER
      (.identity = GLOBAL ext::auth::ClientTokenIdentity)
  )));
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
  CREATE SCALAR TYPE default::`Limit` EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
};
