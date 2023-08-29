CREATE MIGRATION m1badyglq4neyj2b4jaccc7etiwlxbcmhvvlkmolcnwvezx2jjbd7q
    ONTO m1ndmbf5oohr7p4ga3iqkbu33mxy6uacpedtybzo74zfqssjqvj7va
{
  ALTER TYPE default::Artist {
      ALTER LINK keywords {
          USING (SELECT
              .musics.keywords
          );
      };
  };
};
