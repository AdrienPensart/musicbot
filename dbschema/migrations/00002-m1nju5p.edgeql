CREATE MIGRATION m1nju5phzhlxhdadkoezl6fzwhblfmut36uwzzmijeipxjg4anzeva
    ONTO m14r34ka5fo7fpp3z7et6ib6dgb2hpkzepiekod4bt3waybknnylyq
{
  ALTER TYPE default::Music {
      ALTER LINK folders {
          SET REQUIRED USING (<default::Folder><std::uuid>'e6af2402-1f60-11ef-972a-dfb472d7e59b');
      };
  };
};
