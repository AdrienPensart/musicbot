CREATE MIGRATION m1acwuaxdregyugpjkx7fptmy3e2hda4yaq5ww6fjg5sjajlolczna
    ONTO m17u3ztutw3czku6xjpqpxrrwyd2j4puyfbnhvdr3pkea3l3hvicoq
{
  CREATE FUNCTION default::search(NAMED ONLY pattern: std::str) -> SET OF default::Music {
      CREATE ANNOTATION std::title := 'Search musics';
      USING (SELECT
          default::Music
      FILTER
          (((((.name ILIKE pattern) OR (.genre.name ILIKE pattern)) OR (.album.name ILIKE pattern)) OR (.artist.name ILIKE pattern)) OR (.keywords.name ILIKE pattern))
      ORDER BY
          .artist.name ASC THEN
          .album.name ASC THEN
          .track ASC THEN
          .name ASC
      )
  ;};
};
