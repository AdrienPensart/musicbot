CREATE MIGRATION m1zl7bfrsjjfhbqtufffars4gharan5anwygrofhpq5t54z4pnlmaq
    ONTO m1y3zpy7ldhbvnte6o4ovzt7yloelnmnd2w7aeuq3kmqqr7kwesama
{
  ALTER TYPE default::Artist {
      ALTER LINK keywords {
          USING (SELECT
              std::assert_distinct(std::array_unpack(std::array_agg(.musics.keywords)))
          );
      };
  };
};
