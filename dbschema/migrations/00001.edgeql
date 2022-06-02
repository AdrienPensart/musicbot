CREATE MIGRATION m1ol6ewpyqf6dokzsaxwrevtoiygivtk4om6vlsjukwiiudrdglsiq
    ONTO initial
{
  CREATE EXTENSION edgeql_http VERSION '1.0';
  CREATE EXTENSION graphql VERSION '1.0';
  CREATE ABSTRACT TYPE default::Entity {
      CREATE REQUIRED PROPERTY created_at -> std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE REQUIRED PROPERTY updated_at -> std::datetime {
          SET default := (std::datetime_current());
      };
  };
  CREATE TYPE default::Album EXTENDING default::Entity;
  CREATE TYPE default::Artist EXTENDING default::Entity {
      ALTER PROPERTY name {
          SET OWNED;
          SET REQUIRED;
          SET TYPE std::str;
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Album {
      CREATE REQUIRED LINK artist -> default::Artist {
          ON TARGET DELETE  DELETE SOURCE;
      };
      CREATE CONSTRAINT std::exclusive ON ((.name, .artist));
  };
  ALTER TYPE default::Artist {
      CREATE MULTI LINK albums := (.<artist[IS default::Album]);
  };
  CREATE SCALAR TYPE default::Rating EXTENDING std::float32 {
      CREATE CONSTRAINT std::one_of(0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0);
  };
  CREATE SCALAR TYPE default::Size EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
  CREATE TYPE default::Music EXTENDING default::Entity {
      CREATE REQUIRED LINK album -> default::Album {
          ON TARGET DELETE  DELETE SOURCE;
      };
      CREATE CONSTRAINT std::exclusive ON ((.name, .album));
      CREATE REQUIRED PROPERTY duration -> std::duration;
      CREATE MULTI PROPERTY links -> std::str;
      CREATE REQUIRED PROPERTY rating -> default::Rating {
          SET default := 0.0;
      };
      CREATE REQUIRED PROPERTY size -> default::Size;
      CREATE PROPERTY track -> std::int16;
  };
  ALTER TYPE default::Album {
      CREATE MULTI LINK musics := (.<album[IS default::Music]);
  };
  CREATE TYPE default::Genre EXTENDING default::Entity {
      ALTER PROPERTY name {
          SET OWNED;
          SET REQUIRED;
          SET TYPE std::str;
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::Keyword EXTENDING default::Entity {
      ALTER PROPERTY name {
          SET OWNED;
          SET REQUIRED;
          SET TYPE std::str;
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Music {
      CREATE REQUIRED LINK genre -> default::Genre {
          ON TARGET DELETE  DELETE SOURCE;
      };
      CREATE MULTI LINK keywords -> default::Keyword;
  };
  ALTER TYPE default::Genre {
      CREATE MULTI LINK musics := (.<genre[IS default::Music]);
  };
  ALTER TYPE default::Keyword {
      CREATE MULTI LINK musics := (.<keywords[IS default::Music]);
  };
};