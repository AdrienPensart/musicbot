import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self
from urllib.parse import urlparse

import edgedb
import httpx
from async_lru import alru_cache
from attr import asdict as attr_asdict
from beartype import beartype
from edgedb.asyncio_client import AsyncIOClient, create_async_client
from edgedb.options import RetryOptions, TransactionOptions

from musicbot.defaults import DEFAULT_COROUTINES
from musicbot.file import File, Issue
from musicbot.folder import Folder
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.queries import (
    ARTISTS_QUERY,
    BESTS_QUERY,
    FOLDERS_QUERY,
    PLAYLIST_QUERY,
    REMOVE_PATH_QUERY,
    SEARCH_QUERY,
    SOFT_CLEAN_QUERY,
    UPSERT_QUERY,
)
from musicbot.scan_folders import ScanFolders
from musicbot.search_results import SearchResults

logger = logging.getLogger(__name__)


@beartype
@dataclass(unsafe_hash=True)
class MusicDb(MusicbotObject):
    client: AsyncIOClient
    graphql: str

    def __repr__(self) -> str:
        return self.dsn

    def set_readonly(self, readonly: bool = True) -> None:
        """set client to read only mode"""
        options = TransactionOptions(readonly=readonly)
        self.client = self.client.with_transaction_options(options)

    @property
    def dsn(self) -> str:
        return self.client._impl._connect_args["dsn"]

    @classmethod
    def from_dsn(
        cls,
        dsn: str,
        graphql: str | None = None,
        attempts: int = 10,
    ) -> Self:
        if not cls.is_prod():
            os.environ["EDGEDB_CLIENT_SECURITY"] = "insecure_dev_mode"
        client = create_async_client(dsn=dsn)
        options = RetryOptions(attempts=attempts)
        client = client.with_retry_options(options)

        if graphql is None:
            parsed = urlparse(dsn)
            graphql = f"http://{parsed.hostname}:{parsed.port}/db/edgedb/graphql"
        return cls(client=client, graphql=graphql)

    async def query_json(self, query: str) -> Any:
        return await self.client.query_json(query)

    async def graphql_query(self, query: str) -> httpx.Response | None:
        operation = {"query": query}
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url=self.graphql,
                    json=operation,
                )
                return response.raise_for_status()
        except httpx.HTTPError as error:
            self.err(f"{self} : unable to query graphql", error=error)
        return None

    @alru_cache
    async def folders(self) -> list[Folder]:
        results = await self.client.query(FOLDERS_QUERY)
        folders = []
        for result in results:
            logger.error(result)
            folder = Folder(
                path=result.name,
                name=result.name,
                ipv4=result.ipv4,
                username=result.username,
                n_artists=result.n_artists,
                all_artists=result.all_artists,
                n_albums=result.n_albums,
                n_musics=result.n_musics,
                n_keywords=result.n_keywords,
                all_keywords=result.all_keywords,
                n_genres=result.n_genres,
                all_genres=result.all_genres,
                human_size=result.human_size,
                human_duration=result.human_duration,
            )
            folders.append(folder)
        return folders

    async def artists(self) -> list[edgedb.Object]:
        return await self.client.query(ARTISTS_QUERY)

    async def execute_music_filters(
        self,
        query: str,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> set[edgedb.Object]:
        logger.debug(query)
        results = set()
        if not music_filters:
            music_filters = frozenset([MusicFilter()])
        for music_filter in music_filters:
            intermediate_results = await self.client.query(
                query,
                **attr_asdict(music_filter),
            )
            logger.debug(f"{len(intermediate_results)} intermediate results for {music_filter}")
            results.update(intermediate_results)
        logger.debug(f"{len(results)} results")
        return results

    async def make_playlist(
        self,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> Playlist:
        results = await self.execute_music_filters(PLAYLIST_QUERY, music_filters)
        return Playlist.from_edgedb(
            name=" | ".join([music_filter.help_repr() for music_filter in music_filters]),
            results=list(results),
        )

    async def clean_musics(self) -> None | list[edgedb.Object]:
        query = """delete Artist;"""
        if self.dry:
            return None
        return await self.client.query(query)

    async def drop(self) -> None | list[edgedb.Object]:
        query = """reset schema to initial;"""
        if self.dry:
            return None
        return await self.client.query(query)

    async def soft_clean(self) -> None | edgedb.Object:
        self.success("cleaning orphan musics, artists, albums, genres, keywords")
        if self.dry:
            return None
        return await self.client.query_single(SOFT_CLEAN_QUERY)

    async def ensure_connected(self) -> AsyncIOClient:
        return await self.client.ensure_connected()

    async def remove_music_path(self, path: str) -> None | edgedb.Object:
        logger.debug(f"{self} : removed {path}")
        if self.dry:
            return None
        return await self.client.query(REMOVE_PATH_QUERY, path=path)

    async def upsert_path(
        self,
        folder_and_path: tuple[Path, Path],
    ) -> File | None:
        folder, path = folder_and_path
        retries = 3
        last_error = None
        while retries > 0:
            try:
                if not (file := File.from_path(folder=folder, path=path)):
                    return None

                issues = file.issues
                if Issue.NO_TITLE in issues or Issue.NO_ARTIST in issues or Issue.NO_ALBUM in issues:
                    self.warn(f"{file} : missing mandatory fields title/album/artist : {issues}")
                    return None

                if not (input_music := file.music_input):
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
                folders = [Folder(path=folder.path, name=folder.name, ipv4=folder.ipv4, username=folder.username) for folder in result.folders]
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
                self.success(f"{self} : updated {path}")
                logger.debug(output_music)
                return file
            except edgedb.errors.TransactionSerializationError as error:
                retries -= 1
                self.warn(f"{path} : transaction error, {retries} retries left")
                last_error = error
                continue
            except edgedb.errors.NoDataError as error:
                self.err(f"{path} : no data result for query", error=error)
            except OSError as error:
                self.warn(f"{path} : unknown error", error=error)
            break
        self.err(f"{self} : too many transaction failures", errpr=last_error)
        return None

    async def upsert_folders(
        self,
        scan_folders: ScanFolders,
        coroutines: int = DEFAULT_COROUTINES,
    ) -> list[File]:
        failed_files: set[tuple[Path, Path]] = set()
        sem = asyncio.Semaphore(coroutines)

        max_value = len(scan_folders.folders_and_paths)
        if not max_value:
            self.warn(f"No music folder or paths discovered from directories {scan_folders.directories}")
            return []

        files = []
        with self.progressbar(desc="Loading and inserting musics", max_value=max_value) as pbar:

            async def upsert_worker(folder_and_path: tuple[Path, Path]) -> None:
                async with sem:
                    try:
                        if not (file := await self.upsert_path(folder_and_path=folder_and_path)):
                            self.err(f"{self} : unable to insert {folder_and_path}")
                            failed_files.add(folder_and_path)
                        else:
                            files.append(file)
                    finally:
                        pbar.value += 1
                        _ = pbar.update()

            _ = await self.async_gather(upsert_worker, scan_folders.folders_and_paths)
        if failed_files:
            self.warn(f"Unable to insert {len(failed_files)} files")
        return files

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

    async def search(
        self,
        pattern: str,
    ) -> SearchResults:
        result = await self.client.query_single(query=SEARCH_QUERY, pattern=pattern)
        search_results = SearchResults(
            musics=result.musics,
            artists=result.artists,
            albums=result.albums,
            genres=result.genres,
            keywords=result.keywords,
        )
        return search_results
