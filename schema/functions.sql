create or replace function new_filter
(
    min_duration integer default 0,
    max_duration integer default +2147483647,
    min_size integer default 0,
    max_size integer default +2147483647,
    min_rating float default 0.0,
    max_rating float default 1.0,
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
    youtube boolean default null
) returns filter as
$$
begin
    return (0, min_duration, max_duration,
            min_size, max_size,
            min_rating, max_rating,
            artists, no_artists,
            albums, no_albums,
            titles, no_titles,
            genres, no_genres,
            formats, no_formats,
            keywords, no_keywords,
            shuffle, relative, "limit", youtube);
end;
$$ language plpgsql;

create table if not exists music
(
    id serial primary key,
    title text default '',
    album text default '',
    genre text default '',
    artist text default '',
    folder text default '',
    youtube text default null,
    number integer default 0,
    path text default '' unique not null,
    rating float default 0.0,
    duration integer default 0,
    size integer default 0,
    keywords text[] default '{}'
);

create or replace function new_music
(
    title text default '',
    album text default '',
    genre text default '',
    artist text default '',
    folder text default '',
    number integer default 0,
    path text default '',
    rating float default 0.0,
    duration integer default 0,
    size integer default 0,
    keywords text[] default '{}'
) returns music as
$$
begin
    return (0, title, album, genre, artist, folder, null, number, path, rating, duration, size, keywords);
end;
$$ language plpgsql;

create or replace function delete(p text)
returns void as
$$
--begin
    --delete from music_tags mt where mt.music_id = (select id from musics m where m.path = p limit 1);
    --delete from musics m where m.id = (select id from musics m where m.path = path limit 1);
    with delete_music as (
        select id from musics m where m.path = p limit 1
    ),
    delete_tags as (
        delete from music_tags mt using delete_music dm where mt.music_id = dm.id
    )
    delete from musics m using delete_music dm where m.id = dm.id;
--end;
$$ language sql;
--$$ language plpgsql;

create or replace function upsert(arg music default new_music())
returns void as
$$
begin
    delete from music_tags mt where mt.music_id = (select old.id from musics old where old.path = arg.path);
    with upsert_folder as (
        insert into folders as f (name, created_at)
        values (arg.folder, now())
        on conflict (name) do update set
            updated_at=coalesce(EXCLUDED.updated_at, now()),
            name=EXCLUDED.name
        returning f.id as folder_id
    ),
    upsert_artist as (
        insert into artists as a (name, created_at)
        values (arg.artist, now())
        on conflict (name) do update set
            updated_at=coalesce(EXCLUDED.updated_at, now()),
            name=EXCLUDED.name
        returning a.id as artist_iD
    ),
    upsert_album as (
        insert into albums as al (artist_id, name, created_at)
        values ((select artist_id from upsert_artist), arg.album, now())
        on conflict (artist_id, name) do update set
            updated_at=coalesce(EXCLUDED.updated_at, now()),
            name=EXCLUDED.name
        returning al.id as album_id
    ),
    upsert_genre as (
        insert into genres as g (name)
        values (arg.genre)
        on conflict (name) do update set
            updated_at=coalesce(EXCLUDED.updated_at, now()),
            name=EXCLUDED.name
        returning g.id as genre_id
    ),
    upsert_keywords as (
        insert into tags as t (name)
        select distinct k from unnest(arg.keywords) k
        on conflict (name) do update set
            updated_at=coalesce(EXCLUDED.updated_at, now()),
            name=EXCLUDED.name
        returning t.id as tag_id
    ),
    upsert_music as (
        insert into musics as m (artist_id, genre_id, folder_id, album_id, rating, duration, path, title, number, size, youtube, created_at)
        values (
            (select artist_id from upsert_artist),
            (select genre_id from upsert_genre),
            (select folder_id from upsert_folder),
            (select album_id from upsert_album),
            arg.rating, arg.duration, arg.path, arg.title, arg.number, arg.size, arg.youtube, now())
        on conflict (path) do update set
            updated_at=coalesce(EXCLUDED.updated_at, now()),
            artist_id=EXCLUDED.artist_id,
            genre_id=EXCLUDED.genre_id,
            folder_id=EXCLUDED.folder_id,
            album_id=EXCLUDED.album_id,
            rating=EXCLUDED.rating,
            duration=EXCLUDED.duration,
            title=EXCLUDED.title,
            number=EXCLUDED.number,
            size=EXCLUDED.size,
            youtube=coalesce(EXCLUDED.youtube, m.youtube)
        returning m.id as music_id
    )
    insert into music_tags (music_id, tag_id)
    select m.music_id, k.tag_id from upsert_music m, upsert_keywords k
    on conflict (music_id, tag_id) do nothing;
    delete from tags t where t.id = (select t.id from tags t left join music_tags mt on t.id = mt.tag_id group by t.id having count(mt.music_id) = 0);
end;
$$ language plpgsql;
--$$ language sql;

create or replace function upsert_all(ms music[])
returns void as
$$
declare
    m music;
begin
    foreach m in array ms
    loop
        perform upsert(m);
    end loop;
end
$$ language plpgsql;

create or replace function do_filter(mf filter default new_filter())
returns setof music as
$$
    with all_musics as (
        select
            m.id       as id,
            m.title    as title,
            al.name    as album,
            g.name     as genre,
            a.name     as artist,
            f.name     as folder,
            m.youtube  as youtube,
            m.number   as number,
            m.path     as path,
            m.rating   as rating,
            m.duration as duration,
            m.size     as size,
            (
                select coalesce(array_agg(name), '{}')
                from
                (
                    select distinct name
                    from music_tags mt
                    inner join tags t on mt.tag_id = t.id
                    where
                        mt.music_id = m.id and
                        name !~ '/'
                ) as separated_keywords
            ) as keywords
        from musics m
        inner join albums al on al.id = m.album_id
        inner join artists a on a.id = m.artist_id
        inner join genres g on g.id = m.genre_id
        inner join folders f on f.id = m.folder_id
        --where m.title !~ '/' and
        --      al.name !~ '/' and
        --      g.name !~ '/' and
        --      a.name !~ '/'
        order by artist, album, number
    )
    select *
    from all_musics mv
    where
        (array_length(mf.artists, 1) is null or mv.artist = any(mf.artists)) and
        (array_length(mf.no_artists, 1) is null or not (mv.artist = any(mf.no_artists))) and
        (array_length(mf.albums, 1) is null or mv.album = any(mf.albums)) and
        (array_length(mf.no_albums, 1) is null or not (mv.album = any(mf.no_albums))) and
        (array_length(mf.titles, 1) is null or mv.title = any(mf.titles)) and
        (array_length(mf.no_titles, 1) is null or not (mv.title = any(mf.no_titles))) and
        (array_length(mf.genres, 1) is null or mv.genre = any(mf.genres)) and
        (array_length(mf.no_genres, 1) is null or not (mv.genre = any(mf.no_genres))) and
        (array_length(mf.keywords, 1) is null or mf.keywords <@ mv.keywords) and
        (array_length(mf.no_keywords, 1) is null or not (mf.no_keywords && mv.keywords)) and
        (array_length(mf.formats, 1) is null or mv.path similar to '%.(' || array_to_string(mf.formats, '|') || ')') and
        (array_length(mf.no_formats, 1) is null or mv.path not similar to '%.(' || array_to_string(mf.no_formats, '|') || ')') and
        mv.duration between mf.min_duration and mf.max_duration and
        mv.size between mf.min_size and mf.max_size and
        mv.rating between mf.min_rating and mf.max_rating and
        (mf.youtube is null or (mf.youtube is true and mv.youtube is not null) or (mf.youtube is false and mv.youtube is null))
   order by case when (mf.shuffle = 'true') then random() end
   limit mf.limit;
$$ language sql;

create or replace function generate_form(mf filter default new_filter())
returns filter as
$$
    with filtered as (
        select * from do_filter(mf)
    ),
    extract_keywords as (
        select coalesce(array_agg(distinct keywords), array[]::text[]) as keywords
        from (select unnest(array_cat_agg(keywords)) as keywords from filtered) k
    ),
    extract_genres as (
        select coalesce(array_agg(distinct genre), array[]::text[]) as genres from filtered
    ),
    extract_artists as (
        select coalesce(array_agg(distinct artist), array[]::text[]) as artists from filtered
    ),
    extract_titles as (
        select coalesce(array_agg(distinct title), array[]::text[]) as titles from filtered
    ),
    extract_albums as (
        select coalesce(array_agg(distinct album), array[]::text[]) as albums from filtered
    )
    select
        0,
        0,
        0,
        0,
        0,
        CAST ('NaN' AS DOUBLE PRECISION),
        CAST ('NaN' AS DOUBLE PRECISION),
        (select * from extract_artists) as artists,
        ARRAY[]::text[],
        (select * from extract_albums) as albums,
        ARRAY[]::text[],
        (select * from extract_titles) as titles,
        ARRAY[]::text[],
        (select * from extract_genres) as genres,
        ARRAY[]::text[],
        ARRAY[]::text[],
        ARRAY[]::text[],
        (select * from extract_keywords) as keywords,
        ARRAY[]::text[],
        False,
        False,
        0,
        False;
$$ language sql;

create or replace function do_stats(mf filter default new_filter())
returns stats as
$$
    select
        row_number() over () as id,
        count(distinct f.path) as musics,
        count(distinct f.album) as albums,
        count(distinct f.artist) as artists,
        count(distinct f.genre) as genres,
        (select count(distinct k.keywords) from (select unnest(array_cat_agg(f.keywords)) as keywords) as k) as keywords,
        coalesce(sum(f.duration),0) as duration,
        coalesce(sum(f.size),0) as size
    from do_filter(mf) f;
$$ language sql;

drop type if exists playlist cascade;
create type playlist as
(
    name text,
    content text
);

create or replace function generate_playlist(mf filter default new_filter())
returns table(content text) as
$$
        select
            case when mf.relative is false then coalesce('#EXTM3U' || E'\n' || string_agg(f.path, E'\n'), '')
            else coalesce('#EXTM3U' || E'\n' || string_agg(substring(f.path from char_length(f.folder)+2), E'\n'), '')
            end
        from (select path, folder from do_filter(mf) order by rating desc) f;
$$ language sql;

create or replace function generate_bests_artist_keyword(mf filter default new_filter(min_rating := 0.8))
returns setof playlist as
$$
    with recursive
        musics as (select path, folder, artist, keywords from do_filter(mf)),
        keywords as (select path, folder, artist, unnest(keywords) as k from musics group by path, folder, artist, keywords order by k)
        select
            (artist || '/' || k.k) as name,
            case when mf.relative is false then coalesce('#EXTM3U' || E'\n' || string_agg(path, E'\n'), '')
            else coalesce('#EXTM3U' || E'\n' || string_agg(substring(path from char_length(folder)+2), E'\n'), '')
            end
        from keywords k
        group by artist, k;
$$ language sql;


create or replace function generate_bests_artist(mf filter default new_filter(min_rating := 0.8))
returns setof playlist as
$$
    with recursive
        musics as (select path, folder, artist from do_filter(mf))
        select
            (m.artist || '/bests') as name,
            case when mf.relative is false then coalesce('#EXTM3U' || E'\n' || string_agg(path, E'\n'), '')
            else coalesce('#EXTM3U' || E'\n' || string_agg(substring(path from char_length(folder)+2), E'\n'), '')
            end
        from musics m
        group by m.artist;
$$ language sql;

create or replace function generate_bests_genre(mf filter default new_filter(min_rating := 0.8))
returns setof playlist as
$$
    with recursive
        musics as (select path, folder, genre from do_filter(mf))
        select
            (m.genre) as name,
            case when mf.relative is false then coalesce('#EXTM3U' || E'\n' || string_agg(path, E'\n'), '')
            else coalesce('#EXTM3U' || E'\n' || string_agg(substring(path from char_length(folder)+2), E'\n'), '')
            end
        from musics m
        group by m.genre;
$$ language sql;

create or replace function generate_bests_keyword(mf filter default new_filter(min_rating := 0.8))
returns setof playlist as
$$
    with recursive
        musics as (select path, folder, keywords from do_filter(mf)),
        keywords as (select path, folder, unnest(keywords) as k from musics group by path, folder, keywords order by k)
        select
            (k.k) as name,
            case when mf.relative is false then coalesce('#EXTM3U' || E'\n' || string_agg(path, E'\n'), '')
            else coalesce('#EXTM3U' || E'\n' || string_agg(substring(path from char_length(folder)+2), E'\n'), '')
            end
        from keywords k
        group by k;
$$ language sql;


create or replace function generate_bests(mf filter default new_filter(min_rating := 0.8))
returns setof playlist as
$$
    select * from generate_bests_artist(mf) union
    select * from generate_bests_genre(mf) union
    select * from generate_bests_artist_keyword(mf) union
    select * from generate_bests_keyword(mf);
$$ language sql;
