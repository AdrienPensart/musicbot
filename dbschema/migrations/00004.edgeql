CREATE MIGRATION m1vkbcskhpl6xb77uzkdp6axbq7uudh72kwvwldvwj7wx5aw32yzna
    ONTO m1mawhozxatfw7ecqk4ln2jv7rakw4x4ff342vyjorz7y2u7itbs4q
{
  ALTER TYPE default::Music {
      CREATE PROPERTY title := (SELECT
          ((((.artist.name ++ ' - ') ++ .album.name) ++ ' - ') ++ .name)
      );
  };
};
