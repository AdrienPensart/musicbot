import json
import logging
import shutil
import textwrap
from typing import Any

import click
from attr import fields_dict
from beartype import beartype
from click_option_group import optgroup  # type: ignore
from click_skeleton import ExpandedPath, add_options
from rich.table import Table

from musicbot.cli.options import config_string
from musicbot.defaults import (
    DEFAULT_SPOTIFY_CACHE_PATH,
    DEFAULT_SPOTIFY_CLIENT_ID,
    DEFAULT_SPOTIFY_CLIENT_SECRET,
    DEFAULT_SPOTIFY_REDIRECT_URI,
    DEFAULT_SPOTIFY_SCOPE,
    DEFAULT_SPOTIFY_TOKEN,
    DEFAULT_SPOTIFY_USERNAME
)
from musicbot.object import MusicbotObject
from musicbot.spotify import Spotify

logger = logging.getLogger(__name__)


@beartype
def dump_tracks(tracks: list[Any]) -> None:
    tracks = [
        {
            'title': t['track']['name'],
            'artist': t['track']['artists'][0]['name'],
            'album': t['track']['album']['name'],
        } for t in tracks
    ]
    print(json.dumps(tracks))


@beartype
def print_tracks_table(tracks: list[Any]) -> None:
    if not tracks:
        return
    table = Table("Track", "Artist", "Album")
    width = shutil.get_terminal_size().columns // 3
    for t in tracks:
        title = '\n'.join(textwrap.wrap(t['track']['name'], width))
        artist = '\n'.join(textwrap.wrap(t['track']['artists'][0]['name'], width))
        album = '\n'.join(textwrap.wrap(t['track']['album']['name'], width))
        table.add_row(title, artist, album)
    MusicbotObject.console.print(table)


@beartype
def print_distances(distances: list[Any]) -> None:
    if not distances:
        return
    table = Table("Title", "Artist", "Album", "Distance", show_lines=True)
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
        table.add_row(final_title, final_artist, final_album, d)
    MusicbotObject.console.print(table)


@beartype
def print_playlists_table(playlists: list[Any]) -> None:
    if not playlists:
        return
    table = Table("Name", "Size", title="Spotify Playlist")
    for p in playlists:
        table.add_row(p['name'], str(p['tracks']['total']))
    MusicbotObject.console.print(table)


@beartype
def output_tracks(output: str, tracks: list[Any]) -> None:
    if output == 'table':
        print_tracks_table(tracks)
    elif output == 'json':
        dump_tracks(tracks)


@beartype
def sane_spotify(ctx: click.Context, param: click.Parameter, value: str | None) -> Spotify:
    if param.name:
        ctx.params[param.name] = value
    spotify_params = {}
    for field in fields_dict(Spotify):
        spotify_params[field] = ctx.params['spotify_' + field]
        ctx.params.pop('spotify_' + field)
    spotify = Spotify(**spotify_params)
    ctx.params['spotify'] = spotify
    return spotify


spotify_cache_path_option = optgroup.option(
    '--spotify-cache-path',
    help='Spotify cache path',
    type=ExpandedPath(writable=True, readable=True, dir_okay=False),
    envvar='MB_SPOTIFY_CACHE_PATH',
    default=DEFAULT_SPOTIFY_CACHE_PATH,
    callback=config_string,
)

spotify_scope_option = optgroup.option(
    '--spotify-scope',
    help='Spotify OAuth scopes, comma separated',
    envvar='MB_SPOTIFY_SCOPE',
    default=DEFAULT_SPOTIFY_SCOPE,
    callback=config_string,
)

spotify_redirect_uri_option = optgroup.option(
    '--spotify-redirect-uri',
    help='Spotify redirect URI',
    envvar='MB_SPOTIFY_REDIRECT_URI',
    default=DEFAULT_SPOTIFY_REDIRECT_URI,
    callback=config_string,
)

spotify_username_option = optgroup.option(
    '--spotify-username',
    help='Spotify username',
    envvar='MB_SPOTIFY_USERNAME',
    default=DEFAULT_SPOTIFY_USERNAME,
    callback=config_string,
)

spotify_client_id_option = optgroup.option(
    '--spotify-client-id',
    help='Spotify client ID',
    envvar='MB_SPOTIFY_CLIENT_ID',
    default=DEFAULT_SPOTIFY_CLIENT_ID,
    callback=config_string,
)

spotify_client_secret_option = optgroup.option(
    '--spotify-client-secret',
    help='Spotify client secret',
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
    spotify_username_option,
    spotify_client_id_option,
    spotify_client_secret_option,
    spotify_cache_path_option,
    spotify_scope_option,
    spotify_redirect_uri_option,
    spotify_token_option,
)
