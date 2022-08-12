CREATE MIGRATION m17ro7levuo4usv3o5ysiycyfngmnhiuj5ajd6jux3nhrbtxznszyq
    ONTO m14iygpbnrtfjgjehmzpcjmnze5ejamjdcnsepj5atcke5ru2la2tq
{
  CREATE SCALAR TYPE default::`Limit` EXTENDING std::int64 {
      CREATE CONSTRAINT std::min_value(0);
  };
};
