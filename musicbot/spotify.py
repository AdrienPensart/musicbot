import logging
import os
import itertools
import spotipy
import click
from prettytable import PrettyTable
from click_option_group import optgroup
from click_skeleton import ExpandedPath

from musicbot.config import config

logger = logging.getLogger(__name__)


def config_string_spotify(ctx, param, arg_value):  # pylint: disable=unused-argument
    name = param.name
    value = None

    config_value = config.configfile.get('spotify', name, fallback=None)
    if config_value:
        value = config_value
        logger.info(f"{name} : config key loaded : {config_value}")

    name_upper = name.upper().replace('-', '_')
    env_name = 'MB_SPOTIFY_' + name_upper
    env_value = os.getenv(env_name, None)
    if env_value:
        value = env_value
        logger.info(f"{name} : env key {env_name} loaded : {env_value}")

    default_name = 'DEFAULT_' + name_upper
    default_value = globals().get(default_name, None)
    logger.info(f'{name} : default_name: {default_name} default_value: {default_value}')

    if arg_value and arg_value != default_value:
        logger.info(f"{name} : arg value loaded : {arg_value}")
        value = arg_value

    if not value:
        logger.info(f"{name} : default arg value loaded {default_name} : {arg_value}")
        value = default_value

    if env_value and arg_value and env_value != arg_value:
        logger.info(f"{name} : env value {env_value} is not sync with arg value {arg_value}")
    if env_value and config_value and env_value != config_value:
        logger.info(f"{name} : config value {config_value} is not sync with env value {env_value}")
    if arg_value and config_value and arg_value != config_value:
        logger.info(f"{name} : config value {config_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f'missing arg {param.name} or env {env_name} or {param.name} in [spotify] section of {config.config}', ctx, param.name, param.name)
    logger.info(f"{name} : final value {value}")
    return value


def sane_spotify(ctx, param, value):  # pylint: disable=unused-argument
    kwargs = {}
    for field in ('username', 'client_id', 'client_secret', 'cache_path', 'redirect_uri', 'scopes'):
        kwargs[field] = ctx.params[field]
        ctx.params.pop(field)

    ctx.params['spotify'] = Spotify(**kwargs)
    return ctx.params['spotify']


DEFAULT_CACHE_PATH = '~/.spotify_cache'
cache_path_option = [
    optgroup.option(
        '--cache-path',
        help='Spotify cache path',
        is_eager=True,
        type=ExpandedPath(writable=True, readable=True, dir_okay=False),
        default=DEFAULT_CACHE_PATH,
        callback=config_string_spotify,
    )
]

DEFAULT_SCOPES = 'user-library-read,user-follow-read,user-top-read,playlist-read-private,user-modify-playback-state,user-read-currently-playing,user-read-playback-state'
scopes_option = [
    optgroup.option(
        '--scopes',
        help='Spotify scopes',
        is_eager=True,
        default=DEFAULT_SCOPES,
        callback=config_string_spotify,
    )
]

DEFAULT_REDIRECT_URI = 'http://localhost:8888/spotify/callback'
redirect_uri_option = [
    optgroup.option(
        '--redirect-uri',
        help='Spotify redirect URI',
        is_eager=True,
        default=DEFAULT_REDIRECT_URI,
        callback=config_string_spotify,
    )
]

username_option = [
    optgroup.option(
        '--username',
        help='Spotify username',
        is_eager=True,
        callback=config_string_spotify,
    )
]
client_id_option = [
    optgroup.option(
        '--client-id',
        help='Spotify client ID',
        is_eager=True,
        callback=config_string_spotify,
    )
]
client_secret_option = [
    optgroup.option(
        '--client-secret',
        help='Spotify client secret',
        is_eager=True,
        callback=config_string_spotify,
    )
]

token_option = [
    optgroup.option(
        '--token',
        help='Spotify token',
        expose_value=False,
        callback=sane_spotify,
    )
]

spotify_options =\
    [optgroup.group('Spotify options')] +\
    username_option +\
    client_id_option +\
    client_secret_option +\
    token_option +\
    cache_path_option +\
    scopes_option +\
    redirect_uri_option


class Spotify:
    def __init__(self, username, client_id, client_secret, cache_path, scopes, redirect_uri):
        self.scopes = scopes
        self.redirect_uri = redirect_uri
        self.cache_path = cache_path
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = spotipy.util.prompt_for_user_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            cache_path=self.cache_path,
            redirect_uri=self.redirect_uri,
            scope=self.scopes,
        )
        self.sp = spotipy.Spotify(auth=self.token)

    def __repr__(self):
        return f'token: {self.token} | username: {self.username} | client_id: {self.client_id} | client_secret: {self.client_secret} | cache: {self.cache_path} | redirect uri: {self.redirect_uri} | scopes: {self.scopes}'

    def tracks(self):
        offset = 0
        limit = 50
        objects = []
        while True:
            new_objects = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
            objects.append(new_objects['items'])
            length = len(new_objects['items'])
            logger.info(f"chunk size: {length}")
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
            logger.info(f"chunk size: {length}")
            offset += length
            if length < limit:
                break
        logger.debug(f"length: {offset}")
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

    def print_tracks(self):
        pt = PrettyTable()
        pt.field_names = ["Track", "Artist", "Album"]
        for t in self.tracks():
            pt.add_row([t['track']['name'], t['track']['artists'][0]['name'], t['track']['album']['name']])
        print(pt)

    def print_playlists(self):
        pt = PrettyTable()
        pt.field_names = ["Name", "Size"]
        for p in self.playlists():
            pt.add_row([p['name'], p['tracks']['total']])
        print(pt)
