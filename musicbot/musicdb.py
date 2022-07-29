import asyncio
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
from edgedb.asyncio_client import AsyncIOClient, create_async_client
from edgedb.options import RetryOptions, TransactionOptions

from musicbot.defaults import DEFAULT_COROUTINES
from musicbot.exceptions import MusicbotError
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.helpers import async_gather, async_run
from musicbot.link_options import DEFAULT_LINK_OPTIONS, LinkOptions
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.queries import (
    BESTS_QUERY,
    DELETE_QUERY,
    PLAYLIST_QUERY,
    UPSERT_QUERY
)

logger = logging.getLogger(__name__)


@define(hash=True)
class MusicDb(MusicbotObject):
    client: AsyncIOClient

    def __attrs_post_init__(self) -> None:
        self.client = self.client.with_retry_options(
            RetryOptions(attempts=10)
        )

    def set_readonly(self, readonly: bool = True) -> None:
        '''set client to read only mode'''
        self.client = self.client.with_transaction_options(
            TransactionOptions(readonly=readonly)
        )

    @classmethod
    def from_dsn(
        cls,
        dsn: str,
    ) -> "MusicDb":
        if not cls.is_prod():
            os.environ['EDGEDB_CLIENT_SECURITY'] = 'insecure_dev_mode'
        return cls(client=create_async_client(dsn=dsn))

    @beartype
    def sync_query(self, query: str) -> Any:
        future = self.client.query_json(query)
        return async_run(future)

    @beartype
    async def execute_music_filter(
        self,
        query: str,
        music_filter: MusicFilter | None = None,
    ) -> Any:
        music_filter = music_filter if music_filter is not None else MusicFilter()
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
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> Playlist:
        results = await self.execute_music_filter(PLAYLIST_QUERY, music_filter)
        return Playlist.from_edgedb(
            name=name,
            results=results,
            music_filter=music_filter,
            link_options=link_options,
        )

    @cache
    def sync_make_playlist(
        self,
        name: str | None = None,
        music_filter: MusicFilter | None = None,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> Playlist:
        self.sync_ensure_connected()
        return async_run(self.make_playlist(name=name, music_filter=music_filter, link_options=link_options))

    async def clean_musics(self) -> Any:
        query = """delete Artist;"""
        if self.dry:
            return None
        return await self.client.query(query)

    def sync_clean_musics(self) -> Any:
        self.sync_ensure_connected()
        return async_run(self.clean_musics())

    async def soft_clean(self) -> Any:
        query = """
            delete Keyword filter not exists .musics;
            delete Album filter not exists .musics;
            delete Artist filter not exists .musics;
            delete Genre filter not exists .musics;
        """
        if self.dry:
            return None
        return await self.client.execute(query)

    def sync_soft_clean(self) -> Any:
        self.sync_ensure_connected()
        return async_run(self.soft_clean())

    def sync_ensure_connected(self) -> None:
        async_run(self.client.ensure_connected())

    async def delete_music(self, path: str) -> Any:
        if self.dry:
            return None
        return await self.client.query(DELETE_QUERY, path=path)

    def sync_delete_music(self, path: str) -> Any:
        self.sync_ensure_connected()
        return async_run(self.delete_music(path))

    async def upsert_path(
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
            result = await self.client.query_required_single(**params)
            keywords = set(keyword.name for keyword in result.keywords)
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

    def sync_upsert_path(
        self,
        path: Path,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> File | None:
        self.sync_ensure_connected()
        return async_run(self.upsert_path(path=path, link_options=link_options))

    def sync_upsert_folders(
        self,
        folders: Folders,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS,
        coroutines: int = DEFAULT_COROUTINES,
    ) -> list[File]:
        self.sync_ensure_connected()
        files = []
        failed: set[Path] = set()
        sem = asyncio.Semaphore(coroutines)

        with self.progressbar(prefix="Loading and inserting musics", max_value=len(folders.paths)) as pbar:
            async def upsert_worker(path: Path) -> None:
                async with sem:
                    try:
                        file = await self.upsert_path(path, link_options=link_options)
                        if not file:
                            self.err(f"{path} : unable to insert")
                        else:
                            files.append(file)
                    except MusicbotError as e:
                        self.err(e)
                        failed.add(path)
                    finally:
                        pbar.value += 1
                        pbar.update()

            async_gather(upsert_worker, folders.paths)

        if failed:
            with self.progressbar(prefix="Retry failed inserts", max_value=len(failed)) as pbar:
                async def retry_upsert_worker(path: Path) -> None:
                    async with sem:
                        try:
                            file = await self.upsert_path(path, link_options=link_options)
                            if not file:
                                self.err(f"{path} : unable to retry insert")
                            else:
                                files.append(file)
                        except MusicbotError as e:
                            self.err(e)
                        finally:
                            pbar.value += 1
                            pbar.update()
                async_gather(retry_upsert_worker, failed)

        return files

    @beartype
    async def make_bests(
        self,
        music_filter: MusicFilter | None = None,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> list[Playlist]:
        query = BESTS_QUERY.format(filtered_playlist=PLAYLIST_QUERY)
        logger.info(query)
        results = await self.execute_music_filter(query, music_filter)
        result = results[0]
        playlists = []
        for genre in result.genres:
            genre_name = f"genre_{genre.key.genre.name.lower()}"
            self.success(f"Genre {genre_name} : {len(genre.elements)}")
            playlist = Playlist.from_edgedb(name=genre_name, results=genre.elements, music_filter=music_filter, link_options=link_options)
            playlists.append(playlist)
        for keyword in result.keywords:
            keyword_name = f"keyword_{keyword.name.lower()}"
            self.success(f"Keyword {keyword_name} : {len(keyword.musics)}")
            playlist = Playlist.from_edgedb(name=keyword_name, results=keyword.musics, music_filter=music_filter, link_options=link_options)
            playlists.append(playlist)
        for rating in result.ratings:
            rating_name = f"rating_{rating.key.rating}"
            self.success(f"Rating {rating_name} : {len(rating.elements)}")
            playlist = Playlist.from_edgedb(name=rating_name, results=rating.elements, music_filter=music_filter, link_options=link_options)
            playlists.append(playlist)
        for artist in result.keywords_for_artist:
            artist_name = artist.artist
            for keyword in artist.keywords:
                keyword_name = keyword.keyword
                artist_keyword = f"{artist_name}{os.sep}keyword_{keyword_name.lower()}"
                self.success(f"Keyword by artist {artist_keyword} : {len(keyword.musics)}")
                playlist = Playlist.from_edgedb(name=artist_keyword, results=keyword.musics, music_filter=music_filter, link_options=link_options)
                playlists.append(playlist)
        for ratings_for_artist in result.ratings_for_artist:
            artist_name = ratings_for_artist.key.artist.name
            rating_name = ratings_for_artist.key.rating
            artist_rating = f"{artist_name}{os.sep}rating_{rating_name}"
            self.success(f"Rating by artist {artist_rating} : {len(ratings_for_artist.elements)}")
            playlist = Playlist.from_edgedb(name=artist_rating, results=ratings_for_artist.elements, music_filter=music_filter, link_options=link_options)
            playlists.append(playlist)
        return playlists

    def sync_make_bests(
        self,
        music_filter: MusicFilter | None = None,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> list[Playlist]:
        self.sync_ensure_connected()
        return async_run(self.make_bests(music_filter=music_filter, link_options=link_options))
