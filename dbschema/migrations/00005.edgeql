CREATE MIGRATION m147wawb7bicmwmrniw5cmsjsndu2nzvhfkiwlvn3bher5acwmeiba
    ONTO m1ewoulh6y7dpygsok2quapclfwzhwcw2sdo6fibuk7qn7plcyzjua
{
  ALTER TYPE default::Folder {
      CREATE PROPERTY duration := (SELECT
          std::to_duration(seconds := <std::float64>.length)
      );
      CREATE PROPERTY human_duration := (SELECT
          std::to_str(.duration, 'HH24:MI:SS')
      );
      CREATE PROPERTY size := (SELECT
          std::sum(.musics.size)
      );
      CREATE PROPERTY human_size := (SELECT
          default::bytes_to_human(.size)
      );
  };
};
