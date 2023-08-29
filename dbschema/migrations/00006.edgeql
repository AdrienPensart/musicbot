CREATE MIGRATION m1ndmbf5oohr7p4ga3iqkbu33mxy6uacpedtybzo74zfqssjqvj7va
    ONTO m1zl7bfrsjjfhbqtufffars4gharan5anwygrofhpq5t54z4pnlmaq
{
  ALTER TYPE default::Artist {
      ALTER LINK keywords {
          USING (SELECT
              std::assert_distinct(std::array_unpack(std::array_agg((SELECT
                  .musics.keywords
              ORDER BY
                  .name ASC
              ))))
          );
      };
  };
};
