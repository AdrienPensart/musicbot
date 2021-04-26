import logging
import click
import attr
from click_option_group import optgroup  # type: ignore
from click_skeleton import ExpandedPath, add_options
from musicbot.cli.options import config_string
from musicbot.spotify import (
    Spotify,
    DEFAULT_SPOTIFY_USERNAME,
    DEFAULT_SPOTIFY_CLIENT_ID,
    DEFAULT_SPOTIFY_CLIENT_SECRET,
    DEFAULT_SPOTIFY_TOKEN,
    DEFAULT_SPOTIFY_CACHE_PATH,
    DEFAULT_SPOTIFY_SCOPE,
    DEFAULT_SPOTIFY_REDIRECT_URI,
)

logger = logging.getLogger(__name__)


def sane_spotify(ctx: click.Context, param: click.Parameter, value: str) -> Spotify:
    spotify_params = {}
    ctx.params[param.name] = value
    for field in attr.fields_dict(Spotify):
        spotify_params[field] = ctx.params['spotify_' + field]
        ctx.params.pop('spotify_' + field)
    spotify = Spotify(**spotify_params)
    ctx.params['spotify'] = spotify
    return spotify


spotify_cache_path_option = optgroup.option(
    '--spotify-cache-path',
    help='Spotify cache path',
    is_eager=True,
    type=ExpandedPath(writable=True, readable=True, dir_okay=False),
    envvar='MB_SPOTIFY_CACHE_PATH',
    default=DEFAULT_SPOTIFY_CACHE_PATH,
    callback=config_string,
)

spotify_scope_option = optgroup.option(
    '--spotify-scope',
    help='Spotify OAuth scopes, comma separated',
    is_eager=True,
    envvar='MB_SPOTIFY_SCOPE',
    default=DEFAULT_SPOTIFY_SCOPE,
    callback=config_string,
)

spotify_redirect_uri_option = optgroup.option(
    '--spotify-redirect-uri',
    help='Spotify redirect URI',
    envvar='MB_SPOTIFY_REDIRECT_URI',
    is_eager=True,
    default=DEFAULT_SPOTIFY_REDIRECT_URI,
    callback=config_string,
)

spotify_username_option = optgroup.option(
    '--spotify-username',
    help='Spotify username',
    is_eager=True,
    envvar='MB_SPOTIFY_USERNAME',
    default=DEFAULT_SPOTIFY_USERNAME,
    callback=config_string,
)

spotify_client_id_option = optgroup.option(
    '--spotify-client-id',
    help='Spotify client ID',
    is_eager=True,
    envvar='MB_SPOTIFY_CLIENT_ID',
    default=DEFAULT_SPOTIFY_CLIENT_ID,
    callback=config_string,
)

spotify_client_secret_option = optgroup.option(
    '--spotify-client-secret',
    help='Spotify client secret',
    is_eager=True,
    envvar='MB_SPOTIFY_CLIENT_SECRET',
    default=DEFAULT_SPOTIFY_CLIENT_SECRET,
    callback=config_string,
)

spotify_token_option = optgroup.option(
    '--spotify-token',
    help='Spotify token',
    envvar='MB_SPOTIFY_TOKEN',
    expose_value=False,
    default=DEFAULT_SPOTIFY_TOKEN,
    callback=sane_spotify,
)

spotify_options = add_options(
    optgroup('Spotify options'),
    spotify_token_option,
    spotify_username_option,
    spotify_client_id_option,
    spotify_client_secret_option,
    spotify_cache_path_option,
    spotify_scope_option,
    spotify_redirect_uri_option,
)
