import click
import logging
import spotipy
import functools
from spotipy.oauth2 import SpotifyClientCredentials
from musicbot import helpers

logger = logging.getLogger(__name__)


MB_CLIENT_ID = 'MB_CLIENT_ID'
MB_CLIENT_SECRET = 'MB_CLIENT_SECRET'
MB_TOKEN = 'MB_TOKEN'

options = [
    click.option('--client-id', help='Spotify client ID', envvar=MB_CLIENT_ID, default=None),
    click.option('--client-secret', help='Spotify client secret', envvar=MB_CLIENT_SECRET, default=None),
    click.option('--token', help='Spotify token', envvar=MB_TOKEN, default=None)
]


class FailedAuthentication(Exception):
    pass


class Spotify:

    @helpers.timeit
    def __init__(self, client_id=None, client_secret=None, token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token

        if self.token:
            self.sp = spotipy.Spotify(auth=token)
        elif self.client_id and self.client_secret:
            client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        else:
            raise FailedAuthentication("No spotify ID/Secret or token provided")
        self.authenticated = True

    @classmethod
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def new(cls, **kwargs):
        self = Spotify(**kwargs)
        return self

    @helpers.timeit
    def search(self, artist, title):
        try:
            results = self.sp.search(q="{} artist:{}".format(title, artist), limit=1)
            return results['tracks']['items'][0]['external_urls']['spotify']
        except Exception as e:
            logger.debug(e)
            return 'not found'
