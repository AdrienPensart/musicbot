from typing import Any
import logging
import textwrap
import json
import shutil
import click
import attr
from prettytable import PrettyTable, ALL  # type: ignore
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


def dump_tracks(tracks: Any) -> None:
    tracks = [
        {
            'title': t['track']['name'],
            'artist': t['track']['artists'][0]['name'],
            'album': t['track']['album']['name'],
        } for t in tracks
    ]
    print(json.dumps(tracks))


def print_tracks_table(tracks: Any) -> None:
    if not tracks:
        return
    pt = PrettyTable(["Track", "Artist", "Album"])
    pt.align = 'l'
    width = shutil.get_terminal_size().columns // 3
    for t in tracks:
        title = '\n'.join(textwrap.wrap(t['track']['name'], width))
        artist = '\n'.join(textwrap.wrap(t['track']['artists'][0]['name'], width))
        album = '\n'.join(textwrap.wrap(t['track']['album']['name'], width))
        pt.add_row([title, artist, album])
    print(pt)


def print_distances(distances: Any) -> None:
    if not distances:
        return
    pt = PrettyTable(["Title", "Artist", "Album", "Distance"])
    pt.align = 'l'
    pt.hrules = ALL
    for distance in distances:
        st = distance['spotify_track']
        stitle = st['track']['name']
        sartist = st['track']['artists'][0]['name']
        salbum = st['track']['album']['name']
        dtitle = distance['local_track']['title']
        dartist = distance['local_track']['artist']
        dalbum = distance['local_track']['album']
        identical = True

        colored_stitle = click.style(f"{stitle} (spotify)", fg='yellow')
        if stitle != dtitle:
            colored_dtitle = click.style(f"{dtitle} (local)", fg="cyan")
            final_title = f"{colored_stitle}\n{colored_dtitle}"
            identical = False
        else:
            final_title = colored_stitle

        colored_sartist = click.style(f"{sartist} (spotify)", fg='yellow')
        if sartist != dartist:
            colored_dartist = click.style(f"{dartist} (local)", fg="cyan")
            final_artist = f"{colored_stitle}\n{colored_dartist}"
            identical = False
        else:
            final_artist = colored_sartist

        colored_salbum = click.style(f"{salbum} (spotify)", fg='yellow')
        if salbum != dalbum:
            colored_dalbum = click.style(f"{dalbum} (local)", fg="cyan")
            final_album = f"{colored_salbum}\n{colored_dalbum}"
            identical = False
        else:
            final_album = colored_salbum

        if identical:
            continue

        d = distance['distance']
        pt.add_row([
            final_title,
            final_artist,
            final_album,
            d,
        ])
    print(pt)


def print_playlists_table(playlists: Any) -> None:
    if not playlists:
        return
    pt = PrettyTable(["Name", "Size"])
    for p in playlists:
        pt.add_row([p['name'], p['tracks']['total']])
    print(pt.get_string(title='Spotify playlists'))


def output_tracks(output: str, tracks: Any) -> None:
    if output == 'table':
        print_tracks_table(tracks)
    elif output == 'json':
        dump_tracks(tracks)


def sane_spotify(ctx: click.Context, param: click.Parameter, value: str) -> Spotify:
    if param.name:
        ctx.params[param.name] = value
    spotify_params = {}
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
