CREATE MIGRATION m1vvmk4g5onoi2ja7ote3xorjxb7x5w7phvywwcaxx36py6zqgjssq
    ONTO m1n46zkg4ec75ff6drbbztljf3svo4hvnmby2h5u2akmqnmhtpzjiq
{
  DROP GLOBAL default::current_user;
  ALTER TYPE default::Album {
      CREATE CONSTRAINT std::exclusive ON ((.name, .artist));
  };
  ALTER TYPE default::Album {
      DROP CONSTRAINT std::exclusive ON ((.name, .user, .artist));
      DROP LINK user;
  };
  ALTER TYPE default::Artist {
      CREATE CONSTRAINT std::exclusive ON (.name);
  };
  ALTER TYPE default::Artist {
      DROP CONSTRAINT std::exclusive ON ((.name, .user));
      DROP LINK user;
  };
  ALTER TYPE default::Folder {
      DROP CONSTRAINT std::exclusive ON ((.name, .user, .username, .ipv4));
  };
  ALTER TYPE default::Folder {
      CREATE CONSTRAINT std::exclusive ON ((.name, .username, .ipv4));
      DROP LINK user;
  };
  ALTER TYPE default::Genre {
      CREATE CONSTRAINT std::exclusive ON (.name);
  };
  ALTER TYPE default::Genre {
      DROP CONSTRAINT std::exclusive ON ((.name, .user));
      DROP LINK user;
  };
  ALTER TYPE default::Keyword {
      CREATE CONSTRAINT std::exclusive ON (.name);
  };
  ALTER TYPE default::Keyword {
      DROP CONSTRAINT std::exclusive ON ((.name, .user));
      DROP LINK user;
  };
  ALTER TYPE default::Music {
      DROP CONSTRAINT std::exclusive ON ((.name, .user, .album));
  };
  ALTER TYPE default::Music {
      CREATE CONSTRAINT std::exclusive ON ((.name, .album));
      DROP LINK user;
  };
  DROP TYPE default::User;
  DROP EXTENSION auth;
  DROP EXTENSION pgcrypto;
};
