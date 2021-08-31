create schema if not exists musicbot_public;
create schema if not exists musicbot_private;

drop aggregate if exists musicbot_public.array_cat_agg(anyarray) cascade;
create aggregate musicbot_public.array_cat_agg(anyarray) (
    sfunc=array_cat,
    stype=anyarray,
    initcond='{}'
);
