import logging
import os
import sys
import asyncio
from contextlib import contextmanager
from functools import partial
import click
import spotify.sync as spotify
from musicbot.config import config

logger = logging.getLogger(__name__)


def config_string(envvar, configkey, ctx, param, value):
    if not value:
        value = os.getenv(envvar, None)
    if not value:
        value = config.configfile['DEFAULT'].get(configkey, None)
    if not value:
        raise click.BadParameter('or missing env {} / config {} in {}'.format(envvar, configkey, config.config), ctx, param)
    ctx.params[param.name] = value
    return ctx.params[param.name]


MB_SPOTIFY_ID = 'MB_SPOTIFY_ID'
spotify_id_option = [click.option('--spotify-id', help='Spotify ID', callback=partial(config_string, MB_SPOTIFY_ID, 'spotify_id'))]

MB_SPOTIFY_SECRET = 'MB_SPOTIFY_SECRET'
spotify_secret_option = [click.option('--spotify-secret', help='Spotify secret', callback=partial(config_string, MB_SPOTIFY_SECRET, 'spotify_secret'))]

MB_SPOTIFY_TOKEN = 'MB_SPOTIFY_TOKEN'
spotify_token_option = [click.option('--spotify-token', help='Spotify token', callback=partial(config_string, MB_SPOTIFY_TOKEN, 'spotify_token'))]

MB_SPOTIFY_REFRESH_TOKEN = 'MB_SPOTIFY_TOKEN'
spotify_refresh_token_option = [click.option('--spotify-refresh-token', help='Spotify refresh token', callback=partial(config_string, MB_SPOTIFY_REFRESH_TOKEN, 'spotify_refresh_token'))]

options = spotify_id_option + spotify_secret_option + spotify_token_option + spotify_refresh_token_option


@contextmanager
def spotify_client(spotify_id, spotify_secret):
    try:
        client = spotify.Client(spotify_id, spotify_secret)
        yield client
    finally:
        client.close()


@contextmanager
def spotify_user(spotify_token, spotify_refresh_token, **kwargs):
    user = None
    try:
        with spotify_client(**kwargs) as client:
            user = spotify.User.from_token(client, spotify_token, spotify_refresh_token)
            yield user
    except spotify.errors.SpotifyException as e:
        logger.error(e)
        sys.exit(-1)
    finally:
        if user:
            asyncio.run(user.http.close())
