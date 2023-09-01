CREATE MIGRATION m1mvpk5zl3uphormlsjlipcmn5qsphcfsgtnxyh63omeunuolkqola
    ONTO m1rbl4jmjaopmijcojwjlxpqrecj74rapsx3voxcfyx6gmjpuadl3a
{
  CREATE ALIAS default::artists := (
      SELECT
          default::Artist {
              *,
              human_size,
              human_duration,
              all_keywords,
              all_genres,
              n_albums,
              n_musics
          }
      ORDER BY
          .name ASC
  );
};
