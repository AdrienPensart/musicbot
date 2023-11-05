CREATE MIGRATION m1hbswew3psc43baxfkhrr35djp75jyqbtcmmw5ldhtw4onaf7w6gq
    ONTO m1mvpk5zl3uphormlsjlipcmn5qsphcfsgtnxyh63omeunuolkqola
{
  ALTER TYPE default::Album {
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
  };
  ALTER TYPE default::Artist {
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
  };
  ALTER TYPE default::Folder {
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
  };
  ALTER TYPE default::Genre {
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
  };
  ALTER TYPE default::Keyword {
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
  };
  ALTER TYPE default::Music {
      CREATE INDEX fts::index ON (fts::with_options(.name, language := fts::Language.eng));
  };
};
