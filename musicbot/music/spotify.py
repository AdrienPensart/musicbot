import logging
import click

logger = logging.getLogger(__name__)

MB_SPOTIFY_ID = 'MB_SPOTIFY_ID'
spotify_id_option = [click.option('--spotify-id', help='Spotify ID', required=True, envvar=MB_SPOTIFY_ID)]

MB_SPOTIFY_SECRET = 'MB_SPOTIFY_SECRET'
spotify_secret_option = [click.option('--spotify-secret', help='Spotify secret', required=True, envvar=MB_SPOTIFY_SECRET)]

MB_SPOTIFY_TOKEN = 'MB_SPOTIFY_TOKEN'
spotify_token_option = [click.option('--spotify-token', help='Spotify token', required=True, envvar=MB_SPOTIFY_TOKEN)]

options = spotify_id_option + spotify_secret_option + spotify_token_option
