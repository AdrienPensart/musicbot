CREATE MIGRATION m1ujesi6dqtebh73v3bnsq72xpb2hwgg5dllqqkheexmkso4i6twhq
    ONTO m13crgfvep7xcdefcn5pletvar7qnazygaia2z3lcsh4yyob3tv47a
{
  ALTER TYPE default::Folder {
      CREATE LINK albums := (SELECT
          .musics.album
      );
      CREATE PROPERTY n_albums := (SELECT
          std::count(.albums)
      );
  };
};
