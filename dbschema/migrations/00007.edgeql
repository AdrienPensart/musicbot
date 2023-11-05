CREATE MIGRATION m13crgfvep7xcdefcn5pletvar7qnazygaia2z3lcsh4yyob3tv47a
    ONTO m1cppbk6y37woati47fec5jgsfwtlfodvtnmjdyhfqvsordrwx5pbq
{
  ALTER TYPE default::Folder {
      ALTER PROPERTY n_artists {
          USING (SELECT
              std::count(.artists)
          );
      };
  };
};
