CREATE MIGRATION m1wh2vxzziej3fikhfubxhxkaoj2c2vjvurfrmlmgquwhriza33dfq
    ONTO m1gghkh44p76fbqu4e4y236xq7afr567dlmcyzbppgmerkwrnmcwuq
{
  CREATE FUNCTION default::bytes_to_human(size: std::int64, k: std::int64 = 1000, decimals: std::int64 = 2, units: array<std::str> = [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']) ->  std::str {
      CREATE ANNOTATION std::title := 'Convert a byte size to human readable string';
      USING (SELECT
          ('0 B' IF (size = 0) ELSE (WITH
              i := 
                  <std::int64>math::floor((math::ln(math::abs(size)) / math::ln(k)))
          SELECT
              (std::to_str(std::round(<std::decimal>(size / (k ^ i)), decimals)) ++ (units)[i])
          ))
      )
  ;};
};
