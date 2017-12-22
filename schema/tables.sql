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
create table if not exists artists (
    id serial primary key,
    name text unique not null,
    created_at timestamp default null,
    updated_at timestamp default null
);
create table if not exists genres (
    id serial primary key,
    name text unique not null,
    created_at timestamp default null,
    updated_at timestamp default null
);
create table if not exists albums (
    id serial primary key,
    artist_id integer not null,
    name text not null,
    youtube text default null,
    foreign key(artist_id) references artists (id),
    created_at timestamp default null,
    updated_at timestamp default null,
    unique(artist_id,name)
);
create table if not exists musics (
    id serial primary key,
    artist_id integer,
    album_id integer,
    genre_id integer,
    folder_id integer,
    youtube text default null,
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

create table if not exists filter
(
    id serial primary key,
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
    youtube boolean default null,
    constraint min_rating_range check (min_rating between 0.0 and 5.0),
    constraint max_rating_range check (max_rating between 0.0 and 5.0)
);
