create table if not exists musicbot_public.stat
(
    id           bigserial primary key,
    user_id      integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot(),
    musics       bigint not null default 0,
    albums       bigint not null default 0,
    artists      bigint not null default 0,
    genres       bigint not null default 0,
    links        bigint not null default 0,
    keywords     bigint not null default 0,
    duration     bigint not null default 0,
    created_at   timestamp with time zone default now(),
    updated_at   timestamp with time zone default now()
);

create index if not exists stat_user_idx on musicbot_public.stat (user_id);

alter table if exists musicbot_public.stat enable row level security;
--alter table if exists musicbot_public.stat force row level security;

grant select on table musicbot_public.stat to musicbot_anonymous, musicbot_user;
grant insert, update, delete on table musicbot_public.stat to musicbot_user;
grant usage on sequence musicbot_public.stat_id_seq to musicbot_user;

drop policy if exists insert_stat on musicbot_public.stat cascade;
create policy insert_stat on musicbot_public.stat for insert with check (user_id = musicbot_public.current_musicbot());

drop policy if exists select_stat on musicbot_public.stat cascade;
create policy select_stat on musicbot_public.stat for select using (user_id = musicbot_public.current_musicbot());

drop policy if exists update_stat on musicbot_public.stat cascade;
create policy update_stat on musicbot_public.stat for update using (user_id = musicbot_public.current_musicbot());

drop policy if exists upsert_stat on musicbot_public.music cascade;
create policy upsert_stat on musicbot_public.music for update with check (user_id = musicbot_public.current_musicbot());

drop policy if exists delete_stat on musicbot_public.stat cascade;
create policy delete_stat on musicbot_public.stat for delete using (user_id = musicbot_public.current_musicbot());

create or replace function musicbot_public.do_stat(
    min_duration integer default 0,
    max_duration integer default +2147483647,
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
    keywords     text[] default '{}',
    no_keywords  text[] default '{}',
    shuffle      boolean default 'false',
    "limit"      integer default +2147483647
)
returns musicbot_public.stat as
$$
    select
        row_number() over () as id,
        musicbot_public.current_musicbot(),
        count(distinct m.id) as musics,
        count(distinct m.album) as albums,
        count(distinct m.artist) as artists,
        count(distinct m.genre) as genres,
        (select count(distinct link) from (select unnest(musicbot_public.array_cat_agg(m.links)) as link) as l) as links,
        (select count(distinct keyword) from (select unnest(musicbot_public.array_cat_agg(m.keywords)) as keyword) as k) as keywords,
        coalesce(sum(m.duration),0) as duration,
        now(),
        now()
    from musicbot_public.playlist
    (
        min_duration => do_stat.min_duration,
        max_duration => do_stat.max_duration,
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
        keywords     => do_stat.keywords,
        no_keywords  => do_stat.no_keywords,
        shuffle      => do_stat.shuffle,
        "limit"      => do_stat."limit"
    ) m;
$$ language sql stable;
