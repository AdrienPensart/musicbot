CREATE MIGRATION m1cppbk6y37woati47fec5jgsfwtlfodvtnmjdyhfqvsordrwx5pbq
    ONTO m147wawb7bicmwmrniw5cmsjsndu2nzvhfkiwlvn3bher5acwmeiba
{
  DROP ALIAS default::artists;
  ALTER TYPE default::Folder {
      CREATE LINK artists := (SELECT
          .musics.artist
      );
  };
  ALTER TYPE default::Folder {
      CREATE PROPERTY n_artists := ((
          n_artists := std::count(.artists)
      ));
      CREATE PROPERTY all_artists := (SELECT
          std::to_str(std::array_agg(.musics.artist.name), ' ')
      );
  };
  ALTER TYPE default::Genre {
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
      CREATE PROPERTY n_musics := (SELECT
          std::count(.musics)
      );
  };
  ALTER TYPE default::Keyword {
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
  ALTER TYPE default::Music {
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
  };
};
