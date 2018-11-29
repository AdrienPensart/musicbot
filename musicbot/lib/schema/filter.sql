create table if not exists musicbot_public.filter
(
    id serial primary key,
    user_id  integer not null references musicbot_public.user (id) on delete cascade default musicbot_public.current_musicbot_id(),
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
    no_youtubes text[] default '{}',
	created_at timestamp with time zone default now(),
	updated_at timestamp with time zone default now()
);
alter table if exists musicbot_public.filter enable row level security;
grant select on table musicbot_public.filter to musicbot_anonymous, musicbot_user;
grant insert, update, delete on table musicbot_public.filter to musicbot_user;
grant usage on sequence musicbot_public.filter_id_seq to musicbot_user;

drop policy if exists insert_filter on musicbot_public.filter cascade;
create policy insert_filter on musicbot_public.filter for insert with check (user_id = musicbot_public.current_musicbot_id());

drop policy if exists select_filter on musicbot_public.filter cascade;
create policy select_filter on musicbot_public.filter for select using (user_id = musicbot_public.current_musicbot_id());

drop policy if exists update_filter on musicbot_public.filter cascade;
create policy update_filter on musicbot_public.filter for update using (user_id = musicbot_public.current_musicbot_id());

drop policy if exists delete_filter on musicbot_public.filter cascade;
create policy delete_filter on musicbot_public.filter for delete using (user_id = musicbot_public.current_musicbot_id());

create or replace function musicbot_public.default_filters()
returns void as
$$
begin
    insert into musicbot_public.filter as f (name) values ('default') on conflict do nothing;
    insert into musicbot_public.filter as f (name, youtubes) values ('youtube not found', '{not found}') on conflict do nothing;
    insert into musicbot_public.filter as f (name, youtubes) values ('no youtube links', '{}') on conflict do nothing;
    insert into musicbot_public.filter as f (name, min_rating, max_rating) values ('no rating', 0.0, 0.0) on conflict do nothing;
    insert into musicbot_public.filter as f (name, min_rating, no_keywords) values ('best (4.0+)', 4.0, '{cutoff,bad,demo,intro}') on conflict do nothing;
    insert into musicbot_public.filter as f (name, min_rating, no_keywords) values ('best (4.5+)', 4.5, '{cutoff,bad,demo,intro}') on conflict do nothing;
    insert into musicbot_public.filter as f (name, min_rating, no_keywords) values ('best (5.0+)', 5.0, '{cutoff,bad,demo,intro}') on conflict do nothing;
    insert into musicbot_public.filter as f (name, no_keywords) values ('no live', '{live}') on conflict do nothing;
    insert into musicbot_public.filter as f (name, keywords) values ('only live', '{live}') on conflict do nothing;
end;
$$ language plpgsql;
grant execute on function musicbot_public.default_filters to musicbot_user;

create or replace function musicbot_public.do_filter(mf musicbot_public.filter)
returns setof musicbot_public.raw_music as
$$
    select *
    from musicbot_public.raw_music mv
    where
        (array_length(mf.artists, 1)     is null or mv.artist = any(mf.artists)) and
        (array_length(mf.no_artists, 1)  is null or not (mv.artist = any(mf.no_artists))) and
        (array_length(mf.albums, 1)      is null or mv.album = any(mf.albums)) and
        (array_length(mf.no_albums, 1)   is null or not (mv.album = any(mf.no_albums))) and
        (array_length(mf.titles, 1)      is null or mv.title = any(mf.titles)) and
        (array_length(mf.no_titles, 1)   is null or not (mv.title = any(mf.no_titles))) and
        (array_length(mf.genres, 1)      is null or mv.genre = any(mf.genres)) and
        (array_length(mf.no_genres, 1)   is null or not (mv.genre = any(mf.no_genres))) and
        (array_length(mf.youtubes, 1)    is null or mv.youtube = any(mf.youtubes)) and
        (array_length(mf.no_youtubes, 1) is null or not (mv.youtube = any(mf.no_youtubes))) and
        (array_length(mf.keywords, 1)    is null or mf.keywords <@ mv.keywords) and
        (array_length(mf.no_keywords, 1) is null or not (mf.no_keywords && mv.keywords)) and
        (array_length(mf.formats, 1)     is null or mv.path similar to '%.(' || array_to_string(mf.formats, '|') || ')') and
        (array_length(mf.no_formats, 1)  is null or mv.path not similar to '%.(' || array_to_string(mf.no_formats, '|') || ')') and
        mv.duration between mf.min_duration and mf.max_duration and
        mv.size     between mf.min_size     and mf.max_size and
        mv.rating   between mf.min_rating   and mf.max_rating
    order by
        case when(mf.shuffle = 'true') then random() end,
        case when(mf.shuffle = 'false') then mv.artist end,
        case when(mf.shuffle = 'false') then mv.album end,
        case when(mf.shuffle = 'false') then mv.number end,
        mv.title
    limit mf.limit;
$$ language sql stable;
grant execute on function musicbot_public.do_filter to musicbot_user;
