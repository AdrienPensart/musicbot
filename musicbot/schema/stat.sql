create table if not exists musicbot_public.stat
(
    id           bigserial primary key,
    user_id      integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot(),
    musics       bigint not null default 0,
    albums       bigint not null default 0,
    artists      bigint not null default 0,
    genres       bigint not null default 0,
    keywords     bigint not null default 0,
    duration     bigint not null default 0,
    size         bigint not null default 0,
    created_at   timestamp with time zone default now(),
    updated_at   timestamp with time zone default now()
);

create index if not exists stat_user_idx on musicbot_public.stat (user_id);

alter table if exists musicbot_public.stat enable row level security;
grant select on table musicbot_public.stat to musicbot_anonymous, musicbot_user;
grant insert, update, delete on table musicbot_public.stat to musicbot_user;
grant usage on sequence musicbot_public.stat_id_seq to musicbot_user;

drop policy if exists insert_stat on musicbot_public.stat cascade;
create policy insert_stat on musicbot_public.stat for insert with check (user_id = musicbot_public.current_musicbot());

drop policy if exists select_stat on musicbot_public.stat cascade;
create policy select_stat on musicbot_public.stat for select using (user_id = musicbot_public.current_musicbot());

drop policy if exists update_stat on musicbot_public.stat cascade;
create policy update_stat on musicbot_public.stat for update using (user_id = musicbot_public.current_musicbot());

drop policy if exists delete_stat on musicbot_public.stat cascade;
create policy delete_stat on musicbot_public.stat for delete using (user_id = musicbot_public.current_musicbot());


drop aggregate if exists musicbot_public.array_cat_agg(anyarray) cascade;
create aggregate musicbot_public.array_cat_agg(anyarray) (
    SFUNC=array_cat,
    STYPE=anyarray
);

create or replace function musicbot_public.do_stat(
    min_duration integer default 0,
    max_duration integer default +2147483647,
    min_size     integer default 0,
    max_size     integer default +2147483647,
    min_rating   float default 0.0,
    max_rating   float default 5.0,
    artists      text[] default '{}',
    no_artists   text[] default '{}',
    albums       text[] default '{}',
    no_albums    text[] default '{}',
    titles       text[] default '{}',
    no_titles    text[] default '{}',
    genres       text[] default '{}',
    no_genres    text[] default '{}',
    formats      text[] default '{}',
    no_formats   text[] default '{}',
    keywords     text[] default '{}',
    no_keywords  text[] default '{}',
    shuffle      boolean default 'false',
    relative     boolean default 'false',
    "limit"      integer default +2147483647,
    youtubes     text[] default '{}',
    no_youtubes  text[] default '{}',
    spotifys     text[] default '{}',
    no_spotifys  text[] default '{}'
)
returns musicbot_public.stat as
$$
    select
        row_number() over () as id,
        musicbot_public.current_musicbot(),
        count(distinct f.path) as musics,
        count(distinct f.album) as albums,
        count(distinct f.artist) as artists,
        count(distinct f.genre) as genres,
        (select count(distinct k.keywords) from (select unnest(musicbot_public.array_cat_agg(f.keywords)) as keywords) as k) as keywords,
        coalesce(sum(f.duration),0) as duration,
        coalesce(sum(f.size),0) as size,
        now(),
        now()
    from musicbot_public.do_filter(
            min_duration => do_stat.min_duration,
            max_duration => do_stat.max_duration,
            min_size     => do_stat.min_size,
            max_size     => do_stat.max_size,
            min_rating   => do_stat.min_rating,
            max_rating   => do_stat.max_rating,
            artists      => do_stat.artists,
            no_artists   => do_stat.no_artists,
            albums       => do_stat.albums,
            no_albums    => do_stat.no_albums,
            titles       => do_stat.titles,
            no_titles    => do_stat.no_titles,
            genres       => do_stat.genres,
            no_genres    => do_stat.no_genres,
            formats      => do_stat.formats,
            no_formats   => do_stat.no_formats,
            keywords     => do_stat.keywords,
            no_keywords  => do_stat.no_keywords,
            shuffle      => do_stat.shuffle,
            relative     => do_stat.relative,
            "limit"      => do_stat."limit",
            youtubes     => do_stat.youtubes,
            no_youtubes  => do_stat.no_youtubes,
            spotifys     => do_stat.spotifys,
            no_spotifys  => do_stat.no_spotifys
        ) f;
$$ language sql stable;
