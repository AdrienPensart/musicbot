import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

from beartype import beartype
from edgedb.asyncio_client import create_async_client
from edgedb.blocking_client import create_client

from musicbot.defaults import (
    DEFAULT_HTTP,
    DEFAULT_LOCAL,
    DEFAULT_SFTP,
    DEFAULT_SPOTIFY,
    DEFAULT_YOUTUBE
)
from musicbot.file import File
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.queries import PLAYLIST_QUERY, UPSERT_QUERY

logger = logging.getLogger(__name__)


class MusicDb(MusicbotObject):
    def __init__(
        self,
        dsn: str,
    ):
        self.async_client = create_async_client(dsn=dsn)
        self.blocking_client = create_client(dsn=dsn)
        if not self.is_prod():
            os.environ['EDGEDB_CLIENT_SECURITY'] = 'insecure_dev_mode'

    @lru_cache(maxsize=None)
    @beartype
    def make_playlist(
        self,
        music_filter: MusicFilter | None = None,
    ) -> Playlist:
        music_filter = music_filter if music_filter is not None else MusicFilter()
        results = self.blocking_client.query(
            PLAYLIST_QUERY,
            titles=list(music_filter.titles),
            no_titles=list(music_filter.no_titles),

            artists=list(music_filter.artists),
            no_artists=list(music_filter.no_artists),

            albums=list(music_filter.albums),
            no_albums=list(music_filter.no_albums),

            genres=list(music_filter.genres),
            no_genres=list(music_filter.no_genres),

            keywords=list(music_filter.keywords),
            no_keywords=list(music_filter.no_keywords),

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

    def clean_musics(self) -> Any:
        query = """delete Artist;"""
        return self.blocking_client.query(query)

    def delete_music(self, path: str) -> Any:
        query = """delete Music filter .path = <str>$path;"""
        return self.blocking_client.query(query, path=path)

    def upsert_musics(
        self,
        musics: Sequence[File],
        sftp: bool = DEFAULT_SFTP,
        http: bool = DEFAULT_HTTP,
        local: bool = DEFAULT_LOCAL,
        spotify: bool = DEFAULT_SPOTIFY,
        youtube: bool = DEFAULT_YOUTUBE,
    ) -> list[Any]:
        results = []
        with self.progressbar(max_value=len(musics), prefix='Upserting musics') as pbar:
            for music in musics:
                try:
                    result = self.upsert_music(
                        music=music,
                        http=http,
                        sftp=sftp,
                        youtube=youtube,
                        spotify=spotify,
                        local=local,
                    )
                    if result is not None:
                        results.append(result)
                except Exception as e:  # pylint: disable=broad-except
                    self.err(f"{music} : {e}")
                finally:
                    pbar.value += 1
                    pbar.update()
        return results

    def upsert_music(
        self,
        music: File,
        sftp: bool = DEFAULT_SFTP,
        http: bool = DEFAULT_HTTP,
        local: bool = DEFAULT_LOCAL,
        spotify: bool = DEFAULT_SPOTIFY,
        youtube: bool = DEFAULT_YOUTUBE,
    ) -> Any:
        params = self._prepare_upsert_music(
            music=music,
            http=http,
            sftp=sftp,
            youtube=youtube,
            spotify=spotify,
            local=local,
        )
        if not params:
            return None
        return self.blocking_client.query(**params)

    @staticmethod
    def _prepare_upsert_music(
        music: File,
        local: bool = DEFAULT_LOCAL,
        http: bool = DEFAULT_HTTP,
        sftp: bool = DEFAULT_SFTP,
        spotify: bool = DEFAULT_SPOTIFY,
        youtube: bool = DEFAULT_YOUTUBE,
    ) -> dict[str, Any] | None:
        if 'no-title' in music.inconsistencies or 'no-artist' in music.inconsistencies or 'no-album' in music.inconsistencies:
            MusicbotObject.warn(f"{music} : missing mandatory fields title/album/artist : {music.inconsistencies}")
            return None

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

        return dict(
            query=UPSERT_QUERY,
            links=list(links),
            **music.to_dict(),
        )
