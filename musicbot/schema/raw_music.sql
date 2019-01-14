create table if not exists musicbot_public.raw_music
(
    id         serial primary key,
    user_id    integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot_id(),
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
--create index if not exists user_idx on musicbot_public.raw_music (user_id);
--create index if not exists path_user_idx on musicbot_public.raw_music (path, user_id);

alter table if exists musicbot_public.raw_music enable row level security;
grant usage on sequence musicbot_public.raw_music_id_seq to musicbot_user;

grant select on table musicbot_public.raw_music to musicbot_anonymous, musicbot_user;
grant insert, update, delete on table musicbot_public.raw_music to musicbot_user;

alter table if exists musicbot_public.raw_music enable row level security;

drop policy if exists insert_raw_music on musicbot_public.raw_music cascade;
create policy insert_raw_music on musicbot_public.raw_music for insert with check (user_id = musicbot_public.current_musicbot_id());

drop policy if exists select_raw_music on musicbot_public.raw_music cascade;
create policy select_raw_music on musicbot_public.raw_music for select using (user_id = musicbot_public.current_musicbot_id());

drop policy if exists update_raw_music on musicbot_public.raw_music cascade;
create policy update_raw_music on musicbot_public.raw_music for update using (user_id = musicbot_public.current_musicbot_id());

drop policy if exists delete_raw_music on musicbot_public.raw_music cascade;
create policy delete_raw_music on musicbot_public.raw_music for delete using (user_id = musicbot_public.current_musicbot_id());

create or replace function musicbot_public.bulk_insert(data text)
returns void as
$$
begin
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
grant execute on function musicbot_public.bulk_insert to musicbot_user;

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
grant execute on function musicbot_public.upsert_music to musicbot_user;

create or replace function musicbot_public.folders() returns setof text as $$
    select distinct folder from musicbot_public.raw_music order by folder asc;
$$ language sql stable;
grant execute on function musicbot_public.folders to musicbot_user;

create or replace function musicbot_public.artists() returns setof text as $$
    select distinct artist from musicbot_public.raw_music order by artist asc;
$$ language sql stable;
grant execute on function musicbot_public.artists to musicbot_user;

create or replace function musicbot_public.genres() returns setof text as $$
    select distinct genre from musicbot_public.raw_music order by genre asc;
$$ language sql stable;
grant execute on function musicbot_public.genres to musicbot_user;

create or replace function musicbot_public.delete_music(path text) returns void as $$
    delete from musicbot_public.raw_music where path = delete_music.path;
$$ language sql;
grant execute on function musicbot_public.delete_music to musicbot_user;
