import asyncio
import logging
import os
from functools import cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import edgedb
import requests
from attr import asdict, define
from beartype import beartype
from edgedb.asyncio_client import AsyncIOClient, create_async_client
from edgedb.options import RetryOptions, TransactionOptions

from musicbot.defaults import DEFAULT_COROUTINES
from musicbot.exceptions import MusicbotError
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.helpers import async_gather, async_run
from musicbot.music import Folder, Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.queries import (
    BESTS_QUERY,
    DELETE_QUERY,
    PLAYLIST_QUERY,
    SEARCH_QUERY,
    SOFT_CLEAN_QUERY,
    UPSERT_QUERY
)

logger = logging.getLogger(__name__)


@define(hash=True)
class MusicDb(MusicbotObject):
    client: AsyncIOClient
    session: requests.Session = requests.Session()
    graphql: str | None = None

    def __attrs_post_init__(self) -> None:
        self.client = self.client.with_retry_options(
            RetryOptions(attempts=10)
        )
        if self.graphql is None:
            parsed = urlparse(self.client._impl._connect_args['dsn'])
            self.graphql = f"http://{parsed.hostname}:{parsed.port}/db/edgedb/graphql"

    @beartype
    def set_readonly(self, readonly: bool = True) -> None:
        '''set client to read only mode'''
        self.client = self.client.with_transaction_options(
            TransactionOptions(readonly=readonly)
        )

    @classmethod
    def from_dsn(
        cls,
        dsn: str,
        graphql: str | None = None,
    ) -> "MusicDb":
        if not cls.is_prod():
            os.environ['EDGEDB_CLIENT_SECURITY'] = 'insecure_dev_mode'
        return cls(client=create_async_client(dsn=dsn), graphql=graphql)

    @beartype
    def sync_query(self, query: str) -> Any:
        future = self.client.query_json(query)
        return async_run(future)

    @beartype
    def graphql_query(self, query: str) -> Any:
        if not self.graphql:
            return None
        operation = {
            'query': query
        }
        response = self.session.post(
            self.graphql,
            json=operation,
        )
        logger.debug(response)
        return response.json()

    @beartype
    async def execute_music_filter(
        self,
        query: str,
        music_filter: MusicFilter | None = None,
    ) -> Any:
        music_filter = music_filter if music_filter is not None else MusicFilter()
        logger.info(query)
        results = await self.client.query(
            query,
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
            limit=music_filter.limit,
        )
        return results

    @beartype
    async def make_playlist(
        self,
        name: str | None = None,
        music_filter: MusicFilter | None = None,
    ) -> Playlist:
        results = await self.execute_music_filter(PLAYLIST_QUERY, music_filter)
        logger.debug(f"{len(results)} results")
        return Playlist.from_edgedb(
            name=name,
            results=results,
            music_filter=music_filter,
        )

    @cache
    def sync_make_playlist(
        self,
        name: str | None = None,
        music_filter: MusicFilter | None = None,
    ) -> Playlist:
        self.sync_ensure_connected()
        return async_run(self.make_playlist(name=name, music_filter=music_filter))

    @beartype
    async def clean_musics(self) -> Any:
        query = """delete Artist;"""
        if self.dry:
            return None
        return await self.client.query(query)

    @beartype
    def sync_clean_musics(self) -> Any:
        self.sync_ensure_connected()
        return async_run(self.clean_musics())

    @beartype
    async def soft_clean(self) -> Any:
        if self.dry:
            return None
        self.success("cleaning orphan keywords, albums, artists, genres")
        return await self.client.execute(SOFT_CLEAN_QUERY)

    @beartype
    def sync_soft_clean(self) -> Any:
        self.sync_ensure_connected()
        return async_run(self.soft_clean())

    @beartype
    def sync_ensure_connected(self) -> None:
        async_run(self.client.ensure_connected())

    @beartype
    async def delete_music(self, path: str) -> Any:
        if self.dry:
            return None
        return await self.client.query(DELETE_QUERY, path=path)

    @beartype
    def sync_delete_music(self, path: str) -> Any:
        self.sync_ensure_connected()
        return async_run(self.delete_music(path))

    @beartype
    async def upsert_path(
        self,
        folder_and_path: tuple[Path, Path],
    ) -> File | None:
        folder, path = folder_and_path
        try:
            file = File.from_path(folder=folder, path=path)

            if 'no-title' in file.inconsistencies or 'no-artist' in file.inconsistencies or 'no-album' in file.inconsistencies:
                MusicbotObject.warn(f"{file} : missing mandatory fields title/album/artist : {file.inconsistencies}")
                return None

            input_music = file.to_music()
            if not input_music.folders:
                self.err(f"{file} : no folder set")
            folder_obj, *_ = input_music.folders
            data = asdict(input_music)
            data['ipv4'] = folder_obj.ipv4
            data['user'] = folder_obj.user
            data['folder'] = folder_obj.name
            data['path'] = folder_obj.path
            del data['folders']
            params = dict(
                query=UPSERT_QUERY,
                **data,
            )

            if self.dry:
                return file

            result = await self.client.query_required_single(**params)
            keywords = frozenset(keyword.name for keyword in result.keywords)
            folders = frozenset(Folder(path=folder.path, name=folder.name, ipv4=folder.ipv4, user=folder.user) for folder in result.folders)
            output_music = Music(
                title=result.name,
                artist=result.artist.name,
                album=result.album.name,
                genre=result.genre.name,
                size=result.size,
                length=result.length,
                keywords=keywords,
                track=result.track,
                rating=result.rating,
                folders=folders,
            )
            logger.debug(output_music)

            # from deepdiff import DeepDiff  # type: ignore
            # music_diff = DeepDiff(
            #     asdict(input_music),
            #     asdict(output_music),
            #     ignore_order=True,
            # )
            # if music_diff:
            #     MusicbotObject.err(f"{file} : file and music diff detected : ")
            #     MusicbotObject.print_json(music_diff, file=sys.stderr)

            return file
        except edgedb.errors.TransactionSerializationError as e:
            raise MusicbotError(f"{path} : transaction error : {e}") from e
        except edgedb.errors.NoDataError as e:
            raise MusicbotError(f"{path} : no data result for query : {e}") from e
        except OSError as e:
            logger.error(e)
        return None

    @beartype
    def sync_upsert_path(
        self,
        folder_and_path: tuple[Path, Path],
    ) -> File | None:
        self.sync_ensure_connected()
        return async_run(self.upsert_path(folder_and_path=folder_and_path))

    @beartype
    def sync_upsert_folders(
        self,
        folders: Folders,
        coroutines: int = DEFAULT_COROUTINES,
    ) -> list[File]:
        self.sync_ensure_connected()
        files = []
        failed: set[tuple[Path, Path]] = set()
        sem = asyncio.Semaphore(coroutines)

        with self.progressbar(prefix="Loading and inserting musics", max_value=len(folders.folders_and_paths)) as pbar:
            async def upsert_worker(folder_and_path: tuple[Path, Path]) -> None:
                async with sem:
                    try:
                        file = await self.upsert_path(folder_and_path=folder_and_path)
                        if not file:
                            self.err(f"{folder_and_path} : unable to insert")
                        else:
                            files.append(file)
                    except MusicbotError as e:
                        self.err(e)
                        failed.add(folder_and_path)
                    finally:
                        pbar.value += 1
                        pbar.update()

            async_gather(upsert_worker, folders.folders_and_paths)
        return files

    @beartype
    async def make_bests(
        self,
        music_filter: MusicFilter | None = None,
    ) -> list[Playlist]:
        results = await self.execute_music_filter(BESTS_QUERY, music_filter)
        result = results[0]
        playlists = []
        for genre in result.genres:
            genre_name = f"genre_{genre.key.genre.name.lower()}"
            self.success(f"Genre {genre_name} : {len(genre.elements)}")
            playlist = Playlist.from_edgedb(name=genre_name, results=genre.elements, music_filter=music_filter)
            playlists.append(playlist)
        for keyword in result.keywords:
            keyword_name = f"keyword_{keyword.name.lower()}"
            self.success(f"Keyword {keyword_name} : {len(keyword.musics)}")
            playlist = Playlist.from_edgedb(name=keyword_name, results=keyword.musics, music_filter=music_filter)
            playlists.append(playlist)
        for rating in result.ratings:
            rating_name = f"rating_{rating.key.rating}"
            self.success(f"Rating {rating_name} : {len(rating.elements)}")
            playlist = Playlist.from_edgedb(name=rating_name, results=rating.elements, music_filter=music_filter)
            playlists.append(playlist)
        for artist in result.keywords_for_artist:
            artist_name = artist.artist
            for keyword in artist.keywords:
                keyword_name = keyword.keyword
                artist_keyword = f"{artist_name}{os.sep}keyword_{keyword_name.lower()}"
                self.success(f"Keyword by artist {artist_keyword} : {len(keyword.musics)}")
                playlist = Playlist.from_edgedb(name=artist_keyword, results=keyword.musics, music_filter=music_filter)
                playlists.append(playlist)
        for ratings_for_artist in result.ratings_for_artist:
            artist_name = ratings_for_artist.key.artist.name
            rating_name = ratings_for_artist.key.rating
            artist_rating = f"{artist_name}{os.sep}rating_{rating_name}"
            self.success(f"Rating by artist {artist_rating} : {len(ratings_for_artist.elements)}")
            playlist = Playlist.from_edgedb(name=artist_rating, results=ratings_for_artist.elements, music_filter=music_filter)
            playlists.append(playlist)
        return playlists

    @beartype
    def sync_make_bests(
        self,
        music_filter: MusicFilter | None = None,
    ) -> list[Playlist]:
        self.sync_ensure_connected()
        return async_run(self.make_bests(music_filter=music_filter))

    @beartype
    async def search(
        self,
        pattern: str,
    ) -> Playlist:
        results = await self.client.query(query=SEARCH_QUERY, pattern=pattern)
        return Playlist.from_edgedb(
            name=pattern,
            results=results,
        )

    @beartype
    def sync_search(
        self,
        pattern: str,
    ) -> Playlist:
        self.sync_ensure_connected()
        return async_run(self.search(pattern=pattern))
