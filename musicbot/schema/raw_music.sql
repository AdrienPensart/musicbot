create table if not exists musicbot_public.raw_music
(
    id         serial primary key,
    user_id    integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot(),
    path       text not null,
    title      text default '',
    album      text default '',
    genre      text default '',
    artist     text default '',
    folder     text default '',
    youtube    text default '',
    spotify    text default '',
    number     integer default 0,
    rating     float default 0.0,
    duration   integer default 0,
    size       integer default 0,
    keywords   text[] default '{}',
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now(),
    --unique(path, user_id)
    unique(path, user_id) deferrable
    --unique(path, user_id) initially deferred
);

--create index if not exists path_idx on musicbot_public.raw_music (path);
create index if not exists raw_music_user_idx on musicbot_public.raw_music (user_id);
--create index if not exists path_user_idx on musicbot_public.raw_music (path, user_id);

alter table if exists musicbot_public.raw_music enable row level security;
alter table if exists musicbot_public.raw_music force row level security;
grant usage on sequence musicbot_public.raw_music_id_seq to musicbot_user;

grant select on table musicbot_public.raw_music to musicbot_anonymous, musicbot_user;
grant insert, update, delete on table musicbot_public.raw_music to musicbot_user;

alter table if exists musicbot_public.raw_music enable row level security;

drop policy if exists insert_raw_music on musicbot_public.raw_music cascade;
create policy insert_raw_music on musicbot_public.raw_music for insert with check (user_id = musicbot_public.current_musicbot());

drop policy if exists select_raw_music on musicbot_public.raw_music cascade;
create policy select_raw_music on musicbot_public.raw_music for select using (user_id = musicbot_public.current_musicbot());

drop policy if exists update_raw_music on musicbot_public.raw_music cascade;
create policy update_raw_music on musicbot_public.raw_music for update using (user_id = musicbot_public.current_musicbot());

drop policy if exists delete_raw_music on musicbot_public.raw_music cascade;
create policy delete_raw_music on musicbot_public.raw_music for delete using (user_id = musicbot_public.current_musicbot());

create or replace function musicbot_public.bulk_insert(data text)
returns void as
$$
begin
    -- TODO: no need this when postgresql 11.3 will be out
    if data = 'W10=' then
        return;
    end if;
    set constraints musicbot_public.raw_music_path_user_id_key deferred;
    with records as (
        select title, album, genre, artist, folder, youtube, spotify, number, path, rating, duration, size, keywords
        from json_populate_recordset(null::musicbot_public.raw_music, convert_from(decode(data, 'BASE64'), 'UTF-8')::json)
    ), recent_music as (
        insert into musicbot_public.raw_music (title, album, genre, artist, folder, youtube, spotify, number, path, rating, duration, size, keywords)
        select * from records
    ), duplicates as (
    select distinct on (path) id from musicbot_public.raw_music order by path, id desc
    )
    delete from musicbot_public.raw_music where id in (select id from duplicates);
end
$$ language plpgsql;

create or replace function musicbot_public.upsert_music(
    path       text default '',
    title      text default '',
    album      text default '',
    genre      text default '',
    artist     text default '',
    folder     text default '',
    youtube    text default '',
    spotify    text default '',
    number     integer default 0,
    rating     float default 0.0,
    duration   integer default 0,
    size       integer default 0,
    keywords   text[] default '{}'
) returns musicbot_public.raw_music as
$$
declare
    output musicbot_public.raw_music;
begin
    if exists (select 1 from musicbot_public.raw_music as m where m.path = upsert_music.path limit 1) then
        update musicbot_public.raw_music as m
        set artist   = upsert_music.artist,
            genre    = upsert_music.genre,
            folder   = upsert_music.folder,
            album    = upsert_music.album,
            rating   = upsert_music.rating,
            duration = upsert_music.duration,
            title    = upsert_music.title,
            number   = upsert_music.number,
            size     = upsert_music.size,
            youtube  = upsert_music.youtube,
            spotify  = upsert_music.spotify,
            keywords = upsert_music.keywords
        where m.path = upsert_music.path
        returning *
        into output;
    else
        insert into musicbot_public.raw_music (artist, genre, folder, album, rating, duration, path, title, number, size, youtube, spotify, keywords)
        values (artist, genre, folder, album, rating, duration, path, title, number, size, youtube, spotify, keywords)
        returning *
        into output;
    end if;
    return output;
end
$$ language plpgsql;

drop aggregate if exists musicbot_public.array_cat_agg(anyarray) cascade;
create aggregate musicbot_public.array_cat_agg(anyarray) (
    SFUNC=array_cat,
    STYPE=anyarray
);

create or replace function musicbot_public.folders() returns setof text as $$
    select distinct folder from musicbot_public.raw_music order by folder asc;
$$ language sql stable;

drop type if exists musicbot_public.music cascade;
drop type if exists musicbot_public.album cascade;
drop type if exists musicbot_public.artist cascade;
drop type if exists musicbot_public.genre cascade;
drop type if exists musicbot_public.keyword cascade;

create type musicbot_public.music as (id bigint, name text, path text, folder text);
create type musicbot_public.album as (id bigint, name text, musics musicbot_public.music[]);
create type musicbot_public.artist as (id bigint, name text, albums musicbot_public.album[]);
create type musicbot_public.genre as (id bigint, name text);
create type musicbot_public.keyword as (id bigint, name text);

create or replace function musicbot_public.artists_tree() returns setof musicbot_public.artist
as $$
    select row_number() over (order by artist) as id, artist, array_agg((id, album, musics)::musicbot_public.album) as albums
    from (
        select row_number() over (order by album) as id, artist, album, array_agg(row(id, title, path, folder)::musicbot_public.music) as musics
        from musicbot_public.raw_music
        where artist != '' and album != '' and title != ''
        group by artist, album
        order by artist
    ) as albums
    group by artist;
$$ language sql stable;

create or replace function musicbot_public.genres_tree() returns setof musicbot_public.genre
as $$
    select row_number() over () as id, genre from musicbot_public.raw_music where genre != '' group by genre order by genre asc;
$$ language sql stable;

create or replace function musicbot_public.keywords_tree() returns setof musicbot_public.keyword
as $$
    select row_number() over () as id, keyword from (select unnest(musicbot_public.array_cat_agg(keywords)) as keyword from musicbot_public.raw_music where array_length(keywords, 1) > 0) k group by keyword order by keyword asc;
$$ language sql stable;

create or replace function musicbot_public.delete_music(path text) returns void as $$
    delete from musicbot_public.raw_music where path = delete_music.path;
$$ language sql;

create or replace function musicbot_public.delete_all_music() returns void as $$
    delete from musicbot_public.raw_music;
$$ language sql;
