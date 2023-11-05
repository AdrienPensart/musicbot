CREATE MIGRATION m1f7zc7caiioecpoveim5ulxbbknclmyx4dzphag5iavzoloxlxd5a
    ONTO m17eevkmyqw475uqtrfmi4ujusqs7zmgbmwn6fxp6u3c74wjoolhra
{
  ALTER TYPE default::Album {
      ALTER PROPERTY rating {
          USING (SELECT
              <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
          );
      };
  };
  ALTER TYPE default::Artist {
      ALTER PROPERTY rating {
          USING (SELECT
              <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
          );
      };
  };
  ALTER TYPE default::Folder {
      DROP PROPERTY rating;
  };
  ALTER TYPE default::Genre {
      ALTER PROPERTY rating {
          USING (SELECT
              <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
          );
      };
  };
  ALTER TYPE default::Keyword {
      ALTER PROPERTY rating {
          USING (SELECT
              <std::float64>std::round(<std::decimal>math::mean((.musics.rating ?? {0.0})), 2)
          );
      };
  };
};
