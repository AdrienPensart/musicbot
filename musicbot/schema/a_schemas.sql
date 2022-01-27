create schema if not exists musicbot_public;
create schema if not exists musicbot_private;

drop aggregate if exists musicbot_public.array_cat_agg(anycompatiblearray) cascade;
create aggregate musicbot_public.array_cat_agg(anycompatiblearray) (
    sfunc=array_cat,
    stype=anycompatiblearray,
    initcond='{}'
);
