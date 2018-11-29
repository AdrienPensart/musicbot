
create table if not exists musicbot_public.stat
(
    id bigserial primary key,
    musics   bigint not null default 0,
    albums   bigint not null default 0,
    artists  bigint not null default 0,
    genres   bigint not null default 0,
    keywords bigint not null default 0,
    duration bigint not null default 0,
    size     bigint not null default 0
);
--alter table if exists public.stat enable row level security;
--grant select on table public.stat to musicbot_anonymous, musicbot_user;

drop aggregate if exists musicbot_public.array_cat_agg(anyarray) cascade;
create aggregate musicbot_public.array_cat_agg(anyarray) (
    SFUNC=array_cat,
    STYPE=anyarray
);

create or replace function musicbot_public.do_stat(mf musicbot_public.filter)
returns musicbot_public.stat as
$$
    select
        row_number() over () as id,
        count(distinct f.path) as musics,
        count(distinct f.album) as albums,
        count(distinct f.artist) as artists,
        count(distinct f.genre) as genres,
        (select count(distinct k.keywords) from (select unnest(musicbot_public.array_cat_agg(f.keywords)) as keywords) as k) as keywords,
        coalesce(sum(f.duration),0) as duration,
        coalesce(sum(f.size),0) as size
    from musicbot_public.do_filter(mf) f;
$$ language sql stable;
grant execute on function musicbot_public.do_stat to musicbot_user;
