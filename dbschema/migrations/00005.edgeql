CREATE MIGRATION m1ll44jx2l454tqbeaqe6c4kssjsd3gaiuwaom5jtki22dvbgisbfa
    ONTO m1vkbcskhpl6xb77uzkdp6axbq7uudh72kwvwldvwj7wx5aw32yzna
{
  ALTER TYPE default::Album {
      CREATE PROPERTY title := (SELECT
          ((.artist.name ++ ' - ') ++ .name)
      );
  };
  ALTER TYPE default::Music {
      ALTER PROPERTY title {
          USING (SELECT
              ((.album.title ++ ' - ') ++ .name)
          );
      };
  };
};
