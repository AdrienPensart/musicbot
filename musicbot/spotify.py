import itertools
import logging
from functools import cache
from typing import Any

import spotipy  # type: ignore
from attr import asdict, frozen
from spotipy.oauth2 import CacheFileHandler  # type: ignore

logger = logging.getLogger(__name__)


@frozen
class Spotify:
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
        del auth_params['token']
        del auth_params['cache_path']
        del auth_params['username']
        return spotipy.oauth2.SpotifyOAuth(**auth_params, cache_handler=self.cache_handler)

    @property
    def auth_manager(self) -> spotipy.oauth2.SpotifyOAuth:
        return self._auth_manager()

    @property
    def cache_handler(self) -> CacheFileHandler:
        return CacheFileHandler(cache_path=self.cache_path, username=self.username)

    @cache
    def _api(self) -> spotipy.Spotify:
        if self.token:
            return spotipy.Spotify(auth=self.token)
        return spotipy.Spotify(auth_manager=self.auth_manager)

    @property
    def api(self) -> spotipy.Spotify:
        return self._api()

    def new_token(self) -> Any:
        return self.auth_manager.get_access_token(check_cache=False)

    def cached_token(self) -> Any:
        token = self.cache_handler.get_cached_token()
        if not token:
            logger.warning("no cached token")
        self.auth_manager.validate_token(token)
        return token

    def is_token_expired(self) -> bool:
        token = self.cached_token()
        if not token:
            return True
        return self.auth_manager.is_token_expired(token)

    def refresh_token(self) -> Any:
        token = self.cached_token()
        if not token:
            return None
        return self.auth_manager.refresh_access_token(token['refresh_token'])

    def get_download_playlist(self) -> dict[Any, Any]:
        name = "To Download"
        download_playlist = self.playlist(name)
        if download_playlist:
            return download_playlist
        return self.api.user_playlist_create(self.username, name, public=False)

    def set_download_playlist(self, tracks: Any) -> Any:
        download_playlist = self.get_download_playlist()
        track_ids = [track['track']['id'] for track in tracks]

        # erase playlist first
        self.api.user_playlist_replace_tracks(self.username, download_playlist['id'], [])

        # add tracks 100 by 100 (API limit)
        for i in range(0, len(track_ids), 100):
            self.api.user_playlist_add_tracks(self.username, download_playlist['id'], track_ids[i:i + 100])

    def tracks(self) -> list[Any]:
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self.api.current_user_saved_tracks(limit=limit, offset=offset)
            objects.append(new_objects['items'])
            length = len(new_objects['items'])
            logger.info(f"chunk size: {length}")
            offset += len(new_objects['items'])
            if len(new_objects['items']) < limit:
                break
        return list(itertools.chain(*objects))

    def playlists(self) -> list[Any]:
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self.api.current_user_playlists(limit=limit, offset=offset)
            length = len(new_objects['items'])
            objects.append(new_objects['items'])
            logger.info(f"chunk size: {length}")
            offset += length
            if length < limit:
                break
        logger.debug(f"length: {offset}")
        return list(itertools.chain(*objects))

    def playlist(self, name: str) -> Any:
        playlists = self.playlists()
        for p in playlists:
            if p['name'] == name:
                return p
        return None

    def playlist_tracks(self, name: str) -> list[Any]:
        playlists = self.playlists()
        for p in playlists:
            if p['name'] == name:
                tracks = []
                results = self.api.playlist(p['id'], fields="tracks,next")
                new_tracks = results['tracks']
                tracks.append(new_tracks['items'])
                while new_tracks['next']:
                    new_tracks = self.api.next(new_tracks)
                    tracks.append(new_tracks['tracks']['items'])
                return list(itertools.chain(*tracks))
        return []
