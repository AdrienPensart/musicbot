import logging
import functools
import click
import spotify
from musicbot import helpers

logger = logging.getLogger(__name__)


MB_CLIENT_ID = 'MB_CLIENT_ID'
MB_CLIENT_SECRET = 'MB_CLIENT_SECRET'
MB_TOKEN = 'MB_TOKEN'

options = [
    click.option('--client-id', help='Spotify client ID', required=True, envvar=MB_CLIENT_ID),
    click.option('--client-secret', help='Spotify client secret', require=True, envvar=MB_CLIENT_SECRET),
    click.option('--token', help='Spotify token', required=True, envvar=MB_TOKEN)
]


class FailedAuthentication(Exception):
    pass


class Spotify:

    @helpers.timeit
    def __init__(self, client_id, client_secret, token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.sp = spotify.Client(client_id, client_secret)
        self.user = spotify.User.from_token(self.sp, self.token)

    @classmethod
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def new(cls, **kwargs):
        self = Spotify(**kwargs)
        return self

    # @helpers.timeit
    # async def search(self, artist, title):
    #     try:
    #         results = self.sp.search(q="{} artist:{}".format(title, artist), limit=1)
    #         logger.debug(results)
    #         return results['tracks']['items'][0]['external_urls']['spotify']
    #     except Exception as e:  # pylint: disable=broad-except
    #         logger.info(e)
    #         return 'not found'

    @helpers.timeit
    async def playlists(self):
        return await self.user.get_playlists()
