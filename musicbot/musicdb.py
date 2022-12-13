import asyncio
import logging
import os
from functools import cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import edgedb
from attr import asdict, define
from beartype import beartype
from edgedb.asyncio_client import AsyncIOClient, create_async_client
from edgedb.options import RetryOptions, TransactionOptions
from requests import Response, Session

from musicbot.artist import Artist
from musicbot.defaults import DEFAULT_COROUTINES
from musicbot.exceptions import MusicbotError
from musicbot.file import File, Issue
from musicbot.folders import Folders
from musicbot.helpers import async_gather, async_run
from musicbot.music import Folder, Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.queries import (
    ARTISTS_QUERY,
    BESTS_QUERY,
    PLAYLIST_QUERY,
    REMOVE_PATH_QUERY,
    SEARCH_QUERY,
    SOFT_CLEAN_QUERY,
    UPSERT_QUERY
)

logger = logging.getLogger(__name__)


@define(repr=False, hash=True)
class MusicDb(MusicbotObject):
    client: AsyncIOClient
    dsn: str
    session: Session = Session()
    graphql: str | None = None

    def __attrs_post_init__(self) -> None:
        self.client = self.client.with_retry_options(
            RetryOptions(attempts=10)
        )
        if self.graphql is None:
            parsed = urlparse(self.client._impl._connect_args['dsn'])
            self.graphql = f"http://{parsed.hostname}:{parsed.port}/db/edgedb/graphql"

    def __repr__(self) -> str:
        return self.dsn

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
        return cls(
            client=create_async_client(dsn=dsn),
            dsn=dsn,
            graphql=graphql
        )

    @beartype
    def sync_query(self, query: str) -> Any:
        future = self.client.query_json(query)
        return async_run(future)

    @beartype
    def graphql_query(self, query: str) -> Response | None:
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
        return response

    @beartype
    async def artists(self) -> list[Artist]:
        results = await self.client.query(ARTISTS_QUERY)
        artists_list = []
        for result in results:
            keywords = frozenset(result.all_keywords)
            artist = Artist(
                name=result.name,
                length=result.length,
                size=result.size,
                keywords=keywords,
                rating=result.rating,
                albums=result.n_albums,
                musics=result.n_musics,
                genres=result.all_genres,
            )
            artists_list.append(artist)
        return artists_list

    @cache
    def sync_artists(self) -> list[Artist]:
        self.sync_ensure_connected()
        return async_run(self.artists())

    @beartype
    async def execute_music_filters(
        self,
        query: str,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> set[Any]:
        logger.debug(query)
        results = set()
        if not music_filters:
            music_filters = frozenset([MusicFilter()])
        for music_filter in music_filters:
            intermediate_results = await self.client.query(
                query,
                **asdict(music_filter),
            )
            logger.debug(f"{len(intermediate_results)} intermediate results for {music_filter}")
            results.update(intermediate_results)
        logger.debug(f"{len(results)} results")
        return results

    @beartype
    async def make_playlist(
        self,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> Playlist:
        results = await self.execute_music_filters(PLAYLIST_QUERY, music_filters)
        return Playlist.from_edgedb(
            name=" | ".join([music_filter.help_repr() for music_filter in music_filters]),
            results=results,
        )

    @cache
    def sync_make_playlist(
        self,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> Playlist:
        self.sync_ensure_connected()
        return async_run(self.make_playlist(
            music_filters=music_filters
        ))

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
        self.success("cleaning orphan musics, artists, albums, genres, keywords")
        if self.dry:
            return None
        return await self.client.query_single(SOFT_CLEAN_QUERY)

    @beartype
    def sync_soft_clean(self) -> Any:
        self.sync_ensure_connected()
        return async_run(self.soft_clean())

    @beartype
    def sync_ensure_connected(self) -> None:
        async_run(self.client.ensure_connected())

    @beartype
    async def remove_music_path(self, path: str) -> Any:
        if self.dry:
            return None
        return await self.client.query(REMOVE_PATH_QUERY, path=path)

    @beartype
    def sync_remove_music_path(self, path: str) -> Any:
        self.sync_ensure_connected()
        return async_run(self.remove_music_path(path))

    @beartype
    async def upsert_path(
        self,
        folder_and_path: tuple[Path, Path],
    ) -> File | None:
        folder, path = folder_and_path
        try:
            file = File.from_path(folder=folder, path=path)
            if not file:
                return None

            if Issue.NO_TITLE in file.issues or Issue.NO_ARTIST in file.issues or Issue.NO_ALBUM in file.issues:
                self.warn(f"{file} : missing mandatory fields title/album/artist : {file.issues}")
                return None

            input_music = file.music_input
            if not input_music:
                self.err(f"{file} : cannot upsert music without physical folder !")
                return None

            params = dict(
                query=UPSERT_QUERY,
                **input_music,
            )

            if self.dry:
                return file

            result = await self.client.query_required_single(**params)
            keywords = frozenset(keyword.name for keyword in result.keywords)
            folders = [Folder(path=folder.path, name=folder.name, ipv4=folder.ipv4, user=folder.user) for folder in result.folders]
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
                folders=frozenset(folders),
            )
            logger.debug(output_music)

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
        failed_files: set[tuple[Path, Path]] = set()
        sem = asyncio.Semaphore(coroutines)

        max_value = len(folders.folders_and_paths)
        with self.progressbar(desc="Loading and inserting musics", max_value=max_value) as pbar:
            async def upsert_worker(folder_and_path: tuple[Path, Path]) -> None:
                async with sem:
                    try:
                        file = await self.upsert_path(folder_and_path=folder_and_path)
                        if not file:
                            self.err(f"{self} : unable to insert {folder_and_path}")
                        else:
                            files.append(file)
                    except MusicbotError as e:
                        self.err(e)
                        failed_files.add(folder_and_path)
                    finally:
                        pbar.value += 1
                        pbar.update()

            async_gather(upsert_worker, folders.folders_and_paths)
        if failed_files:
            self.warn(f"Unable to insert {len(failed_files)} files")
        return files

    @beartype
    async def make_bests(
        self,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> list[Playlist]:
        results = await self.execute_music_filters(BESTS_QUERY, music_filters)
        playlists = []
        for result in results:
            for genre in result.genres:
                genre_name = f"genre_{genre.key.genre.name.lower()}"
                self.success(f"Genre {genre_name} : {len(genre.elements)}")
                playlist = Playlist.from_edgedb(name=genre_name, results=genre.elements)
                playlists.append(playlist)
            for keyword in result.keywords:
                keyword_name = f"keyword_{keyword.name.lower()}"
                self.success(f"Keyword {keyword_name} : {len(keyword.musics)}")
                playlist = Playlist.from_edgedb(name=keyword_name, results=keyword.musics)
                playlists.append(playlist)
            for rating in result.ratings:
                rating_name = f"rating_{rating.key.rating}"
                self.success(f"Rating {rating_name} : {len(rating.elements)}")
                playlist = Playlist.from_edgedb(name=rating_name, results=rating.elements)
                playlists.append(playlist)
            for artist in result.keywords_for_artist:
                artist_name = artist.artist
                for keyword in artist.keywords:
                    keyword_name = keyword.keyword
                    artist_keyword = f"{artist_name}{os.sep}keyword_{keyword_name.lower()}"
                    self.success(f"Keyword by artist {artist_keyword} : {len(keyword.musics)}")
                    playlist = Playlist.from_edgedb(name=artist_keyword, results=keyword.musics)
                    playlists.append(playlist)
            for ratings_for_artist in result.ratings_for_artist:
                artist_name = ratings_for_artist.key.artist.name
                rating_name = ratings_for_artist.key.rating
                artist_rating = f"{artist_name}{os.sep}rating_{rating_name}"
                self.success(f"Rating by artist {artist_rating} : {len(ratings_for_artist.elements)}")
                playlist = Playlist.from_edgedb(name=artist_rating, results=ratings_for_artist.elements)
                playlists.append(playlist)
        return playlists

    @beartype
    def sync_make_bests(
        self,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> list[Playlist]:
        self.sync_ensure_connected()
        return async_run(self.make_bests(music_filters=music_filters))

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
