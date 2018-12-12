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
    set constraints musicbot_public.raw_music_path_user_id_key deferred;
	--raise notice 'started';
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
	--raise notice '  ended';
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
    --insert into musicbot_public.raw_music as m (artist, genre, folder, album, rating, duration, path, title, number, size, youtube, spotify, keywords)
    --values (artist, genre, folder, album, rating, duration, path, title, number, size, youtube, spotify, keywords)
    --on conflict on constraint raw_music_path_user_id_key do update set
    --on conflict (user_id, path) do update set
    --    path=EXCLUDED.path,
    --    artist=EXCLUDED.artist,
    --    genre=EXCLUDED.genre,
    --    folder=EXCLUDED.folder,
    --    album=EXCLUDED.album,
    --    rating=EXCLUDED.rating,
    --    duration=EXCLUDED.duration,
    --    title=EXCLUDED.title,
    --    number=EXCLUDED.number,
    --    size=EXCLUDED.size,
    --    youtube=EXCLUDED.youtube,
    --    spotify=EXCLUDED.spotify,
    --    updated_at=coalesce(EXCLUDED.updated_at, now())
    --returning *;
end
$$ language plpgsql;
grant execute on function musicbot_public.upsert_music to musicbot_user;

create or replace function musicbot_public.folders() returns setof text as $$
    select distinct folder from musicbot_public.raw_music;
$$ language sql stable;
grant execute on function musicbot_public.folders to musicbot_user;

create or replace function musicbot_public.delete_music(path text) returns void as $$
    delete from musicbot_public.raw_music where path = delete_music.path;
$$ language sql;
grant execute on function musicbot_public.delete_music to musicbot_user;
