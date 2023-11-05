CREATE MIGRATION m17eevkmyqw475uqtrfmi4ujusqs7zmgbmwn6fxp6u3c74wjoolhra
    ONTO m1ouwgig2vkdvlvqbj4znwmxqasevyrnt67jlrsqhm3sjo6ds4i6gq
{
  ALTER TYPE default::Genre {
      CREATE LINK albums := (SELECT
          .musics.album
      );
      CREATE PROPERTY n_albums := (SELECT
          std::count(.albums)
      );
      CREATE LINK artists := (SELECT
          .musics.artist
      );
      CREATE PROPERTY n_artists := (SELECT
          std::count(.artists)
      );
      CREATE PROPERTY all_artists := (SELECT
          std::to_str(std::array_agg(.musics.artist.name), ' ')
      );
  };
  ALTER TYPE default::Keyword {
      CREATE LINK albums := (SELECT
          .musics.album
      );
      CREATE PROPERTY n_albums := (SELECT
          std::count(.albums)
      );
      CREATE LINK artists := (SELECT
          .musics.artist
      );
      CREATE PROPERTY n_artists := (SELECT
          std::count(.artists)
      );
      CREATE PROPERTY all_artists := (SELECT
          std::to_str(std::array_agg(.musics.artist.name), ' ')
      );
  };
};
