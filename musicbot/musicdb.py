import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from beartype import beartype
from edgedb.blocking_client import Client

from musicbot.file import File
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist

logger = logging.getLogger(__name__)


class MusicDb(MusicbotObject):
    def __init__(self, client: Client):
        self.client = client
        if not self.is_prod():
            os.environ['EDGEDB_CLIENT_SECURITY'] = 'insecure_dev_mode'

    @lru_cache(maxsize=None)
    @beartype
    def make_playlist(self, music_filter: MusicFilter | None = None) -> Playlist:
        music_filter = music_filter if music_filter is not None else MusicFilter()
        query = """
with
    artists := (
        select Artist
        filter
            (len(<array<str>>$artists) = 0 or contains(<array<str>>$artists, .name)) and
            (len(<array<str>>$no_artists) = 0 or not contains(<array<str>>$no_artists, .name))
    ),
    albums := (
        select Album
        filter
            (len(<array<str>>$albums) = 0 or contains(<array<str>>$albums, .name)) and
            (len(<array<str>>$no_albums) = 0 or not contains(<array<str>>$no_albums, .name)) and
            .artist in artists
    ),
    genres := (
        select Genre
        filter
            (len(<array<str>>$genres) = 0 or contains(<array<str>>$genres, .name)) and
            (len(<array<str>>$no_genres) = 0 or not contains(<array<str>>$no_genres, .name))
    ),
    #keywords := (
    #    select Keyword
    #    filter
    #        (len(<array<str>>$keywords) = 0 or contains(<array<str>>$keywords, .name)) and
    #        (len(<array<str>>$no_keywords) = 0 or not contains(<array<str>>$no_keywords, .name))
    #),
    select Music {
        name,
        links,
        size,
        genre_name := .genre.name,
        album_name := .album.name,
        artist_name := .album.artist.name,
        all_keywords := array_agg(.keywords.name),
        length := <int64>duration_to_seconds(.duration),
        track,
        rating
    }
    filter
        .length >= <int64>$min_length and .length <= <int64>$max_length
        and .size >= <int64>$min_size and .size <= <int64>$max_size
        and .rating >= <Rating>$min_rating and .rating <= <Rating>$max_rating
        and (len(<array<str>>$titles) = 0 or contains(<array<str>>$titles, .name))
        and (len(<array<str>>$no_titles) = 0 or not contains(<array<str>>$no_titles, .name))
        and .genre in genres
        and .album in albums
        #and (
        #    for music_keyword in .keywords
        #    union (
        #        filter not contains(keywords, music_keyword)
        #    )
        #)
    ;
"""
        results = self.client.query(
            query,
            titles=list(music_filter.titles),
            no_titles=list(music_filter.no_titles),

            artists=list(music_filter.artists),
            no_artists=list(music_filter.no_artists),

            albums=list(music_filter.albums),
            no_albums=list(music_filter.no_albums),

            genres=list(music_filter.genres),
            no_genres=list(music_filter.no_genres),

            # keywords=list(music_filter.keywords),
            # no_keywords=list(music_filter.no_keywords),

            min_size=music_filter.min_size,
            max_size=music_filter.max_size,
            min_length=music_filter.min_length,
            max_length=music_filter.max_length,
            min_rating=music_filter.min_rating,
            max_rating=music_filter.max_rating,
        )

        musics = []
        for result in results:
            keywords = list(keyword for keyword in result.all_keywords)
            if len(music_filter.no_keywords):
                found = False
                for mtag in music_filter.no_keywords:
                    if mtag in keywords:
                        logger.debug(f"no_keyword {mtag} MET in {result.name} : {keywords}")
                        found = True
                        break
                if found:
                    continue

            if len(music_filter.keywords):
                found = False
                for mtag in music_filter.keywords:
                    if mtag not in keywords:
                        logger.debug(f"yes_keyword {mtag} NOT met in {result.name} : {keywords}")
                        break
                    found = True
                if not found:
                    continue

            links = set()
            for link in result.links:
                if 'youtube' in link:
                    if music_filter.youtube:
                        links.add(link)
                elif 'http' in link:
                    if music_filter.http:
                        links.add(link)
                elif 'spotify' in link:
                    if music_filter.spotify:
                        links.add(link)
                elif 'sftp' in link:
                    if music_filter.sftp:
                        links.add(link)
                    continue
                elif music_filter.local:
                    path = Path(link)
                    if not path.exists():
                        self.warn(f'{link} does not exist locally, skipping')
                    else:
                        links.add(link)
                    continue
                else:
                    self.warn(f'{link} format not recognized, keeping')
                    links.add(link)

            music = Music(
                title=result.name,
                artist=result.artist_name,
                album=result.album_name,
                genre=result.genre_name,
                size=result.size,
                length=result.length,
                keywords=keywords,
                track=result.track,
                rating=result.rating,
                links=list(links),
            )
            if not links:
                self.warn(f'{music} : no links available')
            musics.append(music)

        return Playlist(musics=musics, music_filter=music_filter)

    def clean_musics(self) -> None:
        query = """delete Artist;"""
        self.client.query(query)

    def delete_music(self, path: str) -> None:
        query = """delete Music filter .path = <str>$path;"""
        self.client.query(query, path=path)

    def upsert_music(
        self,
        music: File,
        sftp: bool = False,
        http: bool = False,
        local: bool = True,
        spotify: bool = False,
        youtube: bool = False,
    ) -> list[Any]:
        links = set()
        if local:
            links.add(str(music.path))
        if sftp and music.sftp_path:
            links.add(music.sftp_path)
        if http and music.http_path:
            links.add(music.http_path)
        if youtube and music.youtube_path:
            links.add(music.youtube_path)
        if spotify and music.spotify_path:
            links.add(music.spotify_path)
        query = """
with
    upsert_artist := (
        insert Artist {
            name := <str>$artist
        }
        unless conflict on .name else (select Artist)
    ),
    upsert_album := (
        insert Album {
            name := <str>$album,
            artist := upsert_artist
        }
        unless conflict on (.name, .artist) else (select Album)
    ),
    upsert_genre := (
        insert Genre {
            name := <str>$genre
        }
        unless conflict on .name else (select Genre)
    ),
    upsert_keywords := (
        for keyword in { array_unpack(<array<str>>$keywords) }
        union (
            insert Keyword {
                name := keyword
            }
            unless conflict on .name
            else (select Keyword)
        )
    ),
    select (
        insert Music {
            name := <str>$title,
            links := array_unpack(<array<str>>$links),
            size := <Size>$size,
            genre := upsert_genre,
            album := upsert_album,
            keywords := upsert_keywords,
            duration := to_duration(seconds := <float64>$length),
            track := <int16>$track,
            rating := <Rating>$rating
        }
        unless conflict on (.name, .album)
        else (
            update Music
            set {
                links := array_unpack(<array<str>>$links),
                size := <Size>$size,
                genre := upsert_genre,
                album := upsert_album,
                keywords := upsert_keywords,
                duration := to_duration(seconds := <float64>$length),
                track := <int16>$track,
                rating := <Rating>$rating
            }
        )
    );
"""
        return self.client.query(
            query,
            links=list(links),
            **music.to_dict(),
        )
