CREATE MIGRATION m1h32vi6auvkigqcclgh525orxfjhdwbcpzbspbg3vl3ajiekir7gq
    ONTO m1vtq2yfqg5flkw56chh5fx6miersp6rauot2n3yuj7ohhlgzfmybq
{
  ALTER TYPE default::Artist {
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
  };
};
