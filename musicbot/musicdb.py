import logging
import os
from functools import cache
from pathlib import Path
from typing import Any, Sequence

from beartype import beartype
from edgedb.asyncio_client import create_async_client
from edgedb.blocking_client import create_client

from musicbot.file import File
from musicbot.link_options import DEFAULT_LINK_OPTIONS, LinkOptions
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

    @cache
    @beartype
    def make_playlist(
        self,
        music_filter: MusicFilter | None = None,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
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
                    if link_options.youtube:
                        links.add(link)
                elif 'http' in link:
                    if link_options.http:
                        links.add(link)
                elif 'spotify' in link:
                    if link_options.spotify:
                        links.add(link)
                elif 'sftp' in link:
                    if link_options.sftp:
                        links.add(link)
                    continue
                elif link_options.local:
                    path = Path(link)
                    if not path.exists():
                        self.warn(f'{link} does not exist locally, skipping')
                    else:
                        links.add(link)
                    continue
                else:
                    logger.debug(f'{link} format not recognized, keeping')

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
                logger.debug(f'{music} : no links available')
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
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS,
    ) -> list[Any] | None:
        def worker(music: File) -> Any | None:
            try:
                return self.upsert_music(
                    music=music,
                    link_options=link_options,
                )
            except Exception as e:  # pylint: disable=broad-except
                self.err(f"{music} : {e}")
            return None

        results = self.parallel(worker, musics, threads=1)
        return results

    def upsert_music(
        self,
        music: File,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> Any:
        if 'no-title' in music.inconsistencies or 'no-artist' in music.inconsistencies or 'no-album' in music.inconsistencies:
            MusicbotObject.warn(f"{music} : missing mandatory fields title/album/artist : {music.inconsistencies}")
            return None

        params = dict(
            query=UPSERT_QUERY,
            **music.to_dict(link_options),
        )
        return self.blocking_client.query(**params)

    def upsert_path(
        self,
        path: Path,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> File | None:
        try:
            music = File.from_path(path=path)
            self.upsert_music(
                music=music,
                link_options=link_options,
            )
            return music
        except OSError as e:
            logger.error(e)
        return None
