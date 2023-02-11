import itertools
import logging
from functools import cache
from typing import Any

import spotipy  # type: ignore
from attr import asdict, define
from natsort import natsorted
from spotipy.oauth2 import CacheFileHandler  # type: ignore

from musicbot.defaults import DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST, DEFAULT_SPOTIFY_TIMEOUT
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@define(frozen=True)
class Spotify(MusicbotObject):
    username: str
    client_id: str
    client_secret: str
    cache_path: str
    scope: str
    redirect_uri: str
    token: str

    @cache
    def _auth_manager(self) -> spotipy.oauth2.SpotifyOAuth:
        auth_params = asdict(self)
        del auth_params["token"]
        del auth_params["cache_path"]
        del auth_params["username"]
        return spotipy.oauth2.SpotifyOAuth(**auth_params, cache_handler=self.cache_handler)

    @property
    def auth_manager(self) -> spotipy.oauth2.SpotifyOAuth:
        return self._auth_manager()

    @property
    def cache_handler(self) -> CacheFileHandler:
        return CacheFileHandler(cache_path=self.cache_path, username=self.username)

    @cache
    def _api(self, requests_timeout: int = DEFAULT_SPOTIFY_TIMEOUT) -> spotipy.Spotify:
        if self.token:
            return spotipy.Spotify(auth=self.token, requests_timeout=requests_timeout)
        return spotipy.Spotify(auth_manager=self.auth_manager, requests_timeout=requests_timeout)

    @property
    def api(self) -> spotipy.Spotify:
        return self._api()

    def new_token(self) -> Any:
        return self.auth_manager.get_access_token(check_cache=False)

    def cached_token(self) -> Any:
        if not (token := self.cache_handler.get_cached_token()):
            logger.warning("no cached token")
        self.auth_manager.validate_token(token)
        return token

    def is_token_expired(self) -> bool:
        if not (token := self.cached_token()):
            return True
        return self.auth_manager.is_token_expired(token)

    def refresh_token(self) -> Any:
        if not (token := self.cached_token()):
            return None
        return self.auth_manager.refresh_access_token(token["refresh_token"])

    def get_download_playlist(self, name: str = DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST) -> dict[Any, Any] | None:
        if download_playlist := self.playlist(name):
            return download_playlist
        result = self.api.user_playlist_create(self.username, name, public=False)
        logger.debug(result)
        if download_playlist := self.playlist(name):
            return download_playlist
        return None

    def set_download_playlist(self, tracks: Any) -> None:
        if (download_playlist := self.get_download_playlist()) is None:
            self.err("Cannot get download playlist, so we can't update it")
            return

        track_ids = [track["track"]["id"] for track in tracks]

        # erase playlist first
        self.api.user_playlist_replace_tracks(self.username, download_playlist["id"], [])

        # add tracks 100 by 100 (API limit)
        for i in range(0, len(track_ids), 100):
            self.api.user_playlist_add_tracks(self.username, download_playlist["id"], track_ids[i : i + 100])

    def playlists(self) -> list[Any]:
        offset = 0
        limit = 50
        objects = []
        while new_objects := self.api.current_user_playlists(limit=limit, offset=offset):
            length = len(new_objects["items"])
            objects.append(new_objects["items"])
            offset += length
            if length < limit:
                break
        return list(itertools.chain(*objects))

    def playlist(self, name: str) -> Any | None:
        for playlist in self.playlists():
            if playlist["name"] == name:
                return playlist
        return None

    def liked_tracks(self) -> list[Any]:
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self.api.current_user_saved_tracks(limit=limit, offset=offset)
            length = len(new_objects["items"])
            objects.append(new_objects["items"])
            offset += length
            if length < limit:
                break
        return list(natsorted(itertools.chain(*objects), lambda st: st["track"]["artists"][0]["name"]))

    def playlist_tracks(self, name: str) -> list[Any]:
        playlists = self.playlists()
        for p in playlists:
            if p["name"] == name:
                tracks = []
                results = self.api.playlist(p["id"], fields="tracks,next")
                new_tracks = results["tracks"]
                tracks.append(new_tracks["items"])
                while new_tracks["next"]:
                    new_tracks = self.api.next(new_tracks)
                    tracks.append(new_tracks["items"])
                return list(itertools.chain(*tracks))
        return []
