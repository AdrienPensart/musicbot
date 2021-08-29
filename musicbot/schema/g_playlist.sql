create or replace function musicbot_public.do_filter
(
    "min_duration" integer default 0,
    "max_duration" integer default +2147483647,
    "min_rating"   float default 0.0,
    "max_rating"   float default 5.0,
    "artists"      text[] default '{}',
    "no_artists"   text[] default '{}',
    "albums"       text[] default '{}',
    "no_albums"    text[] default '{}',
    "titles"       text[] default '{}',
    "no_titles"    text[] default '{}',
    "genres"       text[] default '{}',
    "no_genres"    text[] default '{}',
    "keywords"     text[] default '{}',
    "no_keywords"  text[] default '{}',
    "shuffle"      boolean default 'false',
    "limit"        integer default +2147483647
)
returns setof musicbot_public.music as
$$
    select *
    from musicbot_public.music m
    where
        (array_length(do_filter.artists, 1)     is null or      m.artist   = any(do_filter.artists)) and
        (array_length(do_filter.no_artists, 1)  is null or not (m.artist   = any(do_filter.no_artists))) and
        (array_length(do_filter.albums, 1)      is null or      m.album    = any(do_filter.albums)) and
        (array_length(do_filter.no_albums, 1)   is null or not (m.album    = any(do_filter.no_albums))) and
        (array_length(do_filter.titles, 1)      is null or      m.title    = any(do_filter.titles)) and
        (array_length(do_filter.no_titles, 1)   is null or not (m.title    = any(do_filter.no_titles))) and
        (array_length(do_filter.genres, 1)      is null or      m.genre    = any(do_filter.genres)) and
        (array_length(do_filter.no_genres, 1)   is null or not (m.genre    = any(do_filter.no_genres))) and
        (array_length(do_filter.keywords, 1)    is null or      do_filter.keywords    <@ m.keywords) and
        (array_length(do_filter.no_keywords, 1) is null or not (do_filter.no_keywords && m.keywords)) and
        m.duration between do_filter.min_duration and
                           do_filter.max_duration and
        m.rating   between do_filter.min_rating   and
                           do_filter.max_rating
    order by
          case when(do_filter.shuffle = 'true')  then random() end,
          case when(do_filter.shuffle = 'false') then m.artist end,
          case when(do_filter.shuffle = 'false') then m.album end,
          case when(do_filter.shuffle = 'false') then m.number end,
          m.title
    limit do_filter.limit;
$$ language sql stable;

create or replace function musicbot_public.playlist
(
    "min_duration" integer default 0,
    "max_duration" integer default +2147483647,
    "min_rating"   float default 0.0,
    "max_rating"   float default 5.0,
    "artists"      text[] default '{}',
    "no_artists"   text[] default '{}',
    "albums"       text[] default '{}',
    "no_albums"    text[] default '{}',
    "titles"       text[] default '{}',
    "no_titles"    text[] default '{}',
    "genres"       text[] default '{}',
    "no_genres"    text[] default '{}',
    "keywords"     text[] default '{}',
    "no_keywords"  text[] default '{}',
    "shuffle"      boolean default 'false',
    "limit"        integer default +2147483647
)
returns setof musicbot_public.link as
$$
    select l.*
    from musicbot_public.do_filter
    (
        "min_duration" => playlist."min_duration",
        "max_duration" => playlist."max_duration",
        "min_rating"   => playlist."min_rating",
        "max_rating"   => playlist."max_rating",
        "artists"      => playlist."artists",
        "no_artists"   => playlist."no_artists",
        "albums"       => playlist."albums",
        "no_albums"    => playlist."no_albums",
        "titles"       => playlist."titles",
        "no_titles"    => playlist."no_titles",
        "genres"       => playlist."genres",
        "no_genres"    => playlist."no_genres",
        "keywords"     => playlist."keywords",
        "no_keywords"  => playlist."no_keywords",
        "shuffle"      => playlist."shuffle",
        "limit"        => playlist."limit"
    ) m
    inner join musicbot_public.link l on l.music_id = m.id;
$$ language sql stable;

create or replace function musicbot_public.m3u_playlist
(
    "min_duration" integer default 0,
    "max_duration" integer default +2147483647,
    "min_rating"   float default 0.0,
    "max_rating"   float default 5.0,
    "artists"      text[] default '{}',
    "no_artists"   text[] default '{}',
    "albums"       text[] default '{}',
    "no_albums"    text[] default '{}',
    "titles"       text[] default '{}',
    "no_titles"    text[] default '{}',
    "genres"       text[] default '{}',
    "no_genres"    text[] default '{}',
    "keywords"     text[] default '{}',
    "no_keywords"  text[] default '{}',
    "shuffle"      boolean default 'false',
    "limit"        integer default +2147483647
)
returns text as
$$
    select coalesce('#EXTM3U' || E'\n' || string_agg(l.url, E'\n'), '')
    from (
        select *
        from musicbot_public.do_filter
        (
            "min_duration" => m3u_playlist."min_duration",
            "max_duration" => m3u_playlist."max_duration",
            "min_rating"   => m3u_playlist."min_rating",
            "max_rating"   => m3u_playlist."max_rating",
            "artists"      => m3u_playlist."artists",
            "no_artists"   => m3u_playlist."no_artists",
            "albums"       => m3u_playlist."albums",
            "no_albums"    => m3u_playlist."no_albums",
            "titles"       => m3u_playlist."titles",
            "no_titles"    => m3u_playlist."no_titles",
            "genres"       => m3u_playlist."genres",
            "no_genres"    => m3u_playlist."no_genres",
            "keywords"     => m3u_playlist."keywords",
            "no_keywords"  => m3u_playlist."no_keywords",
            "shuffle"      => m3u_playlist."shuffle",
            "limit"        => m3u_playlist."limit"
        )
    ) m
    inner join musicbot_public.link l on l.music_id = m.id;
$$ language sql stable;

create or replace function musicbot_public.m3u_bests
(
    "min_duration" integer default 0,
    "max_duration" integer default +2147483647,
    "min_rating"   float default 0.0,
    "max_rating"   float default 5.0,
    "artists"      text[] default '{}',
    "no_artists"   text[] default '{}',
    "albums"       text[] default '{}',
    "no_albums"    text[] default '{}',
    "titles"       text[] default '{}',
    "no_titles"    text[] default '{}',
    "genres"       text[] default '{}',
    "no_genres"    text[] default '{}',
    "keywords"     text[] default '{}',
    "no_keywords"  text[] default '{}',
    "shuffle"      boolean default 'false',
    "limit"        integer default +2147483647
)
returns table
(
    name text,
    content text
) as
$$
    with recursive musics as
    (
        select l.url as url, artist, genre, keywords
        from musicbot_public.do_filter
        (
            "min_duration" => m3u_bests."min_duration",
            "max_duration" => m3u_bests."max_duration",
            "min_rating"   => m3u_bests."min_rating",
            "max_rating"   => m3u_bests."max_rating",
            "artists"      => m3u_bests."artists",
            "no_artists"   => m3u_bests."no_artists",
            "albums"       => m3u_bests."albums",
            "no_albums"    => m3u_bests."no_albums",
            "titles"       => m3u_bests."titles",
            "no_titles"    => m3u_bests."no_titles",
            "genres"       => m3u_bests."genres",
            "no_genres"    => m3u_bests."no_genres",
            "keywords"     => m3u_bests."keywords",
            "no_keywords"  => m3u_bests."no_keywords",
            "shuffle"      => m3u_bests."shuffle",
            "limit"        => m3u_bests."limit"
        ) m
        inner join musicbot_public.link l on l.music_id = m.id
    ),
    bests_artists as (
        select
            (m.artist || '/bests') as name,
            coalesce('#EXTM3U' || E'\n' || string_agg(m.url, E'\n'), '')
        from musics m
        where m.artist != ''
        group by m.artist
    ),
    bests_genres as (
        select
            m.genre as name,
            coalesce('#EXTM3U' || E'\n' || string_agg(m.url, E'\n'), '')
        from musics m
        where m.genre != ''
        group by m.genre
    ),
    bests_artist_keywords as (
        with keywords as (
            select
                url,
                artist,
                unnest(keywords) as k
            from musics
            group by url, artist, keywords
            order by k
        )
        select
            (artist || '/' || k.k) as name,
            coalesce('#EXTM3U' || E'\n' || string_agg(k.url, E'\n'), '')
        from keywords k
        group by artist, k
    ),
    bests_keywords as (
        with keywords as (
            select
                url,
                unnest(keywords) as k
            from musics
            group by url, keywords
            order by k
        )
        select
            (k.k) as name,
            coalesce('#EXTM3U' || E'\n' || string_agg(k.url, E'\n'), '')
        from keywords k
        group by k
    )
    select * from bests_artists union
    select * from bests_genres union
    select * from bests_artist_keywords union
    select * from bests_keywords;
$$ language sql stable;
