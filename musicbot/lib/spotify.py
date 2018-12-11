import click
import logging
from .config import config

logger = logging.getLogger(__name__)


MB_CLIENT_ID = 'MB_CLIENT_ID'
MB_CLIENT_SECRET = 'MB_CLIENT_SECRET'
MB_TOKEN = 'MB_TOKEN'

options = [
    click.option('--client-id', help='Spotify client ID', envvar=MB_CLIENT_ID, default=None),
    click.option('--client-secret', help='Spotify client secret', envvar=MB_CLIENT_SECRET, default=None),
    click.option('--token', help='Spotify token', envvar=MB_TOKEN, default=None)
]


def search(artist, title):
    try:
        if config.spotify is None:
            return 'error'
        results = config.spotify.search(q="{} artist:{}".format(title, artist), limit=1)
        return results['tracks']['items'][0]['external_urls']['spotify']
    except Exception as e:
        logger.debug(e)
        return 'not found'
