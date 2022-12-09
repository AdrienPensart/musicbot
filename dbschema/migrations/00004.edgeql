CREATE MIGRATION m1vtq2yfqg5flkw56chh5fx6miersp6rauot2n3yuj7ohhlgzfmybq
    ONTO m17ro7levuo4usv3o5ysiycyfngmnhiuj5ajd6jux3nhrbtxznszyq
{
  ALTER TYPE default::Album {
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
  };
  ALTER TYPE default::Artist {
      CREATE LINK genres := (SELECT
          .musics.genre
      );
  };
};
