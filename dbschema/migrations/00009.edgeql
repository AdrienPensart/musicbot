CREATE MIGRATION m1ouwgig2vkdvlvqbj4znwmxqasevyrnt67jlrsqhm3sjo6ds4i6gq
    ONTO m1ujesi6dqtebh73v3bnsq72xpb2hwgg5dllqqkheexmkso4i6twhq
{
  ALTER TYPE default::Folder {
      CREATE PROPERTY n_keywords := (SELECT
          std::count(.keywords)
      );
  };
};
