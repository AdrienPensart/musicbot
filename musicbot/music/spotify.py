import logging
import itertools
import spotipy
import click
from musicbot.helpers import config_string

logger = logging.getLogger(__name__)


def sane_spotify(ctx, param, value):
    spotify = config_string(ctx=ctx, param=param, value=value)
    ctx.params['spotify'] = Spotify(spotify)
    return ctx.params['spotify']


spotify_token_option = [click.option('--spotify', help='Spotify token', callback=sane_spotify)]


class Spotify:
    def __init__(self, spotify_token):
        self.sp = spotipy.Spotify(auth=spotify_token)

    def tracks(self):
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
            objects.append(new_objects['items'])
            logger.info("chunk size: %s", len(new_objects['items']))
            offset += len(new_objects['items'])
            if len(new_objects['items']) < limit:
                break
        return list(itertools.chain(*objects))

    def playlists(self):
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self.sp.current_user_playlists(limit=limit, offset=offset)
            length = len(new_objects['items'])
            objects.append(new_objects['items'])
            logger.info("chunk size: %s", length)
            offset += length
            if length < limit:
                break
        logger.debug("length: %s", offset)
        return list(itertools.chain(*objects))

    def playlist(self, name):
        playlists = self.playlists()
        for p in playlists:
            if p['name'] == name:
                tracks = []
                results = self.sp.playlist(p['id'], fields="tracks,next")
                new_tracks = results['tracks']
                tracks.append(new_tracks['items'])
                while new_tracks['next']:
                    new_tracks = self.sp.next(new_tracks)
                    tracks.append(new_tracks['tracks']['items'])
                return list(itertools.chain(*tracks))
        return []
