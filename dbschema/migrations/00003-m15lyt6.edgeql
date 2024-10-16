CREATE MIGRATION m15lyt6fjwshzia44sefayxw7jxkr6rnes5tgh5kmsdcxlvmqzqu2q
    ONTO m1nju5phzhlxhdadkoezl6fzwhblfmut36uwzzmijeipxjg4anzeva
{
  CREATE TYPE default::Playlist {
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
      CREATE MULTI LINK musics: default::Music;
  };
};
