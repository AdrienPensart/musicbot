CREATE MIGRATION m1icg2vz6wsdi67vmfm5rcuozgonrldiyjvzghwuxqdnsbqpzm7d6q
    ONTO initial
{
  CREATE EXTENSION graphql VERSION '1.0';
  CREATE EXTENSION edgeql_http VERSION '1.0';
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
  CREATE TYPE default::Artist {
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY name: std::str {
          CREATE CONSTRAINT std::exclusive;
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
      CREATE CONSTRAINT std::exclusive ON ((.name, .artist));
      CREATE INDEX ON ((.name, .artist));
  };
  ALTER TYPE default::Artist {
      CREATE MULTI LINK albums := (.<artist[IS default::Album]);
  };
  CREATE SCALAR TYPE default::Length EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE SCALAR TYPE default::Rating EXTENDING std::float32 {
      CREATE CONSTRAINT std::one_of(0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0);
  };
  CREATE SCALAR TYPE default::Size EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE TYPE default::Music {
      CREATE REQUIRED LINK album: default::Album {
          ON TARGET DELETE DELETE SOURCE;
      };
      CREATE LINK artist := (SELECT
          .album.artist
      );
      CREATE REQUIRED PROPERTY length: default::Length;
      CREATE REQUIRED PROPERTY rating: default::Rating {
          SET default := 0.0;
      };
      CREATE REQUIRED PROPERTY size: default::Size;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE CONSTRAINT std::exclusive ON ((.name, .album));
      CREATE INDEX ON ((.name, .album));
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY track: std::int16;
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
  };
  ALTER TYPE default::Artist {
      CREATE LINK musics := (SELECT
          .albums.musics
      );
  };
  CREATE TYPE default::Genre {
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY name: std::str {
          CREATE CONSTRAINT std::exclusive;
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
  ALTER TYPE default::Artist {
      CREATE LINK genres := (SELECT
          .musics.genre
      );
  };
  CREATE TYPE default::Keyword {
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY name: std::str {
          CREATE CONSTRAINT std::exclusive;
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
  };
  ALTER TYPE default::Artist {
      CREATE LINK keywords := (SELECT
          .musics.keywords
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>math::mean(.musics.rating), 2)
      );
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
  };
  ALTER TYPE default::Album {
      CREATE LINK keywords := (SELECT
          .musics.keywords
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>math::mean(.musics.rating), 2)
      );
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
  };
  CREATE TYPE default::Folder {
      CREATE REQUIRED PROPERTY ipv4: std::str;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE CONSTRAINT std::exclusive ON ((.name, .ipv4));
      CREATE INDEX ON ((.name, .ipv4));
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
      CREATE REQUIRED PROPERTY user: std::str;
  };
  ALTER TYPE default::Music {
      CREATE MULTI LINK folders: default::Folder {
          CREATE PROPERTY path: std::str;
      };
      CREATE PROPERTY paths := (SELECT
          .folders@path
      );
  };
  ALTER TYPE default::Folder {
      CREATE MULTI LINK musics := (.<folders[IS default::Music]);
  };
  ALTER TYPE default::Genre {
      CREATE MULTI LINK musics := (.<genre[IS default::Music]);
      CREATE LINK keywords := (SELECT
          .musics.keywords
      );
      CREATE PROPERTY length := (SELECT
          std::sum(.musics.length)
      );
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>math::mean(.musics.rating), 2)
      );
  };
  ALTER TYPE default::Keyword {
      CREATE MULTI LINK musics := (.<keywords[IS default::Music]);
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>math::mean(.musics.rating), 2)
      );
  };
  CREATE SCALAR TYPE default::`Limit` EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
};
