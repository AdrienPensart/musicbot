begin;

create table if not exists public.folder (
    id serial primary key,
    user_id  integer not null references public.user (id),
    name text unique not null check (char_length(name) < 256),
    created_at timestamp default now(),
    updated_at timestamp default now()
);
alter table if exists public.folder enable row level security;

grant select on table public.folder to musicbot_anonymous, musicbot_user;
--drop policy if exists select_folder on public.folder cascade;
--create policy select_folder on public.folder for select using (true);

--drop policy if exists insert_music on public.music cascade;
--create policy insert_music on public.music for insert to musicbot_user
--  with check (user_id = current_setting('jwt.claims.user_id')::integer);
--
--drop policy if exists update_music on public.music cascade;
--create policy update_music on public.music for update to musicbot_user
--  using (user_id = current_setting('jwt.claims.user_id')::integer);
--
--drop policy if exists delete_music on public.music cascade;
--create policy delete_music on public.music for delete to musicbot_user
--  using (user_id = current_setting('jwt.claims.user_id')::integer);

create table if not exists public.tag (
    id serial primary key,
    user_id  integer not null references public.user (id),
    name text unique not null check (char_length(name) < 256),
    created_at timestamp default now(),
    updated_at timestamp default now()
);
create index if not exists tag_trigram_idx on public.tag using gist(name gist_trgm_ops);
alter table if exists public.tag enable row level security;
grant select on table public.tag to musicbot_anonymous, musicbot_user;

create table if not exists public.artist (
    id serial primary key,
    user_id  integer not null references public.user (id),
    name text unique not null check (char_length(name) < 256),
    created_at timestamp default now(),
    updated_at timestamp default now()
);
create index if not exists artist_trigram_idx on public.artist using gist(name gist_trgm_ops);
alter table if exists public.artist enable row level security;
grant select on table public.artist to musicbot_anonymous, musicbot_user;

create table if not exists public.genre (
    id serial primary key,
    user_id  integer not null references public.user (id),
    name text unique not null check (char_length(name) < 256),
    created_at timestamp default now(),
    updated_at timestamp default now()
);
create index if not exists genre_trigram_idx on public.genre using gist(name gist_trgm_ops);
alter table if exists public.genre enable row level security;
grant select on table public.genre to musicbot_anonymous, musicbot_user;

create table if not exists public.album (
    id         serial primary key,
    user_id    integer not null references public.user (id),
    artist_id  integer not null references public.artist (id),
    name text  unique not null check (char_length(name) < 256),
    youtube    text default '' check (char_length(youtube) < 128),
    created_at timestamp default now(),
    updated_at timestamp default now(),
    unique(artist_id, name)
);
create index if not exists album_trigram_idx on public.album using gist(name gist_trgm_ops);
alter table if exists public.album enable row level security;
grant select on table public.album to musicbot_anonymous, musicbot_user;

--create table if not exists public.music
--(
--    id       serial primary key,
--    title    text default '',
--    album    text default '',
--    genre    text default '',
--    artist   text default '',
--    folder   text default '',
--    youtube  text default '',
--    number   integer default 0,
--    path     text default '' unique not null,
--    rating   float default 0.0,
--    duration integer default 0,
--    size     integer default 0,
--    keywords text[] default '{}'
--);
--comment on table "music" IS E'@name table_music_not_used';
--create index if not exists title_idx on music (title);
--create index if not exists album_idx on music (album);
--create index if not exists genre_idx on music (genre);
--create index if not exists artist_idx on music (artist);
--create index if not exists folder_idx on music (folder);
--create index if not exists youtube_idx on music (youtube);
--create index if not exists rating_idx on music (rating);
--create index if not exists keywords_idx on music (keywords);
--alter table if exists public.music enable row level security;
--grant select on table public.music to musicbot_anonymous, musicbot_user;

create table if not exists public.music (
    id serial primary key,
    user_id  integer not null references public.user (id),
    artist_id integer not null references public.artist (id),
    album_id integer not null references public.album (id),
    genre_id integer not null references public.genre (id),
    folder_id integer not null references public.folder (id),
    youtube text default '',
    number integer not null,
    rating float not null check (rating between 0.0 and 5.0),
    duration integer not null,
    size integer not null,
    title text not null,
    path text unique not null,
    created_at timestamp default now(),
    updated_at timestamp default now()
);
create index if not exists music_trigram_idx on public.music using gist(title gist_trgm_ops);
alter table if exists public.music enable row level security;
grant select on table public.music to musicbot_anonymous, musicbot_user;

drop policy if exists select_music on public.music cascade;
create policy select_music on public.music for select using (true);

drop policy if exists insert_music on public.music cascade;
create policy insert_music on public.music for insert to musicbot_user
  with check (user_id = current_setting('jwt.claims.user_id')::integer);

drop policy if exists update_music on public.music cascade;
create policy update_music on public.music for update to musicbot_user
  using (user_id = current_setting('jwt.claims.user_id')::integer);

drop policy if exists delete_music on public.music cascade;
create policy delete_music on public.music for delete to musicbot_user
  using (user_id = current_setting('jwt.claims.user_id')::integer);

create table if not exists public.music_tag (
    user_id  integer not null references public.user (id),
    music_id integer not null references public.music (id) on delete cascade,
    tag_id integer not null references public.tag (id) on delete cascade,
    primary key(music_id, tag_id),
    created_at timestamp default now(),
    updated_at timestamp default now()
);
alter table if exists public.music_tag enable row level security;
grant select on table public.music_tag to musicbot_anonymous, musicbot_user;

drop aggregate if exists public.array_cat_agg(anyarray) cascade;
create aggregate public.array_cat_agg(anyarray) (
    SFUNC=array_cat,
    STYPE=anyarray
);

create table if not exists public.stat
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
alter table if exists public.stat enable row level security;
grant select on table public.stat to musicbot_anonymous, musicbot_user;

create table if not exists public.filter
(
    id serial primary key,
    name text unique not null,
    min_duration integer default 0,
    max_duration integer default +2147483647,
    min_size integer default 0,
    max_size integer default +2147483647,
    min_rating float default 0.0 check (min_rating between 0.0 and 5.0),
    max_rating float default 5.0 check (max_rating between 0.0 and 5.0),
    artists text[] default '{}',
    no_artists text[] default '{}',
    albums text[] default '{}',
    no_albums text[] default '{}',
    titles text[] default '{}',
    no_titles text[] default '{}',
    genres text[] default '{}',
    no_genres text[] default '{}',
    formats text[] default '{}',
    no_formats text[] default '{}',
    keywords text[] default '{}',
    no_keywords text[] default '{}',
    shuffle boolean default 'false',
    relative boolean default 'false',
    "limit" integer default +2147483647,
    youtubes text[] default '{}',
    no_youtubes text[] default '{}'
);
alter table if exists public.filter enable row level security;
grant select on table public.filter to musicbot_anonymous, musicbot_user;

end;
