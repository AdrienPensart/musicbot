import logging
import functools
import itertools
from typing import List, Any
import spotipy  # type: ignore
from spotipy.oauth2 import CacheFileHandler  # type: ignore
import attr

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class Spotify:
    username: str
    client_id: str
    client_secret: str
    cache_path: str
    scope: str
    redirect_uri: str
    token: str

    @property
    def _auth_manager(self) -> spotipy.oauth2.SpotifyOAuth:
        auth_params = attr.asdict(self)
        del auth_params['token']
        del auth_params['cache_path']
        del auth_params['username']
        cache_handler = CacheFileHandler(cache_path=self.cache_path, username=self.username)
        return spotipy.oauth2.SpotifyOAuth(**auth_params, cache_handler=cache_handler)

    @functools.cached_property
    def _api(self) -> spotipy.Spotify:
        if self.token:
            return spotipy.Spotify(auth=self.token)
        return spotipy.Spotify(auth_manager=self._auth_manager)

    def cached_token(self) -> Any:
        return self._auth_manager.get_cached_token()

    def is_token_expired(self) -> bool:
        return self._auth_manager.is_token_expired(self.cached_token())

    def refresh_token(self):
        return self._auth_manager.refresh_access_token(self.cached_token()['refresh_token'])

    def tracks(self) -> List[Any]:
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self._api.current_user_saved_tracks(limit=limit, offset=offset)
            objects.append(new_objects['items'])
            length = len(new_objects['items'])
            logger.info(f"chunk size: {length}")
            offset += len(new_objects['items'])
            if len(new_objects['items']) < limit:
                break
        return list(itertools.chain(*objects))

    def playlists(self) -> List[Any]:
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self._api.current_user_playlists(limit=limit, offset=offset)
            length = len(new_objects['items'])
            objects.append(new_objects['items'])
            logger.info(f"chunk size: {length}")
            offset += length
            if length < limit:
                break
        logger.debug(f"length: {offset}")
        return list(itertools.chain(*objects))

    def playlist(self, name: str) -> List[Any]:
        playlists = self.playlists()
        for p in playlists:
            if p['name'] == name:
                tracks = []
                results = self._api.playlist(p['id'], fields="tracks,next")
                new_tracks = results['tracks']
                tracks.append(new_tracks['items'])
                while new_tracks['next']:
                    new_tracks = self._api.next(new_tracks)
                    tracks.append(new_tracks['tracks']['items'])
                return list(itertools.chain(*tracks))
        return []
