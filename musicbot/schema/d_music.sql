create table if not exists musicbot_public.music
(
    id         serial primary key,
    user_id    integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot(),
    title      text default '',
    album      text default '',
    genre      text default '',
    artist     text default '',
    number     integer default 0,
    rating     float default 0.0,
    duration   integer default 0,
    keywords   text[] default '{}',
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now(),
    constraint unique_music unique (title, album, artist, user_id) deferrable
);

create index if not exists music_user_idx on musicbot_public.music (user_id);

alter table if exists musicbot_public.music enable row level security;
alter table if exists musicbot_public.music force row level security;
grant usage on sequence musicbot_public.music_id_seq to musicbot_user;

grant select on table musicbot_public.music to musicbot_anonymous, musicbot_user;
grant insert, update, delete on table musicbot_public.music to musicbot_user;

drop policy if exists insert_music on musicbot_public.music cascade;
create policy insert_music on musicbot_public.music for insert with check (user_id = musicbot_public.current_musicbot());

drop policy if exists select_music on musicbot_public.music cascade;
create policy select_music on musicbot_public.music for select using (user_id = musicbot_public.current_musicbot());

drop policy if exists update_music on musicbot_public.music cascade;
create policy update_music on musicbot_public.music for update using (user_id = musicbot_public.current_musicbot());

drop policy if exists delete_music on musicbot_public.music cascade;
create policy delete_music on musicbot_public.music for delete using (user_id = musicbot_public.current_musicbot());

drop aggregate if exists musicbot_public.array_cat_agg(anyarray) cascade;
create aggregate musicbot_public.array_cat_agg(anyarray) (
    SFUNC=array_cat,
    STYPE=anyarray
);


drop type if exists musicbot_public.music_title cascade;
drop type if exists musicbot_public.album cascade;
drop type if exists musicbot_public.artist cascade;
drop type if exists musicbot_public.genre cascade;
drop type if exists musicbot_public.keyword cascade;

create type musicbot_public.music_title as (id bigint, name text);
create type musicbot_public.album as (id bigint, name text, musics musicbot_public.music_title[]);
create type musicbot_public.artist as (id bigint, name text, albums musicbot_public.album[]);
create type musicbot_public.genre as (id bigint, name text);
create type musicbot_public.keyword as (id bigint, name text);

create or replace function musicbot_public.artists_tree() returns setof musicbot_public.artist
as $$
    select row_number() over (order by artist) as id, artist, array_agg((id, album, musics)::musicbot_public.album) as albums
    from (
        select row_number() over (order by album) as id, artist, album, array_agg(row(id, title)::musicbot_public.music_title) as musics
        from musicbot_public.music
        where artist != '' and album != '' and title != ''
        group by artist, album
        order by artist
    ) as albums
    group by artist;
$$ language sql stable;

create or replace function musicbot_public.genres_tree() returns setof musicbot_public.genre
as $$
    select row_number() over () as id, genre from musicbot_public.music where genre != '' group by genre order by genre asc;
$$ language sql stable;

create or replace function musicbot_public.keywords_tree() returns setof musicbot_public.keyword
as $$
    select row_number() over () as id, keyword from (select unnest(musicbot_public.array_cat_agg(keywords)) as keyword from musicbot_public.music where array_length(keywords, 1) > 0) k group by keyword order by keyword asc;
$$ language sql stable;

create or replace function musicbot_public.delete_all_music() returns void as $$
    delete from musicbot_public.music;
$$ language sql;
