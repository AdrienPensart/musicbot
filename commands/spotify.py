import click
import logging
import spotipy
from lib.spotify import options
from lib import helpers
from spotipy.oauth2 import SpotifyClientCredentials

logger = logging.getLogger(__name__)

@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Spotify'''
    pass

@cli.command()
@helpers.add_options(options)
@click.argument("name")
def artist(client_id, client_secret, token, name):
    '''Spotify test'''
    print("client-id: {} | client-secret: {} | token: {}".format(client_id, client_secret, token))
    if token:
        sp = spotipy.Spotify(auth=token)
    elif client_id and client_secret:
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    else:
        logger.error('You need to provide either token or client-id/client-secrret')
        return
    results = sp.search(q='artist:' + name, type='artist')
    print(results)
