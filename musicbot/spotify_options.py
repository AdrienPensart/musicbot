import logging
import click
import attr
from click_option_group import optgroup  # type: ignore
from click_skeleton import ExpandedPath
from musicbot import defaults
from musicbot.helpers import config_string
from musicbot.spotify import Spotify

logger = logging.getLogger(__name__)


def sane_spotify(ctx: click.Context, param: click.Parameter, value: str) -> Spotify:
    spotify_params = {}
    ctx.params[param.name] = value
    print(f'{ctx.params=}')
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
    default=defaults.DEFAULT_SPOTIFY_CACHE_PATH,
    callback=config_string,
)

spotify_scope_option = optgroup.option(
    '--spotify-scope',
    help='Spotify OAuth scopes, comma separated',
    is_eager=True,
    default=defaults.DEFAULT_SPOTIFY_SCOPE,
    callback=config_string,
)

spotify_redirect_uri_option = optgroup.option(
    '--spotify-redirect-uri',
    help='Spotify redirect URI',
    is_eager=True,
    default=defaults.DEFAULT_SPOTIFY_REDIRECT_URI,
    callback=config_string,
)

spotify_username_option = optgroup.option(
    '--spotify-username',
    help='Spotify username',
    is_eager=True,
    default=defaults.DEFAULT_SPOTIFY_USERNAME,
    callback=config_string,
)

spotify_client_id_option = optgroup.option(
    '--spotify-client-id',
    help='Spotify client ID',
    is_eager=True,
    default=defaults.DEFAULT_SPOTIFY_CLIENT_ID,
    callback=config_string,
)

spotify_client_secret_option = optgroup.option(
    '--spotify-client-secret',
    help='Spotify client secret',
    is_eager=True,
    default=defaults.DEFAULT_SPOTIFY_CLIENT_SECRET,
    callback=config_string,
)

spotify_token_option = optgroup.option(
    '--spotify-token',
    help='Spotify token',
    expose_value=False,
    callback=sane_spotify,
)

options = [
    optgroup.group('Spotify options'),
    spotify_token_option,
    spotify_username_option,
    spotify_client_id_option,
    spotify_client_secret_option,
    spotify_cache_path_option,
    spotify_scope_option,
    spotify_redirect_uri_option,
]
