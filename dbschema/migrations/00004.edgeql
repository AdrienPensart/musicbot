CREATE MIGRATION m1y3zpy7ldhbvnte6o4ovzt7yloelnmnd2w7aeuq3kmqqr7kwesama
    ONTO m1wh2vxzziej3fikhfubxhxkaoj2c2vjvurfrmlmgquwhriza33dfq
{
  ALTER FUNCTION default::bytes_to_human(size: std::int64, k: std::int64 = 1000, decimals: std::int64 = 2, units: array<std::str> = [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']) USING (SELECT
      (('0' ++ (units)[0]) IF (size = 0) ELSE (WITH
          i := 
              <std::int64>math::floor((math::ln(math::abs(size)) / math::ln(k)))
      SELECT
          (std::to_str(std::round(<std::decimal>(size / (k ^ i)), decimals)) ++ (units)[i])
      ))
  );
};
