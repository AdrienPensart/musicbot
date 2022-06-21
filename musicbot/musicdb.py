import logging
import os
import sys
from functools import cache
from pathlib import Path
from typing import Any

import edgedb
from attr import asdict, define
from beartype import beartype
from deepdiff import DeepDiff  # type: ignore
from edgedb.blocking_client import Client, create_client
from edgedb.options import RetryOptions, TransactionOptions

from musicbot.exceptions import MusicbotError
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.link_options import DEFAULT_LINK_OPTIONS, LinkOptions
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.queries import DELETE_QUERY, PLAYLIST_QUERY, UPSERT_QUERY

logger = logging.getLogger(__name__)


@define(hash=True)
class MusicDb(MusicbotObject):
    blocking_client: Client

    def __attrs_post_init__(self) -> None:
        self.blocking_client = self.blocking_client.with_retry_options(
            RetryOptions(attempts=10)
        )

    def set_readonly(self) -> None:
        '''set client to read only mode'''
        self.blocking_client = self.blocking_client.with_transaction_options(
            TransactionOptions(readonly=True)
        )

    @classmethod
    def from_dsn(
        cls,
        dsn: str,
    ) -> "MusicDb":
        if not cls.is_prod():
            os.environ['EDGEDB_CLIENT_SECURITY'] = 'insecure_dev_mode'
        return cls(blocking_client=create_client(dsn=dsn))

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
            shuffle=not music_filter.shuffle,
        )

        musics = []
        for result in results:
            keywords = list(keyword for keyword in result.all_keywords)
            links = set()
            for link in result.links:
                # elif 'youtube' in link:
                #     if link_options.youtube:
                #         links.add(link)
                # elif 'spotify' in link:
                #     if link_options.spotify:
                #         links.add(link)
                if 'http' in link:
                    if link_options.http:
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
                keywords=set(keywords),
                track=result.track,
                rating=result.rating,
                links=set(links),
            )
            if not links:
                logger.debug(f'{music} : no links available')
            musics.append(music)

        return Playlist(musics=musics, music_filter=music_filter)

    def clean_musics(self) -> Any:
        query = """delete Artist;"""
        if self.dry:
            return None
        return self.blocking_client.query(query)

    def delete_music(self, path: str) -> Any:
        if self.dry:
            return None
        return self.blocking_client.query(DELETE_QUERY, path=path)

    def upsert_path(
        self,
        path: Path,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> File | None:
        try:
            file = File.from_path(path=path)

            if 'no-title' in file.inconsistencies or 'no-artist' in file.inconsistencies or 'no-album' in file.inconsistencies:
                MusicbotObject.warn(f"{file} : missing mandatory fields title/album/artist : {file.inconsistencies}")
                return None

            if self.dry:
                return file

            input_music = file.to_music(link_options)
            params = dict(
                query=UPSERT_QUERY,
                **asdict(input_music),
            )
            result = self.blocking_client.query_required_single(**params)
            output_music = Music(
                title=result.name,
                artist=result.artist_name,
                album=result.album_name,
                genre=result.genre_name,
                size=result.size,
                length=result.length,
                keywords=set(result.all_keywords),
                track=result.track,
                rating=result.rating,
                links=set(result.links),
            )

            music_diff = DeepDiff(asdict(input_music), asdict(output_music), ignore_order=True)
            if music_diff:
                MusicbotObject.err(f"{file} : file and music diff detected : ")
                MusicbotObject.print_json(music_diff, file=sys.stderr)

            return file
        except edgedb.errors.TransactionSerializationError as e:
            raise MusicbotError(f"{path} : transaction error : {e}") from e
        except edgedb.errors.NoDataError as e:
            raise MusicbotError(f"{path} : no data result for query : {e}") from e
        except OSError as e:
            logger.error(e)
        return None

    def upsert_folders(
        self,
        folders: Folders,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> list[File]:
        def worker(path: Path) -> File | None:
            try:
                file = self.upsert_path(path, link_options=link_options)
                if not file:
                    MusicbotObject.err(f"{path} : unable to insert")
                    return None
                return file
            except MusicbotError as e:
                self.err(e)
            return None

        return folders.apply(worker, prefix="Loading and inserting musics")
