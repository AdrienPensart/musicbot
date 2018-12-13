create or replace function musicbot_public.do_filter(
    min_duration integer default 0,
    max_duration integer default +2147483647,
    min_size     integer default 0,
    max_size     integer default +2147483647,
    min_rating   float default 0.0,
    max_rating   float default 5.0,
    artists      text[] default '{}',
    no_artists   text[] default '{}',
    albums       text[] default '{}',
    no_albums    text[] default '{}',
    titles       text[] default '{}',
    no_titles    text[] default '{}',
    genres       text[] default '{}',
    no_genres    text[] default '{}',
    formats      text[] default '{}',
    no_formats   text[] default '{}',
    keywords     text[] default '{}',
    no_keywords  text[] default '{}',
    shuffle      boolean default 'false',
    relative     boolean default 'false',
    "limit"      integer default +2147483647,
    youtubes     text[] default '{}',
    no_youtubes  text[] default '{}',
    spotifys     text[] default '{}',
    no_spotifys  text[] default '{}'
) returns setof musicbot_public.raw_music as
$$
    select *
    from musicbot_public.raw_music m
    where
        (array_length(do_filter.artists, 1)     is null or      m.artist   = any(do_filter.artists)) and
        (array_length(do_filter.no_artists, 1)  is null or not (m.artist   = any(do_filter.no_artists))) and
        (array_length(do_filter.albums, 1)      is null or      m.album    = any(do_filter.albums)) and
        (array_length(do_filter.no_albums, 1)   is null or not (m.album    = any(do_filter.no_albums))) and
        (array_length(do_filter.titles, 1)      is null or      m.title    = any(do_filter.titles)) and
        (array_length(do_filter.no_titles, 1)   is null or not (m.title    = any(do_filter.no_titles))) and
        (array_length(do_filter.genres, 1)      is null or      m.genre    = any(do_filter.genres)) and
        (array_length(do_filter.no_genres, 1)   is null or not (m.genre    = any(do_filter.no_genres))) and
        (array_length(do_filter.youtubes, 1)    is null or      m.youtube  = any(do_filter.youtubes)) and
        (array_length(do_filter.no_youtubes, 1) is null or not (m.youtube  = any(do_filter.no_youtubes))) and
        (array_length(do_filter.spotifys, 1)    is null or      m.spotify  = any(do_filter.spotifys)) and
        (array_length(do_filter.no_spotifys, 1) is null or not (m.spotify  = any(do_filter.no_spotifys))) and
        (array_length(do_filter.keywords, 1)    is null or      do_filter.keywords    <@ m.keywords) and
        (array_length(do_filter.no_keywords, 1) is null or not (do_filter.no_keywords && m.keywords)) and
        (array_length(do_filter.formats, 1)     is null or      m.path similar     to '%.(' || array_to_string(do_filter.formats, '|') || ')') and
        (array_length(do_filter.no_formats, 1)  is null or      m.path not similar to '%.(' || array_to_string(do_filter.no_formats, '|') || ')') and
        m.duration between do_filter.min_duration and
                           do_filter.max_duration and
        m.size     between do_filter.min_size     and
                           do_filter.max_size and
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
grant execute on function musicbot_public.do_filter to musicbot_user;

create or replace function musicbot_public.playlist(
    min_duration integer default 0,
    max_duration integer default +2147483647,
    min_size     integer default 0,
    max_size     integer default +2147483647,
    min_rating   float default 0.0,
    max_rating   float default 5.0,
    artists      text[] default '{}',
    no_artists   text[] default '{}',
    albums       text[] default '{}',
    no_albums    text[] default '{}',
    titles       text[] default '{}',
    no_titles    text[] default '{}',
    genres       text[] default '{}',
    no_genres    text[] default '{}',
    formats      text[] default '{}',
    no_formats   text[] default '{}',
    keywords     text[] default '{}',
    no_keywords  text[] default '{}',
    shuffle      boolean default 'false',
    relative     boolean default 'false',
    "limit"      integer default +2147483647,
    youtubes     text[] default '{}',
    no_youtubes  text[] default '{}',
    spotifys     text[] default '{}',
    no_spotifys  text[] default '{}'
) returns text as
$$
        select
            case when playlist.relative is false then
                coalesce('#EXTM3U' || E'\n' || string_agg(f.path, E'\n'), '')
            else
                coalesce('#EXTM3U' || E'\n' || string_agg(substring(f.path from char_length(f.folder)+2), E'\n'), '')
            end
        from (select path, folder from musicbot_public.do_filter(
            min_duration => playlist.min_duration,
            max_duration => playlist.max_duration,
            min_size     => playlist.min_size,
            max_size     => playlist.max_size,
            min_rating   => playlist.min_rating,
            max_rating   => playlist.max_rating,
            artists      => playlist.artists,
            no_artists   => playlist.no_artists,
            albums       => playlist.albums,
            no_albums    => playlist.no_albums,
            titles       => playlist.titles,
            no_titles    => playlist.no_titles,
            genres       => playlist.genres,
            no_genres    => playlist.no_genres,
            formats      => playlist.formats,
            no_formats   => playlist.no_formats,
            keywords     => playlist.keywords,
            no_keywords  => playlist.no_keywords,
            shuffle      => playlist.shuffle,
            relative     => playlist.relative,
            "limit"      => playlist."limit",
            youtubes     => playlist.youtubes,
            no_youtubes  => playlist.no_youtubes,
            spotifys     => playlist.spotifys,
            no_spotifys  => playlist.no_spotifys
		)) f;
$$ language sql stable;
grant execute on function musicbot_public.playlist to musicbot_user;
