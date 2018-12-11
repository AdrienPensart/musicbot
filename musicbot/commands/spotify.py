import click
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from musicbot.lib.spotify import options, search
from musicbot.lib.config import config
from musicbot.lib import helpers

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(options)
@click.pass_context
def cli(ctx, client_id, client_secret, token):
    '''Spotify'''
    logger.info("client-id: {} | client-secret: {} | token: {}".format(client_id, client_secret, token))
    if token:
        ctx.obj.sp = spotipy.Spotify(auth=token)
        config.spotify = ctx.obj.sp
        return
    if client_id and client_secret:
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        ctx.obj.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        config.spotify = ctx.obj.sp
        return
    logger.error('You need to provide either token or client-id/client-secrret')


@cli.command()
@click.argument("artist")
@click.argument("title")
@click.pass_context
def track(ctx, artist, title):
    '''Search track'''
    print(search(artist, title))
