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
returns setof musicbot_public.music as
$$
    select *
    from musicbot_public.music m
    where
        (array_length(playlist.artists, 1)     is null or      m.artist   = any(playlist.artists)) and
        (array_length(playlist.no_artists, 1)  is null or not (m.artist   = any(playlist.no_artists))) and
        (array_length(playlist.albums, 1)      is null or      m.album    = any(playlist.albums)) and
        (array_length(playlist.no_albums, 1)   is null or not (m.album    = any(playlist.no_albums))) and
        (array_length(playlist.titles, 1)      is null or      m.title    = any(playlist.titles)) and
        (array_length(playlist.no_titles, 1)   is null or not (m.title    = any(playlist.no_titles))) and
        (array_length(playlist.genres, 1)      is null or      m.genre    = any(playlist.genres)) and
        (array_length(playlist.no_genres, 1)   is null or not (m.genre    = any(playlist.no_genres))) and
        (array_length(playlist.keywords, 1)    is null or      playlist.keywords    <@ m.keywords) and
        (array_length(playlist.no_keywords, 1) is null or not (playlist.no_keywords && m.keywords)) and
        m.duration between playlist.min_duration and
                           playlist.max_duration and
        m.rating   between playlist.min_rating   and
                           playlist.max_rating
    order by
          case when(playlist.shuffle = 'true')  then random() end,
          case when(playlist.shuffle = 'false') then m.artist end,
          case when(playlist.shuffle = 'false') then m.album end,
          case when(playlist.shuffle = 'false') then m.number end,
          m.title
    limit playlist.limit;
$$ language sql stable;

create or replace function musicbot_public.bests
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
    with recursive music as
    (
        select links, artist, genre, keywords
        from musicbot_public.playlist
        (
            "min_duration" => bests."min_duration",
            "max_duration" => bests."max_duration",
            "min_rating"   => bests."min_rating",
            "max_rating"   => bests."max_rating",
            "artists"      => bests."artists",
            "no_artists"   => bests."no_artists",
            "albums"       => bests."albums",
            "no_albums"    => bests."no_albums",
            "titles"       => bests."titles",
            "no_titles"    => bests."no_titles",
            "genres"       => bests."genres",
            "no_genres"    => bests."no_genres",
            "keywords"     => bests."keywords",
            "no_keywords"  => bests."no_keywords",
            "shuffle"      => bests."shuffle",
            "limit"        => bests."limit"
        ) m
    ),
    bests_artists as (
        select
            (m.artist || '/bests') as name,
            coalesce(string_agg(m.url, E'\n'), '') as content
        from (select unnest(music.links) as url, artist from music) m
        where m.artist != ''
        group by m.artist
        having coalesce(string_agg(m.url, E'\n'), '') as content <> ''
    ),
    bests_genres as (
        select
            m.genre as name,
            coalesce(string_agg(m.url, E'\n'), '') as content
        from (select unnest(music.links) as url, genre from music) m
        where m.genre != ''
        group by m.genre
        having coalesce(string_agg(m.url, E'\n'), '') as content <> ''
    ),
    bests_artist_keywords as (
        with keywords as (
            select
                m.url as url,
                m.artist as artist,
                unnest(m.keywords) as k
            from (select unnest(music.links) as url, artist, keywords from music) m
            group by url, artist, keywords
            order by k
        )
        select
            (artist || '/' || k.k) as name,
            coalesce(string_agg(k.url, E'\n'), '') as content
        from keywords k
        group by artist, k
        having coalesce(string_agg(k.url, E'\n'), '') <> ''
    ),
    bests_keywords as (
        with keywords as (
            select
                m.url as url,
                unnest(m.keywords) as k
            from (select unnest(music.links) as url, artist, keywords from music) m
            group by url, keywords
            order by k
        )
        select
            (k.k) as name,
            coalesce(string_agg(k.url, E'\n'), '') as content
        from keywords k
        group by k
        having coalesce(string_agg(k.url, E'\n'), '') <> ''
    )
    select * from bests_artists union
    select * from bests_genres union
    select * from bests_artist_keywords union
    select * from bests_keywords;
$$ language sql stable;
