CREATE MIGRATION m14iygpbnrtfjgjehmzpcjmnze5ejamjdcnsepj5atcke5ru2la2tq
    ONTO m1flc2pfe5xahy324s7lsau5oqv5wo74w3iiiplkekpnhuxyp2axaq
{
  ALTER TYPE default::Music {
      CREATE PROPERTY paths := (SELECT
          .folders@path
      );
  };
};
