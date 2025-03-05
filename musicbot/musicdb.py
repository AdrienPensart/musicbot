import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

import gel
import httpx
from async_lru import alru_cache
from beartype import beartype
from beartype.typing import Self
from gel.asyncio_client import AsyncIOClient, create_async_client
from gel.options import RetryOptions, TransactionOptions

from musicbot.folder import Folder
from musicbot.music import Music, MusicInput
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist
from musicbot.queries.delete_musics_async_edgeql import delete_musics
from musicbot.queries.drop_schema_async_edgeql import drop_schema
from musicbot.queries.gen_bests_async_edgeql import gen_bests
from musicbot.queries.gen_playlist_async_edgeql import gen_playlist
from musicbot.queries.pike_keywords_async_edgeql import pike_keywords
from musicbot.queries.remove_async_edgeql import remove
from musicbot.queries.select_artists_async_edgeql import select_artists
from musicbot.queries.select_folder_async_edgeql import select_folder
from musicbot.queries.soft_clean_async_edgeql import soft_clean
from musicbot.queries.upsert_album_async_edgeql import upsert_album
from musicbot.queries.upsert_artist_async_edgeql import upsert_artist
from musicbot.queries.upsert_folder_async_edgeql import upsert_folder
from musicbot.queries.upsert_genre_async_edgeql import upsert_genre
from musicbot.queries.upsert_keyword_async_edgeql import upsert_keyword
from musicbot.queries.upsert_music_async_edgeql import upsert_music

logger = logging.getLogger(__name__)


@dataclass
class ArtistAlbums:
    id: UUID
    albums: dict[str, UUID] = field(default_factory=dict)


@dataclass
class UpsertCache:
    folders: dict[str, UUID] = field(default_factory=dict)
    artists_and_albums: dict[str, ArtistAlbums] = field(default_factory=dict)
    genres: dict[str, UUID] = field(default_factory=dict)
    keywords: dict[str, UUID] = field(default_factory=dict)


@beartype
@dataclass(unsafe_hash=True)
class MusicDb(MusicbotObject):
    client: AsyncIOClient
    graphql: str
    upsert_cache: UpsertCache = field(default_factory=UpsertCache, hash=False)

    def __repr__(self) -> str:
        return self.dsn

    def set_readonly(self, readonly: bool = True) -> None:
        """set client to read only mode"""
        options = TransactionOptions(readonly=readonly, deferrable=True)
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
            os.environ["GEL_CLIENT_SECURITY"] = "insecure_dev_mode"
        client = create_async_client(dsn=dsn, max_concurrency=MusicbotObject.coroutines)
        options = RetryOptions(attempts=attempts)
        client = client.with_retry_options(options)

        if graphql is None:
            parsed = urlparse(dsn)
            graphql = f"https://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/db/edgedb/graphql"
        return cls(client=client, graphql=graphql)

    @property
    def graphiql(self) -> str:
        return f"{self.graphql}/explore"

    async def query_json(self, query: str) -> str:
        return await self.client.query_json(query)

    async def graphql_query(self, query: str) -> httpx.Response | None:
        operation = {"query": query}
        try:
            async with httpx.AsyncClient(timeout=60, verify=False) as client:
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
        results = await select_folder(self.client)
        folders = []
        for result in results:
            folder = Folder.from_gel(folder=result)
            folders.append(folder)
        return folders

    async def artists(self) -> list[gel.Object]:
        return await select_artists(self.client)

    async def make_playlist(
        self,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> Playlist:
        if not music_filters:
            music_filters = frozenset([MusicFilter()])

        results = set()
        for music_filter in music_filters:
            intermediate_results = await gen_playlist(
                self.client,
                min_length=music_filter.min_length,
                max_length=music_filter.max_length,
                min_size=music_filter.min_size,
                max_size=music_filter.max_size,
                min_rating=music_filter.min_rating,
                max_rating=music_filter.max_rating,
                artist=music_filter.artist,
                album=music_filter.album,
                genre=music_filter.genre,
                title=music_filter.title,
                keyword=music_filter.keyword,
                pattern=music_filter.pattern,
                limit=music_filter.limit,
            )
            results.update(intermediate_results)
        name = " | ".join([music_filter.help_repr() for music_filter in music_filters])
        return Playlist.from_gel(
            name=name,
            results=list(results),
        )

    async def clean_musics(self) -> None:
        if not self.dry:
            _ = await delete_musics(self.client)

    async def pike_keywords(self) -> list[str]:
        return await pike_keywords(self.client)

    async def drop(self) -> None:
        if not self.dry:
            await drop_schema(self.client)

    async def soft_clean(self) -> None:
        if not self.dry:
            cleaned = await soft_clean(self.client)
            self.success(f"cleaned {cleaned.musics_deleted} musics")
            self.success(f"cleaned {cleaned.artists_deleted} artists")
            self.success(f"cleaned {cleaned.albums_deleted} albums")
            self.success(f"cleaned {cleaned.genres_deleted} genres")
            self.success(f"clceaned {cleaned.keywords_deleted} keywords")

    async def remove_music_path(self, path: str) -> None | gel.Object:
        logger.debug(f"{self} : removed {path}")
        if self.dry:
            return None
        return await remove(self.client, path=path)

    async def upsert_music(self, music_input: MusicInput) -> Music | None:
        if self.dry:
            return None

        retries = 3
        last_error = None

        while retries > 0:
            try:
                if music_input.artist not in self.upsert_cache.artists_and_albums:
                    artist_result = await upsert_artist(self.client, artist=music_input.artist)
                    artist_id = artist_result.id
                    self.upsert_cache.artists_and_albums[music_input.artist] = ArtistAlbums(id=artist_id)
                else:
                    artist_id = self.upsert_cache.artists_and_albums[music_input.artist].id

                if music_input.folder not in self.upsert_cache.folders:
                    folder_result = await upsert_folder(self.client, username=music_input.username, ipv4=music_input.ipv4, folder=music_input.folder)
                    folder_id = folder_result.id
                    self.upsert_cache.folders[music_input.folder] = folder_id
                else:
                    folder_id = self.upsert_cache.folders[music_input.folder]

                if music_input.genre not in self.upsert_cache.genres:
                    genre_result = await upsert_genre(self.client, genre=music_input.genre)
                    genre_id = genre_result.id
                    self.upsert_cache.genres[music_input.genre] = genre_id
                else:
                    genre_id = self.upsert_cache.genres[music_input.genre]

                keyword_ids = []
                for keyword in music_input.keywords:
                    if keyword not in self.upsert_cache.keywords:
                        keyword_result = await upsert_keyword(self.client, keyword=keyword)
                        keyword_id = keyword_result.id
                        self.upsert_cache.keywords[keyword] = keyword_id
                    else:
                        keyword_id = self.upsert_cache.keywords[keyword]
                    keyword_ids.append(keyword_id)

                if music_input.album not in self.upsert_cache.artists_and_albums[music_input.artist].albums:
                    album_result = await upsert_album(self.client, album=music_input.album, artist=artist_id)
                    album_id = album_result.id
                    self.upsert_cache.artists_and_albums[music_input.artist].albums[music_input.album] = album_id
                else:
                    album_id = self.upsert_cache.artists_and_albums[music_input.artist].albums[music_input.album]

                result = await upsert_music(
                    self.client,
                    title=music_input.title,
                    folder=folder_id,
                    path=music_input.path,
                    size=music_input.size,
                    length=music_input.length,
                    rating=music_input.rating,
                    keywords=keyword_ids,
                    album=album_id,
                    genre=genre_id,
                    track=music_input.track,
                )
                keywords = frozenset(keyword.name for keyword in result.keywords)
                folders = [Folder(path=Path(folder.path), name=folder.name, ipv4=folder.ipv4, username=folder.username) for folder in result.folders if folder.path is not None]
                music = Music(
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
                self.success(f"{self} : updated {music_input}")
                return music
            except gel.errors.TransactionSerializationError as error:
                retries -= 1
                self.warn(f"{music_input} : transaction error, {retries} retries left")
                last_error = error
                continue
            except gel.errors.NoDataError as error:
                self.err(f"{music_input} : no data result for query", error=error)
            except OSError as error:
                self.warn(f"{music_input} : unknown error", error=error)
            return None
        self.err(f"{self} : too many transaction failures", error=last_error)
        return None

    async def make_bests(
        self,
        music_filters: frozenset[MusicFilter] = frozenset(),
    ) -> list[Playlist]:
        if not music_filters:
            music_filters = frozenset([MusicFilter()])

        results = []
        for music_filter in music_filters:
            intermediate_result = await gen_bests(
                self.client,
                min_length=music_filter.min_length,
                max_length=music_filter.max_length,
                min_size=music_filter.min_size,
                max_size=music_filter.max_size,
                min_rating=music_filter.min_rating,
                max_rating=music_filter.max_rating,
                artist=music_filter.artist,
                album=music_filter.album,
                genre=music_filter.genre,
                title=music_filter.title,
                keyword=music_filter.keyword,
                pattern=music_filter.pattern,
                limit=music_filter.limit,
            )
            results.append(intermediate_result)

        playlists = []
        for result in results:
            for genre in result.genres:
                genre_name = f"genre_{genre.key.genre.name.lower()}"
                self.success(f"Genre {genre_name} : {len(genre.elements)}")
                playlist = Playlist.from_gel(name=genre_name, results=genre.elements)
                playlists.append(playlist)
            for keyword in result.keywords:
                keyword_name = f"keyword_{keyword.name.lower()}"
                self.success(f"Keyword {keyword_name} : {len(keyword.musics)}")
                playlist = Playlist.from_gel(name=keyword_name, results=keyword.musics)
                playlists.append(playlist)
            for rating in result.ratings:
                rating_name = f"rating_{rating.key.rating}"
                self.success(f"Rating {rating_name} : {len(rating.elements)}")
                playlist = Playlist.from_gel(name=rating_name, results=rating.elements)
                playlists.append(playlist)
            for artist in result.keywords_for_artist:
                artist_name = artist.artist
                for artist_keyword in artist.keywords:
                    keyword_name = artist_keyword.keyword
                    final_artist_keyword = f"{artist_name}{os.sep}keyword_{keyword_name.lower()}"
                    self.success(f"Keyword by artist {final_artist_keyword} : {len(artist_keyword.musics)}")
                    playlist = Playlist.from_gel(name=final_artist_keyword, results=artist_keyword.musics)
                    playlists.append(playlist)
            for ratings_for_artist in result.ratings_for_artist:
                artist_name = ratings_for_artist.key.artist.name
                rating_name = str(ratings_for_artist.key.rating)
                artist_rating = f"{artist_name}{os.sep}rating_{rating_name}"
                self.success(f"Rating by artist {artist_rating} : {len(ratings_for_artist.elements)}")
                playlist = Playlist.from_gel(name=artist_rating, results=ratings_for_artist.elements)
                playlists.append(playlist)
        return playlists
