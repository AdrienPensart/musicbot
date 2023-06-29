CREATE MIGRATION m1gghkh44p76fbqu4e4y236xq7afr567dlmcyzbppgmerkwrnmcwuq
    ONTO m1xu2nzycwhds2djl4kku3twf5e2yiuzsstvpqjsvosq4tbqovojyq
{
  ALTER TYPE default::Album {
      CREATE INDEX ON ((.name, .artist));
  };
  ALTER TYPE default::Folder {
      CREATE INDEX ON ((.name, .ipv4));
  };
  ALTER TYPE default::Music {
      CREATE INDEX ON ((.name, .album));
  };
};
