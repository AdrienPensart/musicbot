import itertools
import logging
import os
from dataclasses import asdict, dataclass
from functools import cached_property
from typing import Any

import spotipy  # type: ignore
from beartype import beartype
from natsort import natsorted
from spotipy.oauth2 import CacheFileHandler, SpotifyOauthError  # type: ignore

from musicbot.defaults import DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST, DEFAULT_SPOTIFY_TIMEOUT
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@beartype
@dataclass(frozen=True)
class Spotify(MusicbotObject):
    username: str
    client_id: str
    client_secret: str
    cache_path: str
    scope: str
    redirect_uri: str
    token: str | None = None

    @cached_property
    def auth_manager(self) -> spotipy.oauth2.SpotifyOAuth:
        auth_params = asdict(self)
        del auth_params["token"]
        del auth_params["cache_path"]
        del auth_params["username"]
        return spotipy.oauth2.SpotifyOAuth(**auth_params, cache_handler=self.cache_handler)

    @cached_property
    def cache_handler(self) -> CacheFileHandler:
        cache_path = os.path.expanduser(self.cache_path)
        return CacheFileHandler(cache_path=cache_path, username=self.username)

    @cached_property
    def api(self) -> spotipy.Spotify:
        if self.token:
            return spotipy.Spotify(auth=self.token, requests_timeout=DEFAULT_SPOTIFY_TIMEOUT)
        return spotipy.Spotify(auth_manager=self.auth_manager, requests_timeout=DEFAULT_SPOTIFY_TIMEOUT)

    def new_token(self) -> Any:
        if self.dry:
            return None
        return self.auth_manager.get_access_token(check_cache=False)

    def cached_token(self) -> Any:
        if not (token := self.cache_handler.get_cached_token()):
            self.warn("no cached token")
        try:
            result = self.auth_manager.validate_token(token)
            logger.debug(result)
        except SpotifyOauthError:
            self.warn("invalid token")
        return token

    def is_token_expired(self, token: Any) -> bool:
        return self.auth_manager.is_token_expired(token)

    def refresh_token(self) -> str | None:
        if not (token := self.cached_token()):
            return None
        if self.dry:
            return None
        return self.auth_manager.refresh_access_token(token["refresh_token"])

    def get_download_playlist(self, name: str = DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST) -> dict[Any, Any] | None:
        if download_playlist := self.playlist(name):
            return download_playlist
        try:
            result = self.api.user_playlist_create(self.username, name, public=False)
            logger.debug(result)
        except SpotifyOauthError as error:
            self.err(f"{self} : unable to get download playlist", error=error)
            return None
        if download_playlist := self.playlist(name):
            return download_playlist
        return None

    def set_download_playlist(self, tracks: Any) -> None:
        if (download_playlist := self.get_download_playlist()) is None:
            self.err("Cannot get download playlist, so we can't update it")
            return

        track_ids = [track["track"]["id"] for track in tracks]

        try:
            # erase playlist first
            result = self.api.user_playlist_replace_tracks(self.username, download_playlist["id"], [])
            logger.debug(result)

            # add tracks 100 by 100 (API limit)
            for i in range(0, len(track_ids), 100):
                j = i + 100
                result = self.api.user_playlist_add_tracks(self.username, download_playlist["id"], track_ids[i:j])
                logger.debug(result)
        except SpotifyOauthError as error:
            self.err(f"{self} : unable to set download playlist", error=error)

    def playlists(self) -> list[Any] | None:
        offset = 0
        limit = 50
        objects = []
        try:
            while new_objects := self.api.current_user_playlists(limit=limit, offset=offset):
                length = len(new_objects["items"])
                objects.append(new_objects["items"])
                offset += length
                if length < limit:
                    break
        except SpotifyOauthError as error:
            self.err(f"{self} : unable to get playlists", error=error)
            return None
        return list(itertools.chain(*objects))

    def playlist(self, name: str) -> Any | None:
        if (playlists := self.playlists()) is None:
            return None
        for playlist in playlists:
            if playlist["name"] == name:
                return playlist
        return None

    def liked_tracks(self) -> list[Any] | None:
        offset = 0
        limit = 50
        objects = []
        try:
            while True:
                new_objects: dict = self.api.current_user_saved_tracks(limit=limit, offset=offset)
                length = len(new_objects["items"])
                objects.append(new_objects["items"])
                offset += length
                if length < limit:
                    break
        except SpotifyOauthError as error:
            self.err(f"{self} : unable to get liked tracks", error=error)
            return None
        return list(natsorted(itertools.chain(*objects), lambda st: st["track"]["artists"][0]["name"]))

    def playlist_tracks(self, name: str) -> list[Any] | None:
        if (playlists := self.playlists()) is None:
            return None
        try:
            for p in playlists:
                if p["name"] == name:
                    tracks = []
                    results: dict = self.api.playlist(p["id"], fields="tracks,next")
                    new_tracks: dict = results["tracks"]
                    tracks.append(new_tracks["items"])
                    while new_tracks["next"]:
                        new_tracks = self.api.next(new_tracks)
                        tracks.append(new_tracks["items"])
                    return list(itertools.chain(*tracks))
        except SpotifyOauthError as error:
            self.err(f"{self} : {name} : unable to get playlist tracks", error=error)
            return None
        return []
