create table if not exists musicbot_public.raw_music
(
    id       serial primary key,
    user_id  integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot_id(),
    path     text not null,
    title    text default '',
    album    text default '',
    genre    text default '',
    artist   text default '',
    folder   text default '',
    youtube  text default '',
	spotify  text default '',
    number   integer default 0,
    rating   float default 0.0,
    duration integer default 0,
    size     integer default 0,
    keywords text[] default '{}',
	created_at timestamp with time zone default now(),
	updated_at timestamp with time zone default now()
);
create index if not exists path_idx    on musicbot_public.raw_music (path);

alter table if exists musicbot_public.raw_music enable row level security;
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

create or replace function musicbot_public.upsert(
    title text default '',
    album text default '',
    genre text default '',
    artist text default '',
    folder text default '',
    youtube text default '',
    spotify text default '',
    number integer default 0,
    path text default '',
    rating float default 0.0,
    duration integer default 0,
    size integer default 0,
    keywords text[] default '{}'
) returns musicbot_public.raw_music as
$$
    insert into musicbot_public.raw_music as m (artist, genre, folder, album, rating, duration, path, title, number, size, youtube, spotify, keywords)
    values (artist, genre, folder, album, rating, duration, path, title, number, size, youtube, spotify, keywords)
    on conflict (path) do update set
        artist=EXCLUDED.artist,
        genre=EXCLUDED.genre,
        folder=EXCLUDED.folder,
        album=EXCLUDED.album,
        rating=EXCLUDED.rating,
        duration=EXCLUDED.duration,
        title=EXCLUDED.title,
        number=EXCLUDED.number,
        size=EXCLUDED.size,
        youtube=EXCLUDED.youtube,
		spotify=EXCLUDED.spotify,
        updated_at=coalesce(EXCLUDED.updated_at, now())
	returning *;
$$ language sql;
grant execute on function musicbot_public.upsert to musicbot_user;
