create extension if not exists pg_trgm;

create table if not exists folders (
    id serial primary key,
    name text unique not null,
    created_at timestamp default null,
    updated_at timestamp default null
);
create table if not exists tags (
    id serial primary key,
    name text unique not null,
    created_at timestamp default null,
    updated_at timestamp default null
);
create index if not exists tags_trigram_idx on tags using gist(name gist_trgm_ops);

create table if not exists artists (
    id serial primary key,
    name text unique not null,
    created_at timestamp default null,
    updated_at timestamp default null
);
create index if not exists artists_trigram_idx on artists using gist(name gist_trgm_ops);

create table if not exists genres (
    id serial primary key,
    name text unique not null,
    created_at timestamp default null,
    updated_at timestamp default null
);
create index if not exists genres_trigram_idx on genres using gist(name gist_trgm_ops);

create table if not exists albums (
    id serial primary key,
    artist_id integer not null,
    name text not null,
    youtube text default '',
    foreign key(artist_id) references artists (id),
    created_at timestamp default null,
    updated_at timestamp default null,
    unique(artist_id,name)
);
create index if not exists albums_trigram_idx on albums using gist(name gist_trgm_ops);

create table if not exists music
(
    id serial primary key,
    title text default '',
    album text default '',
    genre text default '',
    artist text default '',
    folder text default '',
    youtube text default '',
    number integer default 0,
    path text default '' unique not null,
    rating float default 0.0,
    duration integer default 0,
    size integer default 0,
    keywords text[] default '{}'
);
create index if not exists title_idx on music (title);
create index if not exists album_idx on music (album);
create index if not exists genre_idx on music (genre);
create index if not exists artist_idx on music (artist);
create index if not exists folder_idx on music (folder);
create index if not exists youtube_idx on music (youtube);
create index if not exists rating_idx on music (rating);
create index if not exists keywords_idx on music (keywords);


create table if not exists musics (
    id serial primary key,
    artist_id integer,
    album_id integer,
    genre_id integer,
    folder_id integer,
    youtube text default '',
    number integer not null,
    rating float,
    duration integer,
    size integer,
    title text,
    path text unique not null,
    created_at timestamp default null,
    updated_at timestamp default null,
    foreign key(artist_id) references artists (id),
    foreign key(album_id)  references albums (id),
    foreign key(genre_id)  references genres (id),
    foreign key(folder_id) references folders (id),
    constraint rating_range check (rating between 0.0 and 5.0)
);
create index if not exists musics_trigram_idx on musics using gist(title gist_trgm_ops);

create table if not exists music_tags (
    music_id integer not null,
    tag_id integer not null,
    created_at timestamp default null,
    updated_at timestamp default null,
    primary key (music_id, tag_id),
    foreign key(music_id) references musics (id) on delete cascade,
    foreign key(tag_id)   references tags (id)
);
drop aggregate if exists array_cat_agg(anyarray) cascade;
create aggregate array_cat_agg(anyarray) (
    SFUNC=array_cat,
    STYPE=anyarray
);

create table if not exists stats
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

create table if not exists filters
(
    id serial primary key,
    name text unique not null,
    min_duration integer default 0,
    max_duration integer default +2147483647,
    min_size integer default 0,
    max_size integer default +2147483647,
    min_rating float default 0.0,
    max_rating float default 5.0,
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
    no_youtubes text[] default '{}',
    constraint min_rating_range check (min_rating between 0.0 and 5.0),
    constraint max_rating_range check (max_rating between 0.0 and 5.0)
);
