CREATE MIGRATION m1ewoulh6y7dpygsok2quapclfwzhwcw2sdo6fibuk7qn7plcyzjua
    ONTO m1hbswew3psc43baxfkhrr35djp75jyqbtcmmw5ldhtw4onaf7w6gq
{
  ALTER TYPE default::Album {
      CREATE LINK genres := (SELECT
          .musics.genre
      );
      CREATE PROPERTY n_genres := (SELECT
          std::count(.genres)
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
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
  };
  ALTER TYPE default::Artist {
      CREATE PROPERTY n_genres := (SELECT
          std::count(.genres)
      );
  };
  ALTER TYPE default::Folder {
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
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
      CREATE PROPERTY rating := (SELECT
          <std::float64>std::round(<std::decimal>math::mean(.musics.rating), 2)
      );
  };
  ALTER TYPE default::Keyword {
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
  };
};
